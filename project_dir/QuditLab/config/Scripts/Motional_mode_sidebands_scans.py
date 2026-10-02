#RFSoC_FindResonanceFrequency_OpticalPumping.py created 2025-09-26 12:50:13.128316

import json, urllib.request

name = "pynq"
PORT = 9009
host  = f"http://{name}:{PORT}/upload_rows"

def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(host, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

import sys
import os
import datetime
import glob
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

dt_string_start = datetime.datetime.now().strftime("%Y%m%d_%H%M")

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

target_transition  = [[2,4,2]]

centre_freq = list(Get_1762_EOM_Freqs_an1an2(target_transition,f_offset,f_upper))[0]

s1 = 1.46578
s2 = 1.2969
num_scans = 10
#centre_freq = 610.4188 + 20.7737
#centre_freq = 604.5756 + 1.139
#centre_freq = 610.7
centre_freq = centre_freq
freq_step = 0.001
freq_range_factor = 10
threshold = 11

SetPulseTime = 3000 #us
opt_pump_time = 1000

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

Opt_pump_dummy = getGlobal("OpticalPumpTimeGlobal")
if not "%s"%Opt_pump_dummy == "%s us"%opt_pump_time:
    setGlobal("OpticalPumpTimeGlobal", opt_pump_time, "us")


pulse_program_findres = "Shelving_Freq_Cal_Ba137"

range = freq_range_factor*freq_step
freq_start = centre_freq-range
freq_stop = centre_freq+range+freq_step

setEvaluation('Eval3')

def findResonance_withfit_plotPD(start_freq, stop_freq, freq_step, axis, dt_string , threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    flour_exp = []
    fluor_ave = []
    freq_list = []
    while set_freq <= stop_freq:
        if scriptIsStopped():
            break

        RFSoC_Freq = getGlobal("RFSoC_Frequency")
        if not "%s"%RFSoC_Freq == "%s MHz"%set_freq:
            setGlobal("RFSoC_Frequency", np.round(set_freq, 6), "MHz")
        # table line, frequency, phase, duration, phase_reset, jump_flag
        rows = [
            [1,[set_freq],[0],[1000],[0],0],
        ]

        resp = upload_rows(rows, time_unit="us")
        print(json.dumps(resp, indent=2))
        print(1)
        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        #threshold = getShelvingThreshold2(ydata)
        fluor_bool = np.array(ydata) < threshold

        def DC_check(data):
            count = 0
            for value in data:
                if value:
                    count += 1
                    if count >= 15:
                        return True
                else:
                    count = 0
            return False

        PD = np.mean(fluor_bool)
        flour_exp.append(fluor_bool)

        if not DC_check(fluor_bool):
            fluor_ave.append(PD)
            freq_list.append(set_freq)
        else:
            pass

        plotPoint(set_freq, PD, '1762 nm freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 6)
    closeTrace('1762 nm freq scan')
    #print(fluor_ave)
    #print(getShelvingThreshold2(ydata))

    def Lorentzian_1D(x, centre, width, amp, bg):
        return amp/(1+((x-centre)/width)**2) + bg
    #def Lorentzian_1D(x, centre, width, amp, bg):
    #    return -amp/(1+((x-centre)/width)**2) + bg
    #freq_guess = (start_freq+stop_freq)/2
    freq_guess = freq_list[np.argmax(fluor_ave)]
    guess = np.array([freq_guess,0.001,0.5,0])
    #freq_guess = freq_list[np.argmax(fluor_data)]
    #guess = np.array([freq_guess,0.001,10,30])
    popt, pcov = curve_fit(Lorentzian_1D, freq_list, fluor_ave, guess, maxfev = 10000)
    freq_res = popt[0]
    uncertainty = np.sqrt(pcov[0][0])
    print(f'freqs covered: {freq_list}')
    print(f'fluor ave: {fluor_ave}')
    print(f'{freq_res}, amp={popt[2]}, width={popt[1]}, bg={popt[3]}')
    #Sving Raw data for the plots
    freq_string = str(round(freq_res,4)).replace('.','p')
    combined_data = zip(freq_list,fluor_ave)
    filename = f'Z:\Lab Data\Motional_mode_scans\Raw_data_PD\Secular_frequency_{axis}_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    #Saving Raw data of each Experiment
    combined_data = zip(freq_list,flour_exp)
    filename = f'Z:\Lab Data\Motional_mode_scans\Raw_data\Secular_frequency_{axis}_raw_data_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    return freq_res

filename = f'Z:\Lab Data\Motional_mode_scans\Secular_frequency_log_{dt_string_start}.txt'

i = 0
while i < num_scans :
    dt_string_current = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    centre_freq_s1 = centre_freq + s1

    range = freq_range_factor*freq_step
    freq_start = centre_freq_s1-range
    freq_stop = centre_freq_s1+range+freq_step
    axis = 1
    freq_peak_s1 = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, axis, dt_string_current, threshold, pulse_program_findres, script_functions, AWG=True)
    s1 = freq_peak_s1 - centre_freq

    centre_freq_s2 = centre_freq + s2

    range = freq_range_factor*freq_step
    freq_start = centre_freq_s2-range
    freq_stop = centre_freq_s2+range+freq_step
    axis = 2
    freq_peak_s2 = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, axis, dt_string_current, threshold, pulse_program_findres, script_functions, AWG=True)
    s2 =  freq_peak_s2 - centre_freq

    with open(filename,'a') as file:
        file.write(f"{dt_string_current}, {freq_peak_s1}, {freq_peak_s2}, {s1}, {s2}\n")

    i = i + 1
setEvaluation('Eval2')

