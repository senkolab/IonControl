#Shelving_Find_Target_Resonance_Freq_PlotPD.py created 2023-10-06 14:50:31.111782
import sys
import os
import datetime
import glob
import numpy as np
import time as t
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

centre_freq = 621.093636
freq_step = 0.001
freq_range_factor = 5

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

#setEvaluation('Eval3')

for i in np.arange(1531,3031,25):
    setEvaluation('Eval3')
    os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%i)
    setGlobal("Cooling_AOM_Switch_Enable", i, "")
    t.sleep(2)
    freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, threshold, pulse_program_findres, script_functions, AWG=True)
    setEvaluation('Eval2')
#setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
    setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")