#RFSoC_RamanScan_OpticalPumping.py created 2026-07-16 15:30:56.978668

#RFSoC_FindResonanceFrequency_OpticalPumping.py created 2025-09-26 12:50:13.128316

import json, urllib.request, urllib.error

name = "pynq"
PORT = 9009
host  = f"http://{name}:{PORT}/upload_rows"

def upload_rows_1762(rows, time_unit="us"):
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
from Functions_RFSoC import upload_dac0

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

target_transition  = [[2,4,2]]
shelving_freq = list(Get_1762_EOM_Freqs_an1an2(target_transition,f_offset,f_upper))[0]
shelving_freq = 610.72778

centre_freq = 2.9489 # spacing between +2 ande +1 states in S1/2 F=2

#centre_freq = 610.4188 + 20.7737
#centre_freq = 604.5756 + 1.139
#centre_freq = 610.7265
freq_step = 0.0012
freq_range_factor = 5
threshold = 11

RamanPulseTime =300 #us
ShelvingPulseTime = 44.6 #us
opt_pump_time = 1000

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%ShelvingPulseTime:
    setGlobal("Shelving_Pulse_Time", ShelvingPulseTime, "us")

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%ShelvingPulseTime:
    setGlobal("Shelving_Pulse_Time", ShelvingPulseTime, "us")

Opt_pump_dummy = getGlobal("OpticalPumpTimeGlobal")
if not "%s"%Opt_pump_dummy == "%s us"%opt_pump_time:
    setGlobal("OpticalPumpTimeGlobal", opt_pump_time, "us")

Raman_Pulse_Time_dummy = getGlobal("Raman_Pulse_Time")
if not "%s"%Raman_Pulse_Time_dummy == "%s us"%RamanPulseTime:
    setGlobal("Raman_Pulse_Time", RamanPulseTime, "us")

# first, uploading frequency for shelving laser
RFSoC_Freq = getGlobal("RFSoC_Frequency")
if not "%s"%RFSoC_Freq == "%s MHz"%shelving_freq:
    setGlobal("RFSoC_Frequency", np.round(shelving_freq, 6), "MHz")
# table line, frequency, phase, duration, phase_reset, jump_flag
rows = [
    [1,[shelving_freq],[0],[1000],[0],0],
]

resp = upload_rows_1762(rows, time_unit="us")
print(json.dumps(resp, indent=2))
print("Uploaded 1762 successfully.")

pulse_program_findres = "Raman_Freq_Cal_Ba137"

range = freq_range_factor*freq_step
freq_start = centre_freq-range
freq_stop = centre_freq+range+freq_step

setEvaluation('Eval3')

def findResonance_withfit_plotPD(start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('Raman freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    flour_exp = []
    fluor_ave = []
    freq_list = []
    while set_freq <= stop_freq:
        if scriptIsStopped():
            break

        Raman_Freq = getGlobal("Raman_Frequency")
        if not "%s"%Raman_Freq == "%s MHz"%set_freq:
            setGlobal("Raman_Frequency", np.round(set_freq, 6), "MHz")

        tone_1 = 150
        tone_2 = 150 + set_freq
        rep_rate_stabilisation = 0 # set to -1 for first sideband stability

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
                     0, rep_rate_stabilisation, True, 0, "DAC0 tone 1, rep -1"],
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

        plotPoint(set_freq, PD, 'Raman freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 6)
    closeTrace('Raman freq scan')
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
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration_Raw_data\D52_calibration_raw_data_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    #Saving Raw data of each Experiment
        combined_data = zip(freq_list,flour_exp)
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\Calibration_experiments_raw_data_of_each_experiment\D52_calibration_each_exp_raw_data_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{uncertainty}")
    return freq_res

freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program_findres, script_functions, AWG=True)

setEvaluation('Eval2')

Raman_Freq = getGlobal("Raman_Frequency")
if not "%s"%Raman_Freq == "%s MHz"%freq_peak:
    setGlobal("Raman_Frequency", np.round(freq_peak, 6), "MHz")
print(freq_peak)


# NEED TO UPDATE THIS LOGIC AS WELL FOR RAMAN
rows = [
    [1,[freq_peak],[0],[10],[0],0],
]

data = json.dumps({"rows": rows, "time_unit":"us"}).encode()
req = urllib.request.Request(host, data=data, headers={"Content-Type":"application/json"})
print(json.loads(urllib.request.urlopen(req).read().decode()))


