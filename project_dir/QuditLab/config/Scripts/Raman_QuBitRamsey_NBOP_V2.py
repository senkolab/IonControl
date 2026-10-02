#Raman_FrequencyScan_NBOP.py created 2026-07-31 11:36:52.300832

#RFSoC_FrequencyScansPiTimeCalibrations_NBOP.py created 2025-09-26 19:55:38.769639
'''

This script does frequency scans (and optionally pi-time calibrations) using RFSoC. 

'''
import time
import json
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
import shutil
import sys
import os
import datetime
import glob
import numpy as np
import random
    
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_Measurement import *
from Functions_RFSoC import upload_dac0
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

do_pi_time_calibration = True
get_calibration_values_only = True

line_trigger = True

pulse_program = "Raman_QuBitRamsey_NBOP"

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) #13.48#
pitime_n1 = float(getGlobal('pitime_n1'))
pitime_0 = float(getGlobal('pitime_0')) #23.734#
pitime_p1 = float(getGlobal('pitime_p1'))
pitime_p2 = float(getGlobal('pitime_p2'))
ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

threshold = 11
F1PumpTime = 1.5
F1PumpReps = 40
InitReps = 0
fs = 4e9

#target_freq = 8031.85285 + 0.085#in MHz [2,1,1,1] (11.707 MHz)

#target_freq = 8034.80359 #in MHz [2,1,1,0]
#target_freq = 8043.64346 #in MHz [2,-1,1,-1]
#target_freq = 8046.58987 #in MHz [2,-2,1,-1]
#target_freq = 8028.89995 #in MHz [2,2,1,1]
#target_freq = 8031.85285 #in MHz [2,1,1,1]
'''
target_freq = 8031.85285 + 0.085#in MHz [2,1,1,1] (11.707 MHz)
RamanPulseTime = 88 #in us
iden_string = '[S, 2, 1, S, 1, 1]'
shelving_transition  = [[1,4,1],[1,4,-1],[1,3,3]]
'''
rep_rate_enable = 1

target_freq = 8037.75032 #in MHz [2,0,1,0]
shelving_transition  = [[0,2,0],[0,4,-2],[0,3,2]]
RamanPulseTime = 65.4 #in us
iden_string = '[S, 2, 0, S, 1, 0]'

stop_time = 1802
start_time = 0.1
time_step = 200
init_state = shelving_transition[0][0]




def RepRateMode_CenterFreq(target_freq):
    rep_rate = 75.66255
    RepRateMode = int(target_freq/rep_rate)
    center_freq = target_freq - RepRateMode*rep_rate
    return RepRateMode, center_freq, rep_rate


rep_rate_stabilisation, centre_freq, rep_rate = RepRateMode_CenterFreq(target_freq)
set_freq = centre_freq
f_offset_index = [0,2,0]
f_upper_index = [0,4,-2]



pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]

init_n2_index = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]]
init_n1_index = [[-2,3,-1],[0,3,0],[1,4,2],[2,4,3]]
init_0_index = [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]]
init_p1_index = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]]
init_p2_index = [[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

init_freqs_n2 = list(Get_1762_EOM_Freqs_an1an2(init_n2_index,f_offset,f_upper))
init_freqs_n1 = list(Get_1762_EOM_Freqs_an1an2(init_n1_index,f_offset,f_upper))
init_freqs_0 = list(Get_1762_EOM_Freqs_an1an2(init_0_index,f_offset,f_upper))
init_freqs_p1 = list(Get_1762_EOM_Freqs_an1an2(init_p1_index,f_offset,f_upper))
init_freqs_p2 = list(Get_1762_EOM_Freqs_an1an2(init_p2_index,f_offset,f_upper))

init_times_n2 = list(Get_1762_PiTimes(init_n2_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_times_n1 = list(Get_1762_PiTimes(init_n1_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_times_0 = list(Get_1762_PiTimes(init_0_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_times_p1 = list(Get_1762_PiTimes(init_p1_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_times_p2 = list(Get_1762_PiTimes(init_p2_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

init_freqs_array = [init_freqs_n2,init_freqs_n1,init_freqs_0,init_freqs_p1,init_freqs_p2]
init_times_array = [init_times_n2,init_times_n1,init_times_0,init_times_p1,init_times_p2]

shelving_freq = list(Get_1762_EOM_Freqs_an1an2(shelving_transition,f_offset,f_upper))
ShelvingPulseTime = list(Get_1762_PiTimes(shelving_transition,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))



LT_dummy = getGlobal('LineTriggerBoolean')
if not "%s"%LT_dummy == int(line_trigger):
    setGlobal("LineTriggerBoolean", int(line_trigger), "")

F1_pumpTime = getGlobal('F1_PumpTime')
if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
if not "%s"%OptPumpTime == "%s us"% 0:
    setGlobal("OpticalPumpTimeGlobal", 0, "us") # type: ignore

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us") # type: ignore

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")





def phase_ramsey_scans(init_state, ShelvingPulseTime, RamanPulseTime, start_wait_time, stop_wait_time, wait_time_step, dt_string , threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    wait_time = start_wait_time



    dummy_counter = 0

    print(set_freq,ShelvingPulseTime)
    print(init_freqs_array[int(init_state+2)],init_times_array[int(init_state+2)])

    init_row1 = [1, init_freqs_array[int(init_state+2)], [0]*len(init_freqs_array[int(init_state+2)]), init_times_array[int(init_state+2)], [0]*len(init_times_array[int(init_state+2)]), 0]

    tot_init_time = np.sum(init_times_array[int(init_state+2)])
    InitShelvingTime = getGlobal("Init_Shelving_Pulse_Time")
    if not "%s"%InitShelvingTime == "%s us"%tot_init_time:
        setGlobal("Init_Shelving_Pulse_Time", tot_init_time, "us")

    PulseTime = getGlobal("Shelving_Pulse_Time")
    if not "%s"%PulseTime == "%s us"%sum(ShelvingPulseTime):
        setGlobal("Shelving_Pulse_Time", sum(ShelvingPulseTime), "us")

    dummy_row2 = [2, [800], [0], [0.01], [0], 0]
    probe_row3 = [3, shelving_freq, [0]*len(shelving_freq), ShelvingPulseTime, [0]*len(shelving_freq), 1]
    dummy_row4 = [4, [800], [0], [0.01], [0], 0]

    rows = [init_row1,
            dummy_row2,
            probe_row3,
            dummy_row4]
    resp = upload_rows(rows, time_unit="us")
    print(json.dumps(resp, indent=2))
    print(f'Setting freq to {set_freq} MHz with pi time {ShelvingPulseTime} us')

    while wait_time <= stop_wait_time:
        if scriptIsStopped():
            break
        file_names_list_all = []
        file_names_list = []
        flour_exp = []
        fluor_ave = []

        Total_ramsey_exp_time = RamanPulseTime/2 + wait_time + RamanPulseTime/2 + 1

        Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
        if not "%s"%Raman_Pulse_Time_dummy == "%s us"%Total_ramsey_exp_time:
            setGlobal("Raman_Pulse_Time", Total_ramsey_exp_time, "us")

        createTrace(f'Raman Ramsey {wait_time} [in units of pi]', 'Script Data', xLabel=f'X: phase in units of pi + wait time in us Y: PB')        
        phase_index_list = [0,1,2,3,4,5,6,7,8,9,10]
        for i in phase_index_list:
            if scriptIsStopped():
                break
            tone_1 = 150
            tone_2 = 150 + set_freq

            phase_value = 2*np.pi*i/10

            TABLE_DAC0 = [
                [0, False, [
                    [0, [
                        # f_MHz, phase_rad, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, phase_latency_cycles, label
                        [0.0, 0.0, 0.5, 5e6,
                        0, 0, False, 0, "DAC0 tone 0"],
                    ]],
                ]],

                [0, True, [
                    [0, [
                        # f_MHz, phase_rad, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, phase_latency_cycles, label
                        [tone_1, 0.0, 0.5, RamanPulseTime/2,
                        1, 0, True, 0, "T1U1"],
                        [tone_1, 0.0, 0.5, wait_time,
                        1, 0, False, 0, "Wait"],
                        [tone_1, 0.0, 0.5, RamanPulseTime/2,
                        1, 0, True, 0, "T1U2"],
                    ]],
                    [1, [
                        [tone_2, 0, 0.5, RamanPulseTime/2,
                        1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "T2U1"],
                        [tone_2, 0, 0.5, wait_time,
                        1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "Wait"],
                        [tone_2, phase_value, 0.5, RamanPulseTime/2,
                        1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "T2U2"],
                    ]],
                ]],

            ]
            '''
            TABLE_DAC0 = [

                [0, False, [
                    [0, [
                        # f_MHz, phase_rad, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, phase_latency_cycles, label
                        [0, 0.0, 0.5, 28,
                         0, 0, False, 0, "DAC0 tone 0"],
                    ]],
                    [1, [
                        [0, 0, 0.5, 28,
                         0, -1*rep_rate_enable*rep_rate_stabilisation, False, 0, "DAC0 tone 1, rep -1"],
                    ]],
                ]],

                [1, True, [
                    [0, [
                        # f_MHz, phase_rad, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, phase_latency_cycles, label
                        [tone_1, 0.0, 0.5, 28/2,
                         0, 0, True, 0, "DAC0 tone 0"],
                    ]],
                    [1, [
                        [tone_2, 0, 0.5, 28/2,
                         0, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "DAC0 tone 1, rep -1"],
                    ]],
                ]],
            ]
            '''
            response = upload_dac0(
                TABLE_DAC0,
                time_unit="us",
            )
            print("Uploaded Raman successfully.")

            setScan(pulse_program)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count']
            ydata = data[1]
            fluor_bool = np.array(ydata) < threshold
            
            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")

            file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            destination_today = f'Z:\\Lab Data\\Raman_Ramsey_raw_data\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Raman_QubitRamsey_NBOP_V2_*'
            soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Raman_QubitRamsey_NBOP_V2'

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


            PD = 1-np.mean(fluor_bool)
            flour_exp.append(ydata)

            fluor_ave.append(PD)
            plotPoint(wait_time + phase_value/np.pi, PD, f'Raman Ramsey {wait_time} [in units of pi]', plotStyle=2)


        closeTrace(f'Raman Ramsey {wait_time} [in units of pi]')
        
        if scriptIsStopped():
            break
        combined_data = zip(phase_index_list,fluor_ave)
        filename = f'Z:\\Lab Data\\Raman_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qubit_{iden_string}_WaitTime{wait_time}us_{dt_string}.txt'
        wait_time = wait_time + wait_time_step
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{file_names_list}\n")

setEvaluation('Eval3')

phase_ramsey_scans(init_state, ShelvingPulseTime, RamanPulseTime, start_time, stop_time, time_step, dt_string , threshold, pulse_program, script_functions)

setEvaluation('Eval2')