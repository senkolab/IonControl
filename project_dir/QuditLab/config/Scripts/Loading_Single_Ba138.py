#Ba138_LoadSingle.py created 2020-08-26 20:29:28.755609

import numpy as np
import os
import sys
import glob
import time
import gc

from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

ResetLasers = bool(getGlobal("LasersReset"))

Set8GHzSideband(5.82,-5,"ON")
#os.system(f'ssh pi@192.168.168.104 python ~/pll-evalboard-synthesizer/src/Control-Programs/mw1.py 4 6.92e9')

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
MaxTrapAttempts = getGlobal("MaxTrapAttemps")
BGNumStDevs = getGlobal("BGCheckNumStDevs")
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPer = SetPulsesPer(138, script_functions)
CurrPMTInt = getGlobal("PMT_Integration_Time").magnitude #ms
TrapPMTInt = getGlobal("PMT_Integration_Time_Trapping").magnitude #ms
if CurrPMTInt != TrapPMTInt:
    setGlobal("PMT_Integration_Time", TrapPMTInt, 'ms')

TrapRF_bool = getGlobal("TrapRFEnable")
if TrapRF_bool != 1:
    setGlobal("TrapRFEnable", True, '')

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Even_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"

PulseEnergy = 110
IonizationPower = 10
WindowStart, WindowWidth = 160, 55

(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", script_functions)
SetNeutralFluorWindow(WindowStart, WindowWidth, script_functions)

FlushTrapRF(script_functions)

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,script_functions)
ResetAblation(script_functions) # was in if block above previously

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o175x_6o07y_newscale"
filename0 = f"TrappingSingleBa138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filenameNC = f"TrappingSingleBa138_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW_NeutralCounts_{addname}_*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)
filenameNC, base_folder = GetDataFilePath(filenameNC, NewFile=False)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt: {PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
SaveDataToTextFile(filename0, WriteString)

IonTrapped = False
AttemptCount = 0
ZeroNeutralCount = 0
while not IonTrapped  and AttemptCount < MaxTrapAttempts and ZeroNeutralCount < 10:
    if scriptIsStopped():
        if CurrPMTInt != TrapPMTInt:
            setGlobal("PMT_Integration_Time", CurrPMTInt, 'ms')
        WriteString = f"{time.strftime('%H:%M:%S', time.gmtime())}\tNone trapped after {AttemptCount} attempts\n"
        SaveDataToTextFile(filename0, WriteString)
        break
        
    if AttemptCount == 0:
        AblationPulsesDummy = getGlobal("AblationPulsesDummy")
        if AblationPulsesDummy != 1:
            setGlobal("AblationPulsesDummy", 1, "")
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        stopScan()
        if AblationPulsesDummy != 1:
            setGlobal("AblationPulsesDummy", AblationPulsesDummy, "")
        #AttemptCount += 1
    FlushTrapRF(script_functions)
    
    (BGydataAvg, BGydataStd) = GetPMTCounts(BGCountsProgram, script_functions, bg=True) 

    setScan(PulseAblationProgram)
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    NeutralCounts = data[1]
    stopScan()

    print(f"\n Neutral counts is:{NeutralCounts[0]}\n")
    if NeutralCounts[0] <= 0.1:
        ZeroNeutralCount += 1
    else:
        ZeroNeutralCount = 0
    WriteStringNC = f"{NeutralCounts[0]:0.1f}\n"
    SaveDataToTextFile(filenameNC, WriteStringNC)

    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493650(Freq493, Freq650, CoolSweepsNum, script_functions)
    #SweepCool493(Freq493, CoolSweepsNum, script_functions)

    stopScan()
    
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    IonTrapped = CheckIonTrappedNoIsotopeCycle(ydataAvg, ydataStd, AttemptCount, "Ba138", script_functions)
    gc.collect()
if CurrPMTInt != TrapPMTInt:
    setGlobal("PMT_Integration_Time", CurrPMTInt, 'ms')

if len(NeutralCounts) > 1:
    NeutralString = f"{np.mean(NeutralCounts):0.1f}, {np.std(NeutralCounts):0.1f}"
else:
    NeutralString = f"{NeutralCounts[0]:0.1f}"
if IonTrapped:
    WriteString = f"{time.strftime('%H:%M:%S', time.localtime())}\tTrapped after {AttemptCount} attempts, Ion counts: {ydataAvg:0.1f}, {ydataStd:0.1f} std, Neutral counts: {NeutralString}\n"
    SaveDataToTextFile(filename0, WriteString)
    CurrWhichIon = int(getGlobal("WhichIon").magnitude)
    if not CurrWhichIon == 138:
        setGlobal("WhichIon", 138, "")
else:
    WriteString = f"{time.strftime('%H:%M:%S', time.gmtime())}\tNone trapped after {AttemptCount} attempts\n"
    SaveDataToTextFile(filename0, WriteString)