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
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data_FUA\qudit_ramsey_scan_*"
def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
Side_band_cooling_reps = 0



ramsey_wait_times = np.arange(0,1500,100)

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

state = [0,4,0]

initial_state = [state]

pulse_train_U1 = [state]
pulse_train_U2 = [state]

probe_trans = [state]

fractions_U1 = [1/2]
fractions_U2 = [1/2]

simulated_phase_mask_U1=  [0]  
simulated_phase_mask_U2 = [1]

fixed_phase_mask_U1 =     [0] 
fixed_phase_mask_U2 =     [1]

initial_state = [[0,2,0]]

pulse_train_U1 = [[0,2,0],[0,3,2]]
pulse_train_U2 = [[0,3,2],[0,2,0]]

probe_trans = [[0,2,0],[0,3,2]]

fractions_U1 = [1/2,1]
fractions_U2 = [1,1/2]

simulated_phase_mask_U1=  [0,0]  
simulated_phase_mask_U2 = [0,1]

fixed_phase_mask_U1 =     [1,0] 
fixed_phase_mask_U2 =     [1,0]

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

def AWG_Ramsey_uploads(initial_state,pulse_train_U1,ramsey_wait,pulse_train_U2,probe_trans,fractions_U1,fractions_U2,simulated_phase_mask_U1,simulated_phase_mask_U2,fixed_phase_mask_U1,fixed_phase_mask_U2,script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

#==================================do frequency calibration====================================================================================
    #if ramsey_wait%7 ==0:
    delta = 0
    ramsey_real_wait_time = 0
        #eng.SendAWGCommand("RES", nargout=0)
        #time.sleep(5)
        #eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
     #   freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
     #   freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)

    f_offset = float(getGlobal('f_offset'))
    f_upper = float(getGlobal('f_upper'))

    pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
    pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
    pitime_0 = float(getGlobal('pitime_0'))   # [2, 4, 2]
    pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
    pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]
#=================================================================================================================================================
#
#===============================get new frequencies and pulse times===============================================================================
    init_trans = list_of_inits[s12_level+2]
    init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
    init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_pulse_time = sum(init_times_array) 
    Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
    if not "%s"%Init_PulseTime == init_pulse_time:
        setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")
    matlab_init_freqs = matlab.double(init_freqs_array)
    matlab_init_times = matlab.double(init_times_array)
    
    set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    pi_times_probe_trans = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

    
    initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))
    pi_time_initial_state = list(Get_1762_PiTimes(initial_state,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    matlab_initial_state_freq = matlab.double(initial_state_frequency)
    matlab_initial_state_pulse_time = matlab.double(pi_time_initial_state)
    matlab_initial_state_phases = matlab.double([0])
    initial_state_piTime = getGlobal('Shelving_Pulse_Time')
    if not "%s"%initial_state_piTime == pi_time_initial_state[0]:
        setGlobal("Shelving_Pulse_Time", pi_time_initial_state[0], "us")
    
    pulse_train_frequencies_U1 = list(Get_1762_EOM_Freqs_an1an2(pulse_train_U1,f_offset,f_upper))
    pi_time_pulse_train_U1 = list(Get_1762_PiTimes(pulse_train_U1,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    matlab_pulse_train_frequencies_U1 = matlab.double(pulse_train_frequencies_U1)



    pulse_train_frequencies_U2 = list(Get_1762_EOM_Freqs_an1an2(pulse_train_U2,f_offset,f_upper))
    pi_time_pulse_train_U2 = list(Get_1762_PiTimes(pulse_train_U2,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    matlab_pulse_train_frequencies_U2 = matlab.double(pulse_train_frequencies_U2)


    
    
    print(pulse_train_U1, pulse_train_U2)
#=================================================================================================================================================
#
#==========================Correct the pulse times as requeired in U1 and U2 from fractions given=================================================
    corrected_pulse_train_times_U1 = list(2*np.array(pi_time_pulse_train_U1)*np.arcsin(np.sqrt(fractions_U1))/np.pi)
    matlab_pi_time_pulse_train_U1 = matlab.double(corrected_pulse_train_times_U1)
    Ramsey_pulse_time = getGlobal('Ramsey_Pulse_Time_U1U2')
    if not "%s"%Ramsey_pulse_time == sum(corrected_pulse_train_times_U1):
        setGlobal("Ramsey_Pulse_Time_U1U2", sum(corrected_pulse_train_times_U1), "us")
    
    corrected_pulse_train_times_U2 = list(2*np.array(pi_time_pulse_train_U2)*np.arcsin(np.sqrt(fractions_U2))/np.pi)
    matlab_pi_time_pulse_train_U2 = matlab.double(corrected_pulse_train_times_U2)
#=================================================================================================================================================
#
#==========================Phases for U1 and U2 as given in fixed and simulated phase masks=======================================================
    phases_U1 = list((2 * np.pi * 0 * np.array(simulated_phase_mask_U1)) + np.array(fixed_phase_mask_U1)*np.pi)
    matlab_phases_U1 = matlab.double(phases_U1)
    phase_matrix_U2 = []
    for phase_frac in np.linspace(0,1,11):
        phases_U2 = list((2 * np.pi * phase_frac * np.array(simulated_phase_mask_U2)) + np.array(fixed_phase_mask_U2)*np.pi)
        phase_matrix_U2.append([phases_U2])
#=================================================================================================================================================
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++UPLOADING+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if ramsey_wait%3 ==0:
        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(5)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 0", nargout=0) 
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        
        power_factor = matlab.double([1])
        
    #Initialization 
        seg_num = 1
        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
        print(f"Uploaded {seg_num}- Initialization", init_freqs_array, init_times_array)

    #Dummy    
        seg_num = seg_num + 1 
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
        print(f"Uploaded {seg_num}- dummy")

    #Herald shelving       
        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)
        print(f"Uploaded {seg_num}- Herald shelving", initial_state_frequency, pi_time_initial_state)

    #U1
        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_pulse_train_frequencies_U1,matlab_pi_time_pulse_train_U1,matlab_phases_U1,fs,seg_num,nargout = 0)
        print(f"Uploaded {seg_num}- Ramsey U1", pulse_train_frequencies_U1, corrected_pulse_train_times_U1)
        
    #U2
        print("Uploading Ramsey U2", pulse_train_frequencies_U2, corrected_pulse_train_times_U2)
        for phase_U2 in phase_matrix_U2:

            matlab_phase_U2 = matlab.double(phase_U2)
            seg_num = seg_num + 1
            eng.Pulse_upload_with_phases(matlab_pulse_train_frequencies_U2,matlab_pi_time_pulse_train_U2,matlab_phase_U2,fs,seg_num,nargout = 0)
            print(f"Uploaded {seg_num}- U2 Phase -", phase_U2)
    #Probes
        for i,trans in enumerate(probe_trans):
            matlab_set_freq_dummy = matlab.double([set_freq[i]])
            matlab_pi_times_dummy = matlab.double([pi_times_probe_trans[i]])
            seg_num = seg_num + 1
            print(f'uploading - {seg_num}',trans, set_freq[i], pi_times_probe_trans[i])
            eng.Pulse_upload(matlab_set_freq_dummy,matlab_pi_times_dummy,fs,seg_num,power_factor,nargout = 0)
    return pulse_train_frequencies_U1,pulse_train_frequencies_U2, corrected_pulse_train_times_U1,corrected_pulse_train_times_U2,f_offset,f_upper

def AWG_set_Table(Phase_num,probe_trans,script_functions): 
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

    eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 4,2,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 5,4,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 6,2,1,1", nargout=0)
    seq_num = 6
    
    U2_command = f"SOUR:SEQ:DEF 7,{Phase_num+5},1,0"
    eng.SendAWGCommand(U2_command, nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 8,2,1,1", nargout=0)
    seq_num = 8
    for idx, freq in enumerate(probe_trans):
        seq_num = seq_num + 1
        string = f"SOUR:SEQ:DEF {seq_num}, {16+idx},1,0"
        eng.SendAWGCommand(string, nargout=0)
        seq_num = seq_num + 1
        string = f"SOUR:SEQ:DEF {seq_num}, 2,1,1"
        eng.SendAWGCommand(string, nargout=0)
    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
    return  seq_num

s12_level = initial_state[0][0]

periodicity = 100 #us
stop_time = 110
start_time = 0
time_step = 10


F1PumpTime = 2 #us
F1PumpReps = 50
InitReps = 0
fs = 4e9
threshold = 10



pulse_program = "Qudit_ramsey_experiment_bused_fast_upload_AWG"

def Fast_upload_Ramsey_phase_scan(ramsey_wait,pulse_train_U1, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')

    fluor_ave = []
    pulse_time_list = []
    file_names_list = []
    Phase_num = 0

    pulse_train_frequencies_U1,pulse_train_frequencies_U2, corrected_pulse_train_times_U1,corrected_pulse_train_times_U2,f_offset,f_upper = AWG_Ramsey_uploads(initial_state,pulse_train_U1,ramsey_wait,pulse_train_U2,probe_trans,fractions_U1,fractions_U2,simulated_phase_mask_U1,simulated_phase_mask_U2,fixed_phase_mask_U1,fixed_phase_mask_U2,script_functions)  
    while Phase_num <= 10:
        if scriptIsStopped():
            break

        Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
        if not "%s"%Ramsey_wait_time_dummy == "%s us"%ramsey_wait:
            setGlobal("Ramsey_Wait_Time", ramsey_wait, "us")

        print('updating the table')

        Table_length_AWG = AWG_set_Table(Phase_num,probe_trans,script_functions)
        
        Table_length_dummy =  getGlobal('Table_length')
        if not "%s"%Table_length_dummy == Table_length_AWG:
            setGlobal("Table_length", Table_length_AWG, "")

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

        data = getAllData()
        herald_data = data['PMT Index 0'][1]
        print(herald_data)
        ket1_data = data['PMT Index 1'][1]
        print(ket1_data)

        arrays = []
        for idx,herald_outcome in enumerate(herald_data):
            if herald_outcome < threshold:
                arrays.append(ket1_data[idx])
        mean_value = np.mean(np.array(arrays)<threshold)

        matching_files = glob.glob(pattern)
        matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
        file_path = matching_files[-1]
        chunks = file_path.split('\\')
        #print(chunks[-1])
        fname = chunks[-1]
        file_names_list.append(fname)
        #print("=========================================")

        #arrays = []
        #with open(file_path, 'r') as file:
        #    print(file_path)
        #    for line in file:
        #        data = json.loads(line)
        #       if data[0]["0"][0]<threshold:
        #            arrays.append(data[0]["0"][1])
        #mean_value = np.mean(np.array(arrays)<threshold)
        #print("=========================================")

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)
        fluor_ave.append(PD)
        pulse_time_list.append(10*Phase_num)

        plotPoint(10*Phase_num, PD,'Qudit Ramsey, 0 state', plotStyle=2)

        Phase_num = Phase_num + 1

    closeTrace('Qudit Ramsey, 0 state')
    combined_data = zip(pulse_time_list,fluor_ave)
    pulse_train_U1_string = str(pulse_train_U1)
    if len(pulse_train_U1) == 1:
        filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_{pulse_train_U1[0][0]}_{pulse_train_U1[0][1]}_{pulse_train_U1[0][2]}_{wait_time}_us_{dt_string}.txt'
    else:
        filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_{pulse_train_U1_string}_{wait_time}_us_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{pulse_train_U1}\n")
        file.write(f"{pulse_train_frequencies_U1,pulse_train_frequencies_U2}\n")
        file.write(f"{[f_offset,f_upper]}\n")
        file.write(f"{corrected_pulse_train_times_U1,corrected_pulse_train_times_U2}\n")
        file.write(f"{file_names_list}\n")


# looping over different wait times
for wait_time in ramsey_wait_times:

    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

    SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
    if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
        setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

    setEvaluation('Eval3')
    pi_time = Fast_upload_Ramsey_phase_scan(wait_time,pulse_train_U1, threshold, pulse_program, script_functions)
    print(pi_time)
    setEvaluation('Eval2')
    #with open(output_file_pitimes,'a') as outfile:
    #    outfile.write(f'{pi_time}\n')

eng.quit()