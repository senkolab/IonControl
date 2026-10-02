#Ablation-Paper-2021_LoadTime_Ba137.py created 2021-04-12 15:11:54.324236
import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

ResetLasers = bool(getGlobal("LasersReset"))

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
MaxTrapAttempts = getGlobal("MaxTrapAttemps")
BGNumStDevs = getGlobal("BGCheckNumStDevs")
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPerAttempt = int(getGlobal("Ba137PulsesPerAttempt").magnitude)

BGCountsProgram = "PMT_CheckCounts_For-Script_Ba137"
CountsProgram = "PMT_CheckCounts_For-Script_Ba137"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Ba137_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba137"
TotalTrapping = 10
PulseEnergy = 140
IonizationPower = 110
WindowStart = 160
WindowWidth = 55

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation(setScan, startScan, stopScan)
  

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Load-Time_Ba137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,\
Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,\
Cooling Sweeps Num:{CoolSweepsNum}:Sweeps,Pulses Per Attempt: {PulsesPerAttempt:0.0f}:pulses"
WriteString += ""#Extra metadata from Ba137 trapping
#if PulsesPer > 1:
#    WriteStringNeutral = "\tNeutralCounts\tNeutralCounts_std"
#else:
WriteStringNeutral = "\tNeutralCounts"
WriteString += f"\nh,Time\tAttemptNum\tIonCounts137\tIonCounts137_std{WriteStringNeutral}\tBG\tBG_std"
SaveDataToTextFile(filename0, WriteString)

TotalTrapped = 0
AttemptCount = 0
IonTrapped = False
while TotalTrapped < TotalTrapping and AttemptCount < MaxTrapAttempts:
    if scriptIsStopped():
        break
    if IonTrapped:
        AttemptCount = 0
    IonTrapped = False
    NeutralCounts = []
    FlushTrapRF(setScan, startScan, stopScan)
    (BGydataAvg, BGydataStd) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData) 
    for PulseNum in range(PulsesPerAttempt):
        if scriptIsStopped():
            break
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        data = getAllData()['PMT Count'] #Returns all data associated with scan.
        NeutralCount = data[1]
        stopScan()
        NeutralCounts.append(NeutralCount)
        if not "%s"%getGlobal("AblationPulsesDummy") == "%s us"%4:
            setGlobal("AblationPulsesDummy", 4, "")
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, 1, getGlobal, setGlobal)
        stopScan()
    if not "%s"%getGlobal("AblationPulsesDummy") == "%s us"%10:
        setGlobal("AblationPulsesDummy", 10, "")
    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
    stopScan()
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    IonTrapped = CheckIonTrappedNoIsotopeCycle(BGydataAvg, BGydataStd, ydataAvg, AttemptCount, "Ba137", getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=False)
    if IonTrapped:
        TotalTrapped += 1
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    (Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
    if len(NeutralCounts) > 1:
        NeutralString = f"\t{np.mean(NeutralCounts):0.1f}\t{np.std(NeutralCounts):0.1f}"
    else:
        NeutralString = f"\t{NeutralCounts[0]:0.1f}"
    WriteString = f"{time.time()}\t{AttemptCount}\t{ydataAvg:0.1f}\t{ydataStd:0.1f}{NeutralString}\t{BGydataAvg:0.1f}\t{BGydataStd:0.1f}"
    SaveDataToTextFile(filename0, WriteString)