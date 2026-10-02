#Ablation-paper-2021_LoadEffec138_vs_553freq.py created 2021-02-02 10:13:28.951159
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
PulseEnergy = 100
IonizationPower = 8
Scan553Start = -40*1e-6
Scan553End = 40*1e-6
Scan553Res = 5*1e-6

Freqs553 = np.arange(Scan553Start, Scan553End+1e-9, Scan553Res)
(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
Freqs553 += Freq553
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
filename0 = f"Load-Effic-Spect_Ba138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0)


WriteString = f"Metadata,Ionization Freqs.:{Freq553:0.6f} {Scan553Start*1e6:0.0f} {Scan553End*1e6:0.0f} {Scan553Res*1e6:0.0f}:THz MHz,\
Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,\
Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt:{PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
if PulsesPer > 1:
    WriteStringNeutral = "\tNeutralCounts\tNeutralCounts_std"
else:
    WriteStringNeutral = "\tNeutralCounts"
WriteString += f"\nh,Time\tAttemptNum\tIonizationFreq\tTrapped\tIonCounts138\tIonCounts138_std{WriteStringNeutral}\tBG\tBG_std"
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
    for Freq in Freqs553:
        if scriptIsStopped():
            break
            
        if not "%s"%getGlobal("IonizationFreq") == "%s THz"%Freq:
            setScan(PulseAblationDummyProgram)
            startScan(globalOverrides=list(), wait=False)
            setGlobal("IonizationFreq", Freq, "THz")
            time.sleep(FreqSetWaitTime)
            stopScan()

        FlushTrapRF(setScan, startScan, stopScan)
        (BGydataAvg, BGydataStd) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)            
        
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        time.sleep(0.05)
        data = getAllData()['PMT Count'] #Returns all data associated with scan.
        NeutralCounts = data[1]
        stopScan()

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
        WriteString = f"{time.time()}\t{AttemptCount}\t{Freq:0.6f}\t{IonTrapped}\t{ydataAvg:0.1f}\t{ydataStd:0.1f}{NeutralString}\t{BGydataAvg:0.1f}\t{BGydataStd:0.1f}"
        SaveDataToTextFile(filename0, WriteString)