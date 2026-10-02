#RFSoC_QubitRamsey_Heralded.py created 2025-09-30 12:19:49.862301

#Qubit_Ramsey_Ket0_in_D52_FNCS.py created 2025-09-24 16:12:17.564757

#Two_Level_Ramsey_TimeStepped_PhaseScan.py created 2024-09-26 17:50:52.785851

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

#from Functions_RFSoC_RamseyCalibration import *
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
from Functions_RFSoC_FastBussed_calibration import *
from Functions_Measurement import *
from Functions_RFSoC import upload_dac0, upload_dac2
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qubit_ramsey_scan_*"

def RepRateMode_CenterFreq(target_freq):
    rep_rate = 75.66255
    RepRateMode = int(target_freq/rep_rate)
    center_freq = target_freq - RepRateMode*rep_rate
    return RepRateMode, center_freq, rep_rate

line_trigger_wait = 0
Side_band_cooling_reps = 0
Take_calibrations = False
rep_rate_enable = 1

target_freq = 8037.75032 #in MHz [2,0,1,0]
RamanPulseTime = 35 #in us

rep_rate_stabilisation, Raman_set_freq, rep_rate = RepRateMode_CenterFreq(target_freq)

probe_trans = [[0, 2, 0], [0, 2, 0]]

s12_level = probe_trans[0][0]

stop_time = 1700.1
start_time = 10.1
time_step = 200

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

setEvaluation('Eval3')

F1PumpTime = 0.5 #us
F1PumpReps = 30
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
init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
init_pulse_time = sum(init_times_array) 

set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))

print('set freq', set_freq)


pi_times= list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
pi_time_pulse_train = [pi_times[0],10000,pi_times[0]]
times = []
for i in range(len(pi_times)):
    times.append(2*pi_times[i]*np.arcsin(np.sqrt(1/(len(pi_times)+1-i)))/np.pi)


print(times)
#full_freqs = set_freq + [800] + list(np.flip(set_freq))
#print(full_freqs)

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

pulse_program = "Raman_QuBitRamsey_NBOP_heralded"

        
def findPiTime_withfit_plotPD(f_offset,f_upper,stop_time,start_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    #setEvaluation('Eval2')
    wait_time = start_time
    while np.round(wait_time) < stop_time:
        fluor_ave = []
        pulse_time_list = []
        file_names_list = []
        createTrace('Qudit Ramsey ket 0 population', 'Scan Data', xLabel=f'Pulse Time (us)')
        if scriptIsStopped():
            break

        # take calibrations every so often
        if Take_calibrations:
            real_wait_time = 200
            delta = 0
            if probe_trans[0] == [0, 2, 0]:
                freq_offset = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                freq_upper = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[0,4,-2],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
            else:
                freq_offset, freq_upper = Fast_Bussed_Calibration(script_functions)
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
        init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        init_pulse_time = sum(init_times_array) 

        set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        initial_state_frequency = set_freq
        print('set freq', set_freq)


        pi_times= list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        pi_time_initial_state = pi_times

        print(times)
        full_freqs = set_freq + [800] + list(np.flip(set_freq))
        print(full_freqs)


        print('1')

#Pulse Times ==============================================================

        RamanPulseTime

        full_times = list([RamanPulseTime/2]) + [wait_time] + list([RamanPulseTime/2])
        corrected_pulse_train_times = full_times
#==============================================================
        Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
        if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(full_times):
            setGlobal("Ramsey_Wait_Time", sum(full_times), "us")

        half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
        if not "%s"%half_pi_time_dummy == "%s us"%pi_time_initial_state[0]:
            setGlobal("Shelving_Pulse_Time", pi_time_initial_state[0], "us")

        herald_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%herald_time_dummy == "%s us"%pi_time_initial_state[0]:
            setGlobal("Hareld_pulse_time", pi_time_initial_state[0], "us")

        print('2')
        file_names_list_all = []

        fluor_ave = []
        pulse_time_list = []
        file_names_list = []
        fluor_ave_U1 = []
        pulse_time_list_U1 = []
        file_names_list_U1 = []
        init_row1 = [1, init_freqs_array, [0]*len(init_freqs_array),init_times_array, [0]*len(init_freqs_array), 0]
        dummy_row2 = [2, [800], [0], [0.1], [0], 0]
        herald_row3 = [3, [initial_state_frequency[0]], [0], [pi_time_initial_state[0]], [0], 1]
        dummy_row4 = [4, [800], [0], [0.1], [0], 0]
        herald_deshelve_row5 = [5, [initial_state_frequency[0]], [0], [pi_time_initial_state[0]], [0], 1]
        dummy_row6 = [6, [800], [0], [0.1], [0], 0]
        #ramsey_row5 = [5, full_freqs, full_phases, full_times, [1]*(len(full_phases)), 1]
        #dummy_row6 = [6, [800], [0], [0.1], [0], 0]

        rows = [init_row1, dummy_row2, herald_row3, dummy_row4, herald_deshelve_row5, dummy_row6]

        row_num = 6
        for idx, freq in enumerate(set_freq):
            row_num = row_num + 1
            readout_row = [row_num, [freq], [0], [pi_times[idx]], [0], 1]
            rows.append(readout_row)
            row_num = row_num + 1
            dummy_row = [row_num, [800], [0], [0.1], [0], 0]
            rows.append(dummy_row)
        print(rows)
        for phase_index in range(11):
    # Phase Calculations ===================================================================

            Raman_Ramsey_phase = (2 * phase_index  / 10)*np.pi# - (2*set_freq[0]*wait_time))

            print(Raman_Ramsey_phase)
    #=======================================================================================
    # AWG commands======================================================================================
            #full_phases = [0,0,1]


            tone_1 = 150
            tone_2 = 150 + Raman_set_freq

            TABLE_DAC0 = [
                # Row_num, Jump_Flag
                [0, False, [
                    [0, [
                        # f_MHz, phase_rad, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, phase_latency_cycles, label
                        [0, 0.0, 1.0, 5e6,
                            0, 0, False, 0, "Dummy Tone"],
                    ]],
                ]],
                [1, True, [
                    [0, [                    # Tone channel 0
                        # freq, phase, amp, duration_us, phase_mode,
                        # rep_rate_mode, enable, latency, label

                        [tone_1, 0.0, 0.5, RamanPulseTime/2,
                         1, 0, True, 0, "T1U1"],

                        [tone_1, 0.0, 0.00, wait_time,
                         1, 0, True, 0, "T1RF OFF"],

                        [tone_1, 0.0, 0.5, RamanPulseTime/2,
                         1, 0, True, 0, "T1U2"],
                    ]],
                    [1, [                    # Tone channel 1
                        # freq, phase, amp, duration_us, 
                        # phase_mode,,rep_rate_mode, enable, latency, label

                        [tone_2, 0.0, 0.5, RamanPulseTime/2,
                         1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "T2U1"],

                        [tone_2, 0.0, 0.00, wait_time,
                         1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "T2RF OFF"],

                        [tone_2, Raman_Ramsey_phase, 0.5, RamanPulseTime/2,
                         1, -1*rep_rate_enable*rep_rate_stabilisation, True, 0, "T2U2"],
                    ]],
                ]],
                
                ]

            response = upload_dac0(
                TABLE_DAC0,
                time_unit="us",
            )

            response = upload_dac2(
                TABLE_DAC0,
                time_unit="us",
            )

            if phase_index == 0:
                Table_length_dummy =  getGlobal('Table_length')
                if not "%s"%Table_length_dummy == row_num:
                    setGlobal("Table_length", row_num, "")

            resp = upload_rows(rows, time_unit="us")
            print(json.dumps(resp, indent=2))

    
    
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
                if herald_outcome < threshold:
                    arrays.append(ket1_data[idx])
            mean_value = np.mean(np.array(arrays)<threshold)
            print("=========================================")
#--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")

            file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            destination_today = f'Z:\\Lab Data\\Raman_Ramsey_raw_data\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
            pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Raman_qubit_ramsey_*'
            soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Raman_qubit_ramsey'

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
            '''
            matching_files = glob.glob(pattern)
            matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
            file_path = matching_files[-1]
            chunks = file_path.split('\\')
            #print(chunks[-1])        
            fname = chunks[-1]
            file_names_list.append(fname)
            '''
            print("=========================================")
    
    
            if np.isnan(mean_value):
                mean_value = 1
            PD = mean_value
            print("PD is", PD)
            fluor_ave.append(PD)
            pulse_time_list.append(int(10*phase_index))
    
            plotPoint(phase_index, PD,'Qudit Ramsey ket 0 population', plotStyle=2)
        
        closeTrace('Qudit Ramsey ket 0 population')
        freq_string = str(round(set_freq[0],3)).replace('.','p')
        combined_data = zip(pulse_time_list,fluor_ave)
        filename = f'Z:\\Lab Data\\Raman_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qubit_[{probe_trans[0][0]},{probe_trans[0][1]},{probe_trans[0][2]}]_WaitTime{wait_time}us_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{pulse_train}\n")
            file.write(f"{[f_offset,f_upper]}\n")
            file.write(f"{pi_time_pulse_train}\n")
            file.write(f"{corrected_pulse_train_times}\n")
            file.write(f"{fractions_U1}\n")
            file.write(f"{fractions_U2}\n")            
            file.write(f"{probe_trans}\n")
            file.write(f"{phases}\n")
            file.write(f"{file_names_list}\n")

        wait_time = wait_time + time_step

#setEvaluation('Eval3')

pi_time = findPiTime_withfit_plotPD(f_offset,f_upper,stop_time,start_time, time_step, threshold, pulse_program, script_functions)
print(pi_time)
#setEvaluation('Eval2')
#with open(output_file_pitimes,'a') as outfile:
#    outfile.write(f'{pi_time}\n')

