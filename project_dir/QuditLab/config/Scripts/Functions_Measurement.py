#Functions_Measurement.py created 2022-10-07 23:32:04.676018
import numpy as np
import sys
import time
import datetime
import os
import glob
import pandas as pd
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_Physics import *
from scipy.optimize import curve_fit
#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)
#dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
#year = datetime.datetime.now().strftime("%Y")
#month = datetime.datetime.now().strftime("%m")
#day = datetime.datetime.now().strftime("%d")

def set_global_value(key, value, unit, script_functions):
    getGlobal = script_functions[0]
    setGlobal = script_functions[1]

    global_value = getGlobal(key)
    global_split = str(global_value).split(" ")
    global_value = float(global_split[0])
    if len(global_split) > 1:
        global_unit = global_split[1]
    else:
        global_unit = ""
    
    if unit != global_unit:
        raise ValueError(f"Provided unit {unit} must equal global variable unit {global_unit}")
    
    if global_value != value:
        print(f"Set global variable {key} = {value} {unit}")
        setGlobal(key, value, unit)

def setGlobalPulseTimeScan_Meas(start_time, time_step, time_stop, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    #stop_time_new = start_time + time_step*time_steps
    stop_time_new = time_stop
    set_global_value("PulseTimeStart", start_time, "us", script_functions)
    
    set_global_value("PulseTimeStop", stop_time_new, "us", script_functions)

    set_global_value("PulseTimeStep", time_step, "us", script_functions)

def findResonance(start_freq, stop_freq, freq_step, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    freq_min = set_freq
    data_min = 100
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    while set_freq < stop_freq:
        if scriptIsStopped():
            break
        if AWG:
            setGlobal('AWGClockRef',int(1),'')
            time.sleep(0.01)
            setGlobal('AWGClockRef',int(0),'')
            time.sleep(0.1)
            set_global_value("AWG1_Frequency", np.round(set_freq, 6), "MHz", script_functions)
        else:
            set_global_value("PDH_EOM_1762_Freq", set_freq, "MHz", script_functions)
            time.sleep(0.2)
        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        data_counts_ave = np.mean(np.array(ydata))

        if data_counts_ave < data_min:
            data_min = data_counts_ave
            freq_min = set_freq
        plotPoint(set_freq, data_counts_ave, '1762 nm freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 6)
    closeTrace('1762 nm freq scan')

    return np.round(freq_min, 6)

def findResonance_withfit(start_freq, stop_freq, freq_step, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    fluor_data = []
    freq_list = []
    while set_freq <= stop_freq:
        if scriptIsStopped():
            break
        if AWG:
            setGlobal('AWGClockRef',int(1),'')
            time.sleep(0.01)
            setGlobal('AWGClockRef',int(0),'')
            time.sleep(0.1)
            set_global_value("AWG1_Frequency", np.round(set_freq, 3), "MHz", script_functions)
        else:
            set_global_value("PDH_EOM_1762_Freq", set_freq, "MHz", script_functions)
            time.sleep(0.2)
        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        data_counts_ave = np.mean(np.array(ydata))

        fluor_data.append(ydata)
        freq_list.append(set_freq)

        plotPoint(set_freq, data_counts_ave, '1762 nm freq scan', plotStyle=0)
        set_freq = np.round(set_freq + freq_step, 3)
    closeTrace('1762 nm freq scan')
    print(fluor_data)
    threshold = getShelvingThreshold(fluor_data)
    fluor_bool = fluor_data < threshold
    fluor_ave = np.mean(fluor_bool, 1)

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
    print(f'freqs covered: {freq_list}')
    print(f'fluor ave: {fluor_ave}')
    print(f'{freq_res}, amp={popt[2]}, width={popt[1]}, bg={popt[3]}')
    return freq_res

def getShelvingThreshold2(counts):
    counts = [item for sublist in counts[0] for item in sublist]
    
    data_sorted = np.sort(counts, axis=None)
    # print(len(data_sorted))
    data_diff_max = 1
    slice_start = 0
    if len(data_sorted) > 10000:
        while int(data_diff_max) == 1:
            data_sorted_desample = data_sorted[slice_start::round(data_sorted.size/1000)]
            data_sorted_diff = data_sorted_desample[1:-1] - data_sorted_desample[0:-2]
            data_diff_max = max(data_sorted_diff)
            slice_start += 1
        data_sorted = data_sorted_desample
    else:
        data_sorted_diff = data_sorted[1:-1] - data_sorted[0:-2]
        data_diff_max = max(data_sorted_diff)
    data_diff_maxind = np.argmax(data_sorted_diff)
    threshold = data_diff_max/2 + data_sorted[data_diff_maxind]
    return threshold

def findResonance_withfit_plotPD(start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    set_freq = start_freq
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    flour_exp = []
    fluor_ave = []
    freq_list = []
    while set_freq <= stop_freq:
        if scriptIsStopped():
            break
        if AWG:
            setGlobal('AWGClockRef',int(1),'')
            time.sleep(0.01)
            setGlobal('AWGClockRef',int(0),'')
            time.sleep(0.1)
            set_global_value("AWG1_Frequency", np.round(set_freq, 6), "MHz", script_functions)
        else:
            os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%set_freq)
            set_global_value("EOM_1762_Sideband3_Freq", set_freq, "MHz", script_functions)
            time.sleep(0.2)
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


def findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = 0
    fluor_ave = []
    pulse_time_list = []
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break
        set_global_value("Shelving_Pulse_Time", pulse_time, "us", script_functions)
        time.sleep(0.2)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]
        fluor_bool = np.array(ydata) < threshold
        PD = np.mean(fluor_bool)

        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)

        pulse_time = pulse_time + time_step
        
    closeTrace('1762 nm pi-time scan')

    def oscfunc(t, A, w, p, c):  return A * np.cos(w*t + p) + c
    def fit_oscillation(tt, yy):
        '''Fit sin to the input time sequence, and return fitting parameters:
        "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc".

        Option to take on guesses and bounds for the fit too.'''
        tt = np.array(tt)
        yy = np.array(yy)
        ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))
        Fyy = abs(np.fft.fft(yy))
        guess_freq = abs(ff[np.argmax(Fyy[1:])+1])
            
        guess_amp = np.max(yy)-np.min(yy)/2.
        guess_offset = np.mean(yy)

        guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])
        popt, pcov = curve_fit(oscfunc, tt, yy, p0=guess, maxfev=10000)
            
        A, omeg, p, c = popt
        f = omeg/(2.*np.pi)
        
        return omeg

    
    omega_firstpass = fit_oscillation(pulse_time_list,fluor_ave)
    print("firstpass_omega is", omega_firstpass)

    period = 2*np.pi/omega_firstpass
    pulse_time_list = np.array(pulse_time_list)
    fluor_ave = np.array(fluor_ave)
    pulse_time_list_new = pulse_time_list[pulse_time_list <= int(period)]
    fluor_ave_new = fluor_ave[:len(pulse_time_list_new)]

    print(pulse_time_list_new)
    print(fluor_ave_new)
    print(len(pulse_time_list_new))
    print(len(fluor_ave_new))
    omega = fit_oscillation(pulse_time_list_new,fluor_ave_new)
    print("second omega is", omega)
    final_pi_time = np.pi/omega
    print("pi time is", final_pi_time)
    return final_pi_time


def find_and_plotPD_NoF1pump(comp_no, freq, threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    if scriptIsStopped():
        raise Exception("Sweep cancelled by user.")

    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        time.sleep(0.01)
        setGlobal('AWGClockRef',int(0),'')
        time.sleep(0.1)
        set_global_value("AWG1_Frequency", np.round(freq, 3), "MHz", script_functions)
    else:
        set_global_value("PDH_EOM_1762_Freq", freq, "MHz", script_functions)
        time.sleep(0.2)
    setScan(pulse_program)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    #threshold = getShelvingThreshold2(ydata)
    fluor_bool = np.array(ydata) < threshold
    PD = np.mean(fluor_bool)

    plotPoint(comp_no, PD, 'PlotPD No F1 Pump', plotStyle=0)
    return PD


def find_and_plotPD_F1pumpOnly(comp_no, freq, threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    if scriptIsStopped():
        raise Exception("Sweep cancelled by user.")

    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        time.sleep(0.01)
        setGlobal('AWGClockRef',int(0),'')
        time.sleep(0.1)
        set_global_value("AWG1_Frequency", np.round(freq, 3), "MHz", script_functions)
    else:
        set_global_value("PDH_EOM_1762_Freq", freq, "MHz", script_functions)
        time.sleep(0.2)
    setScan(pulse_program)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    #threshold = getShelvingThreshold2(ydata)
    fluor_bool = np.array(ydata) < threshold
    PD = np.mean(fluor_bool)

    plotPoint(comp_no, PD, 'PlotPD F1 Pump Only', plotStyle=0)
    return PD


def find_and_plotPD_repeatF1PumpandShelve(comp_no, freq, threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    if scriptIsStopped():
        raise Exception("Sweep cancelled by user.")

    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        time.sleep(0.01)
        setGlobal('AWGClockRef',int(0),'')
        time.sleep(0.1)
        set_global_value("AWG1_Frequency", np.round(freq, 3), "MHz", script_functions)
    else:
        set_global_value("PDH_EOM_1762_Freq", freq, "MHz", script_functions)
        time.sleep(0.2)
    setScan(pulse_program)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    #threshold = getShelvingThreshold2(ydata)
    fluor_bool = np.array(ydata) < threshold
    PD = np.mean(fluor_bool)

    plotPoint(comp_no, PD, 'PlotPD Repeated F1 Pump and Shelving', plotStyle=0)
    return PD

def find_and_plotPD_repeatF1PumpandShelve2(comp_no, freq, threshold, pulse_program, script_functions, AWG=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    if scriptIsStopped():
        raise Exception("Sweep cancelled by user.")

    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        time.sleep(0.01)
        setGlobal('AWGClockRef',int(0),'')
        time.sleep(0.1)
        set_global_value("AWG1_Frequency", np.round(freq, 3), "MHz", script_functions)
    else:
        set_global_value("PDH_EOM_1762_Freq", freq, "MHz", script_functions)
        time.sleep(0.2)
    setScan(pulse_program)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    #threshold = getShelvingThreshold2(ydata)
    fluor_bool = np.array(ydata) < threshold
    PD = np.mean(fluor_bool)

    plotPoint(comp_no, PD, 'PlotPD Repeated F1 Pump and Shelving2', plotStyle=0)
    plotPoint(comp_no, PD, 'PlotPD Repeated F1 Pump and Shelving2', plotStyle=1)
    return PD

def findPiTimeRough(pulse_program_findpi, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    
    setScan(pulse_program_findpi)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    timedata = data[0]
    ydata = data[1]
    min_index = np.argmin(ydata)
    pi_time = timedata[min_index]
    return pi_time
   
def findPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    pi_start, pi_stop, pi_step = scan
    setGlobalPulseTimeScan_Meas(pi_start, pi_step, pi_stop, script_functions)
    setScan(pulse_program_findpi)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

    Filepath = GetRawDataFolder()
    filename = "Pi_Pulse_Calibration_PulseTime_Scan_Raw"
    files0 = f'{Filepath}\\{filename}*'

    files0 = np.array(glob.glob(files0))
    data_indfirst = 4
    data_indlast = -20
    data = pd.read_csv(files0[-1], delimiter = "\[|\]|,|\"", engine='python',header=None).values
    data = data[:, data_indfirst:data_indlast+1]

    threshold = getShelvingThreshold(data)
    fluor_bool = data < threshold
    fluor_ave = np.mean(fluor_bool, 1)
    fluor_std = np.std(fluor_bool, 1)
    fluor_ave_max_index = np.argmax(fluor_ave)
    optimal_time = pi_start + pi_step*fluor_ave_max_index
    return optimal_time, max(fluor_ave)

def fitPiTime(scan, pulse_program_findpi, script_functions, GetRawDataFolder, getShelvingThreshold):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    pi_start, pi_stop, pi_step = scan
    #pi_stop = pi_start + pi_step*pi_steps
    setGlobalPulseTimeScan_Meas(pi_start, pi_step, pi_stop, script_functions)
    setScan(pulse_program_findpi)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    Filepath = GetRawDataFolder()
    filename = "Pi_Pulse_Calibration_PulseTime_Scan_Raw"
    files0 = f'{Filepath}\\{filename}*'

    files0 = np.array(glob.glob(files0))
    data_indfirst = 4
    data_indlast = -20
    data = pd.read_csv(files0[-1], delimiter = "\[|\]|,|\"", engine='python',header=None).values
    data = data[:, data_indfirst:data_indlast+1]

    threshold = getShelvingThreshold(data)
    fluor_bool = data < threshold
    fluor_ave = np.mean(fluor_bool, 1)
    #fluor_std = np.std(fluor_bool, 1)

    data_x = np.arange(pi_start, pi_stop+2*pi_step, pi_step)
    data_y = fluor_ave
    data_x = data_x[0:len(data_y)]

    def fit_PiPulse(x, pi_time, scale_time, amp, bg):
        rabi = math.pi/scale_time
        return amp*np.cos(rabi*(x-pi_time)/2)**2 + bg

    popt, pcov = curve_fit(fit_PiPulse, data_x, data_y, bounds=([pi_start, pi_start, 0, -10], [pi_stop, pi_stop, 100, 10]))
    xs = np.arange(pi_start, pi_stop, 0.1)
    ys = fit_PiPulse(xs, *popt)
    return popt, xs, ys

def inferOtherTransitions(f4m3_freq, f4m0_freq, which_f4m0=5):
    data_all = np.load('bf_freqdiffs_f4m3f4m0.npy', allow_pickle=True)
    data_all = abs(data_all)
    if f4m3_freq > 0: f4m3_freq *= -1
    if f4m0_freq > 0: f4m0_freq *= -1
    freq_diff = abs(f4m3_freq - f4m0_freq)
    compare_cache = abs(data_all[1,:] - freq_diff)
    index_closest = np.argmin(compare_cache)
    b_closest, value_closest = data_all[:,index_closest]
    
    slope_sign = np.sign(data_all[1,index_closest+1] - value_closest)
    slope_diff_sign = np.sign(freq_diff-value_closest)
    index_dir = int(slope_sign*slope_diff_sign)
    index_other = index_dir + index_closest
    b_other, value_other = data_all[:,index_other]
    
    highest_value, lowest_value = max([value_closest, value_other]),min([value_closest, value_other])
    highest_b, lowest_b = max([b_closest, b_other]),min([b_closest, b_other])
    actual_perc_diff = (highest_value - freq_diff)/(highest_value - lowest_value)
    b_match = lowest_b + (highest_b-lowest_b)*actual_perc_diff
    
    print(f'actual_value:{freq_diff}, lowest_value:{lowest_value}, highest_value:{highest_value}')
    print(f'lowest_b:{lowest_b}, highest_b{highest_b}')
    print(f'found b_match to be {b_match}')
    
    #b_match = data_all[0, index_closest]
    #f2m2, the highest energy state is starting state - index 6
    lower_state = 6
    #First 14 entries are possible to transfer to from initial state
    #upper_states = np.arange(0, 14)
    S12_EnergyLevel = HFStructure_State('ba137', L=0, J=1/2)
    D52_EnergyLevel = HFStructure_State('ba137', L=2, J=5/2)
    S12D52_Transition = Transition_Laser(S12_EnergyLevel, D52_EnergyLevel, lower_state=lower_state)
    freqs = S12D52_Transition.get_energies_specific(b_field=b_match)
    offset = freqs[5] - f4m0_freq
    freqs -= offset
    freqs = abs(freqs)
    return b_match, freqs