#Ablation-Paper-2021_553nm-Spectrum.py created 2020-11-16 13:32:18.845837

import numpy as np
import os
import sys
import glob
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *
from NeutralFluorFunctions import *

ResetLasers = False

NeutralFluorescenceProgram = "Ablation_For-Script_NeutralFluorescence_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
CountsProgram = "PMT_CheckCounts_Combined-Beam"
CountsProgramBG = "PMT_CheckCounts_For-Script_Neutral_BG"
FreqSetWaitTime = getGlobal("TimeSwitchLaserFreqWM")

NumExp = 5
PulseEnergy = 140
IonizationPower = 8
AblationPulsesPer = getGlobal("AblationPulsesPer")
WindowStart = 160
WindowWidth = 55
CalibWindowStart = 145
CalibWindowWidth = 55
Scan553Start = getGlobal("NeutralFluorescence553ScanBeginning").magnitude*1e-6
Scan553End = getGlobal("NeutralFluorescence553ScanEnd").magnitude*1e-6
Scan553Res = getGlobal("NeutralFluorescence553ScanRes").magnitude*1e-6

Freqs553 = np.arange(Scan553Start, Scan553End, Scan553Res)
(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
FreqCalibration = Freq553
Freqs553 += Freq553
print("Scan Start: %f THz, Scan End: %f THz, Scan Resolution: %f THz"%(Scan553Start + Freq553, Scan553End + Freq553, Scan553Res + Freq553))

if ResetLasers:
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation()

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Neut-Fluor-Spect_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0 = GetDataFilePath(BaseFolder, filename0)

(ydataBGAvg, ydataBGStd) = GetPMTCounts(CountsProgramBG, setScan, startScan, stopScan, getAllData)
print(ydataBGAvg)

WriteString = f"Metadata,Ionization Freqs.:{Freq553:0.6f} {Scan553Start*1e6:0.0f} {Scan553End*1e6:0.0f} {Scan553Res*1e6:0.0f}:THz MHz,\
Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Calibration Window Start:{CalibWindowStart}:us,Calibration Window Width:{CalibWindowWidth}:us,\
BG:{ydataBGAvg}:,BG_std:{ydataBGStd}:"
WriteString += ""#Extra metadata from Ba137 trapping
if AblationPulsesPer > 1:
    NeutralWriteString = "\tNeutralCounts\tNeutralCounts_std"
else:
    NeutralWriteString = "\tNeutralCounts"
WriteString += f"\nh,ExpNum\tIonizationFreq{NeutralWriteString}"
SaveDataToTextFile(filename0, WriteString)

Experiment = 0
i = 0
while Experiment < NumExp:
    PulseNum = 0
    for FreqNum, LaserFreq in enumerate(Freqs553):
        if scriptIsStopped():
            break
        if FreqNum == 0 and Experiment == 0:
            PulseNum += 1
            setNeutralParameters(CalibWindowStart, CalibWindowWidth, FreqCalibration, getGlobal, setGlobal)
            time.sleep(FreqSetWaitTime)
            (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
            if not dataStd:
                NeutralWrite = f"\t{dataAvg}"
            else:
                NeutralWrite = f"\t{dataAvg}\t{dataStd}"
            WriteString = f"{PulseNum}\t{FreqCalibration:0.6f}{NeutralWrite}"
            SaveDataToTextFile(filename0, WriteString)

        PulseNum += 1
        setNeutralParameters(WindowStart, WindowWidth, LaserFreq, getGlobal, setGlobal)
        time.sleep(FreqSetWaitTime)
        (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
        if not dataStd:
            NeutralWrite = f"\t{dataAvg}"
        else:
            NeutralWrite = f"\t{dataAvg}\t{dataStd}"
        WriteString = f"{PulseNum}\t{LaserFreq:0.6f}{NeutralWrite}"
        SaveDataToTextFile(filename0, WriteString)

        PulseNum += 1
        setNeutralParameters(CalibWindowStart, CalibWindowWidth, FreqCalibration, getGlobal, setGlobal)
        time.sleep(FreqSetWaitTime)
        (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, setScan, startScan, stopScan, getAllData)
        if not dataStd:
            NeutralWrite = f"\t{dataAvg}"
        else:
            NeutralWrite = f"\t{dataAvg}\t{dataStd}"
        WriteString = f"{PulseNum}\t{FreqCalibration:0.6f}{NeutralWrite}"
        SaveDataToTextFile(filename0, WriteString)
    Experiment += 1
