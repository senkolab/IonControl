#C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts.py created 2023-05-01 13:48:02.583774

import numpy as np
import os
import sys
import glob
import time
from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

ResetLasers = bool(getGlobal("LasersReset"))

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
MaxTrapAttempts = getGlobal("MaxTrapAttemps")
BGNumStDevs = getGlobal("BGCheckNumStDevs")
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPer = SetPulsesPer(137, script_functions)
CurrPMTInt = getGlobal("PMT_Integration_Time").magnitude #ms
TrapPMTInt = getGlobal("PMT_Integration_Time_Trapping").magnitude #ms
if CurrPMTInt != TrapPMTInt:
    setGlobal("PMT_Integration_Time", TrapPMTInt, 'ms')

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Ba137"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Ba137_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba137"

PulseEnergy = 140
IonizationPower = 10
WindowStart, WindowWidth = 160, 55


(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)
SetNeutralFluorWindow(WindowStart, WindowWidth, script_functions)

if ResetLasers:
    SendLasersToTrap(CountsProgram,script_functions)
    ResetAblation(script_functions)  

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o22x_6o11y_4A-BField"
filename0 = f"TrappingSingleBa137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filenameNC = f"TrappingSingleBa137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW_NeutralCounts_*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)
filenameNC, base_folderNC = GetDataFilePath(filenameNC, NewFile=False)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt: {PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
SaveDataToTextFile(filename0, WriteString)

IonTrapped = False
AttemptCount = 0
ZeroNeutralCount = 0
setEvaluation('Eval3')
while not IonTrapped  and AttemptCount < MaxTrapAttempts and ZeroNeutralCount < 20:
    if scriptIsStopped():
        WriteString = f"{time.strftime('%H:%M:%S', time.gmtime())}\tNothing trapped after {AttemptCount} attempts\n"
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

    (BGydataAvg, BGydataStD) = GetPMTCounts(BGCountsProgram, script_functions, bg=True)
  
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
    SweepCool493(Freq493, CoolSweepsNum, script_functions)
    stopScan()
    
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    IonTrapped = CheckIonTrappedNoIsotopeCycle(ydataAvg, ydataStd, AttemptCount, "Ba137", script_functions)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    (Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)
if CurrPMTInt != TrapPMTInt:
    setGlobal("PMT_Integration_Time", CurrPMTInt, 'ms')
setEvaluation('Eval2')

if len(NeutralCounts) > 1:
    NeutralString = f"{np.mean(NeutralCounts):0.1f}, {np.std(NeutralCounts):0.1f}"
else:
    NeutralString = f"{NeutralCounts[0]:0.1f}"

if IonTrapped:
    WriteString = f"{time.strftime('%H:%M:%S', time.localtime())} {AttemptCount} {ydataAvg:0.1f} {NeutralString}\n"
    SaveDataToTextFile(filename0, WriteString)
    CurrWhichIon = int(getGlobal("WhichIon").magnitude)
    if not CurrWhichIon == 137:
        setGlobal("WhichIon", 137, "")
else:
    WriteString = f"{time.strftime('%H:%M:%S', time.gmtime())}\tNothing trapped after {AttemptCount} attempts\n"
    SaveDataToTextFile(filename0, WriteString)
