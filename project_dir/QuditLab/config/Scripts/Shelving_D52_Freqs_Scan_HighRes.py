#Shelving_D52_Freqs_Scan_HighRes.py created 2022-12-10 14:43:30.838182

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

save_global_freq = True
write_meas = True
write_param_file = True
skip_rough = True

WhichIon = getGlobal("WhichIon").magnitude
AWG_Mode_global = "AWG1_Mode"
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
    "Fp3_c_mp2", "Fp3_d_mp1", "Fp3_e_mp0", \
    "Fp2_c_mp2", "Fp2_d_mp1", "Fp2_e_mp0", \
    "Fp1_d_mp1", "Fp1_e_mp0"]


skip = [0]
skip = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
skip = []


#Rough freq. scan - 10 kHz
freqrough_step = 0.01
freqrough_range = 0.05
freqfine_step = 0.001
freqfine_range = 10*freqfine_step
#More precise freq. scan - 1 kHz

pulse_time_default = 3000 #us

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", 0, "")


BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(states_overall_trans)}-states_{addname}_prints_freqs*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Freq-Scan:{freqrough_range},{freqrough_step};Fine-Freq-Scan:{freqfine_range},{freqfine_step}"
#WriteString += f"\nCalibTransitions:{states_overall_trans[calib_transitions]}\tGoodTransitions:{states_overall_trans[good_transitions]}"
SaveDataToTextFile(filename0, WriteString)

writeFolder = r'Z:\Lab Data\D52_Calibration_Ba137'
timenow = datetime.datetime.now()
filename = 'freqmeas_f2m2_singlecoil_4000mA_' + str(timenow.year) + "{:02d}".format(timenow.month) + "{:02d}".format(timenow.day) + "{:02d}".format(timenow.hour) \
+ "{:02d}".format(timenow.minute)+ "{:02d}".format(timenow.second) + '.txt'
filename_freqs = writeFolder + '\\' + filename
#file = open(writeFolder + '\\' + filename,'w+')
#file.close()


#    AWG_Power_dBm = getGlobal('AWG1_Power_dBm').magnitude
#    if not "%s"%AWG_Power_dBm == 3:
#        setGlobal("AWG1_Power_dBm", 3, "")

for i, state in enumerate(states_overall_trans):
    if scriptIsStopped():
        #os.remove(writeFolder + '\\' + filename)
        break
    if i in skip:
        print(f'skipped step {i}')
        continue
    setEvaluation('Eval3')
    state_string = f'{state_string0}{state}'
    state_freq_string_global = state_string + '_Freq'
    state_pi_time_string_global = state_string + '_Pi_Time'
    

    freq0 = getGlobal(state_freq_string_global).magnitude
    freq = freq0

    pulse_time = getGlobal("Shelving_Pulse_Time")  
    if not "%s"%pulse_time == "%s us"%pulse_time_default:
        setGlobal("Shelving_Pulse_Time", pulse_time_default, "us")
    if not skip_rough:
        pi0 = getGlobal(state_pi_time_string_global).magnitude
        if pi0<50:
            set_power_dBm = -10
        else:
            set_power_dBm = 3
        AWG_Power_dBm = getGlobal('AWG1_Power_dBm').magnitude 
        if not "%s"%AWG_Power_dBm == set_power_dBm:
            setGlobal("AWG1_Power_dBm", set_power_dBm, "")
        freq_start = np.round(freq0-freqrough_range,3)
        freq_stop = np.round(freq0+freqrough_range,3)  
        freq = findResonance(freq_start, freq_stop, freqrough_step, pulse_program_findres, script_functions, AWG=True)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough freq. scan gave peak freq. of {freq:0.6f} MHz'
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
    freq = findResonance_withfit(freq_start, freq_stop, freqfine_step, pulse_program_findres, script_functions, AWG=True)
    state_freq = getGlobal(state_freq_string_global)
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freq: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 3), "MHz")

    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine, final freq. calibration is {freq0:0.6f}->{freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)

    write_string = str(freq)
    if write_meas:
        SaveDataToTextFile(filename_freqs, write_string)



















# Update parameters
filepath0 = 'Z:\\Lab Data\\D52_Calibration_Ba137\\'
filename0 = 'freqmeas_f2m2_singlecoil_*'
files0 = filepath0 + filename0 + '*'
files0 = np.array(glob.glob(files0)) 

filename_params = '1762_Transition-Freq_Parameters_' + str(timenow.year) + \
    "{:02d}".format(timenow.month) + "{:02d}".format(timenow.day) + "{:02d}".format(timenow.hour) + \
    "{:02d}".format(timenow.minute)+ "{:02d}".format(timenow.second) + '.txt'
filename_params = filepath0 + filename_params

data_all = getData_1762_Calib(files0)[:,:,0]
    
calib_transitions = [0, 4, 9]
good_transitions = [1, 2, 3, 5, 6, 7, 8, 10, 11, 12]

sensitivities = data_all[:,calib_transitions[1]] - data_all[:,calib_transitions[0]] 
offsets = data_all[:, calib_transitions[2]]

#list_parameters = []
for trans in good_transitions:
    trans_name = states_overall_trans[trans]
    freqs = data_all[:,trans] - offsets
    popt, pcov = curve_fit(linear_fit, sensitivities, freqs)
    write_string = ''.join([str(param) + '\t' for param in popt])
    if write_param_file:
        print(write_string)
        SaveDataToTextFile(filename_params, write_string)