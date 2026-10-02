#Shelving_Measurement_DLevel_SPAM_Calibrate-Freq-and-PiTime.py created 2022-10-08 00:28:39.907214

import sys
import os
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

save_global_freqs = True
save_global_pitimes = False
send_AWG = False
rough_freq_large = False
rough_pitime_large = False
skip = [1,2,3,4,6,7,8,9,10]
skip = []

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
states_use = []
for state in states_overall_trans:
    state_use_string = state_string0 + state + '_Use'
    state_use = getGlobal(state_use_string).magnitude
    if state_use:
        states_use.append(state)
print(states_use)

#Rough freq. scan - 10 kHz
freqrough_step, freqrough_range_small, freqrough_range_large = 0.01, 0.1, 0.2
if rough_freq_large:
    freq_range1 = freqrough_range_large
else:
    freq_range1 = freqrough_range_small
#More precise freq. scan - 1 kHz
freq_step2, freq_range2 = 0.001, freq_range1/5

#rough pi pulse timing scan this is for calibrating the freq. - percentage of pi-time
pirough_range1 = 0.5 

#rough pi pulse timing scan - 1 us - this is for calibrating the pi-time. Ranges in % of previously measured pi-time
pirough_range2_small, pirough_range2_large = 0.5, 0.25
if rough_pitime_large:
    pirough_range2 = pirough_range2_large
else:
    pirough_range2 = pirough_range2_small
#Fine pi pulse timing scan - this is for calibrating the pi-time
pifine_range = pirough_range2/5

pulse_time_default = 1000 #us


if send_AWG:
    awg_clock = 1.048576e9
    awg_num_points = 1048576
    awg_amplitude_dBm = 3
    AWG1 = AWG()

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(states_use)}-level_{addname}_prints*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Freq-Scan:{freq_range1},{freqrough_step};Fine-Freq-Scan:{freq_range2},{freq_step2};Rough-Time-Scan1:{pirough_range1};Rough-Time-Scan2:range{pirough_range2};Fine-Time-Scan:range{pifine_range}"

WriteString += f"\nTransitions:{states_use}"

SaveDataToTextFile(filename0, WriteString)

AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal(AWG_Mode_global, 0, "")

state_freq_globals = []
state_pi_time_globals = []
for i, state in enumerate(states_use):
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
    state_freq_globals.append(state_freq_string_global)
    state_pi_time_globals.append(state_pi_time_string_global)
    
    #Run rough freq. scan to find this transition
    freq0 = getGlobal(state_freq_string_global).magnitude
    freq_start = freq0-freq_range1/2
    freq_stop = freq0+freq_range1/2
    pulse_time = getGlobal("Shelving_Pulse_Time")
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pi_rough = pi0
    pulse_time_set = pi_rough*1.2
    if not "%s"%pulse_time == "%s us"%pulse_time_set:
        setGlobal("Shelving_Pulse_Time", pulse_time_set, "us")    
    #if not "%s"%pulse_time == "%s us"%pulse_time_default:
    #    setGlobal("Shelving_Pulse_Time", pulse_time_default, "us")
    freq = freq0
    freq = findResonance(freq_start, freq_stop, freqrough_step, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough freq. scan gave peak freq. of {freq:0.6f} MHz'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    
    setEvaluation('Eval2')
    #Run a rough time scan 
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pi_start = 0.5*pi0
    pi_stop = 1.5*pi0
    pi_step = 0.1*pi0
    setGlobalPulseTimeScan_Meas(np.round(pi_start,1), np.round(pi_stop,1), np.round(pi_step,1), script_functions)
    pi_rough = pi0
    #pi_rough = findPiTimeRough(pulse_program_findpi, script_functions)
    pulse_time_set = pi_rough*1.2
    pulse_time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%pulse_time == "%s us"%pulse_time_set:
        setGlobal("Shelving_Pulse_Time", pulse_time_set, "us")
    print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Freq. calibrating rough time scan gave pi-pulse of {pulse_time_set:0.1f} us'
    print(print_string)
    SaveDataToTextFile(filename0, print_string)
    
    #Run fine freq. scan to find this calibrated transition
    freq_start = freq-1.5*freqrough_step
    freq_stop = freq+1.5*freqrough_step
    print(f'freq_start:{freq_start}, freq_stop:{freq_stop}')
    freq = freq0
    freq = findResonance(freq_start, freq_stop, freq_step2, pulse_program_findres, script_functions, AWG=True)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq:
        setGlobal("AWG1_Frequency", freq, "MHz")
    state_freq = getGlobal(state_freq_string_global)
    if not "%s"%state_freq == "%s MHz"%freq and save_global_freqs: #Set global variable storing this transition's freq.
        setGlobal(state_freq_string_global, np.round(freq, 6), "MHz")
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
    


os.system("C:/Users/ions/Documents/Beep.bat")
continue_pitime = input('Continue on to do the pi-time calibrations? Only input once the sequences are programmed. y or n')
continue_pitime = continue_pitime == 'y'

if continue_pitime:
    AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
    if not int(AWG_mode_curr) == 2: #Set global variable storing this transition's freq.
        setGlobal(AWG_Mode_global, 2, "")
    #Move past the first dummy segment
    setScan(pulse_program_TriggerAWGEvent)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    for i, state in enumerate(states_use):
        if i in skip:
            print(f'skipped step {i}')
            setScan(pulse_program_TriggerAWGEvent)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            continue
        if scriptIsStopped():
            break
        #Run rough time scan, now that freq. is calibrated
        pi0 = getGlobal(state_pi_time_string_global).magnitude
        pi_start = pi0 - pirough_range2*pi0/2
        pi_stop = pi0 + pirough_range2*pi0/2
        pirough_step2 = pirough_range2*pi0/10
        scan = (np.round(pi_start, 1), np.round(pi_stop,1), np.round(pirough_step2,1))
        pi_rough = pi0
        #pi_rough = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough time scan gave pi-pulse of {pi_rough:0.1f} us'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)

        #Run through even finer time scan to find final calibrated pi pulse time
        pi_start = pi_rough - pifine_range*pi0/2
        pi_stop = pi_rough + pifine_range*pi0/2
        pifine_step = pifine_range*pi0/10
        scan = (np.round(pi_start,1), np.round(pi_stop,1), np.round(pifine_step,1))
        pi_time = pi_rough
        pi_time = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        state_pi = getGlobal(state_pi_time_string_global)
        if not "%s"%state_pi == "%s us"%pi_time and save_global_pitimes: #Set global variable storing this transition's pi pulse time
            setGlobal(state_pi_time_string_global, np.round(pi_time, 1), "us")
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine, final time scan calibration is {pi0:0.1f}->{pi_time:0.1f} us'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        setScan(pulse_program_TriggerAWGEvent)
        startScan(globalOverrides=list(), wait=True)
        stopScan()