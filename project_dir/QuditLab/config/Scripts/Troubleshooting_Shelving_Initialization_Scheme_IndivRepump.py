#Troubleshooting_Shelving_Initialization_Scheme_IndivRepump.py created 2024-03-22 13:27:17.984673

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
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

#Probe_freqs = [620.408,623.057,621.372,545.237,609.538,0]
#Probe_times = [21,24,40,59.2,23.1,70]

Probe_freqs = [609.538]
Probe_times = [23.1]

num_comp = 5

F1PumpTime = 30 #us
F1PumpReps = 120
InitReps = 0
AWG_Power = 3
fs = 1.92192e9
threshold = 12
total_init_reps = F1PumpReps + InitReps



# mp2
init_freqs_array = [545.753,600.617,594.588,606.588]
init_times_array = [88,55.1,103.1,66.1] #us

# mp1
#init_freqs = [602.421,600.539,594.505,603.636]
#init_times = [100,65,140,60] #us

# m0
#init_freqs = [602.412,600.526,597.44,619.746]
#init_times = [100,65,100,90] #us

# mn1
#init_freqs_array = [602.478,603.550,616.823,603.688]
#init_times_array = [100,40,100,60] #us

#init_freqs_array = [609.512]
#init_times_array = [400] #us

#mn2
#init_freqs_array= [610.531,603.534,616.824,603.676]
#init_times_array= [90,40,100,60] #us
init_times_tot=sum(init_times_array)


F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

# defining pulse times per initialisation frequency
Init_PulseTime1 = getGlobal('Init_Shelving_PulseTime_1')
if not "%s"%Init_PulseTime1 == init_times_array[0]:
    setGlobal("Init_Shelving_PulseTime_1", init_times_array[0], "us")

Init_PulseTime2 = getGlobal('Init_Shelving_PulseTime_2')
if not "%s"%Init_PulseTime1 == init_times_array[1]:
    setGlobal("Init_Shelving_PulseTime_2", init_times_array[1], "us")

Init_PulseTime3 = getGlobal('Init_Shelving_PulseTime_3')
if not "%s"%Init_PulseTime1 == init_times_array[2]:
    setGlobal("Init_Shelving_PulseTime_3", init_times_array[2], "us")

Init_PulseTime4 = getGlobal('Init_Shelving_PulseTime_4')
if not "%s"%Init_PulseTime1 == init_times_array[3]:
    setGlobal("Init_Shelving_PulseTime_4", init_times_array[3], "us")

os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_IndivRepump"

comp_reps = 0
        
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
    freq_string = str(round(set_freq,3)).replace('.','p')
    combined_data = zip(rep_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Sessions\\2024\\2024_03\\2024_03_18\\initialization_troubleshooting_data_{freq_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")

freq_num = 0
Probe_Freqs_and_times = zip(Probe_freqs,Probe_times)
for set_freq,pi_time in Probe_Freqs_and_times:
    if scriptIsStopped():
        eng.quit()
        break
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(2)
    
    PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
    if not "%s"%PulseTime_Dummy == "%s us"%pi_time:
        setGlobal("Shelving_Pulse_Time", pi_time, "us")

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

    matlab_set_freq = matlab.double([set_freq])
    matlab_probe_pulse_time = matlab.double([400])

    eng.Pulse_upload(matlab_init1_freq,matlab_init1_time,fs,1,power_factor,nargout = 0)
    eng.Pulse_upload(matlab_init2_freq,matlab_init2_time,fs,2,power_factor,nargout = 0)
    eng.Pulse_upload(matlab_init3_freq,matlab_init3_time,fs,3,power_factor,nargout = 0)
    eng.Pulse_upload(matlab_init4_freq,matlab_init4_time,fs,4,power_factor,nargout = 0)



    eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,5,power_factor_dbm,nargout = 0)

    eng.Pulse_upload_dummy(fs,6,nargout = 0) # Dummy 3rd sequence

    seg_num = 1
    for i in range(total_init_reps):
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
    #seg_num = seg_num + 1
    #string = f"SOUR:SEQ:DEF {seg_num},6,1,1"
    #eng.SendAWGCommand(string, nargout=0)

    #eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
    #eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)

    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

    setEvaluation('Eval3')

    pi_time = findPiTime_withfit_plotPD(num_comp,freq_num, threshold, pulse_program, script_functions)
    print(pi_time)
    setEvaluation('Eval2')
    freq_num = freq_num + 1
eng.quit()