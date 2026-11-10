#Microwave_FrequencyPiTimeCalibration.py created 2026-11-09 17:03:15.991169

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

from Functions_Microwave import *

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from DSI_12000PRO_connet import set_DSI12000PRO


script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)
run_time = datetime.datetime.now()
dt_string = run_time.strftime("%Y%m%d_%H%M%S_%f")

transitions = [
    ['S', 2, 1, 'S', 1, 1],
    # ['S', 2, -1, 'S', 1, 0],
]

transitions = [
    # DmF = -1
    ['S', 2, -2, 'S', 1, -1],
    ['S', 2, -1, 'S', 1,  0],
    ['S', 2,  0, 'S', 1, +1],

    # DmF = 0
    ['S', 2, -1, 'S', 1, -1],
    ['S', 2,  0, 'S', 1,  0],  # Clock transition
    ['S', 2, +1, 'S', 1, +1],

    # DmF = +1
    ['S', 2,  0, 'S', 1, -1],
    ['S', 2, +1, 'S', 1,  0],
    ['S', 2, +2, 'S', 1, +1],
]

# Reference calibrations for theory predictions. Frequencies are in MHz and pi times are in us.
fl, pi_time_l = 8029.019188, 27.98  # Lower transition, mF -1 to -2
fu, pi_time_u = 8046.471323, 16.9  # Upper transition, mF +1 to +2
f0, pi_time_0 = 8037.750920, 34.475  # Clock transition, mF 0 to 0

# Leave a transition out of these dictionaries to use its predicted value.
frequency_overrides_mhz = {}
pi_time_overrides_us = {
    #('S', 2, 1, 'S', 1, 1): 20,
}

do_pi_time_calibration = True
do_frequency_scan = True
line_trigger = True

pulse_program = "Microwave_Calibration_NBOP_Ba137"

threshold = 11
F1PumpTime = 1.5
F1PumpReps = 60
InitReps = 0

freq_step = 0.004 # MHz
freq_range_factor = 10 # number of frequency steps

# Shelving transitions are indexed by the F=2 mF plus two.
list_of_shelving = [
    [[-2,4,-4],[-2,3,-3],[-2,3,-2]],
    [[-1,4,-3],[-1,3,0],[-1,3,-1]],
    [[0,2,0],[0,4,-2],[0,3,2]],
    [[1,4,1],[1,4,-1],[1,3,3]],
    [[2,4,2],[2,4,3],[2,4,4]],
]

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

output_root = r'Z:\Lab Data\Microwave_calibrations'
date_folders = (run_time.strftime('%Y_%m'), run_time.strftime('%d'))
frequency_scan_dir = os.path.join(output_root, 'Frequency_scans', *date_folders)
frequency_scan_raw_data_dir = os.path.join(output_root, 'Experiment_raw_data', 'Frequency_scans', *date_folders)
pulse_time_scan_dir = os.path.join(output_root, 'Pulse_time_scans', *date_folders)
pulse_time_scan_raw_data_dir = os.path.join(output_root, 'Experiment_raw_data', 'Pulse_time_scans', *date_folders)
calibration_runs_dir = os.path.join(output_root, 'Calibration_runs', *date_folders)

def findResonance_withfit_plotPD(init_state, ShelvingPulseTime, start_freq, stop_freq, freq_step, scan_path, raw_data_path, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    flour_exp = []
    fluor_ave = []
    freq_list = []

    dummy_counter = 0

    print(set_freq,ShelvingPulseTime)
    #print(init_freqs_array[int(init_state+2)],init_times_array[int(init_state+2)])

    init_row1 = [1, init_freqs_array, [0]*len(init_freqs_array), init_times_array, [0]*len(init_times_array), 0]

    tot_init_time = np.sum(init_times_array)
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

        Microwave_Freq = getGlobal("Microwave_Frequency")
        if not "%s"%Microwave_Freq == "%s MHz"%set_freq:
            setGlobal("Microwave_Frequency", np.round(set_freq, 6), "MHz")

        set_DSI12000PRO(set_freq, 0, True)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold


        PD = 1-np.mean(fluor_bool)
        flour_exp.append(np.asarray(ydata).tolist())

        fluor_ave.append(PD)
        freq_list.append(set_freq)
        plotPoint(set_freq, PD, '1762 nm freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 4)


    closeTrace('1762 nm freq scan')

    with open(scan_path, 'w') as file:
        for x, y in zip(freq_list, fluor_ave):
            file.write(f"{x},{y}\n")
    with open(raw_data_path, 'w') as file:
        for x, y in zip(freq_list, flour_exp):
            file.write(f"{x},{y}\n")

    if scriptIsStopped():
        return None
    if len(freq_list) < 5 or np.ptp(fluor_ave) == 0:
        print("Could not fit frequency scan")
        return None

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

    f_variance = (np.asarray(freq_list) - f0_guess)**2
    Omega_guess = np.sqrt(
        np.sum(np.multiply(f_variance, fluor_ave)) / np.sum(fluor_ave) / 4)

    A_guess = max(fluor_ave)
    t_guess = np.pi / Omega_guess
    p0 = np.array([f0_guess, A_guess, Omega_guess, t_guess])

    try:
        popt, pcov = curve_fit(sin_squared,freq_list,fluor_ave,p0=p0,maxfev=10000)

        pulse_time_mult_factor = 1.0
        for _ in range(10):
            if pcov[3][3] <= 10000:
                break
            pulse_time_mult_factor = pulse_time_mult_factor + 0.5
            p0 = np.array([
                f0_guess, A_guess, Omega_guess,
                (pulse_time_mult_factor + 1) * t_guess
            ])

            popt, pcov = curve_fit(sin_squared,freq_list,fluor_ave,p0=p0,maxfev=10000)
        if not np.isfinite(pcov[3][3]) or pcov[3][3] > 10000:
            print("Could not resolve the frequency fit after 10 retries")
            return None
    except (RuntimeError, ValueError) as error:
        print(f"Frequency fit failed: {error}")
        return None

    freq_res = popt[0]
    uncertainty = np.sqrt(pcov[0][0])
    print(f'freqs covered: {freq_list}')
    print(f'fluor ave: {fluor_ave}')
    print(f'{freq_res}, amp={popt[2]}, width={popt[1]}, bg={popt[3]}')
    print("frequency uncertainty is", uncertainty)
    return freq_res


def findPiTime_withfit_plotPD(freq_peak, start_time, stop_time, time_step, scan_path, raw_data_path, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    fluor_ave = []
    pulse_time_list = []
    flour_exp = []
    for pulse_time in np.linspace(start_time, stop_time, round((stop_time - start_time) / time_step) + 1).tolist():
        if scriptIsStopped():
            break
        Microwave_Pulse_Time_dummy = getGlobal("Microwave_Pulse_Time")
        if not "%s"%Microwave_Pulse_Time_dummy == "%s us"%pulse_time:
            setGlobal("Microwave_Pulse_Time", pulse_time, "us")
        time.sleep(1)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold
        PD = 1-np.mean(fluor_bool)
        flour_exp.append(np.asarray(ydata).tolist())

        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)


    closeTrace('1762 nm pi-time scan')

    with open(scan_path, 'w') as file:
        for x, y in zip(pulse_time_list, fluor_ave):
            file.write(f"{x},{y}\n")
    with open(raw_data_path, 'w') as file:
        for x, y in zip(pulse_time_list, flour_exp):
            file.write(f"{x},{y}\n")

    if scriptIsStopped():
        return None
    if len(pulse_time_list) < 6 or np.ptp(fluor_ave) == 0:
        print("Could not fit pulse-time scan")
        return None

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

    try:
        omega, uncertainty = fit_oscillation(pulse_time_list, fluor_ave)
    except (RuntimeError, ValueError) as error:
        print(f"Pulse-time fit failed: {error}")
        return None
    if not np.isfinite(omega) or omega == 0:
        print("Could not resolve the pulse-time fit")
        return None

    final_pi_time = np.pi / abs(omega)
    print("pi time is", final_pi_time, "us")
    print("angular frequency uncertainty is", uncertainty)
    return final_pi_time


scan_enabled = do_frequency_scan or do_pi_time_calibration
if scan_enabled:
    f_offset = float(getGlobal('f_offset'))
    f_upper = float(getGlobal('f_upper'))

    pitime_n2 = float(getGlobal('pitime_n2')) #13.48#
    pitime_n1 = float(getGlobal('pitime_n1'))
    pitime_0 = float(getGlobal('pitime_0')) #23.734#
    pitime_p1 = float(getGlobal('pitime_p1'))
    pitime_p2 = float(getGlobal('pitime_p2'))
    ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

    LT_dummy = getGlobal('LineTriggerBoolean')
    if not "%s"%LT_dummy == int(line_trigger):
        setGlobal("LineTriggerBoolean", int(line_trigger), "")

    F1_pumpTime = getGlobal('F1_PumpTime')
    if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"% 0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us") # type: ignore


    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

os.makedirs(calibration_runs_dir, exist_ok=True)
if do_frequency_scan:
    os.makedirs(frequency_scan_dir, exist_ok=True)
    os.makedirs(frequency_scan_raw_data_dir, exist_ok=True)
if do_pi_time_calibration:
    os.makedirs(pulse_time_scan_dir, exist_ok=True)
    os.makedirs(pulse_time_scan_raw_data_dir, exist_ok=True)

output_file_freqs = os.path.join(calibration_runs_dir, f'{dt_string}_microwave_calibration.txt')
with open(output_file_freqs, 'w') as outfile:
    outfile.write("transition\tfrequency_mhz\tfrequency_source\tpi_time_us\tpi_time_source\tstatus\t"
                  "frequency_scan_path\tfrequency_raw_data_path\tpulse_time_scan_path\tpulse_time_raw_data_path\n")
    for number, transition in enumerate(transitions, start=1):
        if scan_enabled and scriptIsStopped():
            break

        if (len(transition) != 6 or tuple(transition[:2]) != ('S', 2)
                or tuple(transition[3:5]) != ('S', 1)
                or transition[2] not in range(-2, 3) or transition[5] not in range(-1, 2)):
            raise ValueError(f"Invalid F=1 to F=2 transition: {transition}")

        centre_freq = frequency_overrides_mhz.get(tuple(transition))
        if centre_freq is None:
            centre_freq = get_transition_frequency_MW(transition, fu=fu, fl=fl, f0=f0)
        MicrowavePulseTime = pi_time_overrides_us.get(tuple(transition))
        if MicrowavePulseTime is None:
            MicrowavePulseTime = get_pi_time_MW(
                transition, pi_time_0=pi_time_0, pi_time_u=pi_time_u, pi_time_l=pi_time_l)
        if not np.isfinite(centre_freq) or centre_freq <= 0:
            raise ValueError(f"Invalid frequency in MHz for {transition}: {centre_freq}")
        if not np.isfinite(MicrowavePulseTime) or MicrowavePulseTime <= 0:
            raise ValueError(f"Invalid pi time in us for {transition}: {MicrowavePulseTime}")

        init_state = int(transition[2])
        transition_name = f'{transition}'
        file_stem = f'{dt_string}_{number:02d}_{transition_name}'
        print(f'{transition_name}: {centre_freq:.6f} MHz, pi-time estimate {MicrowavePulseTime:g} us')

        if scan_enabled:
            shelving_transition = list_of_shelving[init_state + 2]
            init_trans = list_of_inits[init_state+2]

            init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
            init_times_array = list(get_pi_times(init_trans,ref_pitimes_list))

            shelving_freq = list(Get_1762_EOM_Freqs_an1an2(shelving_transition,f_offset,f_upper))
            ShelvingPulseTime = list(get_pi_times(shelving_transition,ref_pitimes_list))

        frequency_scan_path = frequency_raw_data_path = ''
        if do_frequency_scan:
            frequency_scan_path = os.path.join(frequency_scan_dir, f'{file_stem}_frequency.txt')
            frequency_raw_data_path = os.path.join(frequency_scan_raw_data_dir, f'{file_stem}_frequency_each_exp.txt')
            Microwave_Pulse_Time_dummy = getGlobal("Microwave_Pulse_Time")
            if not "%s"%Microwave_Pulse_Time_dummy == "%s us"%MicrowavePulseTime:
                setGlobal("Microwave_Pulse_Time", MicrowavePulseTime, "us")

            true_freq_range = freq_range_factor*freq_step
            freq_start = centre_freq-true_freq_range
            freq_stop = centre_freq+true_freq_range+freq_step
            setEvaluation('Eval3')
            try:
                freq_peak = findResonance_withfit_plotPD(
                    init_state, ShelvingPulseTime, freq_start, freq_stop, freq_step,
                    frequency_scan_path, frequency_raw_data_path, threshold, pulse_program, script_functions)
                if freq_peak is not None:
                    Microwave_Freq = getGlobal("Microwave_Frequency")
                    if not "%s"%Microwave_Freq == "%s MHz"%freq_peak:
                        setGlobal("Microwave_Frequency", np.round(freq_peak, 6), "MHz")
            finally:
                setEvaluation('Eval2')
        else:
            freq_peak = centre_freq

        pi_time = None if do_pi_time_calibration else MicrowavePulseTime
        pulse_time_scan_path = pulse_time_raw_data_path = ''
        if do_pi_time_calibration and freq_peak is not None and not scriptIsStopped():
            pulse_time_scan_path = os.path.join(pulse_time_scan_dir, f'{file_stem}_pulse_time.txt')
            pulse_time_raw_data_path = os.path.join(pulse_time_scan_raw_data_dir, f'{file_stem}_pulse_time_each_exp.txt')
            init_row1 = [1, init_freqs_array, [0]*len(init_freqs_array), init_times_array, [0]*len(init_times_array), 0]

            tot_init_time = np.sum(init_times_array)
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

            if not do_frequency_scan:
                setGlobal("Microwave_Frequency", np.round(freq_peak, 6), "MHz")
            set_DSI12000PRO(freq_peak, 0, True)

            start_time = 0
            stop_time = 4 * MicrowavePulseTime
            time_step = MicrowavePulseTime / 5
            setEvaluation('Eval3')
            try:
                pi_time = findPiTime_withfit_plotPD(
                    freq_peak, start_time, stop_time, time_step, pulse_time_scan_path, pulse_time_raw_data_path,
                    threshold, pulse_program, script_functions)
            finally:
                setEvaluation('Eval2')

        frequency_source = 'fitted' if do_frequency_scan else 'used'
        pi_time_source = 'fitted' if do_pi_time_calibration else 'used'
        status = 'complete'
        if scan_enabled and scriptIsStopped():
            status = 'stopped'
        elif freq_peak is None or pi_time is None:
            status = 'fit_failed'
        freq_text = '' if freq_peak is None else f'{freq_peak:.6f}'
        pi_text = '' if pi_time is None else f'{pi_time:.3f}'
        outfile.write(f'{transition}\t{freq_text}\t{frequency_source if freq_text else ""}\t'
                      f'{pi_text}\t{pi_time_source if pi_text else ""}\t{status}\t'
                      f'{frequency_scan_path}\t{frequency_raw_data_path}\t'
                      f'{pulse_time_scan_path}\t{pulse_time_raw_data_path}\n')
        outfile.flush()
