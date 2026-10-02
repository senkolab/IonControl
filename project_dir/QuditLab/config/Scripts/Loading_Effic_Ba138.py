#LoadEffic_Ba138.py created 2020-08-26 20:29:28.755609
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
PulsesPer = int(getGlobal("AblationPulsesPer"))

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Even_Nat"
#PulseAblationProgram = "PulseAblation_For-Script_Even_Nat_with_RF_Delay"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"

AblationPulsesPer = getGlobal("AblationPulsesPer")
TotalTrapping = 50
PulseEnergy = 110
IonizationPower = 10
#RFDelay = 175
WindowStart = 160
WindowWidth = 55

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
#addname = f"_{RFDelay:0.0f}usRFDelay"
addname = f"Previous-Trap-Params_405PowerIncrease"
#addname = ""
filename0 = f"Load-Effic_Ba138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,\
Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt:{PulsesPer}"
WriteString += ""#Extra data
if AblationPulsesPer > 1:
    WriteStringNeutral = "\tNeutralCounts\tNeutralCounts_std"
else:
    WriteStringNeutral = "\tNeutralCounts"
WriteString += f"\nh,Time\tAttemptNum\tIonCounts138\tIonCounts138_std{WriteStringNeutral}\tBG\tBG_std"
SaveDataToTextFile(filename0, WriteString)

TotalTrapped = 0
AttemptCount = 0

FlushTrapRF(setScan, startScan, stopScan)

while TotalTrapped < TotalTrapping and AttemptCount < MaxTrapAttempts:
    IonTrapped = False
    AttemptCount = 0
    (BGydataAvg, BGydataStd) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)   
    while not IonTrapped and AttemptCount < MaxTrapAttempts:
        if scriptIsStopped():
            break
            
        FlushTrapRF(setScan, startScan, stopScan)
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
        IonTrapped = CheckIonTrapped(BGydataAvg, BGydataStd, ydataAvg, AttemptCount, "Ba138", getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=False)
        AttemptCount += 1
        setGlobal("LoadAttempts", AttemptCount, "")
        if len(NeutralCounts) > 1:
            NeutralString = f"\t{np.mean(NeutralCounts):0.1f}\t{np.std(NeutralCounts):0.1f}"
        else:
            NeutralString = f"\t{NeutralCounts[0]:0.1f}"
        WriteString = f"{time.time()}\t{AttemptCount}\t{ydataAvg:0.1f}\t{ydataStd:0.1f}{NeutralString}\t{BGydataAvg:0.1f}\t{BGydataStd:0.1f}"
        SaveDataToTextFile(filename0, WriteString)
    TotalTrapped += 1