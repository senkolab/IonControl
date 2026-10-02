#plotPD_saved_peak_freqs_copy_usePLL.py created 2023-11-15 13:37:03.349143


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

m_lvl = "F2N2"

dt_string = datetime.datetime.now().strftime("%d%m%Y_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

input_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1S12_F2_freqs_file.txt'
output_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1s12_f2_freqs_file_output_check.txt'
peak_freq_list = []

with open(output_file,'w'):
    pass
with open(input_file,'r') as freq_file:
    for freq_est in freq_file: 
        centre_freq = float(freq_est)
        freq_step = 0.0015
        freq_range_factor = 25

        threshold = 4

        AWG_Power_dBm = -10
        SetPulseTime = 3000 #us

        AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
        if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
            setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

        AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
        if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
            setGlobal("AWG1_Mode", 0, "")

        pulse_program_findres = "Shelving_Freq_Cal_Ba137"

        range = freq_range_factor*freq_step
        freq_start = centre_freq-range
        freq_stop = centre_freq+range+freq_step

        setEvaluation('Eval3')

        freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, threshold, pulse_program_findres, script_functions, AWG=True)
        with open(output_file,'a') as outfile:
            outfile.write(f'{freq_peak}\n')
            

setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
    setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")