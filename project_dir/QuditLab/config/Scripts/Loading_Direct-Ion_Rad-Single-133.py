#Direct_Ion_Load_Rad_Single_133.py created 2021-09-29 00:02:01.371880

import numpy as np
import os
import sys
import glob
import time
import numpy as np

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

CountsProgramBa133 = "PMT_CheckCounts_For-Script_Ba133"
CountsProgramEven = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgramBa133 = "Ion Direct Trap Ba133"
PulseAblationDummyProgramBa133 = "PulseAblation_For-Script_Dummy_Ba133"
PulseAblationDummyProgramEven = "PulseAblation_For-Script_Dummy_Ba138"

#Freq553 = round(541.43293 + 275e-6, 5)
CoolSweepsNum = 2

#(Freq493_Ba132, Freq650_Ba132, Freq553_Ba132) = SetGlobalLaserFreqs("Ba132", getGlobal, setGlobal)
#(Freq493_Ba134, Freq650_Ba134, Freq553_Ba134) = SetGlobalLaserFreqs("Ba134", getGlobal, setGlobal)
#(Freq493_Ba136, Freq650_Ba136, Freq553_Ba136) = SetGlobalLaserFreqs("Ba136", getGlobal, setGlobal)
#(Freq493_Ba138, Freq650_Ba138, Freq553_Ba138) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

(Freq493_Ba133, Freq650_Ba133, Freq553_Ba133) = SetGlobalLaserFreqs("Ba133", getGlobal, setGlobal)

Filepath = r"Z:\Lab Data\Sessions\2021\2021_10\2021_10_13\Ba133_Loading"
filename = "PMTCount169us_800uJ_rad_7o18x_5o91y_Single.txt"

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

ExperimentCount = 0
Experiments = 1
AttemptCount = 0
Attempts = 1000

try:
    Existing_file = np.loadtxt(os.path.abspath(Filepath + "\\" + filename),delimiter = '\t')
    ExperimentCount = int(max(Existing_file[:,9]))
    AttemptStart = int(sum(Existing_file[:,9]==ExperimentCount))
except:
    AttemptStart = 0
    print('No file')

ExperimentStart = ExperimentCount
ExperimentBatch = ExperimentCount+10

SendLasersToTrap(CountsProgramEven,setScan,startScan,stopScan,getAllData)
ResetAblation(setScan, startScan, stopScan)

setScan(PulseAblationDummyProgramEven)
startScan(globalOverrides=list(), wait=False)
time.sleep(2)
stopScan()            

while ExperimentCount < min(ExperimentBatch,Experiments):
    if scriptIsStopped():
        break
    AttemptCount = 0
    if ExperimentCount == ExperimentStart:
        AttemptCount = AttemptStart
    while AttemptCount < Attempts:
           
        FlushTrapRF(setScan, startScan, stopScan)
        
        (BGydataAvg, BGydataStD) = GetPMTCounts(CountsProgramBa133, setScan, startScan, stopScan, getAllData)
    
        setScan(PulseAblationProgramBa133)
        startScan(globalOverrides=list(), wait=True)
        
        setScan(PulseAblationDummyProgramBa133)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493_Ba133, CoolSweepsNum, getGlobal, setGlobal)
        stopScan()
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgramBa133, setScan, startScan, stopScan, getAllData)
        
        ydataAvg133_init = ydataAvg
        
        ydataAvg138_init = 0
        ydataAvg133 = 0
        ydataAvg138 = 0
        ydataAvg136 = 0
        ydataAvg134 = 0
        ydataAvg132 = 0
        
        if ydataAvg133_init > BGydataAvg + 3*BGydataStD or ydataAvg138_init > BGydataAvg + 3*BGydataStD:
            AttemptCount = Attempts+1
            ExperimentCount = Experiments+1
            break

        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        savetextfile.write(str(ydataAvg133_init) + "\t" + str(ydataAvg138_init) + "\t" + str(ydataAvg133) + "\t" + str(ydataAvg138) + "\t" + str(ydataAvg136) + "\t" + str(ydataAvg134) + "\t" + str(ydataAvg132) + "\t" + str(BGydataAvg) + "\t" + str(BGydataStD) + "\t" + str(ExperimentCount) + "\n")
        savetextfile.close()
        AttemptCount += 1
    ExperimentCount += 1