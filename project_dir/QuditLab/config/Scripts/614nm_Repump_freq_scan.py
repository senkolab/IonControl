#614nm_Repump_freq_scan.py created 2024-03-27 18:15:20.522049

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

step = 0.00001

repump_freq = 487.99032
repump_freq_scan_range = 50
start_freq = repump_freq - step*repump_freq_scan_range
stop_freq = repump_freq + step*repump_freq_scan_range

repump_freq_list = np.arange(start_freq,stop_freq,step)

f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')
transition = [[2,4,2]]
freq_peak = list(Get_1762_EOM_Freqs_an1an2(transition,f_offset,f_upper))[0]

pulse_time = 45

F1_pump_attentuations = [0]
F1PumpTime_list = [0] 

F1PumpReps = 1
F1PumpTime = 1 
att = 0

InitReps = 0
AWG_Power = 3
fs = 4e9
threshold = 8
AWG_mode = 0
if AWG_mode == 0:
    # set this mode to 1 if you want to do a plot PD when initialising in any state in S1/2 F=2

    AWG_RunMode = 1 # 0 for triggered mode, 1 for continuous mode
    use_AWG = True # this must be set to False when AWG_mode = 1
    AWG_Power_dBm = 1.5
    # below is the pulse time for the PLL pulse when AWG_mode = 1, the AWG pulse time (for prep) is set via Init_Pulse_Time
    SetPulseTime = 45.8 #us

    PulseTime = getGlobal("Shelving_Pulse_Time")
    if not "%s"%PulseTime == "%s us"%SetPulseTime:
        setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

    OptPumpTime = getGlobal("OpticalPumpTimeGlobal")
    if not "%s"%OptPumpTime == "%s us"%1000:
        setGlobal("OpticalPumpTimeGlobal", 1000, "us")

    AWG_Flag = getGlobal("UseAWG_Flag")
    if not "%s"%AWG_Flag == "%s us"%use_AWG:
        setGlobal("UseAWG_Flag", use_AWG, "")

    AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
    if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
        setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

    AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
    if not int(AWG_mode_curr) == AWG_mode:
        setGlobal("AWG1_Mode", AWG_mode, "")

    AWG_runmode_curr = getGlobal("AWG1_Trig_Cont_Run_Mode").magnitude
    if not int(AWG_runmode_curr) == AWG_RunMode:
        setGlobal("AWG1_Trig_Cont_Run_Mode", int(AWG_RunMode), "")

    Init_reps_zero = getGlobal('InitialisationReps')
    if not "%s"%Init_reps_zero == 0:
        setGlobal("InitialisationReps", 0, "")

    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
        setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")

else: 
    # mp2
    #init_freqs_array = [602.500,600.617,594.588,606.592]
    #init_times_array = [83.8,54.1,112.1,67.1] #us

    # mp1
    #init_freqs = [602.421,600.539,594.505,603.636]
    #init_times = [100,65,140,60] #us

    # m0
    init_freqs_array = [602.507,600.627,597.551,619.787]
    init_times_array = [78,54,72,71] #us

    # mn1
    #init_freqs_array = [602.478,603.550,616.823,603.688]
    #init_times_array = [100,40,100,60] #us

    #init_freqs_array = [609.512]
    #init_times_array = [400] #us

    #mn2
    #init_freqs_array= [610.558,603.573,616.842,603.715]
    #init_times_array= [91.6,31.4,79.4,42.3] #us
    init_pulse_time = sum(init_times_array) #us

    #F1_Pump_Time = getGlobal('F1_PumpTime')
    #if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    #    setGlobal("F1_PumpTime", F1PumpTime, "us")


    F1_Pump_Time = getGlobal('F1_PumpTime')
    if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")


    os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 {att}')



    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    #F1_reps = getGlobal('F1_PumpReps')
    #if not "%s"%F1_reps == 0:
    #    setGlobal("F1_PumpReps", 0, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

    PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
    if not "%s"%PulseTime_Dummy == "%s us"%pulse_time:
        setGlobal("Shelving_Pulse_Time", pulse_time, "us")

    Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
    if not "%s"%Init_PulseTime == init_pulse_time:
        setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

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

    eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 2,3,1,1", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 3,2,1,0", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEF 4,3,1,1", nargout=0)

    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

    eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

    eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)


pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137_repump_test"

def Repump_freq_scan(repump_freq,repump_freq_scan_range, repump_freq_list,threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
    createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'Repump freq')

    fluor_ave = []

    for freq in repump_freq_list:

        if scriptIsStopped():
            break


        #Freq614 = getGlobal('ShelvingRepumpFreq')
        #if not "%s"%Freq614 == freq:
        #    setGlobal("ShelvingRepumpFreq", freq, "THz")

        #time.sleep(13)

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        print("data", data)
        ydata = data[1]
        print("ydata",ydata)
        threshold = 8
        fluor_bool = np.array(ydata) < threshold
        
        PD = np.mean(fluor_bool)
        print("PD is", PD)
        fluor_ave.append(PD)

        plotPoint(freq, PD, '1762 nm pi-time scan', plotStyle=2)
    combined_data = zip(repump_freq_list,fluor_ave)
    F1_pump_str = str(F1PumpTime).replace(',','p')
    closeTrace('1762 nm pi-time scan')
    filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\Repump_freqs_{dt_string}.txt'
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")


setEvaluation('Eval3')

Repump_freq_scan(repump_freq,repump_freq_scan_range, repump_freq_list, threshold, pulse_program, script_functions)

setEvaluation('Eval2')

eng.quit()