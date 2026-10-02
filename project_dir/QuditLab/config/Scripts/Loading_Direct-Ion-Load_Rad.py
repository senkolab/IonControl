import numpy as np
import os
import sys
import glob
import time
import numpy as np
import datetime

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

filename = f"PMTCount161us_75uJ_rad_7o19x_6o15y_{dt_string}.txt"
Filepath = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}'

CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "Ion Direct Trap Pt1"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
CoolSweepsNum = 2

(Freq493, Freq650, Freq553, freq614) = SetGlobalLaserFreqs("Ba138", script_functions)

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

ExperimentCount = 0
Experiments = 5
AttemptCount = 0
Attempts = 10
AttemptStart = 0

ExperimentStart = ExperimentCount
ExperimentBatch = ExperimentCount+10

(BGydataAvg1, BGydataStD1) = GetPMTCounts(CountsProgram, script_functions)

setScan("Toggle_Beam_Samplers")
startScan(globalOverrides=list(), wait=True)

(BGydataAvg2, BGydataStD2) = GetPMTCounts(CountsProgram, script_functions)

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
        #Set8GHzSideband(5.82,10,"ON")
        FlushTrapRF(script_functions)
        
        (BGydataAvg, BGydataStD) = GetPMTCounts(CountsProgram, script_functions)
    
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, CoolSweepsNum, script_functions)
        stopScan()
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, script_functions)
        
    
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, 3*CoolSweepsNum, script_functions)
        stopScan()
        
        (ydataAvg138, ydataStD138) = GetPMTCounts(CountsProgram, script_functions)


        setGlobal("CoolingFreq",607.43189,"THz")
        setGlobal("RepumpFreq",461.3121,"THz")
        FreqCool = getGlobal("CoolingFreq")
        FreqCool = str(FreqCool)
        FreqRepump = getGlobal("RepumpFreq")
        FreqRepump = str(FreqRepump)
        if FreqCool != "607.43189 THz":
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            if scriptIsStopped():
                break
        if FreqRepump != "461.3121 THz":
            FreqRepump = getGlobal("RepumpFreq")
            FreqRepump = str(FreqRepump)
            if scriptIsStopped():
                break
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        time.sleep(3)
        stopScan()
        (ydataAvg136, ydataStD136) = GetPMTCounts(CountsProgram, script_functions)
        print('printing 138',(ydataAvg136, ydataStD136))
        '''
        Set8GHzSideband(8.1,10,"ON")
        setGlobal("CoolingFreq",607.43192,"THz")
        setGlobal("RepumpFreq",461.31133,"THz")
        FreqCool = getGlobal("CoolingFreq")
        FreqCool = str(FreqCool)
        FreqRepump = getGlobal("RepumpFreq")
        FreqRepump = str(FreqRepump)
        if FreqCool != "607.43192 THz":
            FreqCool = getGlobal("CoolingFreq")
            FreqCool = str(FreqCool)
            if scriptIsStopped():
                break
        if FreqRepump != "461.31133 THz":
            FreqRepump = getGlobal("RepumpFreq")
            FreqRepump = str(FreqRepump)
            if scriptIsStopped():
                break
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        time.sleep(3)
        stopScan()
        (ydataAvg134, ydataStD134) = GetPMTCounts(CountsProgram, script_functions)
        print('printing 137',(ydataAvg134, ydataStD134))

        '''
        save_file = glob.glob(os.path.abspath(f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}' + "\\" + filename))
        
        if not save_file:
            savetextfile = open(os.path.abspath(f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}' + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}' + "\\" + filename),'a+')
        savetextfile.write(str(ydataAvg138) + "\t" + str(ydataAvg136) + "\t" + str(BGydataAvg) + "\n")
        savetextfile.close()
        AttemptCount += 1
    ExperimentCount += 1
