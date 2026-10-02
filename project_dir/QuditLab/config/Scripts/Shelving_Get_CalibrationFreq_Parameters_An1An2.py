#Shelving_Get_CalibrationFreq_Parameters_An1An2.py created 2023-08-17 10:59:04.139740

import sys
import os
import numpy as np
import glob
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

save_global_freqs = False
skip = []

AWG_Mode_global = "AWG1_Mode"
AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
if not int(AWG_mode_curr) == 0:
    setGlobal(AWG_Mode_global, 0, "")
setEvaluation('Eval3')

WhichIon = getGlobal("WhichIon").magnitude
pulse_program_TriggerAWGEvent = "TriggerAWGEvent"
if WhichIon == 138:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Even"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses"
    state_string = f'Ba138_Shelving_'
elif WhichIon == 137:
    pulse_program_findres = "Shelving_Freq_Cal_Ba137"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses_Ba137"
    state_string0 = f'Ba137_Shelving_F2P2_'
    states_overall_trans = ["Fp4_a_mp4", "Fp4_b_mp3", "Fp4_c_mp2", "Fp4_d_mp1", "Fp4_e_mp0", \
    "Fp3_b_mp3", "Fp3_c_mp2", "Fp3_d_mp1", "Fp3_e_mp0", \
    "Fp2_c_mp2", "Fp2_d_mp1", "Fp2_e_mp0", \
    "Fp1_d_mp1", "Fp1_e_mp0"]

calib_transitions = [0, 4, 10] #Use F4m4, F4m3 for calibration of other transitions, F2m1 for calibration of global offset
good_transitions = [1, 2, 3, 6, 7, 8, 9, 11, 12, 13]

#Rough freq. scan - 10 kHz
freqrough_step = 0.01
freqrough_range = 0.05
freqfine_step = 0.001
freqfine_range = 10*freqfine_step
#More precise freq. scan - 1 kHz

pulse_time_default = 3000 #us

#Get the latest calibration interpolation parameters
filepath0 = 'Z:\\Lab Data\\D52_Calibration_Ba137\\'
filename0 = '1762_Transition-Freq_Parameters'
files0 = filepath0 + filename0 + '*'
files0 = np.array(glob.glob(files0)) 
files0_latest = files0[-1]
list_parameters = getData_1762_Calib(files0)[0,:,:]
print(list_parameters)