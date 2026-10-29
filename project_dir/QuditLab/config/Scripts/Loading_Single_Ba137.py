#Ba137_LoadSingle.py created 2020-08-26 20:29:28.755609

import numpy as np
import os
import sys
import glob
import time
from datetime import date

import datetime

Check_Ba138 = False

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
time_h_m_s =  datetime.datetime.now().strftime("%H%M%S")

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

ResetLasers = bool(getGlobal("LasersReset"))

Set8GHzSideband(8.101,-20,"ON")
#os.system(f'ssh pi@192.168.168.104 python ~/pll-evalboard-synthesizer/src/Control-Programs/mw1.py 4 8.15e9')

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

PulseEnergy = 110
IonizationPower = 10
WindowStart, WindowWidth = 160, 55

wait_before_checking_ion = 10 #secs

(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)
SetNeutralFluorWindow(WindowStart, WindowWidth, script_functions)

if ResetLasers:
    SendLasersToTrap(CountsProgram,script_functions)
    #ResetAblation(script_functions)  

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o088x_6o02y"
filename0 = f"TrappingSingleBa137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filenameNC = f"TrappingSingleBa137_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW_NeutralCounts_*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)
filenameNC, base_folderNC = GetDataFilePath(filenameNC, NewFile=False)

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt: {PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
SaveDataToTextFile(filename0, WriteString)


IonTrapped = False
AttemptCount = 0
Ba138_Counter = 0
setGlobal("Ba138_Positives", Ba138_Counter, "")
ZeroNeutralCount = 0

setEvaluation('Eval3')
while not IonTrapped  and AttemptCount < MaxTrapAttempts and ZeroNeutralCount < 20:
    if scriptIsStopped():
        WriteString = f"{time.strftime('%H:%M:%S', time.localtime())}\tNothing trapped after {AttemptCount} attempts\n"
        SaveDataToTextFile(filename0, WriteString)
        break

    # set 650 EOM freqs and sidebands
    #os.system(f'ssh pi@192.168.168.105 "cd /home/pi/pll-evalboard-synthesizer/src/Control-Programs/Pi5/ && ./PowersN770"')
    #os.system(f'ssh pi@192.168.168.105 "cd /home/pi/pll-evalboard-synthesizer/src/Control-Programs/Pi5/ && ./FreqsN770"')
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
    print(BGydataAvg, BGydataStD)
    #print(hdsuack)
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

    time_h_m_s =  datetime.datetime.now().strftime("%H:%M:%S")

    WriteStringNC = f"{time_h_m_s} - {NeutralCounts[0]:0.1f}\n"
    SaveDataToTextFile(filenameNC, WriteStringNC)

    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    #SweepCool493(Freq493, CoolSweepsNum, script_functions)
    SweepCool493650(Freq493, Freq650, CoolSweepsNum, script_functions)
    stopScan()

    time.sleep(wait_before_checking_ion)
    
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    IonTrapped = CheckIonTrappedHeadless(ydataAvg, ydataStd, AttemptCount, "Ba137", script_functions)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    
    if IonTrapped and Check_Ba138:
        Ba138_Present = Check_Ba138_Present(PulseAblationDummyProgram, 5.82, 4, script_functions)
        if Ba138_Present:
            IonTrapped = False
            Ba138_Counter +=1
            setGlobal("Ba138_Positives", Ba138_Counter, "")
    else:
        Ba138_Present = False
        
    #else:
    #?    pass
    # We need this in case we check for Ba138!
    Set8GHzSideband(8.101,-20,"ON")
    print("Attempts: ", AttemptCount, " Ba138 Count: ", Ba138_Counter)
    (Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)
    # end of if IonTrapped indent
    

    if IonTrapped and not Ba138_Present:
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493650(Freq493, Freq650, CoolSweepsNum, script_functions)
        stopScan()

        (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions, bg=False)
        IonTrapped = CheckIonTrappedWithBa138Check(ydataAvg, ydataStd, AttemptCount, Ba138_Counter, "Ba137", script_functions)

if CurrPMTInt != TrapPMTInt:
    setGlobal("PMT_Integration_Time", CurrPMTInt, 'ms')
setEvaluation('Eval2')

if len(NeutralCounts) > 1:
    NeutralString = f"{np.mean(NeutralCounts):0.1f}, {np.std(NeutralCounts):0.1f}"
else:
    NeutralString = f"{NeutralCounts[0]:0.1f}"

if IonTrapped:
    WriteString = f"{time.strftime('%H:%M:%S', time.localtime())}\tTrapped after {AttemptCount} attempts, Ion counts: {ydataAvg:0.1f}, \
    {ydataStd:0.1f} std, Neutral counts: {NeutralString}\n"
    SaveDataToTextFile(filename0, WriteString)
    CurrWhichIon = int(getGlobal("WhichIon").magnitude)
    if not CurrWhichIon == 137:
        setGlobal("WhichIon", 137, "")
else:
    WriteString = f"{time.strftime('%H:%M:%S', time.localtime())}\tNothing trapped after {AttemptCount} attempts\n"
    SaveDataToTextFile(filename0, WriteString)