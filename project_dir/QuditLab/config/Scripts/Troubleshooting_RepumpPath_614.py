#Troubleshooting_RepumpPath_614.py created 2024-04-11 11:15:23.825309

#Troubleshooting_Shelving_Initialization_Scheme.py created 2024-03-20 13:09:07.659081

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

f_offset = 545.277190
f_upper = 623.095702

pitime_n2 = 21.031 # [-2, 4, -4]
pitime_n1 = 61.661 # [-2, 3, -3]
pitime_0 = 23.058 # [2, 4, 2]
pitime_p1 = 42.94 # [2, 4, 3]
pitime_p2 = 77.398 # [2, 4, 4]

num_comp = 5
F1PumpTime = 1 #us
F1PumpReps = 80
InitReps = 0
fs = 4e9
threshold = 12

# which D state to repump from?
shelving_trans = [[1,3,3]]
shelving_freq = list(Get_1762_EOM_Freqs(shelving_trans,f_offset,f_upper))
shelving_time = list(Get_1762_PiTimes(shelving_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

#init_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,4,2]] #prepare mp2
init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1
#init_trans = [[-2,3,-1],[-1,3,0],[1,3,2],[2,4,0]] #prepare m0
#init_trans = [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]] #prepare mn1
#init_trans = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]] #prepare mn2
init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) #us



# probing all 5 S12 states population one by one
#probe_trans = [
#[[-2,3,-1],[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]],
#[[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]],
#[[0,4,1],[0,4,-2],[0,4,-1],[0,4,0],[0,3,0],[0,3,1]],
#[[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]],
#[[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]]
#]

probe_trans = [[[-2,3,-1]],
[[-1,3,0]],
[[0,4,-2]],
[[1,4,2]],
[[2,4,2]]]

Probe_freqs = [
list(Get_1762_EOM_Freqs(probe_trans[0],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[1],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[2],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[3],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[4],f_offset,f_upper))
]
Probe_times = [
list(Get_1762_PiTimes(probe_trans[0],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[1],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[2],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[3],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[4],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
]


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

Shelv_time_dummy = getGlobal('ket_0')
if not "%s"%Shelv_time_dummy == shelving_time[0]:
    setGlobal("ket_0", shelving_time[0], "us")

os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_repump_test"

freq_string = str(round(shelving_freq[0],3)).replace('.','p')
filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\repump_path_troubleshooting_mp1InitState_{freq_string}_{dt_string}.txt'
with open(filename,'w'):
    pass

def findPiTime_withfit_plotPD(num_comp,freq_num, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')
    comp_reps = freq_num * num_comp
    max_reps = freq_num * num_comp + num_comp
    fluor_ave = []
    rep_list = []
    while comp_reps <= max_reps:
        if scriptIsStopped():
            eng.quit()
            break

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
        rep_list.append(comp_reps)

        plotPoint(comp_reps, PD, '1762 nm pi-time scan', plotStyle=2)

        comp_reps = comp_reps + 1
        
    closeTrace('1762 nm pi-time scan')

    combined_data = zip(rep_list,fluor_ave)
    
    with open(filename,'a') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
            
freq_num = 0
Probe_Freqs_and_times = zip(Probe_freqs,Probe_times)
for set_freq,pi_time in Probe_Freqs_and_times:
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(2)
    probe_pulse_time = sum(pi_time)
    PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
    if not "%s"%PulseTime_Dummy == "%s us"%probe_pulse_time:
        setGlobal("Shelving_Pulse_Time", probe_pulse_time, "us")

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
    matlab_probe_pulse_time = matlab.double(pi_time)

    matlab_shelving_freq = matlab.double(shelving_freq)
    matlab_shelving_time = matlab.double(shelving_time)

    power_factor = matlab.double([1])
    power_factor_dbm = matlab.double([1])

    eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
    eng.Pulse_upload(matlab_shelving_freq,matlab_shelving_time,fs,2,power_factor_dbm,nargout = 0)
    eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)


    eng.Pulse_upload_dummy(fs,4,nargout = 0) # Dummy 3rd sequence

    eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 2,4,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 5,3,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 6,4,1,1", nargout=0)

    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

    setEvaluation('Eval3')

    findPiTime_withfit_plotPD(num_comp,freq_num, threshold, pulse_program, script_functions)

    setEvaluation('Eval2')
    freq_num = freq_num + 1
eng.quit()