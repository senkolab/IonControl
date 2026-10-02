#Shelving_Measurement_DLevel_SPAM_Calibrate-Freq.py created 2022-11-03 17:37:10.182296
#Do the freq. calibrations by first finding the two sensitive transitions f4m3, f4m0, using the freq. difference to estimate the B-field from the Hamiltonian model, then find the other transitions based on the B-field
#Uses a large fine-scan for the other transitions because the Hamiltonian model isn't good enough
import sys
import os
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

save_global_freqs = True
send_AWG = False
rough_freq_large = False
rough_pitime_large = False

WhichIon = getGlobal("WhichIon").magnitude
AWG_Mode_global = "AWG1_Mode"
pulse_program_TriggerAWGEvent = "TriggerAWGEvent"
if WhichIon == 138:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Even"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses"
    state_string = f'Ba138_Shelving_'
elif WhichIon == 137:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Ba137"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses_Ba137"
    state_string0 = f'Ba137_Shelving_F2P2_'
    states_overall_trans = ["Fp4_a_mp4", "Fp4_b_mp3", "Fp4_c_mp2", "Fp4_d_mp1", "Fp4_e_mp0", \
    "Fp3_b_mp3", "Fp3_c_mp2", "Fp3_d_mp1", "Fp3_e_mp0", \
    "Fp2_c_mp2", "Fp2_d_mp1", "Fp2_e_mp0", \
    "Fp1_d_mp1", "Fp1_e_mp0"]


data_all = np.load('C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\config\\Scripts\\bf_freqdiffs_f4m3f4m0.npy', allow_pickle=True)


states_use = []
for state in states_overall_trans:
    state_use_string = state_string0 + state + '_Use'
    state_use = getGlobal(state_use_string).magnitude
    if state_use:
        states_use.append(state)
print(states_use)

states_use_first = [states_overall_trans[1],states_overall_trans[4]]
states_use_second = []
for state in states_use:
    if state not in states_use_first:
        states_use_second.append(state)

skip = [1,2,3,4,6,7,8,9,10]
skip = []






#Rough freq. scan - 10 kHz
freqrough_step, freqrough_range_small = 0.01, 0.1
if rough_freq_large:
    freq_range1 = 2*freqrough_range_small
else:
    freq_range1 = freqrough_range_small


#More precise freq. scan - 1 kHz
freqfine_step, freqfine_range = 0.001, 0.015
freq_range2 = freqfine_range
#freq_step2, freq_range2 = 0.001, freq_range1/5

pulse_time_default = 1000 #us

if send_AWG:
    awg_clock = 1.048576e9
    awg_num_points = 1048576
    awg_amplitude_dBm = 3
    AWG1 = AWG()

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(states_use)}-level_{addname}_prints_freq*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Freq-Scan:{freq_range1},{freqrough_step};Fine-Freq-Scan:{freqfine_step},{freq_range2};, states_use_first:{states_use_first}"

WriteString += f"\nTransitions:{states_use}"

SaveDataToTextFile(filename0, WriteString)

AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal(AWG_Mode_global, 0, "")











freqs_found_1 = []
for i, state in enumerate(states_use_first):
    if scriptIsStopped():
        break
    setEvaluation('Eval3')
    #Setup list of the global variables for the states
    state_string = f'{state_string0}{state}'
    state_freq_string_global = state_string + '_Freq'
    state_pi_time_string_global = state_string + '_Pi_Time'
    
    #Run rough freq. scan to find this transition
    freq0 = getGlobal(state_freq_string_global).magnitude
    freq_start = freq0-freq_range1/2
    freq_stop = freq0+freq_range1/2
    pulse_time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%pulse_time == "%s us"%pulse_time_default:
        setGlobal("Shelving_Pulse_Time", pulse_time_default, "us")
    freq = freq0
    freq = findResonance(freq_start, freq_stop, freqrough_step, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough freq. scan gave peak freq. of {freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    
    setEvaluation('Eval2')
    SaveDataToTextFile(filename0, print_string)
    
    #Run fine freq. scan to find this calibrated transition
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pulse_time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%pulse_time == "%s us"%pi0:
        setGlobal("Shelving_Pulse_Time", pi0, "us")
    freq_start = freq-1.5*freq_range2
    freq_stop = freq+1.5*freq_range2
    print(f'freq_start:{freq_start}, freq_stop:{freq_stop}')
    freq = freq0
    freq = findResonance(freq_start, freq_stop, freqfine_step, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    state_freq = getGlobal(state_freq_string_global)
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freqs: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 6), "MHz")
    freqs_found_1.append(freq)
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine, final freq. calibration is {freq0:0.6f}->{freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    #Send the freq. to the AWG
    if send_AWG:
        awg_segment = i
        awg_freq = freq
        awg_phase = 0
        Waveform1 = Waveform(awg_clock, awg_freq, num_points=awg_num_points, timeQ=False, phase=awg_phase)
        AWG1.send_single_awseg(Waveform1, awg_segment, amp_dBm=awg_amplitude_dBm)





freq_f4mp3, freq_f4mp0 = freqs_found_1
#freq_f4mp3, freq_f4mp0 = 598.154, 630.675
b_match, freqs_inferred = inferOtherShelvingTransitions(freq_f4mp3, freq_f4mp0, which_f4m0=5)
freqs_inferred = abs(freqs_inferred)
print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: first states f4mp3, f4mp0: {state}: freqs: {freqs_found_1}, b_field_fit = {b_match}, freqs_inferred={freqs_inferred}'
print(print_string)
SaveDataToTextFile(filename0, print_string)






for i, state in enumerate(states_use_second):
    if i in skip:
        print(f'skipped step {i}')
        continue
    if scriptIsStopped():
        break
    setEvaluation('Eval3')
    #Setup list of the global variables for the states
    state_string = f'{state_string0}{state}'
    state_freq_string_global = state_string + '_Freq'
    state_pi_time_string_global = state_string + '_Pi_Time'
    #Find the matching inferred transition freq.
    state_freq = getGlobal(state_freq_string_global)
    diff_freqs = abs(freqs_inferred - state_freq.magnitude)
    freq_inferred = freqs_inferred[np.argmin(diff_freqs)]
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: state:{state}, matching frequency found to be {freq_inferred} MHz from previous {state_freq} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    freq = freq_inferred
    #if not "%s"%state_freq == "%s MHz"%freq_inferred and save_global_freqs: #Set global variable storing this transition's freq.
    #    setGlobal(state_freq_string_global, np.round(freq_inferred, 6), "MHz")
    
    setEvaluation('Eval2')
    
    #Run fine freq. scan to find this calibrated transition
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pulse_time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%pulse_time == "%s us"%pi0:
        setGlobal("Shelving_Pulse_Time", pi0, "us")
    freq_start = freq-1.5*freq_range2
    freq_stop = freq+1.5*freq_range2
    print(f'freq_start:{freq_start}, freq_stop:{freq_stop}')
    #freq = freq0
    freq = findResonance(freq_start, freq_stop, freqfine_step, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    state_freq = getGlobal(state_freq_string_global)
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freqs: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 6), "MHz")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine, final freq. calibration is {state_freq:0.6f}->{freq_inferred:0.6f}->{freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    #Send the freq. to the AWG
    if send_AWG:
        awg_segment = i
        awg_freq = freq
        awg_phase = 0
        Waveform1 = Waveform(awg_clock, awg_freq, num_points=awg_num_points, timeQ=False, phase=awg_phase)
        AWG1.send_single_awseg(Waveform1, awg_segment, amp_dBm=awg_amplitude_dBm)