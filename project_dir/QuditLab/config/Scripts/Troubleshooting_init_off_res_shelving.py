#Troubleshooting_init_off_res_shelving.py created 2024-03-29 11:23:47.169628

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

f_offset = 545.260879
f_upper = 623.078719

pitime_n2 = 20.3088
pitime_n1 = 59.5807
pitime_0 = 22.5572
pitime_p1 = 40.2741
pitime_p2 = 73.4768

probe_trans = [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] #probe mp2
#probe_trans = [[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]] #probe mp1

Probe_freqs = list(Get_1762_EOM_Freqs(probe_trans,f_offset,f_upper))
Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

# probing mp2
#Probe_freqs = [602.515, 620.426, 613.145,607.616,545.772,551.906]
#Probe_freqs = [0]
#Probe_times = [88,20,60,23,91,47]
sum_probe_time = sum(Probe_times) # us
#Probe_times = [70]
num_comp = 10

F1PumpTime = 1 #us
F1PumpReps = 30
InitReps = 0
AWG_Power = 3
#fs = 1.92192e9
fs = 4e9
threshold = 12

reps_list = [0,10,20,30,50,75]

# mp2
#init_freqs_array = [545.766,600.622,594.590,606.598]
#init_times_array = [97,59,106,68] #us

#off_res_freqs_array = [0,545.753,600.622,594.590,606.598]
#off_res_times_array = [70,88,59,106,68] #us

# mp1
#init_freqs_array = [602.505,600.622,594.590,603.719]
#init_times_array = [85,59,106,41] #us

#off_res_freqs_array = [0,602.505,600.622,594.590,603.719]
#off_res_times_array = [70,85,59,106,41] #us

# m0

#init_freqs_array = [602.505,600.622,597.542,619.803]
#init_times_array = [85,58,74,75] #us

#off_res_freqs_array = [0,602.505,600.622,597.542,619.803]
#off_res_times_array = [70,85,58,74,75] #us

# new attempt at init freqs - didn't work!
#init_freqs_array = [545.759,601.916,551.142,600.623]
#init_times_array = [92,76,71,56] #us

# mn1
#init_freqs_array = [602.505,603.578,616.852,603.720]
#init_times_array = [85,31,80,41] #us

#off_res_freqs_array = [0,602.505,603.578,616.852,603.720]
#off_res_times_array = [70,85,31,80,41] #us

#mn2
#init_freqs_array= [610.572,603.588,616.854,603.730]
#init_times_array= [98,34,85,47] #us

# new mp2 init trans
#init_trans = [[-2,3,-3],[0,2,0],[-1,3,1],[1,2,2]] #prepare mp2
# old mp2 init trans
init_trans = [[-2,3,-1],[0,3,2],[-1,3,0],[1,4,2]] #prepare mp2
#init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1

init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
#init_times_array = [60.4,56,170,100.3] #us

init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

# mp2
#init_freqs_array = [545.775,619.5940,594.6104,606.6105]

#off_res_trans = [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] # off res pumping mp2
#off_res_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,4,2],[2,4,2]] # off res pumping mp2
off_res_trans = [[0,3,2],[1,4,2]] # off res pumping mp2
off_res_freqs_array = list(Get_1762_EOM_Freqs(off_res_trans,f_offset,f_upper))
off_res_times_array = list(Get_1762_PiTimes(off_res_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
#off_res_times_array = [3000,3000,3000,3000,3000]
#off_res_freqs_array= [0,602.505,610.567,603.578,616.852,603.720]
#off_res_times_array= [70,85,96,31,80,41] #us

#off_res_freqs_array= [0]
#off_res_times_array= [70] #us

init_pulse_time = sum(init_times_array) #us


PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
if not "%s"%PulseTime_Dummy == "%s us"%sum_probe_time:
    setGlobal("Shelving_Pulse_Time", sum_probe_time, "us")


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



#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_off_res_shelve"


        
def findPiTime_withfit_plotPD(set_freq,reps_list,freq_num, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Pulse Time (us)')

    fluor_ave = []
    rep_list = []
    for off_res_reps in reps_list:

        Init_reps = getGlobal('InitialisationReps')
        if not "%s"%Init_reps == off_res_reps:
            setGlobal("InitialisationReps", off_res_reps, "")

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
        rep_list.append(off_res_reps)

        plotPoint(off_res_reps, PD, '1762 nm pi-time scan', plotStyle=2)


    closeTrace('1762 nm pi-time scan')
    freq_string = str(round(set_freq,3)).replace('.','p')
    probe_string = str(round(Probe_freqs[0],3)).replace('.','p')
    combined_data = zip(rep_list,fluor_ave)
    filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\initialization_troubleshooting_offres_pumping_{freq_string}_500us_data_probefreq_{probe_string}_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
freq_num = 0


Probe_Freqs_and_times = zip(off_res_freqs_array,off_res_times_array)
for set_freq,pi_time in Probe_Freqs_and_times:
    eng.SendAWGCommand("RES", nargout=0)
    time.sleep(2)

    pi_time  = 500
    off_res_time_dummy = getGlobal('ket_0').magnitude
    if not "%s"%off_res_time_dummy == "%s us"%pi_time:
        setGlobal("ket_0", pi_time, "us")


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

    matlab_probe_pulse_time = matlab.double([pi_time])

    matlab_probe_freq = matlab.double(Probe_freqs)
    matlab_probe_time = matlab.double(Probe_times)


    power_factor = matlab.double([1])
    power_factor_dbm = matlab.double([1])

    eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)
    eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,power_factor_dbm,nargout = 0)


    eng.Pulse_upload_dummy(fs,3,nargout = 0) # Dummy 3rd sequence
    eng.Pulse_upload(matlab_probe_freq,matlab_probe_time,fs,4,power_factor_dbm,nargout = 0)

    eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 5,4,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 6,3,1,1", nargout=0)

    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

    setEvaluation('Eval3')

    pi_time = findPiTime_withfit_plotPD(set_freq,reps_list,freq_num, threshold, pulse_program, script_functions)
    print(pi_time)
    setEvaluation('Eval2')
    freq_num = freq_num + 1
eng.quit()