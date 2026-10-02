#Functions_Calibration.py created 2024-07-24 10:23:36.942221

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

import time
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *


def run_calibration(script_functions,do_pi_time_calibration=False,low_power=False,f_offset_input=None,f_upper_input=None,ref_pitimes=None):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

    import time
    import matlab.engine
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(1)

    import os
    import datetime
    import glob
    import numpy as np
    import random
        
    from scipy.optimize import curve_fit
    
    


    line_trigger = True
    pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"

    threshold = 8
    F1PumpTime = 0.5 #us
    F1PumpReps = 20
    InitReps = 0
    fs = 4e9
    Side_band_cooling_reps = 0
    low_power_factor = 1500

    SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
    if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
        setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

    f_offset_index = [0,2,0]
    f_upper_index = [-1,4,-3]
    pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]

    if f_offset_input and f_upper_input:
        [f_offset,f_upper] = [f_offset_input,f_upper_input]
    else:
        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))
        print('getting ion control info',f_upper,f_offset)

    if ref_pitimes:
        [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = ref_pitimes
    else:
        [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = Get_1762_Latest_PiTimes(pitime_ref_index)

    print('offset and upper freqs', f_offset,f_upper)
    print('pitimes',[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2])

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

    output_file_freqs = fr'Z:\Lab Data\D52_Calibration_Ba137\New_initialized_calibration_freq_files\New_initialized_calibration_freq_files_{dt_string}.txt'

    if do_pi_time_calibration:
        full_scan_indices =  [[f_offset_index] + [f_upper_index] + pitime_ref_index]
    elif not do_pi_time_calibration:
        full_scan_indices =  [[f_offset_index]+[f_upper_index]]


    LT_dummy = getGlobal('LineTriggerBoolean')
    if not "%s"%LT_dummy == int(line_trigger):
        setGlobal("LineTriggerBoolean", int(line_trigger), "")

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

    freq_list_fitted = []
    pitime_list_fitted = []

    def findResonance_withfit_plotPD(init_state, pi_pulse_time, start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
        set_freq = start_freq
        createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
        flour_exp = []
        fluor_ave = []
        freq_list = []

        dummy_counter = 0
        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(1)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 0", nargout=0)
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
        print(set_freq,pi_pulse_time)

        print(init_freqs_array[int(init_state+2)],init_times_array[int(init_state+2)])
        matlab_init_freqs = matlab.double(init_freqs_array[int(init_state+2)])
        matlab_init_times = matlab.double(init_times_array[int(init_state+2)])
        power_factor = matlab.double([1])

        if low_power:
            matlab_probe_pulse_time = matlab.double([0.6*low_power_factor])
            power_factor_dbm = matlab.double([pi_pulse_time/low_power_factor])
        else:
            matlab_probe_pulse_time = matlab.double([pi_pulse_time])
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
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
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

    for scan_chunk in full_scan_indices:
        dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        for scan_index in scan_chunk:
            [centre_freq] = Get_1762_EOM_Freqs_an1an2([scan_index],f_offset,f_upper)
            [pi_time] = Get_1762_PiTimes([scan_index],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
            init_state = scan_index[0]
            centre_freq = np.round(centre_freq,6)
            print(centre_freq)
            if np.isnan(pi_time):
                pi_time = 100

            if low_power:
                freq_step = 0.001 # MHz
                freq_range_factor = 10 # kHz

            else:
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

            if low_power:
                long_pi_time = 0.8*low_power_factor
                PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
                if not "%s"%PulseTime_Dummy == "%s us"%long_pi_time:
                    setGlobal("Shelving_Pulse_Time", long_pi_time, "us")
            else:
                PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
                if not "%s"%PulseTime_Dummy == "%s us"%pi_time:
                    setGlobal("Shelving_Pulse_Time", pi_time, "us")

            true_freq_range = freq_range_factor*freq_step
            freq_start = centre_freq-true_freq_range
            freq_stop = centre_freq+true_freq_range+freq_step

            setEvaluation('Eval3')

            freq_peak = findResonance_withfit_plotPD(init_state, pi_time, freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program, script_functions)
            freq_list_fitted.append(freq_peak)
            #if abs(freq_peak - f_offset) < 0.05:
            #    f_offset=freq_peak
            #if abs(freq_peak - f_upper) < 0.05:
            #    f_upper = freq_peak

            #setEvaluation('Eval2')

            if do_pi_time_calibration:

                # time step and stop time for pi time calibration
                stop_time = 3*pi_time
                time_step = pi_time/8

                eng.SendAWGCommand("RES", nargout=0)
                time.sleep(2)
                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
                
                eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

                eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
                time.sleep(0.1)
                eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

                power_factor = matlab.double([1])
                power_factor_dbm = matlab.double([1])

                matlab_init_freqs = matlab.double(init_freqs_array[int(init_state+2)])
                matlab_init_times = matlab.double(init_times_array[int(init_state+2)])

                freq_peak_for_pi = float(freq_peak)
                matlab_set_freq = matlab.double([freq_peak_for_pi])
                matlab_probe_pulse_time = matlab.double([1500])

                eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)

                eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,power_factor_dbm,nargout = 0)

                eng.Pulse_upload_dummy(fs,3,nargout = 0) # Dummy 3rd sequence


                eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)

                eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

                eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
                eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
                eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

                setEvaluation('Eval3')

                pi_time = findPiTime_withfit_plotPD(freq_peak, stop_time, time_step, threshold, pulse_program, script_functions)
                pitime_list_fitted.append(pi_time)

                #setEvaluation('Eval2')

            with open(output_file_freqs,'a') as outfile:
                outfile.write(f'{np.round(freq_peak,6)}, {np.round(pi_time,3)}, {int(init_state)}\n')

            eng.quit()
            eng = matlab.engine.start_matlab()
            eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
            eng.SendAWGCommand("RES", nargout=0)

    eng.quit()

    # just return the two frequencies and 5 pi-times needed out of this function
    # the other frequencies and pi-times will still be saved in the calibration folder as usual

    f_offset_dummy = getGlobal('f_offset')
    if not "%s"%f_offset_dummy == freq_list_fitted[0]:
        setGlobal("f_offset", freq_list_fitted[0], "")
        
    f_upper_dummy = getGlobal('f_upper')
    if not "%s"%f_upper_dummy == freq_list_fitted[1]:
        setGlobal("f_upper", freq_list_fitted[1], "")

    pitime_n2_dummy = getGlobal('pitime_n2')
    if not "%s"%pitime_n2_dummy == pitime_list_fitted[2]:
        setGlobal("pitime_n2", pitime_list_fitted[2], "")

    pitime_n1_dummy = getGlobal('pitime_n1')
    if not "%s"%pitime_n1_dummy == pitime_list_fitted[3]:
        setGlobal("pitime_n1", pitime_list_fitted[3], "")

    pitime_0_dummy = getGlobal('pitime_0')
    if not "%s"%pitime_0_dummy == pitime_list_fitted[4]:
        setGlobal("pitime_0", pitime_list_fitted[4], "")

    pitime_p1_dummy = getGlobal('pitime_p1')
    if not "%s"%pitime_p1_dummy == pitime_list_fitted[5]:
        setGlobal("pitime_p1", pitime_list_fitted[5], "")

    pitime_p2_dummy = getGlobal('pitime_p2')
    if not "%s"%pitime_p2_dummy == pitime_list_fitted[6]:
        setGlobal("pitime_p2", pitime_list_fitted[6], "")

    if do_pi_time_calibration:
        pass
        return np.round(freq_list_fitted[:2],6), np.round(pitime_list_fitted[2:],3)
    elif not do_pi_time_calibration:
        pitime_list_fitted = ref_pitimes

        return np.round(freq_list_fitted[:2],6), np.round(pitime_list_fitted,3)


#Function to get Coherence time of a transition. 
def get_T2_time(transitions):
    print(transitions)
    filename_T2 = 'Z:\Lab Data\D52_Calibration_Ba137\Post_processing_PJ\Figures\Linear_Regression\coherence_times.txt'
    matrix = np.genfromtxt(filename_T2, delimiter='\t', dtype=float)
    pi_times_list = []
    for transition in transitions:
        print(transition)
        row_label = [transition[1],transition[2]]

        Fs = [1,2,3,4]
        states = []
        for i in Fs:
            for j in range(2*i+1):
                mF = i-j
                states.append([i,mF])
        row_labels = states
        col_labels = [-2, -1, 0, 1, 2]

        col_label = transition[0]
        row_index = next((i for i, label in enumerate(row_labels) if label == row_label), None)
        col_index = col_labels.index(col_label)
        if row_index is not None and col_index in range(len(col_labels)):
            pi_times_list.append(matrix[row_index, col_index])
        else:
            pi_times_list.append(np.nan)
    return pi_times_list



def run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None,diff_pass=0.3,check_3pt_coherence=False):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

    import matlab.engine
    import time
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(1)

    import numpy as np
    from scipy.linalg import expm
    from scipy.optimize import minimize

    import sys

    import os
    import datetime
    import glob
    import json
    import numpy as np
    import random
    from scipy.optimize import curve_fit
    sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")
    pattern = "Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_ion_control_raw_data\\fast_calibration_*"
    
    Side_band_cooling_reps = 0
    real_wait_time_bool = True
    f_offset_index = [0,2,0]
    f_upper_index = [-1,4,-3]
    pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]

    if f_offset_input and f_upper_input:
        [f_offset,f_upper] = [f_offset_input,f_upper_input]
    else:
        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))
        print('getting ion control info',f_upper,f_offset)

    if ref_pitimes:
        [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = ref_pitimes
    else:
        pitime_n2 = float(getGlobal('pitime_n2'))
        pitime_n1 = float(getGlobal('pitime_n1'))
        pitime_0 = float(getGlobal('pitime_0'))
        pitime_p1 = float(getGlobal('pitime_p1'))
        pitime_p2 = float(getGlobal('pitime_p2'))
        
    F1PumpTime = 0.5 #us
    F1PumpReps = 50
    InitReps = 0
    fs = 4e9
    threshold = 9
    
    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    probe_transitions = [[target_transition]]
    for probe_trans in probe_transitions:

        
        s12_level = probe_trans[0][0]
        
        periodicity = 100 #us

        if check_3pt_coherence:
        
            wait_times = [periodicity/4,periodicity/2,periodicity*3/4]
            # Phase Calculations ===================================================================

            phases = [np.pi/2, np.pi, 3*np.pi/2]
        else:
            wait_times = [periodicity/4,periodicity*3/4]
            # Phase Calculations ===================================================================

            phases = [np.pi/2, 3*np.pi/2]

        #=======================================================================================

        init_trans = list_of_inits[s12_level+2]
        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        init_pulse_time = sum(init_times_array) 
        
        set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        set_freq = [set_freq[0] + delta]

        freq_og = set_freq[0]

        print('set freq', set_freq)

        f_target_dummy = getGlobal('f_target')
        if not "%s"%f_target_dummy == set_freq[0]:
            setGlobal("f_target", set_freq[0], "")
               

        T2_time = get_T2_time(probe_trans)[0]
      
        pi_times= list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        times = []
        for i in range(len(pi_times)):
            times.append(2*pi_times[i]*np.arcsin(np.sqrt(1/(len(pi_times)+1-i)))/np.pi)
        
        
        print(times)
        full_freqs = set_freq + [0] + list(np.flip(set_freq))
        print(full_freqs)
        
        LT_dummy = getGlobal('LineTriggerBoolean')
        if not "%s"%LT_dummy == 1:
            setGlobal("LineTriggerBoolean", 1, "")

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

        Hareld_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Hareld_pulse_time_dummy == pi_times[0]:
                setGlobal("Hareld_pulse_time", pi_times[0], "us")
        

        pulse_program = "Qudit_ramsey_experiment_fast_calibration"
        
        
                
        def perform_fast_Ramsey_cal(f_offset,f_upper,real_wait_time, threshold, pulse_program, script_functions):
            getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
            createTrace('Fast Calibration Points', 'Script Data', xLabel=f'Pulse Time (us)')
            wait_time_num = 0
            fluor_ave = []
            pulse_time_list = []
            file_names_list = []
            
            if check_3pt_coherence:
                ramsey_points=3
            else:
                ramsey_points=2
                
            while wait_time_num<ramsey_points:
                if scriptIsStopped():
                    break
                
                set_freq = float(getGlobal('f_target'))
                print('set freq', set_freq)

                full_freqs = [float(set_freq),0,float(set_freq)]
       
                print('1')
        
        #Pulse Times ==============================================================
                T_wait = real_wait_time
                full_times = list(times) + [T_wait] + list(np.flip(times))
        #Phases =================================================================
                full_phases = [0,0,phases[wait_time_num]]
        #==============================================================
                Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
                if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(full_times):
                    setGlobal("Ramsey_Wait_Time", sum(full_times), "us")
        
                half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
                if not "%s"%half_pi_time_dummy == "%s us"%sum(full_times):
                    setGlobal("Shelving_Pulse_Time", sum(full_times), "us")
                print('2')

        # AWG commands======================================================================================
                eng.SendAWGCommand("RES", nargout=0)
                time.sleep(5)
                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
                eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
                eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)
        
                eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
                time.sleep(0.1)
                eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
        
                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        
                print('3')
        #----------------------------------------------------------------------------
                matlab_init_freqs = matlab.double(init_freqs_array)
                matlab_init_times = matlab.double(init_times_array)
        #----------------------------------------------------------------------------
                print(full_freqs)
                print(full_times)
                matlab_set_freq = matlab.double(full_freqs)
        #----------------------------------------------------------------------------		
                matlab_herald_pulse_time = matlab.double(pi_times)
                matlab_herald_freq = matlab.double([set_freq])
                matlab_herald_phase = matlab.double([0])
        #----------------------------------------------------------------------------		
                matlab_probe_pulse_time = matlab.double(full_times)
                matlab_probe_phases = matlab.double(full_phases)
        #----------------------------------------------------------------------------
                power_factor = matlab.double([1])
                power_factor_dbm = matlab.double([1])
                print('4.5')
                seg_num = 1
                eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                print('5')
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
		#----------------------------------------------------------------------------
		# Heralding
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_herald_freq,matlab_herald_pulse_time,matlab_herald_phase,fs,seg_num,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
		#----------------------------------------------------------------------------
		# Ramsey
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_set_freq,matlab_probe_pulse_time,matlab_probe_phases,fs,seg_num,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
                print('6')

        
        #-------------------------------------------------------------------------------------------------------------------------
                print('7')
        
                eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)
                seq_num = 6
        
        
                Table_length_dummy =  getGlobal('Table_length')
                if not "%s"%Table_length_dummy == seq_num:
                    setGlobal("Table_length", seq_num, "")
        
                eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        
                eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
        
                eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
        
        
                #total_time = sum([piover2_time,pulse_time,piover2_time])+30
                #PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
                #if not "%s"%PulseTime_Dummy == "%s us"%total_time:
                #    setGlobal("Shelving_Pulse_Time", total_time, "us")
                #time.sleep(0.2)
        
                setScan(pulse_program)
                startScan(globalOverrides=list(), wait=True)
                stopScan()

                #new way of getting the right PMT counts for thresholding/heralding and plotting
                data = getAllData()
                herald_data = data['PMT Index 0'][1]
                print(herald_data)
                ket1_data = data['PMT Index 1'][1]
                print(ket1_data)


                arrays = []
                for idx,herald_outcome in enumerate(herald_data):
                    if herald_outcome < threshold:
                        arrays.append(ket1_data[idx])
                mean_value = np.mean(np.array(arrays)<threshold)
        
                #matching_files = glob.glob(pattern)
                #matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
                #file_path = matching_files[-1]
                #chunks = file_path.split('\\')
                #print(chunks[-1])        
                #fname = chunks[-1]
                #file_names_list.append(fname)
                #print("=========================================")
        
                #arrays = []
                #with open(file_path, 'r') as file:
                #    print(file_path)
                #    for line in file:
                #        data = json.loads(line)
                #        if data[0]["0"][0] < threshold:
                #            arrays.append(data[0]["0"][1])
                #mean_value = np.mean(np.array(arrays)<threshold)
                #print("=========================================")
        
                if np.isnan(mean_value):
                    mean_value = 1
                PD = mean_value
                print("PD is", PD)
                fluor_ave.append(PD)
                wait_time_ramsey = wait_times[wait_time_num]
                pulse_time_list.append(wait_times[wait_time_num])
        
                wait_time_num = wait_time_num + 1

                plotPoint(wait_time_ramsey, PD,'Fast Calibration Points', plotStyle=2)
                
            closeTrace('Fast Calibration Points')

            def unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, t_wait_T):
                omega = np.pi / (pi_time * 1e-6)
                t_pi_over_2 = (pi_time * 1e-6) / 2
                T = T*1e-6
                T_wait_s = T_wait*1e-6
                def U1(omega, t):
                    H = np.array([[0, omega / 2],
                                  [omega / 2, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                def U_wait(omega, t):
                    H = np.array([[0, 0],
                                  [0, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                def U2(omega, t):
                    H = np.array([[0, omega * np.exp(-1j * 2 * np.pi * t_wait_T) / 2],
                                  [omega * np.exp(1j * 2 * np.pi * t_wait_T) / 2, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                U1 = U1(omega, t_pi_over_2)
                U_wait = U_wait(omega, T_wait_s)
                U2 = U2(omega, t_pi_over_2)

                product = U2 @ U_wait @ U1

                ket_zero = np.array([1, 0], dtype=complex)
                result = product @ ket_zero
                state_pop = np.abs(result)**2
				
                #T2_star = T2_time
                #decay_factor = np.exp(- T_wait**2 / T2_star**2)
                #state_pop *= decay_factor
				
                return state_pop

            def call_unitary_product_twice(pi_time, T,T_wait,T2_time, delta):
                result1 = unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, 1/4)
                result2 = unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, 3/4)
                return result1[0], result2[0]

            def fitting_function(delta, pi_time, T,T_wait,T2_time, target_results):
                computed_result1, computed_result2 = call_unitary_product_twice(pi_time, T,T_wait,T2_time, delta[0])
                target_result1, target_result2 = target_results
                error = (computed_result1 - target_result1)**2 + (computed_result2 - target_result2)**2
                return error
            
            pi_time = pi_times[0]
            initial_delta_guess = 0
            result1 = fluor_ave[0]
            
            if check_3pt_coherence:
                result2 = fluor_ave[2]
            else:
                result2 = fluor_ave[1]
                
            target_results = (result1 , result2)
            T = periodicity
            result = minimize(fitting_function, initial_delta_guess, args=(pi_time, T,T_wait,T2_time, target_results),method='Nelder-Mead')
            optimized_delta = result.x[0]/[2*np.pi]
            print(optimized_delta)

            freq_string = str(round(freq_og,6)).replace('.','p')
            freq_string_prev = str(round(set_freq,6)).replace('.','p')
            combined_data = zip(pulse_time_list,fluor_ave)
            
			
            upload_issues = result1==0 or result2==0 or result1==1 or result2==1
            ion_issues = result1==1 and result2==1
            if upload_issues or ion_issues:
                new_set_frequency = [set_freq]
            else:
                new_set_frequency = [np.abs(set_freq) - optimized_delta*1e-6]


                if abs(result1-result2)<0.45:
                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_data\\Fast_calibration_TS_{freq_string}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{freq_og}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_fits\\Fast_calibration_TS_{freq_string_prev}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{set_freq}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

                else:
                    #dt_string_current = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_fits\\Fast_calibration_TS_{freq_string_prev}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{set_freq}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

            return new_set_frequency[0],result1,result2
        
        setEvaluation('Eval3')
		
        iterator = 0.5
        mean_count_diff = diff_pass+1
        
        while mean_count_diff > diff_pass:
            if iterator>3:
                print('Had upload or ion issues repeatedly.')
                eng.quit()
                print('Nonsense to stop script', sdfasd)
                break
            else:
                pass
                    
            new_set_frequency,fluor_ave0,fluor_ave1 = perform_fast_Ramsey_cal(f_offset,f_upper,real_wait_time, threshold, pulse_program, script_functions,)
            
            upload_issues = fluor_ave0==1 or fluor_ave1==1
            ion_issues = fluor_ave0==1 and fluor_ave1==1
            if upload_issues or ion_issues:
                iterator = iterator + 1
            else:
                iterator = abs(fluor_ave0-fluor_ave1)
                mean_count_diff = abs(fluor_ave0-fluor_ave1)
                f_target_dummy = getGlobal('f_target')
                if not "%s"%f_target_dummy == new_set_frequency:
                    setGlobal("f_target", new_set_frequency, "")
                            
        if target_transition==[0,2,0]:
            f_offset_dummy = getGlobal('f_offset')
            if not "%s"%f_offset_dummy == new_set_frequency:
                    setGlobal("f_offset", new_set_frequency, "")

        elif target_transition==[-1,4,-3]:
            f_upper_dummy = getGlobal('f_upper')
            if not "%s"%f_upper_dummy == new_set_frequency:
                    setGlobal("f_upper", new_set_frequency, "")
        else:
            pass
		
        print(new_set_frequency)
        setEvaluation('Eval3')
        return new_set_frequency[0]
	

def run_fast_LT_varying_calibration(script_functions,delta,real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None,diff_pass=0.3):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

    import matlab.engine
    import time
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(1)

    import numpy as np
    from scipy.linalg import expm
    from scipy.optimize import minimize

    import sys

    import os
    import datetime
    import glob
    import json
    import numpy as np
    import random
    from scipy.optimize import curve_fit
    sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")
    pattern = "Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_ion_control_raw_data\\fast_calibration_*"
    
    Side_band_cooling_reps = 0
    real_wait_time_bool = True
    f_offset_index = [0,2,0]
    f_upper_index = [-1,4,-3]
    pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]

    if f_offset_input and f_upper_input:
        [f_offset,f_upper] = [f_offset_input,f_upper_input]
    else:
        f_offset = float(getGlobal('f_offset_LT_varying'))
        f_upper = float(getGlobal('f_upper_LT_varying'))
        print('getting ion control info',f_upper,f_offset)

    if ref_pitimes:
        [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = ref_pitimes
    else:
        pitime_n2 = float(getGlobal('pitime_n2'))
        pitime_n1 = float(getGlobal('pitime_n1'))
        pitime_0 = float(getGlobal('pitime_0'))
        pitime_p1 = float(getGlobal('pitime_p1'))
        pitime_p2 = float(getGlobal('pitime_p2'))
        
    F1PumpTime = 2 #us
    F1PumpReps = 30
    InitReps = 0
    fs = 4e9
    threshold = 9
    
    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    probe_transitions = [[target_transition]]
    for probe_trans in probe_transitions:

        
        s12_level = probe_trans[0][0]
        
        periodicity = 100 #us

        wait_times = [periodicity/4,periodicity*3/4]
        # Phase Calculations ===================================================================

        phases = [np.pi/2, 3*np.pi/2]

        #=======================================================================================

        init_trans = list_of_inits[s12_level+2]
        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        init_pulse_time = sum(init_times_array) 
        
        set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        set_freq = [set_freq[0] + delta]

        freq_og = set_freq[0]

        print('set freq', set_freq)

        f_target_dummy = getGlobal('f_target')
        if not "%s"%f_target_dummy == set_freq[0]:
            setGlobal("f_target", set_freq[0], "")
               

        T2_time = get_T2_time(probe_trans)[0]
      
        pi_times= list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        times = []
        for i in range(len(pi_times)):
            times.append(2*pi_times[i]*np.arcsin(np.sqrt(1/(len(pi_times)+1-i)))/np.pi)
        
        
        print(times)
        full_freqs = set_freq + [0] + list(np.flip(set_freq))
        print(full_freqs)
        
        LT_dummy = getGlobal('LineTriggerBoolean')
        if not "%s"%LT_dummy == 1:
            setGlobal("LineTriggerBoolean", 1, "")

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

        Hareld_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Hareld_pulse_time_dummy == pi_times[0]:
                setGlobal("Hareld_pulse_time", pi_times[0], "us")
        

        pulse_program = "Qudit_ramsey_experiment_fast_calibration"
        
        
                
        def perform_fast_Ramsey_cal(f_offset,f_upper,real_wait_time, threshold, pulse_program, script_functions):
            getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
            createTrace('Fast Calibration Points', 'Script Data', xLabel=f'Pulse Time (us)')
            wait_time_num = 0
            fluor_ave = []
            pulse_time_list = []
            file_names_list = []
            while wait_time_num<2:
                if scriptIsStopped():
                    break
                
                set_freq = float(getGlobal('f_target'))
                print('set freq', set_freq)

                full_freqs = [float(set_freq),0,float(set_freq)]
       
                print('1')
        
        #Pulse Times ==============================================================
                T_wait = real_wait_time
                full_times = list(times) + [T_wait] + list(np.flip(times))
        #Phases =================================================================
                full_phases = [0,0,phases[wait_time_num]]
        #==============================================================
                Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
                if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(full_times):
                    setGlobal("Ramsey_Wait_Time", sum(full_times), "us")
        
                half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
                if not "%s"%half_pi_time_dummy == "%s us"%sum(full_times):
                    setGlobal("Shelving_Pulse_Time", sum(full_times), "us")
                print('2')

        # AWG commands======================================================================================
                eng.SendAWGCommand("RES", nargout=0)
                time.sleep(5)
                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
                eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
                eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)
        
                eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
                time.sleep(0.1)
                eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
        
                eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
                eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        
                print('3')
        #----------------------------------------------------------------------------
                matlab_init_freqs = matlab.double(init_freqs_array)
                matlab_init_times = matlab.double(init_times_array)
        #----------------------------------------------------------------------------
                print(full_freqs)
                print(full_times)
                matlab_set_freq = matlab.double(full_freqs)
        #----------------------------------------------------------------------------		
                matlab_herald_pulse_time = matlab.double(pi_times)
                matlab_herald_freq = matlab.double([set_freq])
                matlab_herald_phase = matlab.double([0])
        #----------------------------------------------------------------------------		
                matlab_probe_pulse_time = matlab.double(full_times)
                matlab_probe_phases = matlab.double(full_phases)
        #----------------------------------------------------------------------------
                power_factor = matlab.double([1])
                power_factor_dbm = matlab.double([1])
                print('4.5')
                seg_num = 1
                eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                print('5')
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
		#----------------------------------------------------------------------------
		# Heralding
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_herald_freq,matlab_herald_pulse_time,matlab_herald_phase,fs,seg_num,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
		#----------------------------------------------------------------------------
		# Ramsey
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_set_freq,matlab_probe_pulse_time,matlab_probe_phases,fs,seg_num,nargout = 0)
                if scriptIsStopped():
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
                print('6')

        
        #-------------------------------------------------------------------------------------------------------------------------
                print('7')
        
                eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)
                seq_num = 6
        
        
                Table_length_dummy =  getGlobal('Table_length')
                if not "%s"%Table_length_dummy == seq_num:
                    setGlobal("Table_length", seq_num, "")
        
                eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        
                eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
        
                eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
        
        
                #total_time = sum([piover2_time,pulse_time,piover2_time])+30
                #PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
                #if not "%s"%PulseTime_Dummy == "%s us"%total_time:
                #    setGlobal("Shelving_Pulse_Time", total_time, "us")
                #time.sleep(0.2)
        
                setScan(pulse_program)
                startScan(globalOverrides=list(), wait=True)
                stopScan()

                #new way of getting the right PMT counts for thresholding/heralding and plotting
                data = getAllData()
                herald_data = data['PMT Index 0'][1]
                print(herald_data)
                ket1_data = data['PMT Index 1'][1]
                print(ket1_data)


                arrays = []
                for idx,herald_outcome in enumerate(herald_data):
                    if herald_outcome < threshold:
                        arrays.append(ket1_data[idx])
                mean_value = np.mean(np.array(arrays)<threshold)
        
                #matching_files = glob.glob(pattern)
                #matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
                #file_path = matching_files[-1]
                #chunks = file_path.split('\\')
                #print(chunks[-1])        
                #fname = chunks[-1]
                #file_names_list.append(fname)
                #print("=========================================")
        
                #arrays = []
                #with open(file_path, 'r') as file:
                #    print(file_path)
                #    for line in file:
                #        data = json.loads(line)
                #        if data[0]["0"][0] < threshold:
                #            arrays.append(data[0]["0"][1])
                #mean_value = np.mean(np.array(arrays)<threshold)
                #print("=========================================")
        
                if np.isnan(mean_value):
                    mean_value = 1
                PD = mean_value
                print("PD is", PD)
                fluor_ave.append(PD)
                wait_time_ramsey = wait_times[wait_time_num]
                pulse_time_list.append(wait_times[wait_time_num])
        
                wait_time_num = wait_time_num + 1

                plotPoint(wait_time_ramsey, PD,'Fast Calibration Points', plotStyle=2)
                
            closeTrace('Fast Calibration Points')

            def unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, t_wait_T):
                omega = np.pi / (pi_time * 1e-6)
                t_pi_over_2 = (pi_time * 1e-6) / 2
                T = T*1e-6
                T_wait_s = T_wait*1e-6
                def U1(omega, t):
                    H = np.array([[0, omega / 2],
                                  [omega / 2, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                def U_wait(omega, t):
                    H = np.array([[0, 0],
                                  [0, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                def U2(omega, t):
                    H = np.array([[0, omega * np.exp(-1j * 2 * np.pi * t_wait_T) / 2],
                                  [omega * np.exp(1j * 2 * np.pi * t_wait_T) / 2, delta]], dtype=complex)
                    U = expm(-1j * H * t)
                    return U

                U1 = U1(omega, t_pi_over_2)
                U_wait = U_wait(omega, T_wait_s)
                U2 = U2(omega, t_pi_over_2)

                product = U2 @ U_wait @ U1

                ket_zero = np.array([1, 0], dtype=complex)
                result = product @ ket_zero
                state_pop = np.abs(result)**2
				
                #T2_star = T2_time
                #decay_factor = np.exp(- T_wait**2 / T2_star**2)
                #state_pop *= decay_factor
				
                return state_pop

            def call_unitary_product_twice(pi_time, T,T_wait,T2_time, delta):
                result1 = unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, 1/4)
                result2 = unitary_product_with_ket_zero(pi_time, T,T_wait,T2_time, delta, 3/4)
                return result1[0], result2[0]

            def fitting_function(delta, pi_time, T,T_wait,T2_time, target_results):
                computed_result1, computed_result2 = call_unitary_product_twice(pi_time, T,T_wait,T2_time, delta[0])
                target_result1, target_result2 = target_results
                error = (computed_result1 - target_result1)**2 + (computed_result2 - target_result2)**2
                return error
            
            pi_time = pi_times[0]
            initial_delta_guess = 0
            result1 = fluor_ave[0]
            result2 = fluor_ave[1]
            target_results = (result1 , result2)
            T = periodicity
            result = minimize(fitting_function, initial_delta_guess, args=(pi_time, T,T_wait,T2_time, target_results),method='Nelder-Mead')
            optimized_delta = result.x[0]/[2*np.pi]
            print(optimized_delta)

            freq_string = str(round(freq_og,6)).replace('.','p')
            freq_string_prev = str(round(set_freq,6)).replace('.','p')
            combined_data = zip(pulse_time_list,fluor_ave)
            
			
            upload_issues = fluor_ave[0]==0 or fluor_ave[1]==0 or fluor_ave[0]==1 or fluor_ave[1]==1
            ion_issues = fluor_ave[0]==1 and fluor_ave[1]==1
            if upload_issues or ion_issues:
                new_set_frequency = [set_freq]
            else:
                new_set_frequency = [np.abs(set_freq) - optimized_delta*1e-6]


                if abs(fluor_ave[0]-fluor_ave[1])<0.45:
                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_data\\Fast_calibration_TS_{freq_string}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{freq_og}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_fits\\Fast_calibration_TS_{freq_string_prev}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{set_freq}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

                else:
                    #dt_string_current = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_fits\\Fast_calibration_TS_{freq_string_prev}_{T_wait}_{dt_string}.txt'
                    with open(filename,'w') as file:
                        for x,y in combined_data:
                            file.write(f"{x},{y}\n")
                        file.write(f"[{set_freq}],[{new_set_frequency[0][0]}]\n")
                        file.write(f"{pi_times},[{pitime_n2},{pitime_n1},{pitime_0},{pitime_p1},{pitime_p2}]\n")
                        file.write(f"{phases}\n")
                        file.write(f"{file_names_list}\n")

            return new_set_frequency[0],fluor_ave[0],fluor_ave[1]
        
        setEvaluation('Eval3')
		
        iterator = 0.5
        mean_count_diff = diff_pass+1
        #while iterator>0.45 or mean_count_diff > 0.1:
        while mean_count_diff > diff_pass:
            if iterator>3:
                print('Had upload or ion issues repeatedly.')
                eng.quit()
                print('Nonsense to stop script', sdfasd)
                break
            else:
                pass
                    
            new_set_frequency,fluor_ave0,fluor_ave1 = perform_fast_Ramsey_cal(f_offset,f_upper,real_wait_time, threshold, pulse_program, script_functions,)
            
            upload_issues = fluor_ave0==1 or fluor_ave1==1
            ion_issues = fluor_ave0==1 and fluor_ave1==1
            if upload_issues or ion_issues:
                iterator = iterator + 1
            else:
                iterator = abs(fluor_ave0-fluor_ave1)
                mean_count_diff = abs(fluor_ave0-fluor_ave1)
                f_target_dummy = getGlobal('f_target')
                if not "%s"%f_target_dummy == new_set_frequency:
                    setGlobal("f_target", new_set_frequency, "")
                            
        if target_transition==[0,2,0]:
            f_offset_dummy = getGlobal('f_offset_LT_varying')
            if not "%s"%f_offset_dummy == new_set_frequency:
                    setGlobal("f_offset_LT_varying", new_set_frequency, "")

        elif target_transition==[-1,4,-3]:
            f_upper_dummy = getGlobal('f_upper_LT_varying')
            if not "%s"%f_upper_dummy == new_set_frequency:
                    setGlobal("f_upper_LT_varying", new_set_frequency, "")
        else:
            pass
		
        print(new_set_frequency)
        setEvaluation('Eval3')
        return new_set_frequency[0]

#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
#freq_list, pitime_list = run_calibration(script_functions,do_pi_time_calibration=True,low_power=False,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
#print(freq_list)
#print(pitime_list)


#import matlab.engine
#eng = matlab.engine.start_matlab()
#eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
#eng.SendAWGCommand("RES", nargout=0)
#time.sleep(1)

#f_upper_input1=623.2605995836025
#f_offset_input1=545.5035902533191
#ref_pitimes=[28.206, 54, 54.605, 40.916, 50]
#new_set_frequency = run_fast_calibration(script_functions, 0, 200,target_transition=[0,2,0],f_offset_input=None, f_upper_input=f_upper_input1,ref_pitimes=ref_pitimes)
#deltas = np.linspace(-0.001,0.001,5)
#for delta in deltas:
#    delta = 0
#    new_set_frequency = run_fast_calibration(script_functions, 0, 100,target_transition=[-1,4,-3],f_offset_input=545.5073623394707, f_upper_input=f_upper_input1,ref_pitimes=[28.206, 54, 54.605, 40.916, 50])
#    f_upper_input1=new_set_frequency
#print(new_set_frequency)