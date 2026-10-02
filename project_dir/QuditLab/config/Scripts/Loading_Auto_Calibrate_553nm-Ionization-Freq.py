#Calibrate_553nm-Ionization-Freq.py created 2021-04-28 15:06:21.461079

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

NeutralFluorescenceProgram = "Ablation_For-Script_NeutralFluorescence_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
CountsProgram = "PMT_CheckCounts_Combined-Beam"
CountsProgramBG = "PMT_CheckCounts_For-Script_Neutral_BG"
#FreqSetWaitTime = getGlobal("TimeSwitchFreqWM_Ionization")
FreqSetWaitTime = 20

NumExp = 1
PulseEnergy = 140
IonizationPower = 30
AblationPulsesPer = getGlobal("AblationPulsesPer")
WindowStart = 170
WindowWidth = 55
#WindowStart = 145
#WindowWidth = 1000
#CalibWindowStart, CalibWindowWidth = 145, 55
CalibWindowStart, CalibWindowWidth = 170, 55

offset_freq = 541.433

Scan553Start = getGlobal("NeutralFluorescence553ScanBeginning").magnitude*1e-6
Scan553End = getGlobal("NeutralFluorescence553ScanEnd").magnitude*1e-6
Scan553Res = getGlobal("NeutralFluorescence553ScanRes").magnitude*1e-6

Freqs553 = np.arange(Scan553Start, Scan553End, Scan553Res)
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", script_functions)
FreqCalibration = Freq553
Freqs553 += Freq553
print("Scan Start: %f THz, Scan End: %f THz, Scan Resolution: %f THz"%(Scan553Start + Freq553, Scan553End + Freq553, Scan553Res + Freq553))

if ResetLasers:
    print("Resetting lasers")
    SendLasersToTrap(CountsProgram,script_functions)
    ResetAblation(script_functions)

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o22x_6o11y"
filename0 = f"Neut-Fluor-Spect_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
filename0, base_folder = GetDataFilePath(filename0)
data_path = filename0
#data_path = r'Z:\Lab Data\Sessions\2021\2021_04\2021_04_29\Neut-Fluor-Spect_140uJ_11uW_1*'


(ydataBGAvg, ydataBGStd) = GetPMTCounts(CountsProgramBG, script_functions, bg=True)

WriteString = f"Metadata,Ionization Freqs.:{Freq553:0.6f} {Scan553Start*1e6:0.0f} {Scan553End*1e6:0.0f} {Scan553Res*1e6:0.0f}:THz MHz,\
Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,Calibration Window Start:{CalibWindowStart}:us,Calibration Window Width:{CalibWindowWidth}:us,\
BG:{ydataBGAvg}:,BG_std:{ydataBGStd}:"
WriteString += ""#Extra metadata from Ba137 trapping
if AblationPulsesPer > 1:
    NeutralWriteString = "\tNeutralCounts\tNeutralCounts_std"
else:
    NeutralWriteString = "\tNeutralCounts"
WriteString += f"\nh,Time\tExpNum\tIonizationFreq{NeutralWriteString}"
SaveDataToTextFile(filename0, WriteString)

Experiment = 0
i = 0
while Experiment < NumExp:
    createTrace('553spectrum_data', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
    PulseNum = 0
    for FreqNum, LaserFreq in enumerate(Freqs553):
        LaserFreq = np.round(LaserFreq, 6)
        if scriptIsStopped():
            break
        if FreqNum == 0 and Experiment == 0:
            PulseNum += 1
            setNeutralParameters(CalibWindowStart, CalibWindowWidth, FreqCalibration, script_functions)
            time.sleep(FreqSetWaitTime)
            (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, script_functions)
            if not dataStd:
                NeutralWrite = f"\t{dataAvg:0.1f}"
            else:
                NeutralWrite = f"\t{dataAvg:0.1f}\t{dataStd:0.1f}"
            WriteString = f"{time.time()}\t{PulseNum}\t{FreqCalibration:0.6f}{NeutralWrite}"
            SaveDataToTextFile(filename0, WriteString)
            cal_1 = dataAvg

        PulseNum += 1
        setNeutralParameters(WindowStart, WindowWidth, LaserFreq, script_functions)
        
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        time.sleep(FreqSetWaitTime)
        stopScan()

        (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, script_functions)
        if not dataStd:
            NeutralWrite = f"\t{dataAvg:0.1f}"
        else:
            NeutralWrite = f"\t{dataAvg:0.1f}\t{dataStd:0.1f}"
        WriteString = f"{time.time()}\t{PulseNum}\t{LaserFreq:0.6f}{NeutralWrite}"
        SaveDataToTextFile(filename0, WriteString)
        data_counts = dataAvg

        PulseNum += 1
        setNeutralParameters(CalibWindowStart, CalibWindowWidth, FreqCalibration, script_functions)

        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        time.sleep(FreqSetWaitTime)
        #time.sleep(0.1)
        stopScan()

        (dataRaw, dataAvg, dataStd) = NeutralFluoresencePulse(NeutralFluorescenceProgram, script_functions)
        if not dataStd:
            NeutralWrite = f"\t{dataAvg:0.1f}"
        else:
            NeutralWrite = f"\t{dataAvg:0.1f}\t{dataStd:0.1f}"
        WriteString = f"{time.time()}\t{PulseNum}\t{FreqCalibration:0.6f}{NeutralWrite}"
        SaveDataToTextFile(filename0, WriteString)
        cal_2 = dataAvg
        #data_counts_cal = data_counts/((cal_1 + cal_2)/2)
        data_counts_cal = data_counts/(cal_2)
        freq_MHz = (LaserFreq - offset_freq)*1e6
        plotPoint(freq_MHz, data_counts_cal, '553spectrum_data', plotStyle=1)
        #plotPoint(freq_MHz, data_counts, '553spectrum_data', plotStyle=1)
        
    Experiment += 1
    closeTrace('553spectrum_data')

freq_data_raw, counts_data_raw = getData_553Spectrum(data_path)
freq_data, counts_data_cal = calibrateData_553(freq_data_raw, counts_data_raw)

data_points_num = np.unique(freq_data).size
freq_data = freq_data[:data_points_num]
freq_data_MHz = (freq_data - offset_freq)*1e6
counts_cal_ave, counts_cal_std = aveData_553(counts_data_cal, data_points_num)

fit_params, perr = createFit_553Spectrum(freq_data_MHz, counts_cal_ave)
print(f'fit params: f0 = {fit_params[0]:0.1f} MHz + offset_freq, saturation = {fit_params[1]:0.1f}, amplitude = {fit_params[2]:0.2f}')

createTrace('553spectrum_data', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
plotList(freq_data_MHz, counts_cal_ave, '553spectrum_data', plotStyle=1)
closeTrace('553spectrum_data')
xfit_freqs = np.arange(min(freq_data_MHz), max(freq_data_MHz), 1)
yfit_counts = fitFunc_553Spectrum(xfit_freqs, fit_params[0], fit_params[1], fit_params[2])
createTrace('553spectrum_fit', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
plotList(xfit_freqs, yfit_counts, '553spectrum_fit')
closeTrace('553spectrum_fit')

freq_ba138 = np.round((fit_params[0]*1e-6 + offset_freq), 6)
if not "%s"%getGlobal("Ba138_IonizationFreq_Opt") == "%s THz"%freq_ba138:
    setGlobal("Ba138_IonizationFreq_Opt", freq_ba138, "THz")