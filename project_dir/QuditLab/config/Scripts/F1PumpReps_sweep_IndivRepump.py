#F1PumpReps_sweep_IndivRepump.py created 2024-04-10 15:14:45.964211

#F1PumpReps_sweep.py created 2024-03-14 11:42:09.052919

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

f_offset = 545.270964
f_upper = 623.091048

pitime_n2 = 21.031 # [-2, 4, -4]
pitime_n1 = 61.661 # [-2, 3, -3]
pitime_0 = 23.058 # [2, 4, 2]
pitime_p1 = 42.94 # [2, 4, 3]
pitime_p2 = 77.398 # [2, 4, 4]

#probe_trans = [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] #probe mp2
#probe_trans = [[2,4,3]] #probe mp2

#probe_trans = [[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]] #probe mp1
#probe_trans = [[0,4,1],[0,4,-2],[0,4,-1],[0,4,0],[0,3,0],[0,3,1]] #probe mp0
#probe_trans = [[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]] #probe mn1
probe_trans = [[-2,3,-1],[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]] #probe mn2
set_freq = list(Get_1762_EOM_Freqs(probe_trans,f_offset,f_upper))
pulse_time = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

#set_freq = [620.426,602.515, 613.145,607.616,545.772,551.906] #probe mn2
#pulse_time = [20,88,60,23,91,47]

# probe mn1
#set_freq = [623.0789,605.4738,600.6366,482.4255,610.5738,619.5910]
#pulse_time = [23.6,23.0,54.6,92.7,93.8,114.5]

# probe m0
#set_freq = [545.2578,531.8872,622.5442,618.4423,613.9035,603.5898]
#pulse_time = [57.2,217.1,27.6,77.6,34.0,36.9]

# probe mp1
#set_freq = [606.6089,597.5601,616.8544,621.3933,593.5576,534.8383]
#pulse_time = [62.6,71.0,84.8,39.2,84.8,100.3]

# probe mp2
#set_freq = [609.5583,603.7341,596.8321,544.5413,537.7889,619.8055]
#pulse_time = [22.6,39.6,74.7,157.1,63.2,76.3]

#set_freq = [609.5581]
#pulse_time = [22.2]

probe_time = sum(pulse_time)
F1_pump_attentuations = [30]
#F1PumpTime_list = [0.5,1,2,3,4,5,6,7,8,9,10,20,30] #us
F1PumpTime_list = [1] #us
#F1PumpReps_list = np.arange(0,300,20) 
#F1PumpReps_list = [0,2,4,6,8,10,20,30,40,50,60,70,80,90,100,120,150,200,250,300,350,400,500]
F1PumpReps_list = [0,10,20,30,40]
InitReps = 0
fs = 4e9
threshold = 12

#init_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,4,2]] #prepare mp2
#init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[1,4,2]] #prepare mp2
#init_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,4,-1]] #prepare mp2

#init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1
#init_trans = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]] #prepare mn2
init_trans = [[-1,3,-2],[0,3,0],[1,3,3],[2,4,4]] #prepare mn2

init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
#init_times_array = [60.4,56,170,100.3] #us

init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
print('this is init_times_array:')
print(init_times_array)
# mp2
#init_freqs_array = [545.775,619.5940,594.6104,606.6105]
#init_times_array = [60.4,170,56,100.3] #us

# mp1
#init_freqs_array = [602.5177,600.6362,594.6091,603.7321]
#init_times_array = [101.0,66.7,125.9,46.3] #us

# m0
#init_freqs_array = [602.5177,600.6362,597.5595,619.8034]
#init_times_array = [100.0,66.7,80.2,94.7] #us

# mn1
#init_freqs_array = [602.5178,603.5901,616.8548,603.7318]
#init_times_array = [80.2,29.8,84.8,39.6] #us

#init_freqs_array = [609.512]
#init_times_array = [400] #us

#mn2
#init_freqs_array= [610.574,603.590,616.855,603.732]
#init_times_array= [98,34,85,47] #us
init_pulse_time = sum(init_times_array)

#F1_Pump_Time = getGlobal('F1_PumpTime')
#if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
#    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

#F1_reps = getGlobal('F1_PumpReps')
#if not "%s"%F1_reps == 0:
#    setGlobal("F1_PumpReps", 0, "")

PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
if not "%s"%PulseTime_Dummy == "%s us"%probe_time:
    setGlobal("Shelving_Pulse_Time", probe_time, "us")

Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
if not "%s"%Init_PulseTime == init_pulse_time:
    setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_IndivRepump"



        
def F1_pump_reps_scan(idx_dummy, F1PumpReps_list,threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'F1 Pump Reps')

    fluor_ave = []
    plot_point = 0
    for F1PumpReps in F1PumpReps_list:

        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(2)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 1", nargout=0)#0 sets AWG to externally triggered mode
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])

        matlab_init1_freq = matlab.double([init_freqs_array[0]])
        matlab_init1_time = matlab.double([init_times_array[0]])
        matlab_init2_freq = matlab.double([init_freqs_array[1]])
        matlab_init2_time = matlab.double([init_times_array[1]])
        matlab_init3_freq = matlab.double([init_freqs_array[2]])
        matlab_init3_time = matlab.double([init_times_array[2]])
        matlab_init4_freq = matlab.double([init_freqs_array[3]])
        matlab_init4_time = matlab.double([init_times_array[3]])

        matlab_set_freq = matlab.double(set_freq)
        matlab_probe_pulse_time = matlab.double(pulse_time)

        eng.Pulse_upload(matlab_init1_freq,matlab_init1_time,fs,1,power_factor,nargout = 0)
        eng.Pulse_upload(matlab_init2_freq,matlab_init2_time,fs,2,power_factor,nargout = 0)
        eng.Pulse_upload(matlab_init3_freq,matlab_init3_time,fs,3,power_factor,nargout = 0)
        eng.Pulse_upload(matlab_init4_freq,matlab_init4_time,fs,4,power_factor,nargout = 0)

        eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,5,power_factor_dbm,nargout = 0)

        eng.Pulse_upload_dummy(fs,6,nargout = 0) # Dummy 3rd sequence

        seg_num = 1
        for i in range(F1PumpReps):
            for it in range(4):
                string = f"SOUR:SEQ:DEF {seg_num},6,1,1"
                eng.SendAWGCommand(string, nargout=0)
                seg_num = seg_num + 1
                table_position = it+1
                string = f"SOUR:SEQ:DEF {seg_num},{table_position},1,0"
                eng.SendAWGCommand(string, nargout=0)
                seg_num = seg_num + 1

        string = f"SOUR:SEQ:DEF {seg_num},6,1,1"
        eng.SendAWGCommand(string, nargout=0)
        seg_num = seg_num + 1
        string = f"SOUR:SEQ:DEF {seg_num},5,1,0"
        eng.SendAWGCommand(string, nargout=0)

        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

        eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

        eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

        if scriptIsStopped():
            break

        F1Pump_reps = getGlobal('F1_PumpReps')
        if not "%s"%F1Pump_reps == F1PumpReps:
            setGlobal("F1_PumpReps", F1PumpReps, "")

        #Init_reps = getGlobal('InitialisationReps')
        #if not "%s"%Init_reps == F1PumpReps:
        #    setGlobal("InitialisationReps", F1PumpReps, "")

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

        plotPoint(F1PumpReps, PD, '1762 nm pi-time scan', plotStyle=2)
        #plotPoint(plot_point, PD, '1762 nm pi-time scan', plotStyle=2)
        plot_point = plot_point + 10
    combined_data = zip(F1PumpReps_list,fluor_ave)
    F1_pump_str = str(F1PumpTime).replace(',','p')
    closeTrace('1762 nm pi-time scan')
    filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\F1_pump_reps_scan_F1_pump_time_{F1_pump_str}us_{F1_pump_attentuations[0]}AttOptPumpPower_mp2_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")

idx_dummy = 0
for F1PumpTime in F1PumpTime_list:

    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    att = F1_pump_attentuations[idx_dummy]
    os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 {att}')


    setEvaluation('Eval3')

    F1_pump_reps_scan(idx_dummy, F1PumpReps_list, threshold, pulse_program, script_functions)

    setEvaluation('Eval2')
    idx_dummy = idx_dummy + 1
eng.quit()