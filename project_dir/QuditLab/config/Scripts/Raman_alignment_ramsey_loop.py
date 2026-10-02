#Raman_alignment_ramsey_loop.py created 2026-07-15 17:50:16.942938

#RFSoC_FastFive_Calibration.py created 2025-11-20 08:55:23.023898

#New_Shelving_Calibration_ParamEstimated_Initialised.py created 2024-04-26 16:49:34.435318

#Shelving_Freq_PiTime_Calibration_PlotPD_ParamEstimated_Initialised.py created 2024-04-08 17:31:06.613195

do_pi_time_calibration = False
line_trigger = True
check_3pt_coherence = False
do_rough_scan = False
steps_per_pi_time = 2

import time
import sys
import os
import datetime
import glob
import numpy as np
import random
    
import json, urllib.request
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

from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
#from Functions_RFSoC_RamseyCalibration import *
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

# set pulse program for pi-time scans
pulse_program = "Hareld_pulse_time_scan"
#pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

pitime_n2 = getGlobal('pitime_n2') # [-1, 4, -3]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [0, 2, 0]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]
ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

threshold = 32

F1PumpTime = 0.5 #us
F1PumpReps = 20
InitReps = 0
#fs = 4e9

Side_band_cooling_reps = 0

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

f_offset_index = [0,2,0]
f_upper_index = [0,4,-2]

# do frequency references first
#pitime_ref_index = [[0,2,0],[-1,4,-3],[-2,3,-3],[2,4,3],[2,4,4]]
#list_var_names = ['pitime_0','pitime_n2','pitime_n1','pitime_p1','pitime_p2']

pitime_ref_index = [[0,2,0],[0,4,-2],[-2,3,-3],[2,4,3],[2,4,4]]
list_var_names = ['pitime_0','pitime_n2','pitime_n1','pitime_p1','pitime_p2']

pitime_ref_index = [[0,2,0]]*100
list_var_names = ['pitime_0']*100

#pitime_ref_index = [[0,4,-2]]
#list_var_names = ['pitime_n2']
#pitime_ref_index = [[0,2,0]]

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

init_times_n2 = list(get_pi_times(init_n2_index,ref_pitimes_list))
init_times_n1 = list(get_pi_times(init_n1_index,ref_pitimes_list))
init_times_0 = list(get_pi_times(init_0_index,ref_pitimes_list))
init_times_p1 = list(get_pi_times(init_p1_index,ref_pitimes_list))
init_times_p2 = list(get_pi_times(init_p2_index,ref_pitimes_list))

init_freqs_array = [init_freqs_n2,init_freqs_n1,init_freqs_0,init_freqs_p1,init_freqs_p2]
init_times_array = [init_times_n2,init_times_n1,init_times_0,init_times_p1,init_times_p2]

output_file_freqs = fr'Z:\Lab Data\D52_Calibration_Ba137\New_initialized_calibration_freq_files\New_initialized_calibration_freq_files_{dt_string}.txt'

if do_pi_time_calibration:
    pitime_ref_index =  pitime_ref_index
else:
    pitime_ref_index =  pitime_ref_index[:]
print(pitime_ref_index)

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

if do_rough_scan:
    freq_offset = run_fast_calibration(script_functions,0,25,target_transition=f_offset_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=False)
    [pi_time] = get_pi_times([f_offset_index],ref_pitimes_list)
    f_offset_dummy = getGlobal('f_offset')
    if not "%s"%f_offset_dummy == freq_offset:
        setGlobal("f_offset", freq_offset, "")
    print('020 pi time', pi_time)    

    freq_upper = run_fast_calibration(script_functions,0,25,target_transition=f_upper_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=True)
    [pi_time] = get_pi_times([f_upper_index],ref_pitimes_list)
    f_upper_dummy = getGlobal('f_upper')
    if not "%s"%f_upper_dummy == freq_upper:
        setGlobal("f_upper", freq_upper, "")


def find_freq_target(index, dt_string, threshold, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions

    real_wait_time = 300
    delta = 0
    
    if index == f_offset_index:
        #with open(output_file_freqs,'a') as outfile:
            
        freq_offset = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=f_offset_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=check_3pt_coherence)
        #[pi_time] = get_pi_times([[0,2,0]],ref_pitimes_list)
        #outfile.write(f'{np.round(freq_offset,6)}, {np.round(pi_time,3)}, {[0,2,0]}\n')
        f_offset_dummy = getGlobal('f_offset')
        if not "%s"%f_offset_dummy == freq_offset:
            setGlobal("f_offset", freq_offset, "")
        freq_target = freq_offset
        
    elif index == f_upper_index:
        #with open(output_file_freqs,'a') as outfile:
        freq_upper = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=f_upper_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=check_3pt_coherence)
        #[pi_time] = get_pi_times([[-1,4,-3]],ref_pitimes_list)
        #outfile.write(f'{np.round(freq_upper,6)}, {np.round(pi_time,3)}, {[-1,4,-3]}\n')
        f_upper_dummy = getGlobal('f_upper')
        if not "%s"%f_upper_dummy == freq_upper:
            setGlobal("f_upper", freq_upper, "")
        freq_target = freq_upper

    else:
        freq_target = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=index,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        
    return freq_target

def findPiTime_withfit_plotPD(freq_peak, stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions
    createTrace('1762 nm pi-time scan', 'Script Data', xLabel=f'Pulse Time (us)')
    pulse_time = 0
    fluor_ave = []
    pulse_time_list = []
    flour_exp = []

    #print(0)
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break
        #print(1)
        #PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
        #if not "%s"%PulseTime_Dummy == "%s us"%pulse_time:
        #    setGlobal("Shelving_Pulse_Time", pulse_time, "us")

        set_global_value("Shelving_Pulse_Time", pulse_time, "us", script_functions)
        #print(2)
        #setScan(pulse_program)
        #print(3)
        #startScan(globalOverrides=list(), wait=True)
        #print(4)
        #stopScan()
        #print(5)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

        # get heralded data properly
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
        fluor_bool = np.array(arrays) < threshold

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)
        flour_exp.append(fluor_bool)
        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)

        pulse_time = pulse_time + time_step
        
    closeTrace('1762 nm pi-time scan')

    def oscfunc(t, w, p, c):
        return 0.5 * np.cos(w * t + p) + c

    def fit_oscillation(tt, yy):
        '''Fit sin to the input time sequence, and return fitting parameters:
        "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc".

        Option to take on guesses and bounds for the fit too.'''
        tt = np.array(tt)
        yy = np.array(yy)
        ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))
        Fyy = abs(np.fft.fft(yy))
        guess_freq = abs(ff[np.argmax(Fyy[1:])+1])
            
        
        guess_offset = np.mean(yy)

        guess = np.array([2.*np.pi*guess_freq, 0, guess_offset])
        popt, pcov = curve_fit(oscfunc, tt, yy, p0=guess, maxfev=10000)
        uncertainty = np.sqrt(pcov[0][0])
        omeg, p, c = popt
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

setEvaluation('Eval3')

#find_f0_f1_fast_cal(dt_string, threshold, script_functions)

#setEvaluation('Eval2')

for i,j in zip(pitime_ref_index,list_var_names):

    freq_target = find_freq_target(i,dt_string, threshold, script_functions)
    #freq_target = list(Get_1762_EOM_Freqs_an1an2(pitime_ref_index,f_offset,f_upper))[0]
    print('fitted freq', freq_target)
    
    [pi_time] = get_pi_times([i],ref_pitimes_list)
    print('guessed pi time', pi_time)
    if do_pi_time_calibration:

        Hareld_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Hareld_pulse_time_dummy == pi_time:
                setGlobal("Hareld_pulse_time", pi_time, "us")

        freq_peak_for_pi = freq_target
        stop_time = 3*pi_time + pi_time/4
        time_step = pi_time/steps_per_pi_time
        init_state = i[0]

        #print('start debug')
        #print(init_freqs_array)
        #print(init_state)
        #print(freq_peak_for_pi)
        #print(sadfasdf)
        init_row1 = [1, init_freqs_array[int(init_state+2)], [0]*len(init_freqs_array[int(init_state+2)]), init_times_array[int(init_state+2)], [0]*len(init_times_array[int(init_state+2)]), 0]    
        dummy_row2 = [2, [800], [0], [0.01], [0], 0]
        herald_row3 = [3, [freq_peak_for_pi], [0]*len([freq_peak_for_pi]), [pi_time], [0]*len([freq_peak_for_pi]), 1]
        dummy_row4 = [4, [800], [0], [0.01], [0], 0]
        pulse_row5 = [3, [freq_peak_for_pi], [0]*len([freq_peak_for_pi]), [1500], [0]*len([freq_peak_for_pi]), 1]
        dummy_row6 = [4, [800], [0], [0.01], [0], 0]


        row_num = 6
        set_global_value("Table_length", row_num, "", script_functions)

        rows = [init_row1, 
                dummy_row2, 
                herald_row3, 
                dummy_row4,
                pulse_row5,
                dummy_row6]

        resp = upload_rows(rows, time_unit="us")
        print(json.dumps(resp, indent=2))  
        print(f'Setting freq to {freq_peak_for_pi} MHz with total probe time of 1500 us')

        setEvaluation('Eval3')

        pi_time = findPiTime_withfit_plotPD(freq_target, stop_time, time_step, threshold, pulse_program, script_functions)

        setEvaluation('Eval2')

        # don't set pitimes from the dummy -1,2,0 and 1,1,1 transitions
        pitime_dummy = getGlobal(j)
        if not "%s"%pitime_dummy == pi_time:
            setGlobal(j, pi_time, "")
    with open(output_file_freqs,'a') as outfile:
        outfile.write(f'{np.round(freq_target,6)}, {np.round(pi_time,3)}, {i}\n')

