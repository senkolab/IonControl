#Qudit_ramsey.py created 2024-06-03 17:12:12.796107

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

import sys
import time
import os
import datetime
import glob
import json
import numpy as np
import random
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"

line_trigger_wait = 0
Side_band_cooling_reps = 0

Take_calibrations = True
real_wait_time_bool = True
#set_freq = 609.536
#probe_trans = [[0,4,1],[0,4,0],[0,3,0],[0,2,0]]
# d=3
probe_trans = [[0,2,-2]]
#probe_trans = [[0,4,-2],[0,4,-1],[0,4,0],[0,4,1],[0,3,1],[0,3,2],[0,2,0],[0,3,0]]
detunings = [0]

s12_level = probe_trans[0][0]

#detuning = 0.005
periodicity = 100 #us

stop_time = 100
start_time = 0
time_step = 10


f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

#f_offset = 545.507593
#f_upper = 623.306899

#pitime_n2 = 24.4 # [-2, 4, -4]
#pitime_n1 = 55.435 # [-2, 3, -3]
#pitime_0 = 50 # [2, 4, 2]
#pitime_p1 = 35 # [2, 4, 3]
#pitime_p2 = 46 # [2, 4, 4]

ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

setEvaluation('Eval3')

F1PumpTime = 0.5 #us
F1PumpReps = 50
InitReps = 0
fs = 4e9
threshold = 10

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

init_trans = list_of_inits[s12_level+2]
init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) 

set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
#set_freq = [545.429083,594.7936,622.70014]
print('set freq', set_freq)


for idx, delta in enumerate(detunings):
    set_freq[idx] = set_freq[idx] + delta

pi_times= list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
times = []
for i in range(len(pi_times)):
    times.append(2*pi_times[i]*np.arcsin(np.sqrt(1/(len(pi_times)+1-i)))/np.pi)


print(times)
full_freqs = set_freq + [0] + list(np.flip(set_freq))
print(full_freqs)

#set_freq = [482.5060]

#Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

line_trigger_wait_global = getGlobal('LineTriggerWait_Global')
if not "%s"%line_trigger_wait_global == "%s us"%line_trigger_wait:
    setGlobal("LineTriggerWait_Global", line_trigger_wait, "us")

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
if not "%s"%Init_PulseTime == init_pulse_time:
    setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")


pulse_program = "Qudit_ramsey_experiment"


        
def findPiTime_withfit_plotPD(f_offset,f_upper,stop_time,start_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    #setEvaluation('Eval2')
    createTrace('Qudit Ramsey ket 0 population', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
    fluor_ave = []
    pulse_time_list = []
    file_names_list = []
    while np.round(pulse_time) < stop_time:
        if scriptIsStopped():
            break

        # take calibrations every so often
        if Take_calibrations:
            if np.round(pulse_time)%200==0 or pulse_time==start_time:
                real_wait_time = 100
                delta = 0
                freq_offset = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                freq_upper = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)

            print('newly calibrated offset and upper freqs', freq_offset, freq_upper)
            #createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')

            #setEvaluation('Eval2')
        else:
            pass

        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))

        list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
        [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
        [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
        ]

        init_trans = list_of_inits[s12_level+2]

        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_trans = list_of_inits[s12_level+2]
        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        init_pulse_time = sum(init_times_array) 

        set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))

        print('set freq', set_freq)


        for idx, delta in enumerate(detunings):
            set_freq[idx] = set_freq[idx] + delta

        pi_times= list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        times = []
        for i in range(len(pi_times)):
            times.append(2*pi_times[i]*np.arcsin(np.sqrt(1/(len(pi_times)+1-i)))/np.pi)


        print(times)
        full_freqs = set_freq + [0] + list(np.flip(set_freq))
        print(full_freqs)


        print('1')

#Pulse Times ==============================================================
        if real_wait_time_bool:
            full_times = list(times) + [pulse_time] + list(np.flip(times))
        else:
            full_times = list(times) + [0] + list(np.flip(times))
#==============================================================
        Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
        if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(full_times):
            setGlobal("Ramsey_Wait_Time", sum(full_times), "us")

        half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
        if not "%s"%half_pi_time_dummy == "%s us"%sum(full_times):
            setGlobal("Shelving_Pulse_Time", sum(full_times), "us")
        print('2')
# Phase Calculations ===================================================================
        zero_phase = []
        phases = []
        for i in range(len(pi_times)):
            zero_phase.append(0)
            print("num_state:",i)
            #pulse_time = 1
            phases.append((2 * np.pi * pulse_time * (i+1) / periodicity) + np.pi)
        full_phases = zero_phase + [0] + list(np.flip(phases))
        print(full_phases)
#=======================================================================================
# AWG commands======================================================================================
        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(5)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

        print('3')
#----------------------------------------------------------------------------
        matlab_init_freqs = matlab.double(init_freqs_array)
        matlab_init_times = matlab.double(init_times_array)
#----------------------------------------------------------------------------
        print(full_freqs)
        print(full_times)
        matlab_set_freq = matlab.double(full_freqs)
        matlab_probe_pulse_time = matlab.double(full_times)
        matlab_probe_phases = matlab.double(full_phases)
#----------------------------------------------------------------------------
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])
        print('4.5')
        seg_num = 1
        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        print('5')
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_set_freq,matlab_probe_pulse_time,matlab_probe_phases,fs,seg_num,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
        print('6')
        # Readout pulses
        for idx, freq in enumerate(set_freq):

            matlab_ro_freq = matlab.double([freq])
            matlab_ro_time = matlab.double([pi_times[idx]])
            print(seg_num,[freq],[pi_times[idx]])
            seg_num = seg_num + 1
            eng.Pulse_upload(matlab_ro_freq,matlab_ro_time,fs,seg_num,power_factor,nargout = 0)
            if scriptIsStopped():
                break
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence

#-------------------------------------------------------------------------------------------------------------------------
        print('7')

        eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
        seq_num = 4

        for idx, freq in enumerate(set_freq):
            seq_num = seq_num + 1
            string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,0"
            eng.SendAWGCommand(string, nargout=0)
            seq_num = seq_num + 1
            string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,1"
            eng.SendAWGCommand(string, nargout=0)

        Table_length_dummy =  getGlobal('Table_length')
        if not "%s"%Table_length_dummy == seq_num:
            setGlobal("Table_length", seq_num, "")

        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

        eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

        eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)


        #total_time = sum([piover2_time,pulse_time,piover2_time])+30
        #PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
        #if not "%s"%PulseTime_Dummy == "%s us"%total_time:
        #    setGlobal("Shelving_Pulse_Time", total_time, "us")
        #time.sleep(0.2)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

        data = getAllData()
        herald_data = data['PMT Index 0'][1]
        print(herald_data)
        ket1_data = data['PMT Index 1'][1]
        print(ket1_data)
        ket2_data = data['PMT Index 2'][1]
        print(ket2_data)

        arrays = []
        for idx,herald_outcome in enumerate(herald_data):
            if herald_outcome < threshold:# and ket1_data[idx] < threshold:
                arrays.append(ket1_data[idx])
        mean_value = np.mean(np.array(arrays)<threshold)

        if not file_names_list_all:
            matching_files = glob.glob(pattern)
            matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
            file_path = matching_files[-1]
            chunks = file_path.split('\\')
            #print(chunks[-1])        
            fname = chunks[-1]
            file_names_list_all.append(fname)
            file_names_list.append(fname)
        else: 
            filename = file_names_list_all[-1]
            parts = filename.split('_')
            original_number_str = parts[-1]
            num_digits = len(original_number_str)
            number = int(original_number_str) + 1
            new_number_str = str(number).zfill(num_digits)
            new_filename = '_'.join(parts[:-1]) + f'_{new_number_str}'
            file_names_list_all.append(new_filename)
            if U1_only:
                file_names_list_U1.append(new_filename)
            else:
                file_names_list.append(new_filename)

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)


        matching_files = glob.glob(pattern)
        matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
        file_path = matching_files[-1]
        chunks = file_path.split('\\')
        #print(chunks[-1])        
        fname = chunks[-1]
        file_names_list.append(fname)
        print("=========================================")

        arrays = []
        with open(file_path, 'r') as file:
            print(file_path)
            for line in file:
                data = json.loads(line)
                arrays.append(data[0]["0"][0])
        mean_value = np.mean(np.array(arrays)<threshold)
        print("=========================================")

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)
        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD,'Qudit Ramsey ket 0 population', plotStyle=2)

        pulse_time = pulse_time + time_step
        
    closeTrace('Qudit Ramsey ket 0 population')
    freq_string = str(round(set_freq[0],3)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_Dimension_{len(set_freq)+1}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{set_freq}\n")
        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
        file.write(f"{phases}\n")
        file.write(f"{file_names_list}\n")

setEvaluation('Eval3')

pi_time = findPiTime_withfit_plotPD(f_offset,f_upper,stop_time,start_time, time_step, threshold, pulse_program, script_functions)
print(pi_time)
#setEvaluation('Eval2')
#with open(output_file_pitimes,'a') as outfile:
#    outfile.write(f'{pi_time}\n')

eng.quit()