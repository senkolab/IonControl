#Shelving_PlotPD_Calibrate_Frequencies.py created 2023-11-20 11:48:11.239293

import sys
import os
import datetime
import glob
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

use_AWG=True

AWG_Flag = getGlobal('UseAWG_Flag')
if not "%s"%AWG_Flag == "%s us"%int(use_AWG):
    setGlobal("UseAWG_Flag", int(use_AWG), "")

dt_string = datetime.datetime.now().strftime("%d%m%Y_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

# input file for AWG and state prep
if use_AWG:
    input_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1S12_F2_freqs_file_AWG_probe.txt'
# input file for PLL and probing
elif not use_AWG:
    input_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1s12_f2_freqs_file_PLL_F2P2_init.txt'
    os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%30)

output_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1s12_f2_freqs_file_output_{dt_string}.txt'

F1_pumpTime = getGlobal('F1_PumpTime')
if not "%s"%F1_pumpTime == "%s us"%0:
    setGlobal("F1_PumpTime", 0, "us")

OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
if not "%s"%OptPumpTime == "%s us"%0:
    setGlobal("OpticalPumpTimeGlobal", 0, "us")

Init_reps_zero = getGlobal('InitialisationReps')
if not "%s"%Init_reps_zero == 0:
    setGlobal("InitialisationReps", 0, "")

with open(output_file,'w'):
    pass
with open(input_file,'r') as freq_file:
    for freq_tuple in freq_file:
        tuple = freq_tuple.strip().split(' ')
        centre_freq = float(tuple[0])
        pi_time = float(tuple[1])
        freq_step = 0.001
        freq_range_factor = 15

        threshold = 5

        AWG_Power_dBm = -10
        SetPulseTime = 3000 #us

        AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
        if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
            setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

        PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
        if not "%s"%PulseTime_Dummy == "%s us"%SetPulseTime:
            setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

        AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
        if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
            setGlobal("AWG1_Mode", 0, "")

        pulse_program_findres = "Shelving_Freq_Cal_Ba137"

        range = freq_range_factor*freq_step
        freq_start = centre_freq-range
        freq_stop = centre_freq+range+freq_step

        setEvaluation('Eval3')

        freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, threshold, pulse_program_findres, script_functions, AWG=use_AWG)
        with open(output_file,'a') as outfile:
            outfile.write(f'{freq_peak} {pi_time}\n')
            

setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
    setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")