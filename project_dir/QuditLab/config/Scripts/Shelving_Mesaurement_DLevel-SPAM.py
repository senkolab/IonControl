#Shelving_Mesaurement_DLevel-SPAM.py created 2022-10-11 16:45:02.370638

#D52_6Level_SPAM_Scan_PulseTime.py created 2022-06-03 15:49:43.550154

import sys
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint)

WhichIon = getGlobal("WhichIon").magnitude
if WhichIon == 138:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Even"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses"
    state_string = f'Ba138_Shelving_'
    
    measurement_scan = "Shelving_Measurement_Ba138_6Level_Qudit_SPAM_Exp"
elif WhichIon == 137:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Ba137"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses_Ba137"
    state_string = f'Ba137_Shelving_F2P2_'
    states_overall_trans = ["Fp4_a_mp4", "Fp4_b_mp3", "Fp4_c_mp2", "Fp4_d_mp1", "Fp4_e_mp0", \
    "Fp3_b_mp3", "Fp3_c_mp2", "Fp3_d_mp1", "Fp3_e_mp0", \
    "Fp2_c_mp2", "Fp2_d_mp1", "Fp2_e_mp0", \
    "Fp1_d_mp1", "Fp1_e_mp0"]
    measurement_scan = "Shelving_Measurement_DLevel_Qudit_SPAM_Exp_Ba137"

states_use = []
for state in states_overall_trans:
    state_use_string = state_string + state + '_Use'
    state_use = getGlobal(state_use_string).magnitude
    if state_use:
        states_use.append(state)
print(states_use)

Measurement_PMT_Int_Time = getGlobal("Measurement_PMT_Int_Time")
Measurement_Experiments = getGlobal("Measurement_Experiments")
AWG_Amp = getGlobal("AWG1_Power_dBm")
Repump_Freq = getGlobal("ShelvingRepumpFreq").magnitude
Repump_Time = getGlobal("Shelve_Repump_Time")
OpticalPump_Time = getGlobal("OpticalPumpTimeGlobal")

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"SPAM_{len(states_use)+1}-level_{addname}_prints*.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=True)
WriteString = f"Metadata,Ion:{WhichIon}, Experiments:{Measurement_Experiments}, States_use:{states_use}, PMT Int. Time:{Measurement_PMT_Int_Time}, AWG amp (dBm):{AWG_Amp}, Repump Freq:{Repump_Freq}, Repump Time:{Repump_Time}, Optical Pump Time {OpticalPump_Time}"
SaveDataToTextFile(filename0, WriteString)

string_state_state = ""
string_state_pitimes = ""
string_state_freqs = ""

StartState = 0
for i in range(len(states_use)+1):
    state_curr = states_use[i-1]
    string_state_state += state_curr + '\t'
    state_pitimes_global = state_string + state_curr + "_Pi_Time"
    pi_time = getGlobal(state_pitimes_global)
    string_state_pitimes += str(pi_time.magnitude) + ' us\t'
    state_freq_global = state_string + state_curr + "_Freq"
    freq = getGlobal(state_freq_global)
    string_state_freqs += str(freq.magnitude) + ' THz\t'
    if i == 0:
        print(f'StartState {i}: state ground')
    else:
        print(f'StartState {i}: state {states_use[i-1]}')
    StartStateGUI = getGlobal("StartState_Which_d")
    if not "%s"%StartStateGUI == "%s"%int(i):
        setGlobal("StartState_Which_d", int(i), "")
    if i == 0:
        startstate_trans = 0
    else:
        startstate_string = states_use[i-1]
        startstate_trans = states_overall_trans.index(startstate_string)+1
    StartState_transGUI = getGlobal("StartState_Overall_trans")
    if not "%s"%StartState_transGUI == "%s"%int(startstate_trans):
        setGlobal("StartState_Overall_trans", int(startstate_trans), "")

    #time_step = 0.1
    #start_time = 27
    #stop_time = 32
        
    #set_time = start_time
    #PulseTimeString = f"{state_string}{startstate_string}_Pi_Time"
    #Try for different pulse times to find the optimal measurement pulse-time
    #while set_time < stop_time:
        #if scriptIsStopped():
        #    break
    #PulseTime = getGlobal(PulseTimeString)
    #if not "%s"%PulseTime == "%s us"%set_time:
    #    setGlobal(PulseTimeString, set_time, "us")
    setScan(measurement_scan)
    startScan(globalOverrides=list(), wait=True)
    #set_time = set_time + time_step
WriteString = string_state_state + '\n' + string_state_freqs + '\n' + string_state_pitimes + '\n'
SaveDataToTextFile(filename0, WriteString)