#Ba137_LoadSingle.py created 2020-08-26 20:29:28.755609

import numpy as np
import os
import sys
import glob
from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

ResetLasers = False

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")

MaxTrapAttempts = getGlobal("MaxTrapAttemps")

BGCountsProgram = "PMT_CheckCounts_For-Script_Ba137"
CountsProgram = "PMT_CheckCounts_For-Script_Ba137"
PulseAblationProgram = "PulseAblation_For-Script_Ba137_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba137"
CoolSweepsNum = 2
PulseEnergy = 140
IonizationPower = 80
WindowStart = 160
WindowWidth = 55


#Freq553 = round(541.43293 + 275e-6, 5)
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

if ResetLasers:
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation()  

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"TrappingSingleBa137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0 = GetDataFilePath(BaseFolder, filename0, NewFile=False)

IonTrapped = False
AttemptCount = 0
while not IonTrapped  and AttemptCount < MaxTrapAttempts:
    if scriptIsStopped():
        break
        
    FlushTrapRF(setScan, startScan, stopScan) 
    (BGydataAvg, BGydataStD) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)
  
    setScan(PulseAblationProgram)
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    NeutralCounts = data[1]
    stopScan()
    
    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
    stopScan()
    
    (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    IonTrapped = CheckIonTrappedNoIsotopeCycle(BGydataAvg, BGydataStD, ydataAvg, AttemptCount, "Ba137", getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    (Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)

if len(NeutralCounts) > 1:
    NeutralString = f"{np.mean(NeutralCounts)}, {np.std(NeutralCounts)}"
else:
    NeutralString = f"{NeutralCounts[0]}"
WriteString = f"Trapped after {AttemptCount} attempts, Ion counts: {ydataAvg}, {ydataStd} std, Neutral counts: {NeutralString}\n"
SaveDataToTextFile(filename0, WriteString)