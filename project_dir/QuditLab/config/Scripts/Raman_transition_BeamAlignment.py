#Raman_transition_BeamAlignment.py created 2026-08-04 14:20:11.526527

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
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

do_pi_time_calibration = True
get_calibration_values_only = True

line_trigger = True



pulse_program = "Raman_Calibration_NBOP_2RFSoCs_Ba137"

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) #13.48#
pitime_n1 = float(getGlobal('pitime_n1'))
pitime_0 = float(getGlobal('pitime_0')) #23.734#
pitime_p1 = float(getGlobal('pitime_p1'))
pitime_p2 = float(getGlobal('pitime_p2'))
ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

threshold = 11
F1PumpTime = 0.5
F1PumpReps = 30
InitReps = 0
fs = 4e9

freq_peak  = 17.5207
target_freq = 8037.75032 #in MHz

dummy_pulse_time = 35


stop_time = 3000
start_time = 0
time_step = 10

shelving_transition  = [[0,2,0]]
init_state = shelving_transition[0][0]


def RepRateMode_CenterFreq(target_freq):
    rep_rate = 75.66255
    RepRateMode = int(target_freq/rep_rate)
    center_freq = target_freq - RepRateMode*rep_rate
    return RepRateMode, center_freq, rep_rate


rep_rate_stabilisation, centre_freq, rep_rate = RepRateMode_CenterFreq(target_freq)

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

shelving_freq = list(Get_1762_EOM_Freqs_an1an2(shelving_transition,f_offset,f_upper))[0]
ShelvingPulseTime = list(Get_1762_PiTimes(shelving_transition,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))[0]

output_file_freqs = fr'Z:\Lab Data\D52_Calibration_Ba137\New_initialized_calibration_freq_files\New_initialized_calibration_freq_files_{dt_string}.txt'


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


freq_list_fitted = []


def findPiTime_withfit_plotPD(do_pi_time_calibration, dummy_pulse_time, freq_peak, start_time, stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
    fluor_ave = []
    pulse_time_list = []
    flour_exp = []
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break
        if do_pi_time_calibration:

            Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
            if not "%s"%Raman_Pulse_Time_dummy == "%s us"%pulse_time:
                setGlobal("Raman_Pulse_Time", pulse_time, "us")
            #time.sleep(1)
        else:
            Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
            if not "%s"%Raman_Pulse_Time_dummy == "%s us"%dummy_pulse_time:
                setGlobal("Raman_Pulse_Time", dummy_pulse_time, "us")

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold
        PD = 1-np.mean(fluor_bool)
        flour_exp.append(fluor_bool)

        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)

        pulse_time = pulse_time + time_step
        
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

    
    omega, uncertainty = fit_oscillation(pulse_time_list,fluor_ave)
    print("firstpass_omega is", omega)

    period = 2*np.pi/omega
    pulse_time_list = np.array(pulse_time_list)
    fluor_ave = np.array(fluor_ave)

    final_pi_time = np.pi/omega
    print("pi time is", final_pi_time)

    freq_string = str(round(freq_peak,4)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_raw_data\\New_D52_calibration_raw_data_pitime_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
    combined_data = zip(pulse_time_list,flour_exp)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_each_exp_raw_data\\New_D52_calibration_each_exp_raw_data_{freq_string}_pitime_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")

    return final_pi_time

with open(output_file_freqs,'w'):
    pass



Raman_Freq = getGlobal("Raman_Frequency")
if not "%s"%Raman_Freq == "%s MHz"%freq_peak:
    setGlobal("Raman_Frequency", np.round(freq_peak, 6), "MHz")

setEvaluation('Eval2')


tone_1 = 150
tone_2 = 150 + freq_peak

TABLE_DAC0 = [
    [0, False, [
        [0, [
            # f_MHz, phase_rad, amp, duration_us, phase_mode,
            # rep_rate_mode, enable, phase_latency_cycles, label
            [tone_1, 0.0, 0.5, 5e6,
             0, 0, True, 0, "DAC0 tone 0"],
        ]],
        [1, [
            [tone_2, 0, 0.5, 5e6,
             0, -1*rep_rate_stabilisation, True, 0, "DAC0 tone 1, rep -1"],
        ]],
    ]],
]

response = upload_dac0(
    TABLE_DAC0,
    time_unit="us",
)
print("Uploaded Raman successfully.")
print(f'Setting freq to {freq_peak} MHz with total probe time of 1500 us')

setEvaluation('Eval3')

RamanPulseTime = findPiTime_withfit_plotPD(do_pi_time_calibration, dummy_pulse_time, freq_peak, start_time, stop_time, time_step, threshold, pulse_program, script_functions)

setEvaluation('Eval2')

