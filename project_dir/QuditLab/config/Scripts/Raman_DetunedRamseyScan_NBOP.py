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
line_trigger = True

pulse_program = "Raman_Ramsey_NBOP_2RFSoCs_Ba137"

f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

pitime_n2 = getGlobal('pitime_n2') # [-1, 4, -3]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [0, 2, 0]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]
ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

threshold = 11
F1PumpTime = 0.5
F1PumpReps = 30
InitReps = 0
fs = 4e9

target_freq = 8037.75032 #in MHz
RamanPulseTime = 38 #in us
do_freq_scan = False
Raman_upload_freq = 17.520 # MHz

detuning = 0.002 # MHz
wait_time_step = 100 # in us
stop_time = 3000 # in us

shelving_transition  = [[0,2,0],[0,3,2],[0,4,-2]]
init_state = shelving_transition[0][0]

def RepRateMode_CenterFreq(target_freq):
    rep_rate = 75.66255
    RepRateMode = int(target_freq/rep_rate)
    center_freq = target_freq - RepRateMode*rep_rate
    return RepRateMode, center_freq, rep_rate

rep_rate_stabilisation, Raman_freq, rep_rate = RepRateMode_CenterFreq(target_freq)

f_offset_index = [0,2,0]
f_upper_index = [0,4,-2]
pitime_ref_index = [[0,2,0],[0,4,-2],[-2,3,-3],[2,4,3],[2,4,4]]

init_n2_index = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]]
init_n1_index = [[-2,3,-1],[0,3,0],[1,4,2],[2,4,3]]
init_0_index = [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]]
init_p1_index = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]]
init_p2_index = [[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]

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

Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
if not "%s"%Raman_Pulse_Time_dummy == "%s us"%RamanPulseTime:
    setGlobal("Raman_Pulse_Time", RamanPulseTime, "us")


freq_list_fitted = []
freq_step = 0.003 # MHz
freq_range_factor = 7 # kHz 

def findResonance_withfit_plotPD(init_state, ShelvingPulseTime, start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    flour_exp = []
    fluor_ave = []
    freq_list = []

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

    while set_freq <= stop_freq:
        if scriptIsStopped():
            # eng.quit()
            break

        dummy_counter = dummy_counter + 1
        if scriptIsStopped():
            break

        Raman_Freq = getGlobal("Raman_Frequency")
        if not "%s"%Raman_Freq == "%s MHz"%set_freq:
            setGlobal("Raman_Frequency", np.round(set_freq, 6), "MHz")

        tone_1 = 150
        tone_2 = 150 + set_freq

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

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold
        

        PD = 1-np.mean(fluor_bool)
        flour_exp.append(ydata)

        fluor_ave.append(PD)
        freq_list.append(set_freq)
        plotPoint(set_freq, PD, '1762 nm freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 4)


    closeTrace('1762 nm freq scan')

    def sin_squared(f, f0, A, Omega, t):
            delta = f - f0
            return A * (Omega**2 /
                        (Omega**2 + delta**2)) * (np.sin(
                            np.sqrt(Omega**2 +
                                    delta**2) * t / 2))**2

    f0_guess = np.sum(np.multiply(freq_list, fluor_ave)) / np.sum(fluor_ave)
    f_range = freq_list[-1] - freq_list[0]
    top_30_percent = freq_list[-1] - f_range / 3
    bot_30_percent = freq_list[0] + f_range / 3
    if f0_guess > top_30_percent or f0_guess < bot_30_percent:
        f0_guess = freq_list[np.argmax(fluor_ave)]

    f_variance = (freq_list - f0_guess)**2
    Omega_guess = np.sqrt(
        np.sum(np.multiply(f_variance, fluor_ave)) / np.sum(fluor_ave) / 4)

    A_guess = max(fluor_ave)
    t_guess = np.pi / Omega_guess
    p0 = np.array([f0_guess, A_guess, Omega_guess, t_guess])
    
    popt, pcov = curve_fit(sin_squared,freq_list,fluor_ave,p0=p0,maxfev=10000)

    pulse_time_mult_factor = 1.0
    while pcov[3][3] > 10000:
        pulse_time_mult_factor = pulse_time_mult_factor + 0.5
        p0 = np.array([
            f0_guess, A_guess, Omega_guess,
            (pulse_time_mult_factor + 1) * t_guess
        ])

        popt, pcov = curve_fit(sin_squared,freq_list,fluor_ave,p0=p0,maxfev=10000)

    freq_res = popt[0]
    uncertainty = np.sqrt(pcov[0][0])
    print(f'freqs covered: {freq_list}')
    print(f'fluor ave: {fluor_ave}')
    print(f'{freq_res}, amp={popt[2]}, width={popt[1]}, bg={popt[3]}')
    freq_string = str(round(freq_res,4)).replace('.','p')
    combined_data = zip(freq_list,fluor_ave)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_raw_data\\New_D52_calibration_raw_data_freq_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    combined_data = zip(freq_list,flour_exp)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_each_exp_raw_data\\New_D52_calibration_each_exp_raw_data_freq_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    return freq_res

def findPiTime_withfit_plotPD(freq_peak, stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('Raman Ramsey scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    wait_time = 0
    fluor_ave = []
    wait_time_list = []
    flour_exp = []
    while wait_time <= stop_time:
        if scriptIsStopped():
            break
        Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
        if not "%s"%Raman_Pulse_Time_dummy == "%s us"%RamanPulseTime+wait_time:
            setGlobal("Raman_Pulse_Time", RamanPulseTime+wait_time, "us")
        time.sleep(1)
        
        
        tone_1 = 150
        tone_2 = 150 + freq_peak

        TABLE_DAC0 = [
            [0, False, [
                [0, [
                    # f_MHz, phase_rad, amp, duration_us, phase_mode,
                    # rep_rate_mode, enable, phase_latency_cycles, label
                    [0, 0.0, 1.0, 5e6,
                     0, 0, False, 0, "Dummy Tone"],
                ]],
            ]],
            [1, True, [
                [0, [
                    # f_MHz, phase_rad, amp, duration_us, phase_mode,
                    # rep_rate_mode, enable, phase_latency_cycles, label
                    [[tone_1,0,tone_1], [0.0,0.0,0.0], [0.5,0.5,0.5], [RamanPulseTime/2,wait_time,RamanPulseTime/2],
                     [1,1,1], [0,0,0], True, 0, "DAC0 tone 0"],
                ]],
                [1, [
                    [[tone_2,0,tone_2], [0.0,0.0,0.0], [0.5,0.5,0.5], [RamanPulseTime/2,wait_time,RamanPulseTime/2],
                     [1,1,1], [-1*rep_rate_stabilisation,-1*rep_rate_stabilisation,-1*rep_rate_stabilisation], True, 0, "DAC0 tone 1, rep -1"],
                ]],
            ]],
        ]

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
        PD = 1-np.mean(fluor_bool)
        flour_exp.append(fluor_bool)

        fluor_ave.append(PD)
        wait_time_list.append(wait_time)

        plotPoint(wait_time, PD, 'Raman Ramsey scan', plotStyle=2)

        wait_time = wait_time + time_step
        
    closeTrace('Raman Ramsey scan')

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

    
    omega, uncertainty = fit_oscillation(wait_time_list,fluor_ave)
    print("firstpass_omega is", omega)

    period = 2*np.pi/omega
    wait_time_list = np.array(wait_time_list)
    fluor_ave = np.array(fluor_ave)

    final_pi_time = np.pi/omega
    print("pi time is", final_pi_time)

    freq_string = str(round(freq_peak,4)).replace('.','p')
    combined_data = zip(wait_time_list,fluor_ave)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_raw_data\\New_D52_calibration_raw_data_pitime_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
    combined_data = zip(wait_time_list,flour_exp)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_each_exp_raw_data\\New_D52_calibration_each_exp_raw_data_{freq_string}_pitime_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")

    return final_pi_time

with open(output_file_freqs,'w'):
    pass






'''
[centre_freq] = Get_1762_EOM_Freqs_an1an2([scan_index],f_offset,f_upper)
[pi_time] = Get_1762_PiTimes([scan_index],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
init_state = scan_index[0]
centre_freq = np.round(centre_freq,6)
print(centre_freq)
if np.isnan(pi_time):
    pi_time = 100
pi_tyime = ShelvingPulseTime
if pi_time < 50:
    freq_step = 0.006 # MHz
    freq_range_factor = 10 # kHz
elif 50 <= pi_time < 110:
    freq_step = 0.0025 # MHz
    freq_range_factor = 10 # kHz
elif 110 <= pi_time < 200:
    freq_step = 0.001 # MHz
    freq_range_factor = 10 # kHz            
elif pi_time >= 200:
    freq_step = 0.0005 # MHz
    freq_range_factor = 10 # kHz       



'''
true_freq_range = freq_range_factor*freq_step
freq_start = centre_freq-true_freq_range
freq_stop = centre_freq+true_freq_range+freq_step

setEvaluation('Eval3')
if do_freq_scan:
    freq_peak = findResonance_withfit_plotPD(init_state, ShelvingPulseTime, freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program, script_functions)
else:
    freq_peak  = Raman_upload_freq
    
freq_list_fitted.append(freq_peak)


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

RamanPulseTime = findPiTime_withfit_plotPD(freq_peak, stop_time, time_step, threshold, pulse_program, script_functions)

setEvaluation('Eval2')

with open(output_file_freqs,'a') as outfile:
    outfile.write(f'{np.round(freq_peak,6)}, {np.round(RamanPulseTime,3)}, {int(init_state)}\n')


