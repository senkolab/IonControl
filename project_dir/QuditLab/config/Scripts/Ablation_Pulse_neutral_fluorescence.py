6662.3

#Pulse_neutral_fluorescence.py created 2021-07-27 16:49:03.544028

import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *
from NeutralFluorFunctions import *

ResetLasers = bool(getGlobal("LasersReset")) #N.B: set to FALSE in Global Variables when testing 

NeutralFluorescenceProgram = "Ablation_For-Script_NeutralFluorescence_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
CountsProgram = "PMT_CheckCounts_Combined-Beam"
CountsProgramBG = "PMT_CheckCounts_For-Script_Neutral_BG"
FreqSetWaitTime = getGlobal("TimeSwitchLaserFreqWM")

LaserFreq = getGlobal("Ba138_IonizationFreq_Opt").magnitude

#PulseEnergy = 110 #uJ, just for header/metadata/note keeping purposes, N.B : cannot be adjusted within the script ! 
LowPulseEnergy = 75 #uJ, just for header/metadata/note keeping purposes, N.B : cannot be adjusted within the script ! 
HighPulseEnergy = 145 #uJ, just for header/metadata/note keeping purposes, N.B : cannot be adjusted within the script ! 

IonizationPower = 4 #553nm power 
AblationPulsesPer = getGlobal("AblationPulsesPer") #N.B: Changed Global Variable to 10
WindowStart = 145
WindowWidth = 55

offset_freq = 541.433

#(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)

if ResetLasers: #T_1/F_0 global variable; N.B: Set to FALSE when testing the script
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation(setScan, startScan, stopScan)

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o25x_6o10y_Condition"
filename0 = f"Neut-Fluor-Spect_{LowPulseEnergy:0.0f}uJ_{HighPulseEnergy:0.0f}uJ_{addname}_*.txt"
filename0, base_folder = GetDataFilePath(BaseFolder, filename0, NewFile=True)
data_path = filename0
#data_path = r'Z:\Lab Data\Sessions\2021\2021_04\2021_04_29\Neut-Fluor-Spect_140uJ_11uW_1*'

# Separate file for Metadata 
filename1 = f"Neut-Fluor-Spect_Metadata_{LowPulseEnergy:0.0f}uJ_{HighPulseEnergy:0.0f}uJ_{addname}.txt"
filename1, base_folder = GetDataFilePath(BaseFolder, filename1, NewFile=False)
data_path_1 = filename1

filename_3 =  f"Neut-Fluor-Spect_Headers_{LowPulseEnergy:0.0f}uJ_{HighPulseEnergy:0.0f}uJ_{addname}.txt"
filename_3, base_folder = GetDataFilePath(BaseFolder, filename_3, NewFile=False)
data_path_3 = filename_3

(ydataBGAvg, ydataBGStd) = GetPMTCounts(CountsProgramBG, setScan, startScan, stopScan, getAllData) #collect BG counts 

# Metadata = filename1,, RawData = filename0
WriteString = f"Metadata,Ionization Freqs.:{LaserFreq:0.6f}  \
Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,\
BG:{ydataBGAvg}:,BG_std:{ydataBGStd}:"
WriteString += "" #Extra metadata from Ba137 trapping
if AblationPulsesPer > 1:
    #NeutralWriteString = "\tNeutralCounts\tNeutralCounts_std"
    NeutralWriteString = "\tNeutralCounts"
else:
    NeutralWriteString = "\tNeutralCounts"
#WriteString += f"\nh,Time\tExpNum\tIonizationFreq{NeutralWriteString}"
SaveDataToTextFile(filename1, WriteString)
WriteString0 = f"\nh,Time\tIonizationFreq{NeutralWriteString}"
SaveDataToTextFile(filename_3, WriteString0)

# Collecting & saving 553nm fluorescence PMT counts, N.B. RAW DATA only 
setNeutralParameters(WindowStart, WindowWidth, LaserFreq, getGlobal, setGlobal)
#time.sleep(FreqSetWaitTime)
(dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
dataRaw_arr = np.array(dataRaw)
dataRaw_str = str(dataRaw_arr)[1:-1]
NeutralWrite = f"\t{dataRaw_str}"
WriteString = f"{time.time()}\t{LaserFreq:0.6f}{NeutralWrite}"
SaveDataToTextFile(filename0, WriteString)
data_counts = dataRaw