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
F1PumpReps = 40
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

MicrowavePulseTime = 72 #in us
pi_over_2_time = MicrowavePulseTime/2
shelving_transition  = [[0,2,0],[0,4,-2],[0,3,2]]

start_time = 0
stop_time = start_time + 2000
time_step = 100


init_state = shelving_transition[0][0]

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

        plotPoint(Wait_time, PD, '1762 nm pi-time scan', plotStyle=0)

        Wait_time = Wait_time + time_step
        
    closeTrace('1762 nm pi-time scan')

    def oscfunc(t, A, w, p, c, d):
        return A * np.cos(w * t + p) * np.exp(-t / d) + c

    def fit_oscillation(tt, yy):
        tt = np.array(tt)
        yy = np.array(yy)
        ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))
        Fyy = abs(np.fft.fft(yy))
        guess_freq = abs(ff[np.argmax(Fyy[1:])+1])
            
        guess_amp = np.max(yy)-np.mean(yy)
        guess_offset = np.mean(yy)

        guess = np.array([guess_amp, 2.*np.pi*guess_freq, np.pi, guess_offset, 1e4])
        popt, pcov = curve_fit(oscfunc, tt, yy, p0=guess, maxfev=10000)
        uncertainty = np.sqrt(pcov[1][1])
        A, omeg, p, c, d = popt
        f = omeg/(2.*np.pi)
        
        return omeg, uncertainty

    
    omega, uncertainty = fit_oscillation(Wait_time_list,fluor_ave)
    print("firstpass_omega is", omega)

    period = 2*np.pi/omega
    pulse_time_list = np.array(pulse_time_list)
    fluor_ave = np.array(fluor_ave)

    final_pi_time = np.pi/omega
    print("pi time is", final_pi_time)

    freq_string = str(round(freq_peak,4)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)

    with open(output_file_freqs,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")


    return final_pi_time

#set_DSI12000PRO(set_freq, -10, True)
print(set_freq)

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

print("Uploaded Microwave successfully.")

setEvaluation('Eval3')

MicrowavePulseTime = Detuned_Ramsey(start_time, stop_time, time_step, threshold, pulse_program, script_functions)

setEvaluation('Eval2')


