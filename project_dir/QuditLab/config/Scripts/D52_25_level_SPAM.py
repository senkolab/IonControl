#D52_25_level_SPAM.py created 2024-03-01 16:24:43.974455

import time
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(2)

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

use_an1_an2 = True

D = 25
#init_kets = [24]
#init_kets = list(np.flip(range(0,25)))
init_kets = range(0,25)
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

f_offset = 545.3702
f_upper = 623.181321

pitime_n2 = 24.3 # [-2, 4, -4]
pitime_n1 = 43.7 # [-2, 3, -3]
pitime_0 = 50.9 # [2, 4, 2]
pitime_p1 = 37.75 # [2, 4, 3]
pitime_p2 = 49.98 # [2, 4, 4]

if not use_an1_an2:
    recent_init_files = glob.glob(fr'Z:\Lab Data\D52_Calibration_Ba137\initialization_freqs_file\initialization_freqs_*.txt')
    print('here is', recent_init_files[-1])
    latest_init_file = recent_init_files[-1] 

    recent_spam_freq_files = glob.glob(fr'Z:\Lab Data\25lvl_SPAM\Frequency_files\25lvl_SPAM_Freqs_with_piTimes_and_init_states_*.txt')
    print('here is', recent_spam_freq_files[-1])
    latest_spam_freq_file = recent_spam_freq_files[-1] 

    input_init_file = latest_init_file

    input_file = latest_spam_freq_file

    with open(input_file,'r') as freq_file:
        SPAM_list = []
        for idx, line in enumerate(freq_file):
            parts = line.strip().split(', ')
            centre_freq, pulse_time, init_state = map(float, parts)
            SPAM_list.append([centre_freq, pulse_time, init_state])

    with open(input_init_file,'r') as freq_file:
        init_freqs = []
        pulse_times = []
        init_state = []
        for idx, line in enumerate(freq_file):
            parts = line.strip().split(', ')
            centre_freq, pulse_time, init_state = map(float, parts)
            init_freqs.append(centre_freq)
            pulse_times.append(pulse_time)
else:

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