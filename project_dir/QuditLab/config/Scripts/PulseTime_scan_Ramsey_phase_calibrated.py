
import time
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

import sys
import os
import datetime
import glob
import numpy as np
import random
    
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

do_f0_f1_calibration = False

do_fn_calibration = False

do_pi_time_calibration = True
line_trigger = True

start_time_factor = 0.0
stop_time_factor = 2
time_step_factor = 15

target_transitions = [[2,4,3]]

#target_transitions = [[0, 2, 0],[-2, 3, -2],[-2, 4, 0],[2, 2, 1],[2, 4, 3],[0, 3, 0],[0, 4, -2],[1, 3, -1],[-2, 2, 0],[-1, 2, -2],[-1, 4, 1],[-1, 4, -1],[2, 1, 1],[-1, 1, 1]]

#target_transitions = [[-2, 4, -4],[-1, 4, -3],[0, 4, -2],[2, 4, 3],[-2, 3, -3],[1, 4, -1],[2, 4, 4],[0, 3, 1],[-1, 3, -1],[2, 4, 2],[1, 4, 1],[-1, 3, 0],[-2, 3, -2],[1, 3, 3],[1, 4, 0],[0, 4, -1],[1, 4, 2],[1, 3, 2],[0, 3, 0],[0, 3, 2],[-1, 3, -2],[1, 2, -1],[0, 4, 0],[-2, 3, -1],[2, 4, 1],[-1, 4, -2],[2, 2, 0],[2, 4, 0],[-2, 2, -1],[0, 2, -2],[1, 2, 2],[-1, 3, 1],[-2, 2, -2],[-1, 2, -2],[-1, 2, 1],[2, 2, 1],[-1, 3, -3],[0, 2, 0],[2, 1, 0],[0, 2, 2],[2, 2, 2],[0, 4, 1],[0, 3, -1],[-2, 2, 0],[-1, 2, 0],[1, 3, 1],[1, 4, 3],[0, 1, 1],[1, 2, 1],[-1, 1, -1],[-2, 1, -1],[-1, 4, -1],[1, 3, -1],[-2, 3, 0],[-2, 1, 0],[0, 2, -1],[2, 3, 0],[1, 1, -1],[1, 1, 1]]
#target_transitions.reverse()

target_transitions_string = str(target_transitions)
do_f0_f1_calibration_string = str(do_f0_f1_calibration)
do_fn_calibration_string = str(do_fn_calibration)
line_trigger_string = str(line_trigger)

#pulse_program = "Shelving_MacroAllLasersInit_NoShutter_Scan"
pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
pulse_program = "Hareld_pulse_time_scan"
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

pitime_n2 = getGlobal('pitime_n2') # [-2, 4, -4]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [2, 4, 2]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]

threshold = 8

F1PumpTime = 2 #us
F1PumpReps = 40
InitReps = 0
fs = 4e9

Side_band_cooling_reps = 0

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

f_offset_index = [0,2,0]
f_upper_index = [-1,4,-3]
#pitime_ref_index = [[-2,1,0],[-2,1,0],[1,1,1],[2,4,3],[2,4,4]]



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

def find_f0_f1_fast_cal(dt_string , threshold, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions

    real_wait_time = 100
    delta = 0
    with open(output_file_freqs,'a') as outfile:
        freq_offset = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        [pi_time] = Get_1762_PiTimes([[0,2,0]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
        outfile.write(f'{np.round(freq_offset,6)}, {np.round(pi_time,3)}, {[0,2,0]}\n')
        f_offset_dummy = getGlobal('f_offset')
        if not "%s"%f_offset_dummy == freq_offset:
            setGlobal("f_offset", freq_offset, "")

        freq_upper = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        [pi_time] = Get_1762_PiTimes([[-1,4,-3]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
        outfile.write(f'{np.round(freq_upper,6)}, {np.round(pi_time,3)}, {[-1,4,-3]}\n')
        f_upper_dummy = getGlobal('f_upper')
        if not "%s"%f_upper_dummy == freq_upper:
            setGlobal("f_upper", freq_upper, "")
        
    return freq_offset,freq_upper

def find_freq_target(index, dt_string, threshold, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions

    real_wait_time = 100
    delta = 0
    
    freq_target = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=index,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        
    return freq_target

def findPiTime_withfit_plotPD(target_triplet,freq_peak, start_time, stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions
    createTrace('1762 nm pi-time scan', 'Script Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
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
        print('pulse time is', pulse_time)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

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

        PD = mean_value
        flour_exp.append(np.array(arrays)<threshold)

        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=2)

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
    filename = f'Z:\Lab Data\D52_Calibration_Ba137\\Pulse_time_scans\\Pulse_time_scan_{str([target_triplet])}_f0f1_{do_f0_f1_calibration_string}_fn_{do_fn_calibration_string}_LT_{line_trigger_string}_{dt_string}.txt'
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


if do_f0_f1_calibration:

    setEvaluation('Eval3')

    find_f0_f1_fast_cal(dt_string, threshold, script_functions)

    setEvaluation('Eval2')

if do_pi_time_calibration:
    for i in target_transitions:
        if do_fn_calibration:
            freq_target = find_freq_target(i,dt_string, threshold, script_functions)
            print('calibrated freq: ',freq_target)
        else:
            freq_target = list(Get_1762_EOM_Freqs_an1an2([i],f_offset,f_upper))[0]
            print('guessed freq', freq_target)
        
        [pi_time] = Get_1762_PiTimes([i],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)
        #start_time = start_time_factor*pi_time
        #stop_time = stop_time_factor*pi_time
        #time_step = pi_time/time_step_factor
        start_time = 0
        stop_time = 100000
        time_step = 10000
        init_state = i[0]

        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))

        pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
        pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
        pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
        pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
        pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

        list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
        [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
        [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
        ]

        init_trans = list_of_inits[init_state+2]
        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        init_pulse_time = sum(init_times_array) 

        Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
        if not "%s"%Init_PulseTime == init_pulse_time:
            setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

        Hareld_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Hareld_pulse_time_dummy == pi_time:
            setGlobal("Hareld_pulse_time", pi_time, "us")

        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(2)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 1", nargout=0) #0 sets AWG to externally triggered mode
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)


        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])
        #==========================================================
        matlab_init_freqs = matlab.double(init_freqs_array)
        matlab_init_times = matlab.double(init_times_array)
        #==========================================================
        hareld_pulse_freq = matlab.double([freq_target])
        hareld_pulse_time = matlab.double([pi_time])
        #==========================================================
        matlab_set_freq = matlab.double([freq_target])
        matlab_probe_pulse_time = matlab.double([500])
        #==========================================================
        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
        #==========================================================
        eng.Pulse_upload(hareld_pulse_freq,hareld_pulse_time,fs,2,power_factor_dbm,nargout = 0) 
        #==========================================================
        eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)
        #==========================================================
        eng.Pulse_upload_dummy(fs,4,nargout = 0) 
        #==========================================================
        eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 2,4,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
        #eng.SendAWGCommand("SOUR:SEQ:DEF 5,3,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 5,4,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 6,4,1,1", nargout=0)
        #==========================================================
        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

        eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

        eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)



        setEvaluation('Eval3')

        pi_time = findPiTime_withfit_plotPD(i,freq_target, start_time, stop_time, time_step, threshold, pulse_program, script_functions)

        setEvaluation('Eval2')

        with open(output_file_freqs,'a') as outfile:
            outfile.write(f'{np.round(freq_target,6)}, {np.round(pi_time,3)}, {i}\n')
    
eng.quit()

eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)

eng.quit()

