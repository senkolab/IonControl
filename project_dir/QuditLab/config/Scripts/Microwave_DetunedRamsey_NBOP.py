#Microwave_FrequencyScans_NBOP.py created 2026-08-13 11:08:33.276135

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
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from DSI_12000PRO_connet import set_DSI12000PRO

script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

line_trigger = True

#pulse_program = "Microwave_Calibration_NBOP_Ba137"
pulse_program = "Microwave_DetunedRamsey_NBOP_Ba137"
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
F1PumpReps = 60
InitReps = 0
fs = 4e9

#target_freq = 2.95073618 #in MHz [2,0,2.1]
#target_freq = 8034.80359 #in MHz [2,1,1,0]
#target_freq = 8043.64346 #in MHz [2,-1,1,-1]
#target_freq = 8046.58987 #in MHz [2,-2,1,-1]
#target_freq = 8028.89995 #in MHz [2,2,1,1]

centre_freq = 8037.750224 #in MHz [2,0,1,0]
detuning = 0.0005

set_freq = centre_freq - detuning

MicrowavePulseTime = 97 #in us
pi_over_2_time = MicrowavePulseTime/2
shelving_transition  = [[0,2,0],[0,4,-2],[0,3,2]]

start_time = 0
stop_time = start_time + 10000
time_step = 100


init_state = shelving_transition[0][0]

f_offset_index = [0,2,0]
f_upper_index = [0,4,-2]

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

init_trans = list_of_inits[init_state+2]

init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
init_pulse_time = sum(init_times_array)

shelving_freq = list(Get_1762_EOM_Freqs_an1an2(shelving_transition,f_offset,f_upper))
ShelvingPulseTime = list(get_pi_times(shelving_transition,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

output_file_freqs = fr'Z:\Lab Data\Microwave_Ramsey_Raw_data\MW_detuned_ramsey_[S, 2, 0, S, 1, 0]_{dt_string}.txt'

Microwave_Freq = getGlobal("Microwave_Frequency")
if not "%s"%Microwave_Freq == "%s MHz"%set_freq:
    setGlobal("Microwave_Frequency", np.round(set_freq, 6), "MHz")

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

Microwave_Pulse_Time_dummy = getGlobal("Microwave_Pulse_Time")
if not "%s"%Microwave_Pulse_Time_dummy == "%s us"%pi_over_2_time:
    setGlobal("Microwave_Pulse_Time", pi_over_2_time, "us")


def Detuned_Ramsey(start_time, stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    Wait_time = start_time
    fluor_ave = []
    Wait_time_list = []
    flour_exp = []
    while Wait_time <= stop_time:
        if scriptIsStopped():
            break
        Microwave_Wait_time_dummy = getGlobal("Microwave_Wait_Time")
        if not "%s"%Microwave_Wait_time_dummy == "%s us"%Wait_time:
            setGlobal("Microwave_Wait_Time", Wait_time, "us")
        time.sleep(1)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold
        PD = 1-np.mean(fluor_bool)
        flour_exp.append(fluor_bool)

        fluor_ave.append(PD)
        Wait_time_list.append(Wait_time)
        x = Wait_time
        y = PD
        plotPoint(Wait_time, PD, '1762 nm pi-time scan', plotStyle=0)

        Wait_time = Wait_time + time_step
 
        with open(output_file_freqs,'a') as file:
            file.write(f"{x},{y}\n")
        
    closeTrace('1762 nm pi-time scan')
    return Wait_time_list, fluor_ave

#set_DSI12000PRO(set_freq, -10, True)
print(set_freq)

init_row1 = [1, init_freqs_array, [0]*len(init_freqs_array), init_times_array, [0]*len(init_times_array), 0]

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

print("Uploaded Microwave successfully.")

setEvaluation('Eval3')

start_time_list = np.linspace(0, 100e3, 11)
stop_time_list = np.linspace(0, 100e3, 11) + 4000
for start_time, stop_time in zip(start_time_list, stop_time_list):
    output_file_freqs = fr'Z:\Lab Data\Microwave_Ramsey_Raw_data\MW_detuned_ramsey_[S, 2, 0, S, 1, 0]_{np.round(start_time)}-{np.round(stop_time)}_{dt_string}.txt'
    Wait_time_list, fluor_ave = Detuned_Ramsey(start_time, stop_time, time_step, threshold, pulse_program, script_functions)
    print(Wait_time_list, fluor_ave)
setEvaluation('Eval2')


