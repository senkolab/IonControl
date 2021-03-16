import numpy as np
import os
import sys
import glob
import time
import numpy as np

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "Ion Direct Trap Pt1"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"

#Freq553 = round(541.43293 + 275e-6, 5)
CoolSweepsNum = 2

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

Filepath = r"Z:\Lab Data\Sessions\2020\2020_11\2020_11_20"
filename = "PMTCount169us_1mJ_rad_7o18734x_5o9006y.txt"

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

ExperimentCount = 0
Experiments = 1000
AttemptCount = 0
Attempts = 10

try:
    Existing_file = np.loadtxt(os.path.abspath(Filepath + "\\" + filename),delimiter = '\t')
    ExperimentCount = int(max(Existing_file[:,6]))
    AttemptStart = int(sum(Existing_file[:,6]==ExperimentCount))
except:
    AttemptStart = 0
    print('No file')

ExperimentStart = ExperimentCount
ExperimentBatch = ExperimentCount+10

(BGydataAvg1, BGydataStD1) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

setScan("Toggle_Beam_Samplers")
startScan(globalOverrides=list(), wait=True)

(BGydataAvg2, BGydataStD2) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

if BGydataAvg2 < BGydataAvg1:
    setScan("Toggle_Beam_Samplers")
    startScan(globalOverrides=list(), wait=True)

os.system('ssh pi@192.168.168.122 cd Documents; python press_stop_button.py')
time.sleep(4)
os.system('ssh pi@192.168.168.122 cd Documents; python press_start_button.py')

setScan(PulseAblationDummyProgram)
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
        
        (BGydataAvg, BGydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
    
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
        stopScan()
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        
        ydataAvg138 = ydataAvg
        ydataAvg136 = 0
        ydataAvg134 = 0
        ydataAvg132 = 0
        if ydataAvg > BGydataAvg + 3*BGydataStD:
            setScan(PulseAblationDummyProgram)
            startScan(globalOverrides=list(), wait=False)
            SweepCool493(Freq493, 3*CoolSweepsNum, getGlobal, setGlobal)
            stopScan()
            
            (ydataAvg138, ydataStD138) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            setGlobal("CoolingFreq",607.42614,"THz")
            setGlobal("RepumpFreq",461.31211,"THz")
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            FreqRepump = getGlobal("RepumpFreq")
            FreqRepump = str(FreqRepump)
            while FreqCool != "607.42614 THz":
                FreqCool = getGlobal("CoolingFreq")
                FreqCool = str(FreqCool)
                if scriptIsStopped():
                    break
            while FreqRepump != "461.31211 THz":
                FreqRepump = getGlobal("RepumpFreq")
                FreqRepump = str(FreqRepump)
                if scriptIsStopped():
                    break
            setScan(PulseAblationDummyProgram)
            startScan(globalOverrides=list(), wait=False)
            time.sleep(3)
            stopScan()
            (ydataAvg136, ydataStD136) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            setGlobal("CoolingFreq",607.42618,"THz")
            setGlobal("RepumpFreq",461.31221,"THz")
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            FreqRepump = getGlobal("RepumpFreq")
            FreqRepump = str(FreqRepump)
            while FreqCool != "607.42618 THz":
                FreqCool = getGlobal("CoolingFreq")
                FreqCool = str(FreqCool)
                if scriptIsStopped():
                    break
            while FreqRepump != "461.31221 THz":
                FreqRepump = getGlobal("RepumpFreq")
                FreqRepump = str(FreqRepump)
                if scriptIsStopped():
                    break
            setScan(PulseAblationDummyProgram)
            startScan(globalOverrides=list(), wait=False)
            time.sleep(3)
            stopScan()
            (ydataAvg134, ydataStD134) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            setGlobal("CoolingFreq",607.42624,"THz")
            setGlobal("RepumpFreq",461.31204,"THz")
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            FreqRepump = getGlobal("RepumpFreq")
            FreqRepump = str(FreqRepump)
            while FreqCool != "607.42624 THz":
                FreqCool = getGlobal("CoolingFreq")
                FreqCool = str(FreqCool)
                if scriptIsStopped():
                    break
            while FreqRepump != "461.31204 THz":
                FreqRepump = getGlobal("RepumpFreq")
                FreqRepump = str(FreqRepump)
                if scriptIsStopped():
                    break
            setScan(PulseAblationDummyProgram)
            startScan(globalOverrides=list(), wait=False)
            time.sleep(3)
            stopScan()
            (ydataAvg132, ydataStD132) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
            
            setGlobal("CoolingFreq",607.42596,"THz")
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            while FreqCool != "607.42596 THz":
                FreqCool = getGlobal("CoolingFreq")
                FreqCool = str(FreqCool)
                if scriptIsStopped():
                    break

        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        savetextfile.write(str(ydataAvg138) + "\t" + str(ydataAvg136) + "\t" + str(ydataAvg134) + "\t" + str(ydataAvg132) + "\t" + str(BGydataAvg) + "\t" + str(BGydataStD) + "\t" + str(ExperimentCount) + "\n")
        savetextfile.close()
        AttemptCount += 1
    ExperimentCount += 1