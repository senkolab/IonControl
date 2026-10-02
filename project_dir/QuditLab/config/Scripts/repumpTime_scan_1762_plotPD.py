#repumpTime_scan_1762_plotPD.py created 2023-11-10 14:20:09.973331

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

dt_string = datetime.datetime.now().strftime("%d%m%Y_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

#input_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1s12_f2_freqs_file_output.txt'
output_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\Repump+time_scan{dt_string}.txt'


set_comparisons= 10
threshold = 5

set_F1pumpTime = 20 #us
set_F1pumpTime_repeated = 8 #us

set_initReps_zero = 0
set_initReps_repeated = 10

AWG_Power_dBm = -10
SetPulseTime = 3000 #us

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", 0, "")

pulse_program = "Shelving_InitScheme_Comparison_Ba137"

repump_times=[10,30,50,70,100,150,200,250,300,400,500]
freq_list = [603.477244]
with open(output_file,'w'):
    pass

for k in freq_list:
    freq = float(k)
    createTrace('PlotPD F1 Pump Only', 'Script Data', xLabel=f'Repump Time (us)')

    F1Only_PD = []

    #Loop 
    for i in repump_times:

    #First Part

        F1_pumpTime = getGlobal('F1_PumpTime')
        if not "%s"%F1_pumpTime == "%s us"%set_F1pumpTime:
            setGlobal("F1_PumpTime", set_F1pumpTime, "us")

        Init_reps_zero = getGlobal('InitialisationReps')
        if not "%s"%Init_reps_zero == set_initReps_zero:
            setGlobal("InitialisationReps", set_initReps_zero, "")

        repumpTime = getGlobal('Shelve_Repump_Time')
        if not "%s"%repumpTime == "%s us"%i:
            setGlobal("Shelve_Repump_Time", i, "us")

        setEvaluation('Eval3')

        PD_F1_only = find_and_plotPD_F1pumpOnly(i, freq, threshold, pulse_program, script_functions, AWG=True)
        F1Only_PD.append(PD_F1_only)

        setEvaluation('Eval2')

        with open(output_file,'a') as outfile:
            outfile.write(f'{i}   {PD_F1_only}\n')
            
    closeTrace('PlotPD F1 Pump Only')

print("F1 only mean,std",np.mean(F1Only_PD),np.std(F1Only_PD))
#print("F1 and Shelving Repeated mean,std",np.mean(F1_and_Shelving_PD),np.std(F1_and_Shelving_PD))