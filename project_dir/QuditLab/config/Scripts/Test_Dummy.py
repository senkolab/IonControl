#Test_Dummy.py created 2020-11-12 13:02:15.900256

import numpy as np
import os
import sys
import glob
import time

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "Ion Direct Trap Pt1"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"

#Freq553 = round(541.43293 + 275e-6, 5)
CoolSweepsNum = 2

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

Filepath = r"Z:\Lab Data\Sessions\2020\2020_11\2020_11_12"
filename = "PMTCount_Debug_Dummy.txt"
 
ExperimentCount = 0
Experiments = 375
AttemptCount = 0
Attempts = 10

while ExperimentCount < Experiments:
    if scriptIsStopped():
        break
    AttemptCount = 0
    if ExperimentCount == -1:
        AttemptCount = 5
    while AttemptCount < Attempts:
        print('Script Start \n')
        global_vars = list(globals().items())
        for var, obj in global_vars:
            print(var, sys.getsizeof(obj))
        if scriptIsStopped():
            break
            
        FlushTrapRF(setScan, startScan, stopScan)
        
        #(BGydataAvg, BGydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        
        setScan(PulseAblationDummyProgram)
        #startScan(globalOverrides=list(), wait=False)
        #SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
        #stopScan()
        #FreqCool = getGlobal("CoolingFreq")
        #FreqCool = str(FreqCool)
        #while FreqCool != "607.42596 THz":
        #    FreqCool = getGlobal("CoolingFreq")
        #    FreqCool = str(FreqCool)
        #    if scriptIsStopped():
        #        break
        #(ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        
        #ydataAvg138 = ydataAvg
        #ydataAvg136 = 0
        #ydataAvg134 = 0
        #ydataAvg132 = 0
        #if ydataAvg > BGydataAvg + 3*BGydataStD:
        #    setScan(PulseAblationDummyProgram)
            #startScan(globalOverrides=list(), wait=False)
            #SweepCool493(Freq493, 3*CoolSweepsNum, getGlobal, setGlobal)
            #stopScan()
            
            #FreqCool = getGlobal("CoolingFreq")
            #FreqCool = str(FreqCool)
            #while FreqCool != "607.42596 THz":
            #    FreqCool = getGlobal("CoolingFreq")
            #    FreqCool = str(FreqCool)
            #    if scriptIsStopped():
            #        break

        #    (ydataAvg138, ydataStD138) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            #setGlobal("CoolingFreq",607.42614,"THz")
            #setGlobal("RepumpFreq",461.31211,"THz")
            #FreqCool = getGlobal("CoolingFreq")
            #FreqCool = str(FreqCool)
            #FreqRepump = getGlobal("RepumpFreq")
            #FreqRepump = str(FreqRepump)
            #while FreqCool != "607.42614 THz":
            #    FreqCool = getGlobal("CoolingFreq")
            #    FreqCool = str(FreqCool)
            #    if scriptIsStopped():
            #        break
            #while FreqRepump != "461.31211 THz":
            #    FreqRepump = getGlobal("RepumpFreq")
            #    FreqRepump = str(FreqRepump)
            #    if scriptIsStopped():
            #        break
        #    setScan(PulseAblationDummyProgram)
        #    startScan(globalOverrides=list(), wait=False)
        #    time.sleep(1)
        #    stopScan()
        #    (ydataAvg136, ydataStD136) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            #setGlobal("CoolingFreq",607.42618,"THz")
            #setGlobal("RepumpFreq",461.31221,"THz")
            #FreqCool = getGlobal("CoolingFreq")
            #FreqCool = str(FreqCool)
            #FreqRepump = getGlobal("RepumpFreq")
            #FreqRepump = str(FreqRepump)
            #while FreqCool != "607.42618 THz":
            #    FreqCool = getGlobal("CoolingFreq")
            #    FreqCool = str(FreqCool)
            #    if scriptIsStopped():
            #        break
            #while FreqRepump != "461.31221 THz":
            #    FreqRepump = getGlobal("RepumpFreq")
            #    FreqRepump = str(FreqRepump)
            #    if scriptIsStopped():
            #        break
        #    setScan(PulseAblationDummyProgram)
        #    startScan(globalOverrides=list(), wait=False)
        #    time.sleep(1)
        #    stopScan()
        #    (ydataAvg134, ydataStD134) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            #setGlobal("CoolingFreq",607.42624,"THz")
            #setGlobal("RepumpFreq",461.31204,"THz")
            #FreqCool = getGlobal("CoolingFreq")
            #FreqCool = str(FreqCool)
            #FreqRepump = getGlobal("RepumpFreq")
            #FreqRepump = str(FreqRepump)
            #while FreqCool != "607.42624 THz":
            #    FreqCool = getGlobal("CoolingFreq")
            #    FreqCool = str(FreqCool)
            #    if scriptIsStopped():
            #        break
            #while FreqRepump != "461.31204 THz":
            #    FreqRepump = getGlobal("RepumpFreq")
            #    FreqRepump = str(FreqRepump)
            #    if scriptIsStopped():
            #        break
        #    setScan(PulseAblationDummyProgram)
        #    startScan(globalOverrides=list(), wait=False)
        #    time.sleep(1)
        #    stopScan()
        #    (ydataAvg132, ydataStD132) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            #setGlobal("CoolingFreq",607.42596,"THz")
            #FreqCool = getGlobal("CoolingFreq")
            #FreqCool = str(FreqCool)
            #while FreqCool != "607.42596 THz":
            #    FreqCool = getGlobal("CoolingFreq")
            #    FreqCool = str(FreqCool)
            #    if scriptIsStopped():
            #        break
        #try:
        #    save_file
        #except:
        #    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        
        #if not save_file:
        #    savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        #else:
        #    savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        #savetextfile.write(str(ydataAvg138) + "\t" + str(ydataAvg136) + "\t" + str(ydataAvg134) + "\t" + str(ydataAvg132) + "\t" + str(BGydataAvg) + "\t" + str(BGydataStD) + "\t" + str(ExperimentCount) + "\n")
        #savetextfile.close()
        AttemptCount += 1
    ExperimentCount += 1