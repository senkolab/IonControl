#Shelving_Measurement_DLevel_SPAM_Calibrate_PiTime_Interpolate.py created 2022-12-16 17:43:56.160632

import sys
import os
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

save_global_pitimes = True
use_fitting = True
use_awg_segments = True
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
    "Fp3_c_mp2", "Fp3_d_mp1", "Fp3_e_mp0", \
    "Fp2_c_mp2", "Fp2_d_mp1", "Fp2_e_mp0", \
    "Fp1_d_mp1", "Fp1_e_mp0"]
#states_good = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
calib_transitions = [0, 1, 2, 3, 4] #use f4 transitions for +2, +1, 0, -1, -2 calibrations
transitions_dmp2 = []
transitions_dmp1 = []
transitions_dm0 = [5, 8]
transitions_dmn1 = [6, 9, 11]
transitions_dmn2 = [7, 10, 12]
good_transitions = [transitions_dmp2, transitions_dmp1, transitions_dm0, transitions_dmn1, transitions_dmn2] #Transitions to be interpolated from calibrations

bad_calib_trans = []

pisteps_rough = 20
pisteps_fine = pisteps_rough*2
pitimestep_finefraction = 1/200
pitimestep_roughfraction = 5*pitimestep_finefraction

pulse_time_default = 1000 #us





#Get the latest calibration interpolation parameters
filepath0 = r'Z:\\Lab Data\\D52_Calibration_Ba137\\'
filename0 = '1762_Transition-PiTime_Parameters_'
files0 = filepath0 + filename0 + '*'
files0 = np.array(glob.glob(files0)) 
files0_latest = np.array([files0[-1]])
list_parameters = getData_1762_Calib(files0_latest)[0,:,:]
print(list_parameters)







BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(calib_transitions)}-level_{addname}_prints_pitime_interpolate*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Time-Scan:{pitimestep_roughfraction}, Fine-Time-Scan:{pitimestep_finefraction}"
WriteString += f"\nTransitions:{calib_transitions}"
SaveDataToTextFile(filename0, WriteString)

setEvaluation('Eval2')

if use_awg_segments:
    mode = 2
else:
    mode = 0
AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
if not int(AWG_mode_curr) == mode: #Set global variable storing this transition's freq.
    setGlobal(AWG_Mode_global, mode, "")

setGlobal('AWGClockRef',int(1),'')
time.sleep(0.01)
setGlobal('AWGClockRef',int(0),'')
time.sleep(0.1)

times_found = []
which_segment = 0
if use_awg_segments:
    #Move past the first dummy segment
    setScan(pulse_program_TriggerAWGEvent)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    which_segment += 1
for i, state in enumerate(calib_transitions):
    if scriptIsStopped():
        break
    #Run rough time scan, now that freq. is calibrated
    state_string = f'{state_string0}{states_overall_trans[state]}'
    
    if not use_awg_segments:
        state_freq_string_global = state_string + '_Freq'
        freq0 = getGlobal(state_freq_string_global).magnitude
        AWG1_Freq = getGlobal("AWG1_Frequency")
        if not "%s"%AWG1_Freq == "%s MHz"%freq0:
            setGlobal("AWG1_Frequency", freq0, "MHz")

    state_pi_time_string_global = state_string + '_Pi_Time'
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pi_start = 0.6*pi0
    pi_stop = 1.4*pi0
    #pi_steps = pisteps_rough
    pi_step = pitimestep_roughfraction*pi0
    scan = (np.round(pi_start, 2), np.round(pi_stop,2), pi_step)
    pi_time = pi0
    if use_fitting:
        popt, xs, ys = fitPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        pi_time, scale_time, amp, bg = popt
        fidelity_rough = (amp-bg)/amp
        fidelity = max(ys)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fitting time scan gave pi-pulse of {pi0:0.1f}.>{pi_time:0.1f} us, fidelity {fidelity}, scale_time:{scale_time}, amp={amp}, bg={bg}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        createTrace('pi-fit', 'Scan Data', xLabel=f'Time (us)')
        plotList(xs, ys, 'pi-fit', plotStyle=0)
        closeTrace('pi-fit')
    else:
        pi_rough, fidelity = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough time scan gave pi-pulse of {pi_rough:0.1f} us, fidelity {fidelity}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        #pirough_step2 = (pi_stop-pi_start)/pi_steps
        #Run through even finer time scan to find final calibrated pi pulse time
        pi_start = pi_rough - 1.1*pi_step
        pi_stop = pi_rough + 1.1*pi_step
        pi_steps = pisteps_fine
        pifine_step = pitimestep_finefraction*pi0
        #pifine_step = (pi_stop-pi_start)/pi_steps
        scan = (np.round(pi_start, 2), np.round(pi_stop,2), pifine_step)
        pi_time, fidelity = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine time scan gave pi-pulse of {pi_rough:0.1f}->{pi_time:0.1f} us, fidelity {fidelity}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
    state_pi = getGlobal(state_pi_time_string_global)
    if not "%s"%state_pi == "%s us"%pi_time and save_global_pitimes: #Set global variable storing this transition's pi pulse time
        setGlobal(state_pi_time_string_global, np.round(pi_time, 1), "us")
    if use_awg_segments:
        setScan(pulse_program_TriggerAWGEvent)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        which_segment += 1
    times_found.append(pi_time)

for i, state in enumerate(bad_calib_trans):
    if scriptIsStopped():
        break
    #Run rough time scan, now that freq. is calibrated
    state_string = f'{state_string0}{states_overall_trans[state]}'
    if use_awg_segments:
        num_steps_to_segment = state + 1 - which_segment
        for j in range(num_steps_to_segment):
            setScan(pulse_program_TriggerAWGEvent)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            which_segment += 1
    else:
        state_freq_string_global = state_string + '_Freq'
        freq0 = getGlobal(state_freq_string_global).magnitude
        AWG1_Freq = getGlobal("AWG1_Frequency")
        if not "%s"%AWG1_Freq == "%s MHz"%freq0:
            setGlobal("AWG1_Frequency", freq0, "MHz")
    state_pi_time_string_global = state_string + '_Pi_Time'
    pi0 = getGlobal(state_pi_time_string_global).magnitude
    pi_start = 0.6*pi0
    pi_stop = 1.4*pi0
    #pi_steps = pisteps_rough
    pi_step = pitimestep_roughfraction*pi0
    scan = (np.round(pi_start, 2), np.round(pi_stop,2), pi_step)
    pi_time = pi0
    if use_fitting:
        popt, xs, ys = fitPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        pi_time, scale_time, amp, bg = popt
        fidelity_rough = (amp-bg)/amp
        fidelity = max(ys)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fitting time scan gave pi-pulse of {pi0:0.1f}.>{pi_time:0.1f} us, fidelity {fidelity}, scale_time:{scale_time}, amp={amp}, bg={bg}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        createTrace('pi-fit', 'Scan Data', xLabel=f'Time (us)')
        plotList(xs, ys, 'pi-fit', plotStyle=0)
        closeTrace('pi-fit')
    else:
        pi_rough, fidelity = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Rough time scan gave pi-pulse of {pi_rough:0.1f} us, fidelity {fidelity}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        #pirough_step2 = (pi_stop-pi_start)/pi_steps
        #Run through even finer time scan to find final calibrated pi pulse time
        pi_start = pi_rough - 1.1*pi_step
        pi_stop = pi_rough + 1.1*pi_step
        pi_steps = pisteps_fine
        pifine_step = pitimestep_finefraction*pi0
        #pifine_step = (pi_stop-pi_start)/pi_steps
        scan = (np.round(pi_start, 2), np.round(pi_stop,2), pifine_step)
        pi_time, fidelity = findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold)
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {i}: {state}: Fine time scan gave pi-pulse of {pi_rough:0.1f}->{pi_time:0.1f} us, fidelity {fidelity}'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
    state_pi = getGlobal(state_pi_time_string_global)
    if not "%s"%state_pi == "%s us"%pi_time and save_global_pitimes: #Set global variable storing this transition's pi pulse time
        setGlobal(state_pi_time_string_global, np.round(pi_time, 1), "us")
    times_found.append(pi_time)

#times_found = [60, 32.4, 19.1, 68, 55.9, 110]
#calib_transitions = [0, 1, 2, 3, 4]

#calib_mean = np.mean(times_found)

which_trans = 0
for i, transitions in enumerate(good_transitions):
    if scriptIsStopped():
        break
    calib_trans = calib_transitions[i]
    calib_trans_name = states_overall_trans[calib_trans]
    x = calib_pitime = times_found[i]
    for trans in transitions:
        if scriptIsStopped():
            break
        state_overall_trans = states_overall_trans[trans]
        #pitimes = data_all[:,trans]
        #pitimes_ratio = pitimes/calib_mean
        state_string = f'{state_string0}{state_overall_trans}'
        state_pitime_string_global = state_string + '_Pi_Time'
        params = list_parameters[which_trans]
        pi_time = (params[0] + params[1]*x)# + params[2]*x**3)/params[3]*calib_mean
        state_pitime = getGlobal(state_pitime_string_global).magnitude
        if not "%s"%state_pitime == "%s MHz"%pi_time and save_global_pitimes and (trans not in bad_calib_trans): #Set global variable storing this transition's freq.
            setGlobal(state_pitime_string_global, np.round(pi_time, 1), "us")
        print_string = f'{time.strftime("%H:%M:%S", time.gmtime())}: State {trans}: {state_overall_trans}: Calibrated pi-time. {state_pitime:0.1f}->{pi_time:0.1f} us'
        print(print_string)
        SaveDataToTextFile(filename0, print_string)
        which_trans += 1