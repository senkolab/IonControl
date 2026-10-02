#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

#D52_Qudit_phase_ramsey_with_buses.py created 2024-06-27 14:44:06.006471

#Qudit_ramsey.py created 2024-06-03 17:12:12.796107

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

import sys
import os
import datetime
import glob
import json
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"
def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
Side_band_cooling_reps = 0


#initial_state = [[0,2,2]]

do_calibrations = True

#ramsey_wait_times = np.arange(0,5100,500)
repeat_experiments = 1
ramsey_wait_times = [0]
f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

# using -2 and +2 as bus states for D=5 ramsey =======================================================================
#pulse_train = [[-1,3,-1],[-1,2,0],[-1,2,0],[0,2,0],     [0, 2, 0], [-1, 2, 0], [-1, 2, 0],[-1,3,-1], [-1, 2, -3]]

# changes for looking at D=3 ramsey
#pulse_train = [[0,2,],[0,3,0], [0, 3, 0], [0, 2, 0]]

#optional detunings
#detunings = [0.0,0.0,0.0,0.0]
#U1 only
#pulse_train = [[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,2,0],[2,2,0],[2,4,4],[2,4,3],[2,2,0]]

#probe_trans = [[0,3,0],[0,2,0]]

#fractions = [1/3,1/2,   1/2,1/3]

#simulated_phase_mask = [0,0,    2,1]
#fixed_phase_mask = [0,0,      1,1]

# no bussing D=9 Ramsey ============================================================================================
#pulse_train = [[0,4,-2],[0,4,-1],[0,4,0],[0,4,1],[0,3,1],[0,3,2],[0,2,0],[0,3,0],       [0,3,0],[0,2,0],[0,3,2],[0,3,1],[0,4,1],[0,4,0],[0,4,-1],[0,4,-2]]

#optional detunings
#detunings = [0.0,0.002,0.002,0.0]
#U1 only
#pulse_train = [[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,2,0],[2,2,0],[2,4,4],[2,4,3],[2,2,0]]

#probe_trans = [[0,4,-2],[0,4,-1],[0,4,0],[0,4,1],[0,3,1],[0,3,2],[0,2,0],[0,3,0]]

#fractions = [1/9,1/8,1/7,1/6,1/5,1/4,1/3,1/2,   1/2,1/3,1/4,1/5,1/6,1/7,1/8,1/9]

#simulated_phase_mask = [0,0,0,0,0,0,0,0,    8,7,6,5,4,3,2,1]
#fixed_phase_mask =     [0,0,0,0,0,0,0,0,    1,1,1,1,1,1,1,1]


# bussed D=2 Ramsey ============================================================================================
#pulse_train = [[0,2,2],[0,3,2],    [0,3,2],[0,2,2]]

#optional detunings
#detunings = [0.0,0.002,0.002,0.0]
#U1 only
#pulse_train = [[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,2,0],[2,2,0],[2,4,4],[2,4,3],[2,2,0]]

#probe_trans = [[0,2,2],[0,3,2]]

#fractions = [1/2,1, np.nan,  1,1/2]

#simulated_phase_mask = [0,0,   np.nan,  0,1]
#fixed_phase_mask =     [0,0,   np.nan,  1,1]

'''
# 5 Level Bused Qudit Ramsey
initial_state = [[-2,2,-2]]

pulse_train_U1 = [[-2,2,-2],[-2,1,-1],[-2,2,-2],[-2,3,-3],[-2,2,-2],[-2,4,-1],[-2,2,-2],[-2,4,-2]]
fractions_U1 =       [1/5,      1,      1/4,        1,        1/3,      1,      1/2,        1]

pulse_train_U2 = [[-2,4,-2],[-2,2,-2],[-2,4,-2],[-2,4,-1],[-2,2,-2],[-2,4,-1],[-2,3,-3],[-2,2,-2],[-2,3,-3],[-2,1,-1],[-2,2,-2],[-2,1,-1]]
fractions_U2 =       [1,        1/2,      1,        1,       1/3,        1,         1,        1/4,      1,       1,       1/5,       1]
 
probe_trans = [[-2,2,-2],[-1,1,-1],[-2,3,-3],[0,4,-1],[0,4,-2]]


simulated_phase_mask_U1=  [0,0,0,0,0,0,0,0]  
simulated_phase_mask_U2 = [0,4,0,0,3,0,0,2,0,0,1,0]

fixed_phase_mask_U1 =     [1, 0, 1, 0, 1, 0, 1, 0] 
fixed_phase_mask_U2 =     [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
'''

'''
# 12 level Qudit Ramsey
initial_state = [[-2,2,-2]]

pulse_train_U1 = [[-2,2,-2],[-2,1,-1],[-2,2,-2],[-2,3,-3],[0,2,-2],[0,4,-1],[0,2,-2],[0,4,-2],[-2,2,-2],[-2,4,-4],[-2,2,-2],[-2,2,-1],[0,2,-2],[0,4,0],[-2,2,-2],[-2,3,-2],[-1,2,-2],[-1,4,-3],[0,2,-2],[0,4,1],[-1,2,-2],[-1,3,-1]]

fractions_U1 = [1/12, 1, 1/11, 1, 1/10, 1, 1/9, 1, 1/8, 1, 1/7, 1, 1/6, 1, 1/5, 1, 1/4, 1, 1/3, 1, 1/2, 1]

#pulse_train_U2 = [[-2,3,-2],[-2,2,-2],[-2,3,-2],[0,4,0],[0,2,-2],[0,4,0],[-2,2,-1],[-2,2,-2],[-2,2,-1],[-2,4,-4],[-2,2,-2],[-2,4,-4],[0,4,-2],[0,2,-2],[0,4,-2],[0,4,-1],[0,2,-2],[0,4,-1],[-2,3,-3],[-2,2,-2],[-2,3,-3],[-2,1,-1],[-2,2,-2],[-2,1,-1]]
#fractions_U2 =       [1,      1,      1,        1,      1/2,     1,        1,      1/3,       1,         1,       1/4,        1,      1,       1/5,     1,        1,      1/6,      1,       1,       1/7,       1,        1,          1/8,      1]

pulse_train_U2 = [[-1,3,-1],[-1,2,-2],[-1,3,-1],[0,4,1],[0,2,-2],[0,4,1],[-1,4,-3],[-1,2,-2],[-1,4,-3],[-2,3,-2],[-2,2,-2],[-2,3,-2],[0,4,0],[0,2,-2],[0,4,0],[-2,2,-1],[-2,2,-2],[-2,2,-1],[-2,4,-4],[-2,2,-2],[-2,4,-4],[0,4,-2],[0,2,-2],[0,4,-2],[0,4,-1],[0,2,-2],[0,4,-1],[-2,3,-3],[-2,2,-2],[-2,3,-3],[-2,1,-1],[-2,2,-2],[-2,1,-1]]
fractions_U2 =       [1,      1/2,      1,        1,      1/3,     1,        1,      1/4,       1,         1,       1/5,        1,      1,       1/6,     1,        1,      1/7,      1,       1,       1/8,       1,        1,          1/9,      1,    1,    1/10,    1,    1,    1/11,    1,    1,    1/12,    1]
 
probe_trans = [[-2, 2, -2], [-2, 1, -1], [-2, 3, -3], [0, 4, -1], [0, 4, -2], [-2, 4, -4], [-2, 2, -1], [0, 4, 0], [-2, 3, -2], [-1, 4, -3], [0, 4, 1], [-1, 3, -1]]


simulated_phase_mask_U1=  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
simulated_phase_mask_U2 = [0,11,0,0,10,0,0,9,0,0,8,0,0,7,0,0,6,0,0,5,0,0,4,0,0,3,0,0,2,0,0,1,0]

fixed_phase_mask_U1 =     [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0] 
fixed_phase_mask_U2 =     [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
'''
'''
# From Ramsey Specific state finding
initial_state = [[1,4,0]]

pulse_train_U1 =  [[1,4,0],[1, 4, 1], [1, 3, 3], [1, 4, 0], [1, 4, 2], [1, 3, 2], [1, 2, -1], [1, 2, 2], [1, 4, -1], [0, 4, -1], [0, 4, -1], [0, 4, -2], [0, 3, 1]]

fractions_U1 = [1, 0.09090909090909091, 0.1, 0.1111111111111111, 0.125, 0.14285714285714285, 0.16666666666666666, 0.2, 1, 1, 0.25, 0.3333333333333333, 0.5]

pulse_train_U2 =  [[0, 3, 1], [0, 4, -2], [0, 4, -1], [0, 4, -1], [1, 4, -1], [0, 4, -1], [1, 2, 2], [1, 2, -1], [1, 3, 2], [1, 4, 2], [1, 4, 0], [1, 3, 3], [1, 4, 1]]

fractions_U2 = [0.5, 0.3333333333333333, 0.25, 1, 1, 1, 0.2, 0.16666666666666666, 0.14285714285714285, 0.125, 0.1111111111111111, 0.1, 0.09090909090909091]

probe_trans = [[1,4,1],[1,3,3],[1,4,0],[2,4,2],[0,3,2],[-2,2,-1],[0,2,2],[0,4,-1],[0,4,-2],[0,3,1]]

#probe_trans = [[0,4,-1], [0, 4, -2],[1,4,1], [1, 3, 3], [1, 4, 0], [0, 3, 1], [2, 4, 2], [0, 3, 2], [-2, 2, -1], [0, 3, 0],[0,2,2],[-2,2,-2]]#, [-2, 3, -1], [1, 4, 0], [0, 2, 0]]


simulated_phase_mask_U1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
simulated_phase_mask_U2 = [10, 9, 8, 0, 0, 0, 7, 6, 5, 4, 3, 2, 1]

fixed_phase_mask_U1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
fixed_phase_mask_U2 = [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1]
'''
'''
initial_state = [[1,4,1]]
pulse_train_U1 =  [[1,4,1], [1, 4, 1], [1, 3, 3], [1, 4, 2], [1, 3, 2], [1, 2, -1], [1, 2, 2], [1, 4, -1], [0, 4, -1], [0, 4, -1], [0, 4, -2], [0, 3, 1], [0, 3, 0], [0, 4, 0], [2, 4, 0], [2, 4, 0], [2, 4, 3], [2, 4, 4]]
fractions_U1 = [1,0.07142857142857142, 0.07692307692307693, 0.08333333333333333, 0.09090909090909091, 0.1, 0.1111111111111111, 1, 1, 0.125, 0.14285714285714285, 0.16666666666666666, 0.2, 1, 1, 0.25, 0.3333333333333333, 0.5]
simulated_phase_mask_U1 = [0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
fixed_phase_mask_U1 = [0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0]
probe_trans =  [[1, 2, 1],[1, 4, 1], [1, 3, 3], [2, 4, 2], [1, 3, 2], [1, 2, -1], [1, 2, 2], [1, 4, -1], [0, 4, -2], [0, 3, 1], [-1, 3, 0], [1, 4, 0], [2, 4, 3], [2, 4, 4]]
pulse_train_U2 =  [[2, 4, 4], [2, 4, 3], [2, 4, 0], [2, 4, 0], [0, 4, 0], [2, 4, 0], [0, 3, 0], [0, 3, 1], [0, 4, -2], [0, 4, -1], [0, 4, -1], [1, 4, -1], [0, 4, -1], [1, 2, 2], [1, 2, -1], [1, 3, 2], [1, 4, 2], [1, 3, 3], [1, 4, 1], [1, 2, 1]]
fractions_U2 = [0.5, 0.3333333333333333, 0.25, 1, 1, 1, 0.2, 0.16666666666666666, 0.14285714285714285, 0.125, 1, 1, 1, 0.1111111111111111, 0.1, 0.09090909090909091, 0.08333333333333333, 0.07692307692307693, 0.07142857142857142, 1]
simulated_phase_mask_U2 = [13, 12, 11, 0, 0, 0, 10, 9, 8, 7, 0, 0, 0, 6, 5, 4, 3, 2, 1, 0]
fixed_phase_mask_U2 = [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0]
'''
'''
initial_state = [[0,2,0]]
pulse_train_U1 =  [[0,2,0], [0,2,0], [0,3,-1]]
fractions_U1 = [1, 1/3, 1/2]
simulated_phase_mask_U1 = [0, 0, 0]
fixed_phase_mask_U1 = [1, 0, 0]
pulse_train_U2 =  [[0,3,-1], [0,2,0], [0,4,-2]]
#fractions_U2 = [1/2, 1/3, 1]
fractions_U2 = [0, 0, 0]
simulated_phase_mask_U2 = [2, 1, 0]
fixed_phase_mask_U2 = [1, 1, 0]
probe_trans =  [[0,4,-2], [0,2,0], [-1,3,-1]]
'''

initial_state = [[0,3,2]]
pulse_train_U1 =  [[0, 3, 2], [0, 2, 2]]
fractions_U1 = [1/2, 1]
simulated_phase_mask_U1 = [0, 0]
fixed_phase_mask_U1 = [1, 0]
pulse_train_U2 =  [[0, 2, 2], [0, 3, 2], [0, 4, -2]]
fractions_U2 = [1, 1/2, 1]
#fractions_U2 = [0, 0, 0, 0, 0, 0]
simulated_phase_mask_U2 = [0, 1, 0]
fixed_phase_mask_U2 = [1, 0, 0]
probe_trans =  [[0,3,2],[0,4,-2],[0,2,2]]


# 3Level Bused Qudit ramsey

#initial_state = [[0,4,-1]]

#pulse_train_U1 = [[0,4,-1],[0,3,1],[0,4,-1],[0,3,2]]
#fractions_U1 =     [1/3,      1,      1/2,        1]

#pulse_train_U2 = [[0,3,2],[0,4,-1],[0,3,2],[0,3,1],[0,4,-1],[0,3,1]]
#fractions_U2 =   [1,        1/2,      1,        1,       1/3,      1]
 
#probe_trans = [[0,4,-1],[0,3,1],[0,3,2]]


#simulated_phase_mask_U1=  [0,0,0,0]  
#simulated_phase_mask_U2 = [0,2,0,0,1,0]

#fixed_phase_mask_U1 =     [1, 0, 1, 0] 
#fixed_phase_mask_U2 =     [1, 0, 0, 1, 0, 0]

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

pulse_train = pulse_train_U1 + pulse_train_U2
fractions = fractions_U1 + fractions_U2
simulated_phase_mask = simulated_phase_mask_U1 + simulated_phase_mask_U2
fixed_phase_mask = fixed_phase_mask_U1 + fixed_phase_mask_U2

phase_shifts = zip(simulated_phase_mask,fixed_phase_mask)

D = 2
detunings = np.zeros(len(probe_trans))

s12_level = initial_state[0][0]

periodicity = 100 #us
stop_time = 100
start_time = 0
time_step = 10

F1PumpTime = 2 #us
F1PumpReps = 50
InitReps = 0
fs = 2e9
threshold = 10

pulse_program = "Qudit_ramsey_experiment_bused"


        
def findPiTime_withfit_plotPD(ramsey_wait,stop_time,start_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
    fluor_ave = []
    pulse_time_list = []
    file_names_list = []
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break

        print('1')
        setEvaluation('Eval2')
        if do_calibrations:
            delta = 0
            ramsey_real_wait_time = 150
            freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
            freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        setEvaluation('Eval3')

        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))

        pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
        pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
        pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
        pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
        pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]


        init_trans = list_of_inits[s12_level+2]
        init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
        init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        init_pulse_time = sum(init_times_array) 

        set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))

        initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))

        pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))

        for idx, delta in enumerate(detunings):
            set_freq[idx] = set_freq[idx] + delta

        for delta in detunings:
            pulse_train_frequencies[0] = pulse_train_frequencies[0] + delta

        pi_time_initial_state = list(Get_1762_PiTimes(initial_state,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

        pi_time_pulse_train = list(Get_1762_PiTimes(pulse_train,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

        pi_times_probe_trans = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))



        print(pulse_train)

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

        corrected_pulse_train_times = []

        for i,_ in enumerate(fixed_phase_mask):
            if np.isnan(_):
                corrected_pulse_train_times.append(ramsey_wait)
            else:
                frac = fractions[i]
                corrected_pulse_train_times.append(2*pi_time_pulse_train[i]*np.arcsin(np.sqrt(frac))/np.pi)

        print(corrected_pulse_train_times)

        Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
        if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(corrected_pulse_train_times):
            setGlobal("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us")

        half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
        if not "%s"%half_pi_time_dummy == "%s us"%sum(corrected_pulse_train_times):
            setGlobal("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us")
        print('2')

# Phase Calculations ===================================================================

        phases = []
        for i,_ in enumerate(fixed_phase_mask):
            if np.isnan(_):
                phases.append(0)
            else:
                pi_phase = fixed_phase_mask[i]
                real_phase = simulated_phase_mask[i]
                x = (2 * np.pi * pulse_time * real_phase / periodicity)
                y = pi_phase*np.pi
                print(i,x,y)
                phases.append(x + y)
            
        full_phases = phases
        print(full_phases)
#=======================================================================================
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
#---------------------------------------------------------------------------- S1/2 inits
        matlab_init_freqs = matlab.double(init_freqs_array)
        matlab_init_times = matlab.double(init_times_array)
#---------------------------------------------------------------------------- D5/2 init pulse
        print(initial_state_frequency)
        print(pi_time_initial_state)



        matlab_initial_state_freq = matlab.double(initial_state_frequency)
        matlab_initial_state_pulse_time = matlab.double(pi_time_initial_state)
        matlab_initial_state_phases = matlab.double([0])
#---------------------------------------------------------------------------------------------------------- pulse_train
        print(pulse_train_frequencies)
        print(corrected_pulse_train_times)
        matlab_pulse_train_freqs = matlab.double(pulse_train_frequencies)
        matlab_pulse_train_times = matlab.double(corrected_pulse_train_times)
        matlab_pulse_train_phases = matlab.double(full_phases)

        print(len(pulse_train_frequencies),len(corrected_pulse_train_times),len(full_phases))

        #for i in range(15):
        #    print(pulse_train_frequencies[i],corrected_pulse_train_times[i])

#---------------------------------------------------------------------------- Uploading
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])
        print('4.5')
        seg_num = 1
        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1 
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
        print('5')
        seg_num = seg_num + 1
        eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)



        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence

        seg_num = seg_num + 1

        eng.Pulse_upload_with_phases(matlab_pulse_train_freqs,matlab_pulse_train_times,matlab_pulse_train_phases,fs,seg_num,nargout = 0)
        if scriptIsStopped():
            break
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
        print('6')
        # Readout pulses
        for idx, freq in enumerate(set_freq):

            matlab_ro_freq = matlab.double([freq])
            matlab_ro_time = matlab.double([pi_times_probe_trans[idx]])
            print(seg_num,[freq],[pi_times_probe_trans[idx]])
            seg_num = seg_num + 1
            eng.Pulse_upload(matlab_ro_freq,matlab_ro_time,fs,seg_num,power_factor,nargout = 0)
            if scriptIsStopped():
                break
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence

#-------------------------------------------------------------------------------------------------------------------------
        print('7')

        eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)
        seq_num = 6

        for idx, freq in enumerate(set_freq):
            seq_num = seq_num + 1
            string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,0"
            eng.SendAWGCommand(string, nargout=0)
            seq_num = seq_num + 1
            string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,1"
            eng.SendAWGCommand(string, nargout=0)

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

        data = getAllData()
        herald_data = data['PMT Index 0'][1]
        print(herald_data)
        ket1_data = data['PMT Index 1'][1]
        print(ket1_data)
        ket2_data = data['PMT Index 2'][1]
        print(ket2_data)

        arrays = []
        for idx,herald_outcome in enumerate(herald_data):
            if herald_outcome < threshold and ket1_data[idx] < threshold:
                arrays.append(ket2_data[idx])
        mean_value = np.mean(np.array(arrays)<threshold)

        if pulse_time == start_time:
            matching_files = glob.glob(pattern)
            matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
            file_path = matching_files[-1]
            chunks = file_path.split('\\')
            #print(chunks[-1])        
            fname = chunks[-1]
            file_names_list.append(fname)
        else: 
            filename = file_names_list[-1]
            parts = filename.split('_')
            original_number_str = parts[-1]
            num_digits = len(original_number_str)
            number = int(original_number_str) + 1
            new_number_str = str(number).zfill(num_digits)
            new_filename = '_'.join(parts[:-1]) + f'_{new_number_str}'
            file_names_list.append(new_filename)

        if np.isnan(mean_value):
            mean_value = 1
        PD = mean_value
        print("PD is", PD)
        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD,'Qudit Ramsey, 0 state', plotStyle=2)

        pulse_time = pulse_time + time_step
        freq_string = str(round(set_freq[0],3)).replace('.','p')
        combined_data = zip(pulse_time_list,fluor_ave)
        filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_bussed_qubit_WaitTime{ramsey_wait}us_{repeat_ind}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{pulse_train}\n")
            file.write(f"{[f_offset,f_upper]}\n")
            file.write(f"{pi_time_pulse_train}\n")
            file.write(f"{fractions_U1}\n")
            file.write(f"{fractions_U2}\n")
            file.write(f"{phases}\n")
            file.write(f"{file_names_list}\n")

    closeTrace('Qudit Ramsey, 0 state')
    freq_string = str(round(set_freq[0],3)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_bussed_qubit_WaitTime{ramsey_wait}us_{repeat_ind}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{pulse_train}\n")
        file.write(f"{[f_offset,f_upper]}\n")
        file.write(f"{pi_time_pulse_train}\n")
        file.write(f"{fractions_U1}\n")
        file.write(f"{fractions_U2}\n")
        file.write(f"{phases}\n")
        file.write(f"{file_names_list}\n")


# looping over different wait times
for repeat_ind in range(repeat_experiments):
    for wait_time in ramsey_wait_times:
        print('this worked')
        setEvaluation('Eval3')
        pi_time = findPiTime_withfit_plotPD(wait_time,stop_time,start_time, time_step, threshold, pulse_program, script_functions)
        print(pi_time)
        setEvaluation('Eval2')
        #with open(output_file_pitimes,'a') as outfile:
        #    outfile.write(f'{pi_time}\n')

eng.quit()