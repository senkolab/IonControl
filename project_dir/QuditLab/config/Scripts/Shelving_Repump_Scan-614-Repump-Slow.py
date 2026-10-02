#Scan614Repump.py created 2022-02-11 13:57:15.706416
#This script is the slow version of Shelving_Repump_Scan-614-Repump.py, it plots in situ. and only saves data from successful shelving

#To run: be sure that the 1762 nm freq. is set to the desired uppper state. 
#If exact, find the pulse time for a pi pulse to improve propability of shelving, else use 1000 us
#Find the counts threshold for a bright unshelved ion and put this into the variable below, i.e. the threshold between bright and dark with the set integration time in the shelving program
import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
from Functions_NeutralFluor import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

ResetLasers = bool(getGlobal("LasersReset"))

ShelvingProgram = "Shelving_Pulse_Even_Single"
ShelvingRepumpProgram = "Repump_Shelve_Even"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
CountsProgramBG = "PMT_CheckCounts_For-Script_BG"
FreqSetWaitTime = getGlobal("TimeSwitchLaserFreqWM")

threshold_counts = 800
pulse_time = 1000 #us
pulse_time_global = getGlobal("Shelving_Pulse_Time").magnitude
if not "%s"%pulse_time_global == "%s THz"%pulse_time:
    setGlobal("Shelving_Pulse_Time", pulse_time, "us")
NumExp = 5
RepumpPower = 33
offset_freq = 487.989

Scan614Start = getGlobal("Repump614ScanBeginning").magnitude*1e-6
Scan614End = getGlobal("Repump614ScanEnd").magnitude*1e-6
Scan614Res = getGlobal("Repump614ScanRes").magnitude*1e-6

Freqs614 = np.arange(Scan614Start, Scan614End, Scan614Res)
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", script_functions)
Freqs614 += Freq614

print("Scan Start: %f THz, Scan End: %f THz, Scan Resolution: %f THz"%(Scan614Start + Freq614, Scan614End + Freq614, Scan614Res + Freq614))

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,script_functions)

#BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""#"7o19x_6o05y"
filename0 = f"614Spectrum_{RepumpPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
data_path = filename0
#data_path = r'Z:\Lab Data\Sessions\2021\2021_04\2021_04_29\Neut-Fluor-Spect_140uJ_11uW_1*'
(ydataBGAvg, ydataBGStd) = GetPMTCounts(CountsProgramBG, script_functions, bg=True)
WriteString = f"Metadata,Ionization Freqs.:{Freq614:0.6f} {Scan614Start*1e6:0.0f} \
{Scan614End*1e6:0.0f} {Scan614Res*1e6:0.0f}:THz MHz,CheckShelved Time:100 us\
BG:{ydataBGAvg}:,BG_std:{ydataBGStd}:"
WriteString += ""#Extra metadata from Ba137 trapping
WriteString += f"\nh,Time\tExperiment\tFreq614\tCountsAve\tCountsSTD"
SaveDataToTextFile(filename0, WriteString)

createTrace('614spectrum_data', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
i = 0
for FreqNum, LaserFreq in enumerate(Freqs614):
    if scriptIsStopped():
        break
    Experiment = 0
    LaserFreq = np.round(LaserFreq, 6)
    ShelvingRepumpFreq = getGlobal("ShelvingRepumpFreq")
    if not "%s"%ShelvingRepumpFreq == "%s THz"%LaserFreq:
        setGlobal("ShelvingRepumpFreq", LaserFreq, "THz")
        time.sleep(FreqSetWaitTime)
    counts_ave_array = np.zeros(NumExp)
    counts_std_array = np.zeros(NumExp)
    while Experiment < NumExp:
        if scriptIsStopped():
            break
        Shelved = False
        #Keep trying to shelve, then run repump program
        while Shelved == False:
            setScan(ShelvingProgram)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count'] #Returns all data associated with scan.
            ydata = data[1]
            print(ydata)
            if ydata[-1] < threshold_counts:
                Shelved = True
        setScan(ShelvingRepumpProgram)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions)
        counts_ave_array[Experiment] = ydataAvg
        counts_std_array[Experiment] = ydataStd
        
        WriteString = f"{time.time()}\t{Experiment}\t{LaserFreq:0.6f}\t{ydataAvg:0.6f}\t{ydataStd:0.6f}"
        SaveDataToTextFile(filename0, WriteString)
        freq_MHz = (LaserFreq - offset_freq)*1e6
        Experiment += 1
    plotPoint(freq_MHz, np.mean(counts_ave_array), '614spectrum_data', plotStyle=1)
closeTrace('614spectrum_data')