#Test_initialized_pulse_time_scan.py created 2024-03-13 16:08:11.263692

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

set_freq = 609.524

stop_time = 35
start_time = 15
time_step = 1

F1PumpTime = 20 #us
F1PumpReps = 20
InitReps = 10
total_init_reps = F1PumpReps + InitReps
AWG_Power = 3
fs = 1.92192e9
threshold = 5

# mp2
init_freqs_array = [602.478,600.595,594.561,606.571]
init_times_array = [85.2,56.5,108.7,64.7] #us

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
init_pulse_time = sum(init_times_array) #us

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

os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_timed_inits"

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

matlab_init_freqs = matlab.double(init_freqs_array)
matlab_init_times = matlab.double(init_times_array)

matlab_set_freq = matlab.double([set_freq])
matlab_probe_pulse_time = matlab.double([400])
power_factor = matlab.double([1])
power_factor_dbm = matlab.double([1])

eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,power_factor_dbm,nargout = 0)


eng.Pulse_upload_dummy(fs,3,nargout = 0) # Dummy 3rd sequence



seg_num = 1

for i in range(total_init_reps):
    if scriptIsStopped():
        eng.quit()
        break

    string = f"SOUR:SEQ:DEF {seg_num},3,1,1"
    eng.SendAWGCommand(string, nargout=0)
    seg_num = seg_num + 1

    string = f"SOUR:SEQ:DEF {seg_num},1,1,0"
    eng.SendAWGCommand(string, nargout=0)
    seg_num = seg_num + 1


string = f"SOUR:SEQ:DEF {seg_num},3,1,1"
eng.SendAWGCommand(string, nargout=0)
seg_num = seg_num + 1
string = f"SOUR:SEQ:DEF {seg_num},2,1,0"
eng.SendAWGCommand(string, nargout=0)
seg_num = seg_num + 1
string = f"SOUR:SEQ:DEF {seg_num},3,1,1"
eng.SendAWGCommand(string, nargout=0)


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

        plotPoint(pulse_time, PD, '1762 nm pi-time scan', plotStyle=0)

        pulse_time = pulse_time + time_step
        
    closeTrace('1762 nm pi-time scan')

setEvaluation('Eval3')

pi_time = findPiTime_withfit_plotPD(stop_time, time_step, threshold, pulse_program, script_functions)
print(pi_time)
setEvaluation('Eval2')
#with open(output_file_pitimes,'a') as outfile:
#    outfile.write(f'{pi_time}\n')

eng.quit()
