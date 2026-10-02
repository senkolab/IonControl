#Ablation-Paper-2021_LoadEff_Ba138-vs-PulsesPer.py created 2021-04-19 15:57:17.799771
import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

ResetLasers = bool(getGlobal("LasersReset"))

#Prepare script
CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
MaxTrapAttempts = getGlobal("MaxTrapAttemps")
FreqSetWaitTime = getGlobal("TimeSwitchLaserFreqWM")
BGNumStDevs = getGlobal("BGCheckNumStDevs")
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPer = int(getGlobal("AblationPulsesPer"))

#Parameters
BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Even_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
WindowStart = 160
WindowWidth = 55
PulseEnergy = 92
IonizationPower = 80
PulsesPerStart = 1
PulsesPerStop = 3
PulsesPerRes = 2
PulsesPer = np.arange(PulsesPerStart, PulsesPerStop+0.1, PulsesPerRes)

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)   
    ResetAblation(setScan, startScan, stopScan)

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "_14Hz_3Pulse"
filename0 = f"Load-Effic-PulseNum_Ba138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0)


WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,\
Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,\
Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt:{PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
WriteStringNeutral = "\tNeutralCounts\t"
WriteString += f"\nh,Time\tAttemptNum\tPulsesPer\tTrapped\tIonCounts138\tIonCounts138_std{WriteStringNeutral}\tBG\tBG_std"
SaveDataToTextFile(filename0, WriteString)

LoopsTotal = 50
LoopCount = 0
PulseCount = 0
AttemptCount = 0
while LoopCount < LoopsTotal:
    LoopCount += 1
    AttemptCount = 0
    if scriptIsStopped():
        break
    for PulsePer in PulsesPer:
        if scriptIsStopped():
            break
            
        if not getGlobal("AblationPulsesPer") == int(PulsePer):
            setGlobal("AblationPulsesPer", int(PulsePer), "")

        FlushTrapRF(setScan, startScan, stopScan)
        (BGydataAvg, BGydataStd) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)            
        
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        time.sleep(0.05)
        data = getAllData()['PMT Count'] #Returns all data associated with scan.
        NeutralCounts = data[1]
        stopScan()
        time.sleep(0.5)

        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
        stopScan()
        
        (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        AttemptCount += 1
        PulseCount += 1
        setGlobal("LoadAttempts", AttemptCount, "")

        if ydataAvg > BGydataAvg + BGNumStDevs*BGydataStd:
            IonTrapped = True
        else:
            IonTrapped = False
        
        if len(NeutralCounts) > 1:
            NeutralString = f"\t{np.mean(NeutralCounts):0.1f}\t{np.std(NeutralCounts):0.1f}"
        else:
            NeutralString = f"\t{NeutralCounts[0]:0.1f}"
        WriteString = f"{time.time()}\t{AttemptCount}\t{PulsePer}\t{IonTrapped}\t{ydataAvg:0.1f}\t{ydataStd:0.1f}{NeutralString}\t{BGydataAvg:0.1f}\t{BGydataStd:0.1f}"
        SaveDataToTextFile(filename0, WriteString)