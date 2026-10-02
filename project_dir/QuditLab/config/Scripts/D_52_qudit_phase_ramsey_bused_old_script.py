#D_52_qudit_phase_ramsey_bused_old_script.py created 2024-07-10 19:13:18.965689

#D52_Qudit_phase_ramsey_with_buses.py created 2024-06-27 14:44:06.006471

#Qudit_ramsey.py created 2024-06-03 17:12:12.796107

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

import sys
import os
import datetime
import glob
import json
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
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"

Side_band_cooling_reps = 0


initial_state = [[0,2,0]]

f_offset = 545.424641
f_upper = 623.247528

pitime_n2 = 25.403 # [-2, 4, -4]
pitime_n1 = 48.234 # [-2, 3, -3]
pitime_0 = 53.104 # [2, 4, 2]
pitime_p1 = 38.523 # [2, 4, 3]
pitime_p2 = 48.584 # [2, 4, 4]




# using -2 and +2 as bus states for D=5 ramsey =======================================================================
pulse_train = [[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,2,0],[2,2,0],[2,4,4],[2,4,3],[2,2,0],      [2,2,0],[2,4,3],[2,4,4],[2,2,0],[-2,2,0],[-2,3,-3],[-2,4,-4],[-2,2,0]]
#U1 only
pulse_train = [[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,2,0],[2,2,0],[2,4,4],[2,4,3],[2,2,0]]

probe_trans = [[0,2,0],[-2,3,-3],[-2,4,-4],[2,4,3],[2,4,4]]

fractions = [1,1/5,1/4,1,1,1/3,1/2,1,     1,1/2,1/3,1,1,1/4,1/5,1]

simulated_phase_mask = [0,0,0,0,0,0,0,0,     0,4,3,0,0,2,1,0]
fixed_phase_mask = [0,0,0,1,0,0,0,1,      0,1,1,1,0,1,1,1]


phase_shifts = zip(simulated_phase_mask,fixed_phase_mask)





# using  0 as bus states for D=5 ramsey =====================================================================================
pulse_train = [[0,2,0],[0,4,-2],[0,4,-1],[0,2,0],[0,2,0],[0,3,2],[0,3,1],[0,2,0],      [0, 2, 0], [0, 3, 1], [0, 3, 2], [0, 2, 0], [0, 2, 0], [0, 4, -1], [0, 4, -2], [0, 2, 0]]
#U1 only
#pulse_train = [[0,2,0],[0,4,-2],[0,4,-1],[0,2,0],[0,2,0],[0,3,2],[0,3,1],[0,2,0]]

probe_trans = [[0,2,0],[0,4,-2],[0,4,-1],[0,3,2],[0,3,1]]

fractions = [1,1/5,1/4,1,1,1/3,1/2,1,     1,1/2,1/3,1,1,1/4,1/5,1]

simulated_phase_mask = [0,0,0,0,0,0,0,0,     0,4,3,0,0,2,1,0]
fixed_phase_mask = [0,0,0,1,0,0,0,1,      0,1,1,1,0,1,1,1]


# using  0 as bus states for D=3 ramsey =====================================================================================
pulse_train = [[0,2,0],[0,4,-2],[0,4,-1],[0,2,0],      [0, 2, 0], [0, 4, -1], [0, 4, -2], [0, 2, 0]]
#U1 only
#pulse_train = [[0,2,0],[0,4,-2],[0,4,-1],[0,2,0]]

probe_trans = [[0,2,0],[0,4,-2],[0,4,-1]]

fractions = [1,1/3,1/2,1,     1,1/2,1/3,1]

simulated_phase_mask = [0,0,0,0,    0,2,1,0]
fixed_phase_mask = [0,0,0,1,     0,1,1,1]



phase_shifts = zip(simulated_phase_mask,fixed_phase_mask)


D = 5
detunings = np.zeros(len(probe_trans))

s12_level = initial_state[0][0]

detuning = 0.00
periodicity = 100 #us

stop_time = 110
start_time = 0
time_step = 10


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
init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) 

set_freq = list(Get_1762_EOM_Freqs(probe_trans,f_offset,f_upper))

initial_state_frequency = list(Get_1762_EOM_Freqs(initial_state,f_offset,f_upper))

pulse_train_frequencies = list(Get_1762_EOM_Freqs(pulse_train,f_offset,f_upper))


for delta in detunings:
    set_freq[0] = set_freq[0] + delta

pi_time_initial_state = list(Get_1762_PiTimes(initial_state,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

pi_time_pulse_train = list(Get_1762_PiTimes(pulse_train,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

pi_times_probe_trans = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

corrected_pulse_train_times = []

for i,_ in enumerate(pulse_train):
    frac = fractions[i]
    corrected_pulse_train_times.append(2*pi_time_pulse_train[i]*np.arcsin(np.sqrt(frac))/np.pi)


print(corrected_pulse_train_times)

print(pulse_train)


#set_freq = [482.5060]

#Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))



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

os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Qudit_ramsey_experiment_bused"


        
def findPiTime_withfit_plotPD(stop_time,start_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
    fluor_ave = []
    pulse_time_list = []
    file_names_list = []
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break

        print('1')

#Pulse Times ==============================================================
        #full_times = [pi_times[0]] + list(times) + [0] + list(np.flip(times))
#==============================================================
        Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
        if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(corrected_pulse_train_times):
            setGlobal("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us")

        half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
        if not "%s"%half_pi_time_dummy == "%s us"%sum(corrected_pulse_train_times):
            setGlobal("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us")
        print('2')
# Phase Calculations ===================================================================

        phases = []
        for i,_ in enumerate(pulse_train):
            pi_phase = fixed_phase_mask[i]
            real_phase = simulated_phase_mask[i]
            x = (2 * np.pi * pulse_time * real_phase / periodicity)
            y = pi_phase*np.pi
            print(i,x,y)
            phases.append(x + y)
            
        full_phases = phases
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
#---------------------------------------------------------------------------- S1/2 inits
        matlab_init_freqs = matlab.double(init_freqs_array)
        matlab_init_times = matlab.double(init_times_array)
#---------------------------------------------------------------------------- D5/2 init pulse
        print(initial_state_frequency)
        print(pi_time_initial_state)
        matlab_initial_state_freq = matlab.double(initial_state_frequency)
        matlab_initial_state_pulse_time = matlab.double(pi_time_initial_state)
        matlab_initial_state_phases = matlab.double([0])
#---------------------------------------------------------------------------------------------------------- pulse_train
        print(pulse_train_frequencies)
        print(corrected_pulse_train_times)
        matlab_pulse_train_freqs = matlab.double(pulse_train_frequencies)
        matlab_pulse_train_times = matlab.double(corrected_pulse_train_times)
        matlab_pulse_train_phases = matlab.double(full_phases)
#---------------------------------------------------------------------------- Uploading
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])
        print('4.5')
        seg_num = 1
        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1 
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
        print('5')
        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence

        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_pulse_train_freqs,matlab_pulse_train_times,matlab_pulse_train_phases,fs,seg_num,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
        print('6')
        # Readout pulses
        for idx, freq in enumerate(set_freq):

            matlab_ro_freq = matlab.double([freq])
            matlab_ro_time = matlab.double([pi_times_probe_trans[idx]])
            print(seg_num,[freq],[pi_times_probe_trans[idx]])
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
        eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)
        seq_num = 6

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

        matching_files = glob.glob(pattern)
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
                arrays.append(data[0]["0"][2])
        mean_value = np.mean(np.array(arrays)<threshold)
        print("=========================================")

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)
        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD,'Qudit Ramsey, 0 state', plotStyle=2)

        pulse_time = pulse_time + time_step
        
    closeTrace('Qudit Ramsey, 0 state')
    freq_string = str(round(set_freq[0],3)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_Dimension_{len(set_freq)+1}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{pulse_train}\n")
        file.write(f"{pi_time_pulse_train}\n")
        file.write(f"{phases}\n")
        file.write(f"{file_names_list}\n")

setEvaluation('Eval3')

pi_time = findPiTime_withfit_plotPD(stop_time,start_time, time_step, threshold, pulse_program, script_functions)
print(pi_time)
setEvaluation('Eval2')
#with open(output_file_pitimes,'a') as outfile:
#    outfile.write(f'{pi_time}\n')

eng.quit()