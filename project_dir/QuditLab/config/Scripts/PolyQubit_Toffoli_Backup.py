#PolyQubit_BVA.py created 2025-03-24 17:41:40.347163

#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

import matlab.engine

import sys
import os
import datetime
import glob
import json
import numpy as np
import shutil
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
from Functions_Gates import *
from Functions_phase_correction import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

kets_to_measure = np.arange(10,16)
kets_to_measure = [12,14]

do_calibrations = True
repeat_experiments = 1
dim = 16
sub_dim = 16

mappings = {
    0: '0', 1: '[2, 0]', 2: '[4, -2]', 3: '[3, 1]', 
    4: '[4, -1]', 5: '[3, 0]', 6: '[3, 2]', 7: '[4, 0]', 
    8: '[2, -2]', 9: '[2, 2]', 10: '[4, 1]', 11: '[3, -1]', 
    12: '[1, 1]', 13: '[2, -1]', 14: '[1, -1]', 15: '[2, 1]'}

init_states = [
    [0, 2, 0], [0, 2, 0], [0, 4, -2], [0, 3, 1], 
    [0, 4, -1], [-1, 3, 0], [0, 3, 2], [0, 4, 0], 
    [-2, 2, -2], [0, 2, 2], [0, 4, 1], [-2, 3, -1], 
    [1, 1, 1], [-2, 2, -1], [-1, 1, -1], [2, 2, 1]]

for ket_idx in kets_to_measure:

    init_state = init_states[ket_idx]

    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(1)

    f_offset = float(getGlobal('f_offset'))
    f_upper = float(getGlobal('f_upper'))

    pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
    pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
    pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
    pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
    pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    pulse_train, _, phase_shifts, angles, probe_trans = PolyQubit_Toffoli(int(np.log2(sub_dim)), mappings,pi_t = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2])
    print('running init state:', init_state)
    print('Toffoli pulse, phase, and angle (1 single pulse!)', pulse_train, phase_shifts, angles)
    probe_trans = [[2, 2, 0], [0, 4, -2], [0, 3, 1], [1, 4, -1], [-1, 3, 0], [1, 3, 2], [1, 4, 0], [0, 2, -2], [1, 2, 2], [1, 4, 1], [-1, 3, -1], [1, 1, 1], [1, 2, -1], [-1, 1, -1], [2, 2, 1]]
    print('probe trans are', probe_trans)

    #print(script_stopper)

    s12_level = init_state[0]

    F1PumpTime = 1.5 #us
    F1PumpReps = 80
    InitReps = 0
    fs = 4e9
    threshold = 9

    pulse_program = "PolyQubit_Toffoli_pulse_program"
            
    def findPiTime_withfit_plotPD(threshold ,pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

        script_stop_dummy = 0
        file_names_list_all = []
        file_names_list = []
        
        while script_stop_dummy<1:
            script_stop_dummy += 2

            if scriptIsStopped():
                eng.quit()
                break
    
            print('1')
            setEvaluation('Eval2')

            if do_calibrations:
                print('Running calibrations..')
                delta = 0
                ramsey_real_wait_time = 150
                freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
            setEvaluation('Eval3')
    
            f_offset = float(getGlobal('f_offset'))
            f_upper = float(getGlobal('f_upper'))
    
            pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
            pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
            pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
            pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
            pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]
    
    
            init_trans = list_of_inits[s12_level+2]
            init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
            init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
            init_pulse_time = sum(init_times_array) 
    
            probe_freq_list = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    
            initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2([init_state],f_offset,f_upper))
    
            pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))
    
            pi_time_initial_state = list(Get_1762_PiTimes([init_state],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
            
            print('---------------------------------------')
            print(pi_time_initial_state)
            pi_time_pulse_train = list(Get_1762_PiTimes(pulse_train,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    
            pi_times_probe_trans = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    
            print(pulse_train)
    
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
            if not "%s"%SB_cooling_reps == 0:
                setGlobal("Sideband_Cooling_Reps", 0, "")

            if ket_idx==0 and init_state[0]==0 and init_state[1]==2 and init_state[2]==0:
                print('Herald pulse time is non-zero here.')
                Heralding_pulse_time_dummy = getGlobal('Hareld_pulse_time')
                if not "%s"%Heralding_pulse_time_dummy == "%s us"%pi_time_initial_state[0]:
                    setGlobal("Hareld_pulse_time", pi_time_initial_state[0], "us")
            else:
                print("Post-Herald pulse time is 0")
                Heralding_pulse_time_dummy = getGlobal('Hareld_pulse_time')
                if not "%s"%Heralding_pulse_time_dummy == "%s us"%0:
                    setGlobal("Hareld_pulse_time", 0, "us")

            corrected_pulse_train_times = []

            for i,angle in enumerate(angles):
                corrected_pulse_time = pi_time_pulse_train[i]*angle
                corrected_pulse_train_times.append(corrected_pulse_time)
            print(corrected_pulse_train_times)

            AOM_ON_time = getGlobal('Shelving_Pulse_Time')
            if not "%s"%AOM_ON_time == "%s us"%sum(corrected_pulse_train_times):
                setGlobal("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us")
            print('2')  
    
            # Phase Calculations ===================================================================

            full_phases = list(np.pi*np.array(phase_shifts)) #------------------------------------------------------------
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

            consolePrint(str(initial_state_frequency))
            consolePrint(str(pi_time_initial_state))
            
            matlab_initial_state_freq = matlab.double(initial_state_frequency)
            matlab_initial_state_pulse_time = matlab.double(pi_time_initial_state)
            matlab_initial_state_phases = matlab.double([0])
            #---------------------------------------------------------------------------------------------------------- pulse_train
            print(pulse_train_frequencies)
            print(corrected_pulse_train_times)
            matlab_pulse_train_freqs = matlab.double(pulse_train_frequencies)
            matlab_pulse_train_times = matlab.double(corrected_pulse_train_times)
            matlab_pulse_train_phases = matlab.double(full_phases)
    
            print(len(pulse_train_frequencies),len(corrected_pulse_train_times),len(full_phases))

    
            #for i in range(15):
            #    print(pulse_train_frequencies[i],corrected_pulse_train_times[i])
    
            #---------------------------------------------------------------------------- Uploading
            power_factor = matlab.double([1])
            power_factor_dbm = matlab.double([1])
            print('4.5')
            seg_num = 1
            eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
            if scriptIsStopped():
                eng.quit()
                break
            
            seg_num = seg_num + 1 
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
            print('5')
            seg_num = seg_num + 1
            eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)
            
            seg_num = seg_num + 1 
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
            #++++++++++++++++++++++++++Herald will be here++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            seg_num = seg_num + 1
            eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)

            seg_num = seg_num + 1 
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
            
            # Deshelving after herald. 
            seg_num = seg_num + 1
            eng.Pulse_upload_with_phases(matlab_pulse_train_freqs,matlab_pulse_train_times,matlab_pulse_train_phases,fs,seg_num,nargout = 0)
            if scriptIsStopped():
                eng.quit()
                break
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
            print('6')
            # Readout pulses
            for idx, freq in enumerate(probe_freq_list):
                matlab_ro_freq = matlab.double([freq])
                matlab_ro_time = matlab.double([pi_times_probe_trans[idx]])
                seg_num = seg_num + 1
                print(seg_num,[freq],[pi_times_probe_trans[idx]])
                eng.Pulse_upload(matlab_ro_freq,matlab_ro_time,fs,seg_num,power_factor,nargout = 0)
                if scriptIsStopped():
                    eng.quit()
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
            eng.SendAWGCommand("SOUR:SEQ:DEF 7,7,1,0", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 8,8,1,1", nargout=0)
            seq_num = 8
    
            for idx, freq in enumerate(probe_freq_list):
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
            ket3_data = data['PMT Index 3'][1]
            print(ket3_data)
            ket4_data = data['PMT Index 4'][1]
            print(ket4_data)
            ket5_data = data['PMT Index 5'][1]
            print(ket5_data)
            arrays = []
            for idx,herald_outcome in enumerate(herald_data):
                if herald_outcome < threshold:# and ket1_data[idx] < threshold:
                    if ket1_data[idx] > threshold or ket2_data[idx] > threshold or ket3_data[idx] > threshold or ket4_data[idx] > threshold or ket5_data[idx] > threshold: 
                        arrays.append([ket1_data[idx],ket2_data[idx],ket3_data[idx],ket4_data[idx],ket5_data[idx]])
            mean_value = np.mean(np.array(arrays)>threshold , axis = 0)
    
            #--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")

            file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            destination_today = f'Z:\\Lab Data\\Algorithms\\Polyqubit_Toffoli\\IonControl_raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Toffoli_4_polyqubit_*'
            soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Toffoli_4_polyqubit'

            def copy_file(src_file, dest_path):
             
                if not os.path.isfile(src_file):
                    print(f"Source file does not exist: {src_file}")
                    return
             
                dest_folder = os.path.dirname(dest_path)
             
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                    print(f"Created destination folder: {dest_folder}")
             
                shutil.copy2(src_file, dest_path)
                print(f"File copied from {src_file} to {dest_path}")

            #if not file_names_list_all:
            matching_files = glob.glob(pattern)
            matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
            file_path = matching_files[-1]
            chunks = file_path.split('\\')
            print(chunks[:-1])        
            fname = chunks[-1]
            file_names_list_all.append(destination_today+fname)
            file_names_list.append(destination_today+fname)
            source_file = file_path_today + fname
            copied_file = destination_today + fname
            copy_file(source_file,copied_file)
            
            
            PD = mean_value
            print("PD is", PD)

            filename = f'Z:\\Lab Data\\Algorithms\\Polyqubit_Toffoli\\Toffoli_logs\\Toffoli_D{int(np.log2(sub_dim))}_polyqubit_Ket_{ket_idx}_{dt_string}.txt'
            with open(filename,'w') as file:

                file.write(f"{PD}\n")
                file.write(f"{pulse_train}\n")
                file.write(f"{[f_offset,f_upper]}\n")
                file.write(f"{pi_time_pulse_train}\n")
                file.write(f"{corrected_pulse_train_times}\n")
                file.write(f"{probe_trans}\n")
                file.write(f"{phase_shifts}\n")
                file.write(f"{copied_file}")



    print('Starting function calls.')
    setEvaluation('Eval3')
    pi_time = findPiTime_withfit_plotPD(threshold, pulse_program, script_functions)
    print(pi_time)
    setEvaluation('Eval2')

    eng.quit()
    time.sleep(1)
