#Initialized_pulsetime_Scan.py created 2024-02-08 11:29:39.976108

#Shelving_Find_Target_Resonance_Freq_PlotPD_Initialised.py created 2024-02-02 11:22:42.353979
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)

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
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

Side_band_cooling_reps = 0

#s12_level = 2
#set_freq = 609.536
probe_trans = [[-1,4,-3]]

"""
f_offset = 545.382016
f_upper = 623.184223

pitime_n2 = 24.938 # [-2, 4, -4]
pitime_n1 = 41.95 # [-2, 3, -3]
pitime_0 = 53.154 # [2, 4, 2]
pitime_p1 = 41.394 # [2, 4, 3]
pitime_p2 = 51.819 # [2, 4, 4]
"""

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

init_trans = list_of_inits[probe_trans[0][0]+2]
init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) 

set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
sideband_freqs = [0]
#Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

stop_time = 200
start_time = 0
time_step = 10

F1PumpTime = 2 #us
F1PumpReps = 50
InitReps = 0
fs = 4e9
threshold = 10

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

os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"

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

matlab_init_freqs = matlab.double(init_freqs_array)
matlab_init_times = matlab.double(init_times_array)

matlab_set_freq = matlab.double(set_freq)
matlab_probe_pulse_time = matlab.double([1000])
power_factor = matlab.double([1])
power_factor_dbm = matlab.double([1])

eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
eng.Pulse_upload_dummy(fs,2,nargout = 0)
eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)




eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 4,2,1,1", nargout=0)



#eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
#eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
#eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
#eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)

eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

        
def findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    pulse_time = start_time
    fluor_ave = []
    pulse_time_list = []
    while pulse_time <= stop_time:
        if scriptIsStopped():
            break



        PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
        if not "%s"%PulseTime_Dummy == "%s us"%pulse_time:
            setGlobal("Shelving_Pulse_Time", pulse_time, "us")
        time.sleep(0.2)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        print("data", data)
        ydata = data[1]
        print("ydata",ydata)
        fluor_bool = np.array(ydata) < threshold
        
        PD = np.mean(fluor_bool)
        print("PD is", PD)
        fluor_ave.append(PD)
        pulse_time_list.append(pulse_time)

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=2)

        pulse_time = pulse_time + time_step
        
    closeTrace('1762 nm pi-time scan')
    freq_string = str(round(set_freq[0],3)).replace('.','p')
    combined_data = zip(pulse_time_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\initialization_raw_data_{freq_string}_redsideband_{Side_band_cooling_reps}reps_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
setEvaluation('Eval3')

pi_time = findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions)
print(pi_time)
setEvaluation('Eval2')
#with open(output_file_pitimes,'a') as outfile:
#    outfile.write(f'{pi_time}\n')

eng.quit()