#Shelving_D52_PiTimes_Scan.py created 2022-12-16 16:46:46.406508

#Shelving_Measurement_DLevel_SPAM_CalibratePiTime.py created 2022-10-19 17:01:09.348605

import sys
import os
import numpy as np
import datetime
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

save_global_pitimes = False
write_param_file = False
write_data = True
use_fitting = True
use_awg_segments = False
rough_pitime_large = True
skip = [0,1,2,3,4,5,6,7,8,9,10,12]
skip = [3, 4, 5, 6, 7, 8, 9, 10, 11]
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
    "Fp1_d_mp1", "Fp1_e_mp0"]#Took out f3m3
states_good = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
calib_transitions = [0, 1, 2, 3, 4] #use f4 transitions for +2, +1, 0, -1, -2 calibrations
transitions_dmp2 = []
transitions_dmp1 = []
transitions_dm0 = [5, 8]
transitions_dmn1 = [6, 9, 11]
transitions_dmn2 = [7, 10, 12]
good_transitions = [transitions_dmp2, transitions_dmp1, transitions_dm0, transitions_dmn1, transitions_dmn2] #Transitions to be interpolated from calibrations
states_use = []
for state in states_good:
    states_use.append(states_overall_trans[state])
#for state in states_overall_trans:
#    state_use_string = state_string0 + state + '_Use'
#    state_use = getGlobal(state_use_string).magnitude
#    if state_use:
#        states_use.append(state)
#print(states_use)

pisteps_rough = 20
pisteps_fine = pisteps_rough*2
pitimestep_finefraction = 1/200
pitimestep_roughfraction = 5*pitimestep_finefraction

pulse_time_default = 1000 #us



BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Shelving_Measurement_Calibration_{len(states_use)}-level_{addname}_prints_pitime*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Rough-Time-Scan:{pitimestep_roughfraction}, Fine-Time-Scan:{pitimestep_finefraction}"
WriteString += f"\nTransitions:{states_use}"
SaveDataToTextFile(filename0, WriteString)

writeFolder = r'Z:\Lab Data\D52_Calibration_Ba137'
timenow = datetime.datetime.now()
add_name = '110deg'
filename = 'pitimemeas_f2m2_' + add_name + str(timenow.year) + "{:02d}".format(timenow.month) + "{:02d}".format(timenow.day) + "{:02d}".format(timenow.hour) \
+ "{:02d}".format(timenow.minute)+ "{:02d}".format(timenow.second) + '.txt'
filename_pitimes_calib = writeFolder + '\\' + filename


#AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
#if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
#    setGlobal(AWG_Mode_global, 0, "")

setGlobal('AWGClockRef',int(1),'')
time.sleep(0.01)
setGlobal('AWGClockRef',int(0),'')
time.sleep(0.1)


if use_awg_segments:
    mode = 2
else:
    mode = 0
AWG_mode_curr = getGlobal(AWG_Mode_global).magnitude
if not int(AWG_mode_curr) == mode: #Set global variable storing this transition's freq.
    setGlobal(AWG_Mode_global, mode, "")

if use_awg_segments:
    #Move past the first dummy segment
    setScan(pulse_program_TriggerAWGEvent)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
for i, state in enumerate(states_use):
    if i in skip:
        print(f'skipped step {i}')
        #if use_awg_segments:
        #    setScan(pulse_program_TriggerAWGEvent)
        #    startScan(globalOverrides=list(), wait=True)
        #    stopScan()
        continue
    if scriptIsStopped():
        break
    setEvaluation('Eval2')
    #Run rough time scan, now that freq. is calibrated
    state_string = f'{state_string0}{state}'

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
    write_string = str(pi_time)
    if write_data:
        SaveDataToTextFile(filename_pitimes_calib, write_string)
    if use_awg_segments:
        setScan(pulse_program_TriggerAWGEvent)
        startScan(globalOverrides=list(), wait=True)
        stopScan()






filepath0 = 'Z:\\Lab Data\\D52_Calibration_Ba137\\'
filename0 = 'pitimemeas_'
files0 = filepath0 + filename0 + '*'
files0 = files00 = np.array(glob.glob(files0)) 

filename_params = '1762_Transition-PiTime_Parameters_' + str(timenow.year) + \
    "{:02d}".format(timenow.month) + "{:02d}".format(timenow.day) + "{:02d}".format(timenow.hour) + \
    "{:02d}".format(timenow.minute)+ "{:02d}".format(timenow.second) + '.txt'
filename_params = filepath0 + filename_params

data_all = getData_1762_Calib(files0)[:,:,0]
data_all_calib = data_all[:, calib_transitions]
calib_mean = np.mean(data_all_calib, 1) #Get mean of all calibrated points, global amplitude for fit

list_parameters = []
for i, transitions in enumerate(good_transitions):
    calib_trans = calib_transitions[i]
    calib_trans_name = states_overall_trans[calib_trans]
    calib_pitimes = data_all[:,calib_trans]
    for trans in transitions:
        trans_name = states_overall_trans[trans]
        pitimes = data_all[:,trans]
        pitimes_ratio = pitimes/calib_mean
        popt, pcov = curve_fit(poly_fit, calib_pitimes, pitimes_ratio)
        list_parameters.append(list(popt))
        write_string = ''.join([str(param) + '\t' for param in popt])
        if write_param_file:
            print(write_string)
            SaveDataToTextFile(filename_params, write_string)