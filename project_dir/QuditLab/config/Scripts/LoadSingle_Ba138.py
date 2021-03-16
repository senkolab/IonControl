#Ba138_LoadSingle.py created 2020-08-26 20:29:28.755609

import numpy as np
import os
import sys
import glob
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

ResetAblationAndLasers = False

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
MaxTrapAttempts = getGlobal("MaxTrapAttemps")

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Even_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
CoolSweepsNum = 2
PulseEnergy = 140
IonizationPower = 80
WindowStart = 160
WindowWidth = 55

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

if ResetAblationAndLasers:
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation()

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Load-Effic-Spect_Ba138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0 = GetDataFilePath(BaseFolder, filename0, NewFile=False)

WriteString = "Metadata,IonizationFreq:%0.6f,CoolingFreq:%0.6f,RepumpFreq:%0.6f,WindowStart:%0.3f,WindowWidth:%0.3f,BG:%f,BGstd:%f"
Data = (Freq553, Freq493, Freq650, WindowStart, WindowWidth, BGydataAvg, BGydataStd)
SaveDataToTextFile(FilePath0, filename0, WriteString, Data)

IonTrapped = False
AttemptCount = 0
while not IonTrapped  and AttemptCount < MaxTrapAttempts:
    if scriptIsStopped():
        break
        
    FlushTrapRF(setScan, startScan, stopScan)
    (BGydataAvg, BGydataStd) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData) 

    setScan(PulseAblationProgram)
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    NeutralCounts = data[1]
    stopScan()

    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
    stopScan()
    
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    IonTrapped = CheckIonTrapped(BGydataAvg, BGydataStd, ydataAvg, AttemptCount, "Ba138", getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")

if len(NeutralCounts) > 1:
    NeutralString = f"{np.mean(NeutralCounts)}, {np.std(NeutralCounts)}"
else:
    NeutralString = f"{NeutralCounts[0]}"
WriteString = f"Trapped after {AttemptCount} attempts, Ion counts: {ydataAvg}, {ydataStd} std, Neutral counts: {NeutralString}\n"
SaveDataToTextFile(filename0, WriteString)