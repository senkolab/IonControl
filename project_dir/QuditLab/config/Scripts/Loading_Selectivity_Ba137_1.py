#Ablation-Paper-2021_Isotope-Selectivity-Ba137.py created 2021-01-19 10:19:09.273933
import numpy as np
import os
import sys
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

CountsProgram = "PMT_CheckCounts_For-Script_Ba137"
BGCountsProgram = "PMT_CheckCounts_For-Script_Ba137"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Ba137_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba137"
Experiments = 50
PulseEnergy = 140
IonizationPower = 80
WindowStart = 160
WindowWidth = 55

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation(setScan, startScan, stopScan)

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Isotope-Select_Ba137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,\
Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt:{PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
if PulsesPer > 1:
    WriteStringNeutral = "\tNeutralCounts\tNeutralCounts_std"
else:
    WriteStringNeutral = "\tNeutralCounts"
WriteString += f"\nh,Time\tAttemptNum\tTrapped\tIonCounts137\tIonCounts137_std\tIonCounts138\
\tIonCounts138_std\tIonCounts136\tIonCounts136_std\tIonCounts134\tIonCounts134_std{WriteStringNeutral}\tBG\tBG_std"
SaveDataToTextFile(filename0, WriteString)

TimesTrapped = 0
AttemptCount = 0
while TimesTrapped < Experiments and AttemptCount < MaxTrapAttempts:
    AttemptCount = 0
    IonTrapped = False
    Ba137Trapped = False
    Ba134Trapped = False
    Ba136Trapped = False
    Ba138Trapped = False
    while not IonTrapped and AttemptCount < MaxTrapAttempts:
        if scriptIsStopped():
            break

        FlushTrapRF(setScan, startScan, stopScan)
        (BGyAvg, BGyStd) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)    
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        data = getAllData()['PMT Count'] #Returns all data associated with scan.
        NeutralCounts = data[1]
        stopScan()

        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
        stopScan()
        #Check for different isotopes
        (IonTrapped, Ba137, Ba134, Ba136, Ba138) = CheckIonIsotopeSelectivity(BGyAvg, BGyStd, BGNumStDevs, getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=True)
        #Unpack and save data
        Ba137Avg, Ba137Std, Ba137Trapped = Ba137
        Ba134Avg, Ba134Std, Ba134Trapped = Ba134
        Ba136Avg, Ba136Std, Ba136Trapped = Ba136
        Ba138Avg, Ba138Std, Ba138Trapped = Ba138
        if len(NeutralCounts) > 1:
            NeutralString = f"\t{np.mean(NeutralCounts):0.1f}\t{np.std(NeutralCounts):0.1f}"
        else:
            NeutralString = f"\t{NeutralCounts[0]:0.1f}"
        WriteString = f"{time.time()}\t{AttemptCount}\t{IonTrapped}\t{Ba137Avg:0.1f}\t{Ba137Std:0.1f}\
\t{Ba138Avg:0.1f}\t{Ba138Std:0.1f}\t{Ba136Avg:0.1f}\t{Ba136Std:0.1f}\t{Ba134Avg:0.1f}\t{Ba134Std:0.1f}{NeutralString}\t{BGyAvg:0.1f}\t{BGyStd:0.1f}"
        SaveDataToTextFile(filename0, WriteString)
        AttemptCount += 1
        setGlobal("LoadAttempts", AttemptCount, "")
        (Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
    if IonTrapped:
        TimesTrapped += 1