#D52_25_level_Calibrated_SPAM.py created 2024-05-28 16:24:43.974455

import time
import matlab.engine

import sys
import os
import datetime
import glob
import numpy as np
    
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

init_kets_total = np.arange(0,25)

#f_offset = 545.349146
#f_upper = 623.156494

pitime_n2 = 21.246 # [-2, 4, -4]
pitime_n1 = 37.496 # [-2, 3, -3]
pitime_0 = 45.354 # [2, 4, 2]
pitime_p1 = 34.746 # [2, 4, 3]
pitime_p2 = 43.903 # [2, 4, 4]

def get_calibration_reference():
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(1)


    pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
    
    threshold = 12

    F1PumpTime = 0.5 #us
    F1PumpReps = 20
    InitReps = 0
    fs = 4e9

    Side_band_cooling_reps = 0

    SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
    if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
        setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

    f_offset_index = [0,2,0]
    f_upper_index = [-1,4,-3]
    scan_indeces =[[-2,3,-1],[-1,3,0],[1,4,2],[1,3,2],[2,4,0],[1,4,0],[-1,3,-2],[-2,2,0], \
                 [-1,2,0],[1,2,2],[1,4,-1],[0,2,2],[-1,4,-2],[-2,4,-4],[0,4,-2], \
                 [0,4,-1],[0,4,0],[0,4,1],[2,4,2],[2,4,3],[2,4,4],[-2,3,-3],[-2,3,-2], \
                 [-1,3,-1],[0,3,0],[0,3,1],[0,3,2],[1,3,3],[-2,2,-2],[-2,2,-1],[2,2,1], \
                 [2,2,2],[-1,1,-1],[-2,1,0],[1,1,1],[-1,1,1]]

    #random.shuffle(scan_indeces)

    pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]


    [f_offset,f_upper] = Get_1762_Latest_EOM_Freqs([f_offset_index,f_upper_index])

    [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = Get_1762_Latest_PiTimes(pitime_ref_index)

    init_n2_index = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]]
    init_n1_index = [[-2,3,-1],[0,3,0],[1,4,2],[2,4,3]]
    init_0_index = [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]]
    init_p1_index = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]]
    init_p2_index = [[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]

    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")

    init_freqs_n2 = list(Get_1762_EOM_Freqs(init_n2_index,f_offset,f_upper))
    init_freqs_n1 = list(Get_1762_EOM_Freqs(init_n1_index,f_offset,f_upper))
    init_freqs_0 = list(Get_1762_EOM_Freqs(init_0_index,f_offset,f_upper))
    init_freqs_p1 = list(Get_1762_EOM_Freqs(init_p1_index,f_offset,f_upper))
    init_freqs_p2 = list(Get_1762_EOM_Freqs(init_p2_index,f_offset,f_upper))

    init_times_n2 = list(Get_1762_PiTimes(init_n2_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_times_n1 = list(Get_1762_PiTimes(init_n1_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_times_0 = list(Get_1762_PiTimes(init_0_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_times_p1 = list(Get_1762_PiTimes(init_p1_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_times_p2 = list(Get_1762_PiTimes(init_p2_index,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

    init_freqs_array = [init_freqs_n2,init_freqs_n1,init_freqs_0,init_freqs_p1,init_freqs_p2]
    init_times_array = [init_times_n2,init_times_n1,init_times_0,init_times_p1,init_times_p2]

    output_file_freqs = fr'Z:\Lab Data\D52_Calibration_Ba137\New_initialized_calibration_freq_files\New_initialized_calibration_freq_files_{dt_string}.txt'


    F1_pumpTime = getGlobal('F1_PumpTime')
    if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"%0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us")

    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

    SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
    if not "%s"%SB_cooling_reps == 0:
        setGlobal("Sideband_Cooling_Reps", 0, "")

    freq_list_fitted_reference = []

    def findResonance_withfit_plotPD(init_state, pi_pulse_time, start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        set_freq = start_freq
        createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
        flour_exp = []
        fluor_ave = []
        freq_list = []

        dummy_counter = 0
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 0", nargout=0)
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        matlab_init_freqs = matlab.double(init_freqs_array[int(init_state+2)])
        matlab_init_times = matlab.double(init_times_array[int(init_state+2)])

        matlab_probe_pulse_time = matlab.double([pi_pulse_time])
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])

        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
        eng.Pulse_upload_dummy(fs,3,nargout = 0) # Dummy 3rd sequence

        while set_freq <= stop_freq:
            if scriptIsStopped():
                eng.quit()
                break
            #if dummy_counter >0:
                #eng.SendAWGCommand("SOUR:SEQ:DEL:2",nargout = 0)
            #eng.SendAWGCommand("TRAC:DEL 2",nargout = 0)        
            matlab_set_freq = matlab.double([set_freq])
            eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,power_factor_dbm,nargout = 0)

            eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)
            eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
            time.sleep(0.5)

            eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)

            eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

            eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

            eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
            dummy_counter = dummy_counter + 1
            if scriptIsStopped():
                eng.quit()
                break

            setScan(pulse_program)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count']
            ydata = data[1]
            #threshold = getShelvingThreshold2(ydata)
            fluor_bool = np.array(ydata) < threshold
            
            #def upload_error(pd_last,pd_current):
            #    if abs(pd_last-pd_current)>0.8:
            #        return True
            #    else:
            #        return False
            
            # check for decrystalisation
            #def DC_check(data):
            #    count = 0
            #    for value in data:
            #        if value:
            #            count += 1
            #            if count >= 100:
            #                return True
            #        else:
            #            count = 0
            #    return False

            PD = np.mean(fluor_bool)
            flour_exp.append(ydata)

            fluor_ave.append(PD)
            freq_list.append(set_freq)
            plotPoint(set_freq, PD, '1762 nm freq scan', plotStyle=0)
            set_freq = np.round(set_freq + freq_step, 4)


        closeTrace('1762 nm freq scan')
        #print(fluor_ave)
        #print(getShelvingThreshold2(ydata))

        def sin_squared(f, f0, A, Omega, t):
                delta = f - f0
                return A * (Omega**2 /
                            (Omega**2 + delta**2)) * (np.sin(
                                np.sqrt(Omega**2 +
                                        delta**2) * t / 2))**2

        # best way to find centre freq when pi-time is uncertain
        f0_guess = np.sum(np.multiply(freq_list, fluor_ave)) / np.sum(fluor_ave)
        # need to check if this will be a good f0_guess
        # it won't be if we are too frequency uncertain
        f_range = freq_list[-1] - freq_list[0]
        top_30_percent = freq_list[-1] - f_range / 3
        bot_30_percent = freq_list[0] + f_range / 3
        if f0_guess > top_30_percent or f0_guess < bot_30_percent:
            f0_guess = freq_list[np.argmax(fluor_ave)]

        # Omega_guess = 0.1 * ((freq_list[-1] - freq_list[0]))  # in MHz
        f_variance = (freq_list - f0_guess)**2
        Omega_guess = np.sqrt(
            np.sum(np.multiply(f_variance, fluor_ave)) / np.sum(fluor_ave) / 4)

        A_guess = max(fluor_ave)
        t_guess = np.pi / Omega_guess
        p0 = np.array([f0_guess, A_guess, Omega_guess, t_guess])
        
        # Fit the data to the Rabi fringe function with initial guesses
        popt, pcov = curve_fit(sin_squared,freq_list,fluor_ave,p0=p0,maxfev=10000)

        # check that the fit succeeded - if not change pulse time guess
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
        #Sving Raw data for the plots
        freq_string = str(round(freq_res,4)).replace('.','p')
        combined_data = zip(freq_list,fluor_ave)
        filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_raw_data\\New_D52_calibration_raw_data_freq_{freq_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{uncertainty}")
        #Saving Raw data of each Experiment
        combined_data = zip(freq_list,flour_exp)
        filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_each_exp_raw_data\\New_D52_calibration_each_exp_raw_data_freq_{freq_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{uncertainty}")
        return freq_res

    def findPiTime_withfit_plotPD(freq_peak, stop_time, time_step, threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
        pulse_time = 0
        fluor_ave = []
        pulse_time_list = []
        flour_exp = []
        while pulse_time <= stop_time:
            if scriptIsStopped():
                break
            PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
            if not "%s"%PulseTime_Dummy == "%s us"%pulse_time:
                setGlobal("Shelving_Pulse_Time", pulse_time, "us")
            time.sleep(1)

            setScan(pulse_program)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count']
            ydata = data[1]
            fluor_bool = np.array(ydata) < threshold
            PD = np.mean(fluor_bool)
            flour_exp.append(fluor_bool)

            fluor_ave.append(PD)
            pulse_time_list.append(pulse_time)

            plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)

            pulse_time = pulse_time + time_step
            
        closeTrace('1762 nm pi-time scan')

        def oscfunc(t, A, w, p, c, d):
            return A * np.cos(w * t + p) * np.exp(-t / d) + c

        def fit_oscillation(tt, yy):
            '''Fit sin to the input time sequence, and return fitting parameters:
            "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc".

            Option to take on guesses and bounds for the fit too.'''
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
        #pulse_time_list_new = pulse_time_list[pulse_time_list <= int(period)]
        #fluor_ave_new = fluor_ave[:len(pulse_time_list_new)]
        #pulse_time_list_new = pulse_time_list
        #fluor_ave_new = fluor_ave

        #print(pulse_time_list_new)
        #print(fluor_ave_new)
        #print(len(pulse_time_list_new))
        #print(len(fluor_ave_new))
        #omega, uncertainty = fit_oscillation(pulse_time_list_new,fluor_ave_new)
        #print("second omega is", omega)
        final_pi_time = np.pi/omega
        print("pi time is", final_pi_time)

        #Saving Raw data for the plots
        freq_string = str(round(freq_peak,4)).replace('.','p')
        combined_data = zip(pulse_time_list,fluor_ave)
        filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_raw_data\\New_D52_calibration_raw_data_pitime_{freq_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            #file.write(f"{uncertainty}")
        #Saving Raw data of each Experiment
            combined_data = zip(pulse_time_list,flour_exp)
        filename = f'Z:\Lab Data\D52_Calibration_Ba137\\New_initialized_calibration_freq_each_exp_raw_data\\New_D52_calibration_each_exp_raw_data_{freq_string}_pitime_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{uncertainty}")

        return final_pi_time

    with open(output_file_freqs,'w'):
        pass


    full_scan_indeces = [[f_offset_index] + [f_upper_index]]

    for scan_chunk in full_scan_indeces:
        dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        for scan_index in scan_chunk:
            [centre_freq] = Get_1762_EOM_Freqs([scan_index],f_offset,f_upper)
            [pi_time] = Get_1762_PiTimes([scan_index],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
            init_state = scan_index[0]
            centre_freq = np.round(centre_freq,6)
            
            if np.isnan(pi_time):
                pi_time = 100

            if pi_time < 50:
                freq_step = 0.006 # MHz
                freq_range_factor = 9 # kHz
            elif 50 <= pi_time < 110:
                freq_step = 0.0025 # MHz
                freq_range_factor = 9 # kHz
            elif 110 <= pi_time < 200:
                freq_step = 0.001 # MHz
                freq_range_factor = 10 # kHz            
            elif pi_time >= 200:
                freq_step = 0.0005 # MHz
                freq_range_factor = 10 # kHz       

            #pi_time = 3000
            PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
            if not "%s"%PulseTime_Dummy == "%s us"%pi_time:
                setGlobal("Shelving_Pulse_Time", pi_time, "us")

            #pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
            #pulse_program = "Shelving_InitScheme_NoShutter_Scan"

            true_freq_range = freq_range_factor*freq_step
            freq_start = centre_freq-true_freq_range
            freq_stop = centre_freq+true_freq_range+freq_step

            setEvaluation('Eval3')

            freq_peak = findResonance_withfit_plotPD(init_state, pi_time, freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program, script_functions)
            freq_list_fitted_reference.append(freq_peak)
            #if abs(freq_peak - f_offset) < 0.05:
            #    f_offset=freq_peak
            #if abs(freq_peak - f_upper) < 0.05:
            #    f_upper = freq_peak

            setEvaluation('Eval2')

            with open(output_file_freqs,'a') as outfile:
                outfile.write(f'{np.round(freq_peak,6)}, {np.round(pi_time,3)}, {int(init_state)}\n')

            eng.quit()
            eng = matlab.engine.start_matlab()
            eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
            eng.SendAWGCommand("RES", nargout=0)
    
    return freq_list_fitted_reference
    

def SPAM_runs(init_kets, f_offset, f_upper):
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)

    D = 25
    init_kets = init_kets
    #init_kets = [23]
    #init_kets = list(np.flip(range(0,25)))
    #init_kets = ra4]nge(0,25)
    SetPulseTime = 500
    threshold = 12

    F1PumpTime = 0.5 #us
    F1PumpReps = 60
    InitReps = 0

    fs = 4e9
    #fs = 3.267264e9
    #fs = 6.2078016e9

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

    init_freqs = []
    pulse_times = []
    #init_trans = [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 4, 2], [2, 4, 3], [1, 3, 2], [2, 4, 0], [1, 4, 0], [0, 3, 0], [-1, 3, -2]]
    for i in list_of_inits:
        init_freqs.append(list(Get_1762_EOM_Freqs(i,f_offset,f_upper)))
        pulse_times.append(list(Get_1762_PiTimes(i,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)))

    SPAM_list_trans = [[-2, 4, -4], #ket 1
                        [-1, 4, -3], #ket 2
                        [0, 4, -2], #ket 3
                        [1, 4, -1], #ket 4
                        [0, 4, 0], #ket 5
                        [0, 4, 1], #ket 6
                        [2, 4, 2], #ket 7
                        [2, 4, 3], #ket 8
                        [2, 4, 4], #ket 9
                        [-2, 3, -3], #ket 10
                        [-2, 3, -2], #ket 11
                        [-1, 3, -1], #ket 12       
                        [0, 3, 0], #ket 13
                        [0, 3, 1], #ket 14
                        [0, 3, 2], #ket 15
                        [1, 3, 3], #ket 16
                        [-2, 2, -2], #ket 17
                        [-2, 2, -1],#ket 18
                        [0, 2, 0], #ket 19                 
                        [2, 2, 1], #ket 20
                        [2, 2, 2], #ket 21
                        [-1, 1, -1], #ket 22
                        [-2, 1, 0], #ket 23
                        [1, 1, 1]] #ket 24


    probe_freq = [0] + list(Get_1762_EOM_Freqs(SPAM_list_trans,f_offset,f_upper))
    pulse_time = [10] + list(Get_1762_PiTimes(SPAM_list_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    SPAM_list_trans = [[2, 4, -4]] + SPAM_list_trans
    combined_data = zip(probe_freq,pulse_time,SPAM_list_trans)

    SPAM_list = []

    for i,j,k in combined_data:
        SPAM_list.append([i,j,k[0]])
    print(SPAM_list)

    print(SPAM_list)
    init_freqs_array = [
    init_freqs[0],
    init_freqs[1],
    init_freqs[2],
    init_freqs[3],
    init_freqs[4]
    ]

    init_times_array = [
    pulse_times[0],
    pulse_times[1],
    pulse_times[2],
    pulse_times[3],
    pulse_times[4]
    ]
    print(init_freqs_array,init_times_array)
    
    SPAM_list.sort(key=lambda x: float(x[1]), reverse=False)


    filename = f'Z:\Lab Data\\25lvl_SPAM\\SPAM_frequencies_raw_data\SPAM_measurement_Order_{dt_string}.txt'

    SPAM_list = SPAM_list[:D]

    for i,ket in enumerate(SPAM_list):
        with open(filename,'a') as file:
            file.write(f"{ket[0]}, {ket[1]}, {ket[2]}\n")

    init_freqs = []
    pulse_times = []
    #init_trans = [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 4, 2], [2, 4, 3], [1, 3, 2], [2, 4, 0], [1, 4, 0], [0, 3, 0], [-1, 3, -2]]
    for i in list_of_inits:
        init_freqs.append(list(Get_1762_EOM_Freqs(i,f_offset,f_upper)))
        pulse_times.append(list(Get_1762_PiTimes(i,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)))

    init_freqs_array = [
    init_freqs[0],
    init_freqs[1],
    init_freqs[2],
    init_freqs[3],
    init_freqs[4]
    ]

    init_times_array = [
    pulse_times[0],
    pulse_times[1],
    pulse_times[2],
    pulse_times[3],
    pulse_times[4]
    ]

    PulseTime = getGlobal("Shelving_Pulse_Time")
    if not "%s"%PulseTime == "%s us"%SetPulseTime:
        setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

    F1_pumpTime = getGlobal('F1_PumpTime')
    if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"%0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us")

    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

    for i,ket in enumerate(SPAM_list):
        pulse_time = ket[1]
        str_ket = f'ket_{i}'
        PulseTime = getGlobal(str_ket)
        if not "%s"%PulseTime == pulse_time:
            setGlobal(str_ket, pulse_time, "us")

    print('ran')

    os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
    os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

    freq_list_fitted = []

    def Set_AWG_for_SPAM(init_ket, dt_string , pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        #set_freq = start_freq
        #createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
        rep = 0
        number_of_reps = 1
        while rep < number_of_reps:
            if scriptIsStopped():
                eng.quit()
                break
            

            eng.SendAWGCommand("RES", nargout=0)
            time.sleep(10)
            eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
            eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
            eng.SendAWGCommand("INIT:CONT 0", nargout=0)
            eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
            eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

            eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
            time.sleep(0.1)
            eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

            eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
            eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
            zero_freq = [0]
            print('ran 2')
            if scriptIsStopped():
                eng.quit()
                break

            init_state = SPAM_list[init_ket][2]
            set_prep_freq = np.round(SPAM_list[init_ket][0],3)
            set_prep_pulse_time = np.round(SPAM_list[init_ket][1],3)
            
            matlab_init_freqs = matlab.double(init_freqs_array[int(init_state+2)])
            matlab_init_times = matlab.double(init_times_array[int(init_state+2)])
                    
            matlab_set_prep_freq = matlab.double([set_prep_freq])
            matlab_set_prep_pulse_time = matlab.double([set_prep_pulse_time])
            
        
            power_factor = matlab.double([1])
            power_factor_dbm = matlab.double([1])
            seg_num = 1
            eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
            print('ran 2')
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)
            if scriptIsStopped():
                eng.quit()
                break

            seg_num = seg_num+1
            eng.Pulse_upload(matlab_set_prep_freq,matlab_set_prep_pulse_time,fs,seg_num,power_factor_dbm,nargout = 0)
            print(set_prep_freq, set_prep_pulse_time)
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)

            if scriptIsStopped():
                eng.quit()
                break

            for i,ket in enumerate(SPAM_list):
                if scriptIsStopped():
                    eng.quit()
                    break
                
                set_probe_freq = np.round(ket[0],3)
                set_probe_time = np.round(ket[1],3)
                seg_num = seg_num + 1
                print(seg_num)
                if set_probe_time == 0:
                    power_factor_dbm = matlab.double([0])
                matlab_set_probe_freq = matlab.double([set_probe_freq])
                matlab_probe_pulse_time = matlab.double([set_probe_time])
                eng.Pulse_upload(matlab_set_probe_freq,matlab_probe_pulse_time,fs,seg_num,power_factor_dbm,nargout = 0)
                print(set_probe_freq, set_probe_time)
                power_factor_dbm = matlab.double([1])
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)


            eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
            seg_num = 4
            table_length = len(SPAM_list) 
            for i in range(table_length):
                if scriptIsStopped():
                    eng.quit()
                    break
                seg_num = seg_num + 1
                string = f"SOUR:SEQ:DEF {seg_num},{seg_num},1,0"
                eng.SendAWGCommand(string, nargout=0)
                seg_num = seg_num + 1
                string = f"SOUR:SEQ:DEF {seg_num},{seg_num},1,1"
                eng.SendAWGCommand(string, nargout=0)
            print(seg_num)

            Table_length_dummy =  getGlobal('Table_length')
            if not "%s"%Table_length_dummy == seg_num:
                setGlobal("Table_length", seg_num, "")


            eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

            eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

            eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
                    
            if scriptIsStopped():
                eng.quit()
                break

            setScan(pulse_program)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count']
            ydata = data[1]



            rep = rep + 1
        

    pulse_program = "D52_25level_SPAM_pulses"
    for init_ket in init_kets:
        #os.system(f'ssh pi@192.168.168.24 python press_hard_switch.py')
        #time.sleep(20)
        #os.system(f'ssh pi@192.168.168.24 python press_button.py')
        #time.sleep(180)
        Set_AWG_for_SPAM(init_ket, dt_string , pulse_program, script_functions)
    eng.quit()
    
    
    
    
    
    
# now we interweave these two meta-functions to take calibration while taking SPAM

chunk_size = 5
chunked_init_kets = np.split(init_kets_total, len(init_kets_total) // chunk_size)

for init_kets in chunked_init_kets:
    os.system(f'ssh pi@192.168.168.24 python press_hard_switch.py')
    time.sleep(15)
    os.system(f'ssh pi@192.168.168.24 python press_button.py')
    time.sleep(60)
    freq_list_fitted_reference = get_calibration_reference()
    if scriptIsStopped():
        break
    f_offset = freq_list_fitted_reference[0]
    f_upper = freq_list_fitted_reference[1]

    SPAM_runs(list(init_kets), f_offset, f_upper)