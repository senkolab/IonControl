#Scan614Repump.py created 2022-02-11 13:57:15.706416
#This script collects repump probability vs shelving repump freq.

#To run: be sure that the 1762 nm freq. is set to the desired uppper state. 
#If exact, find the pulse time for a pi pulse to improve propability of shelving, else use 1000 us
#This script will run the experiment Repump614Scan_NumExp times (global variable). It will throw out experiments where the ion wasn't shelved in the first place, then calculate the average probability of repumping for these post-selected experiments
#For further analysis code, look in Z:Useful Programs + Analysis Codes
import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
#from Functions_NeutralFluor import *

script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

WhichIon = int(getGlobal("WhichIon").magnitude)

ResetLasers = bool(getGlobal("LasersReset"))
#if WhichIon == 138:
#    ShelvingRepumpProgram = "Repump_Shelve_Scan_Even"
#    CountsProgram = "PMT_CheckCounts_For-Script_Even"
#elif WhichIon == 137:
ShelvingRepumpProgram = "Repump_Shelve_Scan_Ba137"
CountsProgram = "PMT_CheckCounts_For-Script_Ba137"
CountsProgramBG = "PMT_CheckCounts_For-Script_BG"
FreqSetWaitTime = getGlobal("TimeSwitchFreqWM_ShelvingRepump")
numExp = int(getGlobal("Repump614Scan_NumExp").magnitude)

RepumpPower = 10
offset_freq = 609.877
pulse_time = 1000 #us
pulse_time_global = getGlobal("Shelving_Pulse_Time").magnitude
if not "%s"%pulse_time_global == "%s THz"%pulse_time:
    setGlobal("Shelving_Pulse_Time", pulse_time, "us")
raw_filename = "Repump_Shelve_Scan_487o98950-0o00001-487o99001THz_3000usRepumpTime_2msIntTime_1000msShelveTime_17uWRepumpPower_Ba-138-N12-D0_Raw" 


Scan614Start = getGlobal("Repump614ScanBeginning").magnitude*1e-6
Scan614End = getGlobal("Repump614ScanEnd").magnitude*1e-6
Scan614Res = getGlobal("Repump614ScanRes").magnitude*1e-6

Freqs614 = np.arange(Scan614Start, Scan614End, Scan614Res)
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)
ShelvingRepumpFreq = getGlobal("ShelvingRepumpFreq")
if not "%s"%ShelvingRepumpFreq == "%s THz"%Freq614:
    setGlobal("ShelvingRepumpFreq", Freq614, "THz")
    time.sleep(FreqSetWaitTime)
Freqs614 += Freq614
print("Scan Start: %f THz, Scan End: %f THz, Scan Resolution: %f THz"%(Scan614Start + Freq614, Scan614End + Freq614, Scan614Res + Freq614))

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,script_functions)


BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""#"7o19x_6o05y"
filename0 = f"614Spectrum_{RepumpPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)
data_path = filename0
#data_path = r'Z:\Lab Data\Sessions\2021\2021_04\2021_04_29\Neut-Fluor-Spect_140uJ_11uW_1*'
(ydataBGAvg, ydataBGStd) = GetPMTCounts(CountsProgramBG, script_functions, bg=True)
WriteString = f"Metadata,Ionization Freqs.:{Freq614:0.6f} {Scan614Start*1e6:0.0f} \
{Scan614End*1e6:0.0f} {Scan614Res*1e6:0.0f}:THz MHz,CheckShelved Time:100 us\
BG:{ydataBGAvg}:,BG_std:{ydataBGStd}:"
WriteString += ""#Extra metadata from Ba137 trapping
WriteString += f"\nh,Time\tExperiment\tFreq614\tCountsShelve\tCountsRepump"
SaveDataToTextFile(filename0, WriteString)

createTrace('614spectrum_data', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
for FreqNum, LaserFreq in enumerate(Freqs614):
    Experiment = 0
    LaserFreq = np.round(LaserFreq, 6)
    if not "%s"%ShelvingRepumpFreq == "%s THz"%LaserFreq:
        setGlobal("ShelvingRepumpFreq", LaserFreq, "THz")
        time.sleep(FreqSetWaitTime)
    if scriptIsStopped():
        break
    setScan(ShelvingRepumpProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()
    dataShelve = data['PMT Count Shelve']
    dataRepump = data['PMT Count Repump']
    WriteString = f"{time.time()}\t{Experiment}\t{LaserFreq:0.6f}\t{dataShelve}\t{dataRepump}"
    SaveDataToTextFile(filename0, WriteString)
    freq_MHz = (LaserFreq - offset_freq)*1e6

    data_raw = GetRawData(raw_filename, last=1)
    data_shelve_raw = np.array(data_raw[:, 2:numExp+2])
    data_repump_raw = np.array(data_raw[:, numExp+4:2*numExp+4])
    data_mean, data_var, _ = cleanDataShelve614Repump(data_shelve_raw, data_repump_raw)
    plotPoint(freq_MHz, data_mean, '614spectrum_data', plotStyle=1)
closeTrace('614spectrum_data')
#data_raw = GetRawData(raw_filename, last=len(Freqs614))
#data_shelve_raw = np.array(data_raw[:, 2:numExp+2])
#data_repump_raw = np.array(data_raw[:, numExp+4:2*numExp+4])
#data_mean, data_var, num_points = cleanDataShelve614Repump(data_shelve_raw, data_repump_raw)
#print(data_mean)