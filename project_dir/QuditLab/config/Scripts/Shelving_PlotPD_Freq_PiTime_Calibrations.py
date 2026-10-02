#Shelving_PlotPD_Freq_PiTime_Calibrations.py created 2023-11-22 11:48:11.239293

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

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

recent_calibration_files = glob.glob(fr'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration_Good\1s12_f2_freqs_file_output_frequencies_*.txt')
print('here are', recent_calibration_files[-1])
latest_calibration_file = recent_calibration_files[-1] 

input_file = latest_calibration_file
output_file_freqs = fr'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration\1s12_f2_freqs_file_output_frequencies_{dt_string}.txt'
output_file_pitimes = fr'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration\1s12_f2_freqs_file_output_pitimes_{dt_string}.txt'


do_pi_time_calibration = False
threshold = 5
#for frequency calibration
freq_step = 0.001 # MHz
freq_range_factor = 20
#AWG_Power_dBm = -10
SetPulseTime = 3000 #us

#for pi time calibration
stop_time = 200 #us
time_step = 10 #us

F1_pumpTime = getGlobal('F1_PumpTime')
if not "%s"%F1_pumpTime == "%s us"%0:
    setGlobal("F1_PumpTime", 0, "us")

OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
if not "%s"%OptPumpTime == "%s us"%0:
    setGlobal("OpticalPumpTimeGlobal", 0, "us")

Init_reps_zero = getGlobal('InitialisationReps')
if not "%s"%Init_reps_zero == 0:
    setGlobal("InitialisationReps", 0, "")

AWG_Flag = getGlobal('UseAWG_Flag')
if not "%s"%AWG_Flag == "%s us"%int(1):
    setGlobal("UseAWG_Flag", int(1), "")

freq_list_fitted = []

with open(output_file_freqs,'w'):
    pass
with open(input_file,'r') as freq_file:
    for freq in freq_file:
        parts = freq.strip().split(', ')
        centre_freq, strength = map(float, parts)

        # calculating AWG power from transition strengths
        #AWG1_Power_dBm = np.round(-20.9369*strength -31.142)
        AWG1_Power_dBm = strength

        AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
        if not "%s"%AWG_Power_dBm_global == AWG1_Power_dBm:
            setGlobal("AWG1_Power_dBm", AWG1_Power_dBm, "")

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

        freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program_findres, script_functions, AWG=True)
        freq_list_fitted.append(freq_peak)

        setEvaluation('Eval2')
        with open(output_file_freqs,'a') as outfile:
            outfile.write(f'{freq_peak}, {strength}\n')
            
if do_pi_time_calibration:
    with open(output_file_pitimes,'w'):
        pass
    with open(input_file,'r') as freq_file:
        for freq in freq_list_fitted:

            AWG1_Freq = getGlobal("AWG1_Frequency")
            if not "%s"%AWG1_Freq == "%s MHz"%freq:
                setGlobal("AWG1_Frequency", np.round(freq, 6), "MHz")

            AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
            if not "%s"%AWG_Power_dBm_global == 3:
                setGlobal("AWG1_Power_dBm", 3, "")

            pulse_program_findpi = "Shelving_PulseTime_Scan_FreqPiTimeCalibration_Ba137"

            setEvaluation('Eval3')

            pi_time = findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program_findpi, script_functions)

            setEvaluation('Eval2')
            with open(output_file_pitimes,'a') as outfile:
                outfile.write(f'{pi_time}\n')
