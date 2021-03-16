#Ablation-Paper-2021_TOF-Spectroscopy.py created 2020-11-23 12:33:01.652170

import numpy as np
import os
import sys
import glob
import time

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

NeutralFluorescenceProgram = "Ablation_For-Script_NeutralFluorescence_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
WindowStartGlobal = "NeutralFluorescenceWindowStart"
WindowWidthGlobal = "NeutralFluorescenceWindowWidth"
FreqSetWaitTime = getGlobal("TimeSwitchLaserFreqWM")

def NeutralFluoresencePulse(NeutProgram, setScan, startScan, stopScan, getAllData):
    setScan(NeutProgram)
    startScan(globalOverrides=list(), wait=True)
    time.sleep(0.05)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    ydataAvg = np.mean(np.array(ydata))
    ydataStD = np.std(np.array(ydata))
    ydataVar = ydataStD/np.sqrt(len(ydata))
    stopScan()   
    return (ydata, ydataAvg, ydataStD, ydataVar)

Filepath = r"Z:\Lab Data\Sessions\2021\2021_01\2021_01_27"
filename = "TOF-Spectrum_8uW_60uJ_5HzRep_5Samp_004.txt"

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

Scan553Start = getGlobal("NeutralFluorescence553ScanBeginning").magnitude*1e-6
Scan553End = getGlobal("NeutralFluorescence553ScanEnd").magnitude*1e-6
Scan553Res = getGlobal("NeutralFluorescence553ScanRes").magnitude*1e-6
Freqs553 = np.arange(Scan553Start, Scan553End, Scan553Res)
FreqCalibration = Freq553
Freqs553 += Freq553
print("Scan Start: %f THz, Scan End: %f THz, Scan Resolution: %f THz"%(Scan553Start + Freq553, Scan553End + Freq553, Scan553Res + Freq553))

ScanWindowStart = getGlobal("NeutralFluorescenceWindowScanBeginning").magnitude
ScanWindowEnd = getGlobal("NeutralFluorescenceWindowScanEnd").magnitude
ScanWindowRes = getGlobal("NeutralFluorescenceWindowScanRes").magnitude
WindowStartCalibration = 145
WindowWidthCalibration = 55
WindowWidthData = 1
WindowStart = np.arange(ScanWindowStart, ScanWindowEnd, ScanWindowRes)
print("Scan Start: %f us, Scan End: %f us, Scan Resolution: %f us"%(ScanWindowStart, ScanWindowEnd , ScanWindowRes))

ExperimentCount = 0


#os.system('ssh pi@192.168.168.122 cd Documents; python press_stop_button.py')
#time.sleep(4)
#os.system('ssh pi@192.168.168.122 cd Documents; python press_start_button.py')

ResetAblation()
#save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))  
for LaserFreq in Freqs553:
    if scriptIsStopped():
        break
    if ExperimentCount == 0:
        ExperimentCount += 1
        #Set laser freq., window start time (calibration)
        if not "%s"%getGlobal("IonizationFreq") == "%s THz"%FreqCalibration:
            setGlobal("IonizationFreq", FreqCalibration, "THz")
            time.sleep(FreqSetWaitTime)
        if not "%s"%getGlobal(WindowStartGlobal) == "%s us"%WindowStartCalibration:
            setGlobal(WindowStartGlobal, WindowStartCalibration, "us")
        if not "%s"%getGlobal(WindowWidthGlobal) == "%s us"%WindowWidthCalibration:
            setGlobal(WindowWidthGlobal, WindowWidthCalibration, "us")
        time.sleep(0.1)
        (dataRaw, dataAvg, dataStD, dataVar) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
        print("Step number: %i, Laser frequency setpoint: %f, Average Data: %f, Var: %f"%(ExperimentCount, FreqCalibration, dataAvg, dataVar))
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        savetextfile.write(str(ExperimentCount) + "\t" + str(FreqCalibration) + "\t" + str(WindowStartCalibration) + "\t" + str(dataAvg) + "\t" + str(dataStD) + "\t" + str(dataVar) + "\t" + str(dataRaw) + "\n")
        savetextfile.close()

    for WinStart in WindowStart:
        if scriptIsStopped():
            break
        ExperimentCount += 1
        #Set laer freq., window start time
        if not "%s"%getGlobal("IonizationFreq") == "%s THz"%LaserFreq:
            setGlobal("IonizationFreq", LaserFreq, "THz")
            time.sleep(FreqSetWaitTime)
        if not "%s"%getGlobal(WindowStartGlobal) == "%s us"%WinStart:
            setGlobal(WindowStartGlobal, WinStart, "us")
        if not "%s"%getGlobal(WindowWidthGlobal) == "%s us"%WindowWidthData:
            setGlobal(WindowWidthGlobal, WindowWidthData, "us")
        time.sleep(0.1)
        (dataRaw, dataAvg, dataStD, dataVar) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
        print("Step number: %i, Laser frequency setpoint: %f, Average Data: %f, Var: %f"%(ExperimentCount, LaserFreq, dataAvg, dataVar))
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        savetextfile.write(str(ExperimentCount) + "\t" + str(LaserFreq) + "\t" + str(WinStart) + "\t" + str(dataAvg) + "\t" + str(dataStD) + "\t" + str(dataVar) + "\t" + str(dataRaw) + "\n")
        savetextfile.close()

        ExperimentCount += 1
        #Set laser freq., window start time (calibration)
        if not "%s"%getGlobal("IonizationFreq") == "%s THz"%FreqCalibration:
            setGlobal("IonizationFreq", FreqCalibration, "THz")
            time.sleep(FreqSetWaitTime)
        if not "%s"%getGlobal(WindowStartGlobal) == "%s us"%WindowStartCalibration:
            setGlobal(WindowStartGlobal, WindowStartCalibration, "us")
        if not "%s"%getGlobal(WindowWidthGlobal) == "%s us"%WindowWidthCalibration:
            setGlobal(WindowWidthGlobal, WindowWidthCalibration, "us")
        time.sleep(0.1)
        (dataRaw, dataAvg, dataStD, dataVar) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
        print("Step number: %i, Laser frequency setpoint: %f, Average Data: %f, Var: %f"%(ExperimentCount, FreqCalibration, dataAvg, dataVar))
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename),'a+')
        savetextfile.write(str(ExperimentCount) + "\t" + str(FreqCalibration) + "\t" + str(WindowStartCalibration) + "\t" + str(dataAvg) + "\t" + str(dataStD) + "\t" + str(dataVar) + "\t" + str(dataRaw) + "\n")
        savetextfile.close()
