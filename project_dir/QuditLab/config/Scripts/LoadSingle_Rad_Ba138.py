#Ba138_LoadSingle.py created 2020-08-26 20:29:28.755609

import numpy as np
import os
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

CurrLoadAttempts = getGlobal("LoadAttempts")
if int(CurrLoadAttempts) != 0:
    setGlobal("LoadAttempts", 0, "")
IonTrapped = False
MaxTrapAttempts = getGlobal("MaxTrapAttemps")

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Even_Rad"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"

#Freq553 = round(541.43293 + 275e-6, 5)
CoolSweepsNum = 2

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

#Get BG counts data
(BGydataAvg, BGydataStD) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)    

 
AttemptCount = 0
while not IonTrapped  and AttemptCount < MaxTrapAttempts:
    if scriptIsStopped():
        break
        
    FlushTrapRF(setScan, startScan, stopScan)
    setScan(PulseAblationProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
    stopScan()
    
    (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    AttemptCount += 1
    setGlobal("LoadAttempts", AttemptCount, "")
    
    IonTrapped = CheckIonTrapped(BGydataAvg, BGydataStD, ydataAvg, AttemptCount, "Ba138", getGlobal, setGlobal)