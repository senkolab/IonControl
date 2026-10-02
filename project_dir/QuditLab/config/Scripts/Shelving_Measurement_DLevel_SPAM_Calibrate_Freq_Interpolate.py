#Shelving_Measurement_DLevel_SPAM_Calibrate_Freq_Interpolate.py created 2022-11-27 11:54:23.033045

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


BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(good_transitions) + len(calib_transitions)}-level_{addname}_prints_freq_interpolate*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Freq-Scan:{freqrough_range},{freqrough_step};Fine-Freq-Scan:{freqfine_range},{freqfine_step}"
#WriteString += f"\nCalibTransitions:{states_overall_trans[calib_transitions]}\tGoodTransitions:{states_overall_trans[good_transitions]}"
SaveDataToTextFile(filename0, WriteString)














#Go through all calibration transitions, finding the frequency
state_freq_globals = []
state_pi_time_globals = []
freqs_found = []
for i, state in enumerate(calib_transitions):
    if scriptIsStopped():
        break
    state_overall_trans = states_overall_trans[state]
    #Setup list of the global variables for the states
    state_string = f'{state_string0}{state_overall_trans}'
    state_freq_string_global = state_string + '_Freq'
    state_pi_time_string_global = state_string + '_Pi_Time'
    state_freq_globals.append(state_freq_string_global)
    state_pi_time_globals.append(state_pi_time_string_global)

    #Run rough freq. scan to find this transition
    AWG_Power_dBm = getGlobal('AWG1_Power_dBm').magnitude
    if not "%s"%AWG_Power_dBm == 3:
        setGlobal("AWG1_Power_dBm", 3, "")

    freq0 = getGlobal(state_freq_string_global).magnitude
    freq_start = np.round(freq0-freqrough_range,3)
    freq_stop = np.round(freq0+freqrough_range,3)
    pulse_time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%pulse_time == "%s us"%pulse_time_default:
        setGlobal("Shelving_Pulse_Time", pulse_time_default, "us")    
    freq = freq0
    freq = findResonance(freq_start, freq_stop, freqrough_step, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state_overall_trans}: Rough freq. scan gave peak freq. of {freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)

    #Run fine freq. scan to find this calibrated transition
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    if pi0>120:
        set_power_dBm = -10
    else:
        set_power_dBm = -20
    AWG_Power_dBm = getGlobal('AWG1_Power_dBm').magnitude
    if not "%s"%AWG_Power_dBm == set_power_dBm:
        setGlobal("AWG1_Power_dBm", set_power_dBm, "")

    freq_start = np.round(freq-1*freqfine_range,3)
    freq_stop = np.round(freq+1*freqfine_range,3)
    print(f'freq_start:{freq_start}, freq_stop:{freq_stop}')
    #freq = freq0
    freq = findResonance_withfit(freq_start, freq_stop, freqfine_step, pulse_program_findres, script_functions, AWG=True)
    freqF4m4 = freq
    state_freq = getGlobal(state_freq_string_global)
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freqs: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 3), "MHz")
    freqs_found.append(freq)
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state_overall_trans}: Fine, final freq. calibration is {freq0:0.6f}->{freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)

freqF4m4, freqF4m0, freqF2m1 = freqs_ffound





#Get calibration sensitivity
x = freqF4m0 - freqF4m4
#Go through each transition, using parameters to get interpolated frequency and setting the global variable
for i, state in enumerate(good_transitions):
    if scriptIsStopped():
        break
    state_overall_trans = states_overall_trans[state]
    #Setup list of the global variables for the states
    state_string = f'{state_string0}{state_overall_trans}'
    state_freq_string_global = state_string + '_Freq'
    params = list_parameters[i]
    #freq = params[0]*x**3 + params[1]*x**2 + params[2]*x + params[3] + freqF2m1
    freq = params[0]*x + params[1] + freqF2m1
    state_freq = getGlobal(state_freq_string_global).magnitude
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freqs: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 3), "MHz")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {state}: {state_overall_trans}: Calibrated freq. {state_freq:0.3f}->{freq:0.3f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)