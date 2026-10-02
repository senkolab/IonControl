#Herald_pulse_time_scan.py created 2024-06-06 13:40:14.757393

#Initialized_pulsetime_Scan.py created 2024-02-08 11:29:39.976108

#Shelving_Find_Target_Resonance_Freq_PlotPD_Initialised.py created 2024-02-02 11:22:42.353979
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
print('success')

import shutil
import time
import random
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

scan_indices = [[2,4,4]]
SaveString = 'No_EOM_40uW' #for example

for scan_index in scan_indices:

    probe_trans = [scan_index]

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

    init_trans = list_of_inits[probe_trans[0][0]+2]
    init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
    init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_pulse_time = sum(init_times_array) 

    set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    #set_freq = [482.5060]
    pi_time = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))[0]
    #Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

    stop_time = 1000
    start_time = 0
    time_step = 100

    F1PumpTime = 0.5 #us
    F1PumpReps = 50
    InitReps = 0
    fs = 4e9
    threshold = 8

    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")
        
    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"%0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us")

    Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
    if not "%s"%Init_PulseTime == init_pulse_time:
        setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

    Hareld_pulse_time_dummy = getGlobal('Hareld_pulse_time')
    if not "%s"%Hareld_pulse_time_dummy == pi_time:
        setGlobal("Hareld_pulse_time", pi_time, "us")

    pulse_program = "Repump_time_scan_614EOM"

    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(2)
    eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
    eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
    eng.SendAWGCommand("INIT:CONT 1", nargout=0) #0 sets AWG to externally triggered mode
    eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
    eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

    eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
    time.sleep(0.1)
    eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

    eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
    eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)


    power_factor = matlab.double([1])
    power_factor_dbm = matlab.double([1])
    #==========================================================
    matlab_init_freqs = matlab.double(init_freqs_array)
    matlab_init_times = matlab.double(init_times_array)
    #==========================================================
    hareld_pulse_freq = matlab.double(set_freq)
    hareld_pulse_time = matlab.double([pi_time+100])
    #==========================================================
    matlab_set_freq = matlab.double(set_freq)
    matlab_probe_pulse_time = matlab.double([stop_time+500])
    #==========================================================
    eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
    #==========================================================
    eng.Pulse_upload(hareld_pulse_freq,hareld_pulse_time,fs,2,power_factor_dbm,nargout = 0) 
    #==========================================================
    eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)
    #eng.Pulse_upload_dummy(fs,3,nargout = 0) 
    #==========================================================
    eng.Pulse_upload_dummy(fs,4,nargout = 0) 
    #==========================================================
    eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 2,4,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 5,3,1,0", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 5,4,1,0", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 6,4,1,1", nargout=0)
    #==========================================================
    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

            
    def findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
        repump_time = start_time
        fluor_ave = []
        repump_time_list = []
        file_names_list = []
        file_names_list_all = []

        while repump_time <= stop_time:
            if scriptIsStopped():
                eng.quit()
                break

            RepumpTime_Dummy = getGlobal('Shelve_Repump_Time').magnitude
            if not "%s"%RepumpTime_Dummy == "%s us"%np.round(repump_time,3):
                setGlobal("Shelving_Pulse_Time", np.round(repump_time,3), "us")
            time.sleep(0.2)

            if scriptIsStopped():
                eng.quit()
                break

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

#--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")

            file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            destination_today = f'Z:\\Lab Data\\EOM_repump_time_scans\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\EOM_repump_time_*'

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

            print("=========================================")

            PD = mean_value

            fluor_ave.append(PD)
            repump_time_list.append(repump_time)
            print("PD is", PD)
            fluor_ave.append(PD)
            repump_time_list.append(repump_time)

            plotPoint(repump_time, PD, '1762 nm pi-time scan', plotStyle=2)

            repump_time = repump_time + time_step
            
        closeTrace('1762 nm pi-time scan')
        freq_string = str(round(set_freq[0],3)).replace('.','p')
        combined_data = zip(repump_time_list,fluor_ave)
        filename = f'Z:\Lab Data\614nm_EOM_repump_time_scans\RepumpTime_Scan_{SaveString}_{freq_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{file_names_list}\n")
    setEvaluation('Eval3')

    pi_time = findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions)

    setEvaluation('Eval2')

eng.quit()