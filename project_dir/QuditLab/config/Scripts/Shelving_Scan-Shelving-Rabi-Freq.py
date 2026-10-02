#Scan_Shelving_Rabi_Freq.py created 2022-01-12 12:00:58.990537

import numpy as np
import os
import sys
import glob
import time

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseShelvingProgram = "Shelving_Pulse_Even"
PulseRepumpProgram = "Repump_Shelve_Even"

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

Filepath = r"Z:\Lab Data\Sessions\2022\2022_01\2022_01_12\Shelving_Rabi_Freq_Scan_02"
filename = "Shelving_Rabi_Freq_Scan_600010000Hz"

#EOM_Shift = getGlobal("EOM_1762_Freq")
#EOM_Shift = int(EOM_Shift)

#filename = filename + f"_{EOM_Shift}Hz"

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

ExperimentCount = 0
Experiments = 1000

TimeArray = np.arange(0,100,1)

(BGydataAvg1, BGydataStD1) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)

savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_BGCount.txt"),'w+')
savetextfile.write(str(BGydataAvg1))
savetextfile.close()

for PulseTime in TimeArray:
    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_Time.txt"))
        
    if not save_file:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_Time.txt"),'w+')
    else:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_Time.txt"),'a+')
    savetextfile.write(str(PulseTime) + "\t")
    savetextfile.close()

ydataAvg = 0
RepumpCount = 0

while ExperimentCount < Experiments:
    if scriptIsStopped():
        break
    if RepumpCount >=20:
            break
    for PulseTime in TimeArray:
        if scriptIsStopped():
            break
        
        RepumpCount = 0
        while ydataAvg < BGydataAvg1 + 5*BGydataStD1 and RepumpCount < 20:
            if scriptIsStopped():
                break
            setScan(PulseRepumpProgram)
            startScan(globalOverrides=list(), wait=True)
            (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            RepumpCount = RepumpCount + 1
        
        if RepumpCount >=20:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_RepumpFail.txt"),'w+')
            savetextfile.write("Repump failed after 20 attempts.")
            savetextfile.close()
            break

        PulseTimeVar = getGlobal("Shelving_Pulse_Time")
        
        if not "%s"%PulseTimeVar == "%s ms"%PulseTime:
            setGlobal("Shelving_Pulse_Time", PulseTime, "ms") 
        
        setScan(PulseShelvingProgram)
        startScan(globalOverrides=list(), wait=True)
        
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_data.txt"))
        
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_data.txt"),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_data.txt"),'a+')
        savetextfile.write(str(ydataAvg) + "\t")
        savetextfile.close()

    ExperimentCount = ExperimentCount + 1

    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_data.txt"))
       
    if not save_file:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_data.txt"),'w+')
    else:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_data.txt"),'a+')
    savetextfile.write("\n")
    savetextfile.close()