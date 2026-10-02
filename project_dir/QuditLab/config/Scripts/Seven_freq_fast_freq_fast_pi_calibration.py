#Seven_freq_fast_freq_fast_pi_calibration.py created 2024-10-09 16:18:27.674547


#New_Shelving_Calibration_ParamEstimated_Initialised.py created 2024-04-26 16:49:34.435318

#Shelving_Freq_PiTime_Calibration_PlotPD_ParamEstimated_Initialised.py created 2024-04-08 17:31:06.613195

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

do_reference_freqs = True
do_pi_time_calibration = True

line_trigger = True

#pulse_program = "Shelving_MacroAllLasersInit_NoShutter_Scan"
# pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
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
F1PumpReps = 30
InitReps = 0
fs = 4e9

Side_band_cooling_reps = 0

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

f_offset_index = [0,2,0]
f_upper_index = [-1,4,-3]

pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]
#pitime_ref_index = [[2,4,3],[2,4,4]]
list_var_names = ['pitime_n2','pitime_n1','pitime_0','pitime_p1','pitime_p2']
#list_var_names = ['pitime_p1','pitime_p2']

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

if do_reference_freqs and do_pi_time_calibration:
    full_scan_indeces =  [f_offset_index] + [f_upper_index] + pitime_ref_index
    full_scan_indeces = [full_scan_indeces]
    #full_scan_indeces = [[[2,4,4]]]
elif not do_reference_freqs and do_pi_time_calibration:
    full_scan_indeces = pitime_ref_index
    full_scan_indeces = [full_scan_indeces]
    #full_scan_indeces = [[[2,4,4]]]
elif do_reference_freqs and not do_pi_time_calibration:
    full_scan_indeces =  [f_offset_index] + [f_upper_index]
    full_scan_indeces = [full_scan_indeces]
    #full_scan_indeces = [[[2,4,4]]]
else:
    full_scan_indeces =  [[f_offset_index] + [f_upper_index]]

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

def findPiTime_withfit_plotPD(freq_peak, stop_time, pi_time_guess, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = pi_time_guess/2
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
        plot_time = (50*pulse_time)/pi_time_guess

        plotPoint(plot_time, PD+1, '1762 nm pi-time scan', plotStyle=2)

        pulse_time = pulse_time + pi_time_guess
        
    closeTrace('1762 nm pi-time scan')

    def oscfunc(t, w):
        return 0.5+0.5 * np.cos(w * t)

    def fit_oscillation(tt, yy):
        '''Fit sin to the input time sequence, and return fitting parameters:
        "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc".

        Option to take on guesses and bounds for the fit too.'''
        tt = np.array(tt)
        yy = np.array(yy)
        # ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))
        # Fyy = abs(np.fft.fft(yy))
        # guess_freq = abs(ff[np.argmax(Fyy[1:])+1])
            
        # guess_amp = np.max(yy)-np.mean(yy)
        # guess_offset = np.mean(yy)

        guess = np.array([np.pi/pi_time_guess])
        popt, pcov = curve_fit(oscfunc, tt, yy, p0=guess, maxfev=10000)
        uncertainty = np.sqrt(pcov[0][0])
        omeg = popt[0]
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

    return final_pi_time, fluor_ave[0], fluor_ave[1]

with open(output_file_freqs,'w'):
    pass




setEvaluation('Eval3')

if do_reference_freqs:
    find_f0_f1_fast_cal(dt_string, threshold, script_functions)
else:
    pass

setEvaluation('Eval2')

if do_pi_time_calibration:
    for i,j in zip(pitime_ref_index,list_var_names):

        freq_target = find_freq_target(i,dt_string, threshold, script_functions)
        [pi_time] = Get_1762_PiTimes([i],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)

        Herald_dummy = getGlobal('Hareld_pulse_time').magnitude
        if not "%s"%Herald_dummy == "%s us"%pi_time:
            setGlobal("Hareld_pulse_time", pi_time, "us")
        time.sleep(1)

        print('Frequency and pi-time being used now - ',freq_target,pi_time)

        stop_time = 2*pi_time
        pi_time_guess = pi_time
        init_state = i[0]
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


        freq_peak_for_pi = float(freq_target)

        hareld_pulse_freq = matlab.double([freq_peak_for_pi])
        hareld_pulse_time = matlab.double([pi_time_guess])


        freq_peak_for_pi = float(freq_target)
        matlab_set_freq = matlab.double([freq_peak_for_pi])
        matlab_probe_pulse_time = matlab.double([1500])

        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)

        eng.Pulse_upload(hareld_pulse_freq,hareld_pulse_time,fs,2,power_factor_dbm,nargout = 0) 

        eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)

        eng.Pulse_upload_dummy(fs,4,nargout = 0)


        eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 2,4,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 5,3,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 6,4,1,1", nargout=0)

        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

        setEvaluation('Eval3')


        iterator = 0.5
        mean_count_diff = 0.31
        #while iterator>0.45 or mean_count_diff > 0.1:
        while iterator>0.15 or mean_count_diff > 0.3:
            if iterator>3:
                print('Had upload or ion issues repeatedly.')
                eng.quit()
                print('Nonsense to stop script', sdfasd)
                break
            else:
                pass

            pi_time_found, fluor_ave0, fluor_ave1 = findPiTime_withfit_plotPD(freq_target, stop_time, pi_time_guess, threshold, pulse_program, script_functions)

            upload_issues = fluor_ave0==1 or fluor_ave1==1
            ion_issues = fluor_ave0==1 and fluor_ave1==1
            if upload_issues or ion_issues:
                iterator = iterator + 1
            else:
                iterator = abs(fluor_ave0-fluor_ave1)
                mean_count_diff = abs(fluor_ave0+fluor_ave1-1)
                pi_time_guess = pi_time_found


        setEvaluation('Eval2')
        pitime_dummy = getGlobal(j)
        if not "%s"%pitime_dummy == pi_time_found:
            setGlobal(j, pi_time_found, "")
        with open(output_file_freqs,'a') as outfile:
            outfile.write(f'{np.round(freq_target,6)}, {np.round(pi_time_found,3)}, {i}\n')
    
eng.quit()

eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)

eng.quit()
