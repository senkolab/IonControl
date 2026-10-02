#Shelving_Find_Target_Resonance_Freq_PlotPD_Original.py created 2023-11-02 09:35:36.882536

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

centre_freq = 609.345
freq_step = 0.001
freq_range_factor = 20

threshold = 4

AWG_Power_dBm = 3
SetPulseTime = 3000 #us

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == 1: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", 1, "")

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

pulse_program_findres = "Shelving_Freq_Cal_Ba137"

range = freq_range_factor*freq_step
freq_start = centre_freq-range
freq_stop = centre_freq+range+freq_step

setEvaluation('Eval3')

freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, threshold, pulse_program_findres, script_functions, AWG=True)

setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
    setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")