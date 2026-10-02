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

Side_band_cooling_reps = 0

s12_levels = [-2,-1,0,1,2]
#s12_levels = [0,1]


f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

for s12_level in s12_levels:

    list_of_probes = [[[-2,3,-1],[-2,2,-2],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]],
    [[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]],
    [[0,4,1],[0,4,-2],[0,4,-1],[0,4,0],[0,3,0],[0,3,1]],
    [[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]],
    [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] 
    ]

    #list_of_probes = [[[-2,3,-1],[-2,2,-2],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]],
    #[[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]],
    #[[0,2,2]],
    #[[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]],
    #[[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] 
    #]

    probe_trans = list_of_probes[s12_level+2]
    #probe_trans = [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] #probe mp2
    #probe_trans = [[1,1,1]] #probe mp1
    #probe_trans = [[0,4,1],[0,4,-2],[0,4,-1],[0,4,0],[0,3,0],[0,3,1]] #probe mp0
    #probe_trans = [[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]] #probe mn1
    #probe_trans = [[-2,3,-1],[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]] #probe mn2
    set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    pulse_time = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

    probe_time = sum(pulse_time)
    F1_pump_attentuations = [0]
    #F1PumpTime_list = [0.5,1,2,3,4,5,6,7,8,9,10,20,30] #us
    F1PumpTime_list = [1.5] #us
    #F1PumpReps_list = [60]
    F1PumpReps_list = [0,3,6,9,12,15,20,30,40,50,60,70,80,90,100]
    #F1PumpReps_list = [0,10,20,30,40,50,60]   
    #F1PumpReps_list = [40,50,60]#,50,80,100]
    InitReps = 0
    fs = 4e9
    threshold = 7
    #list_of_inits = [[[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]],
    #[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    #[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    #[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    #[[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]
    #]
    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    # giving a terrible list of init states to compare state choice here
    #list_of_inits = [[[-1,4,1],[0,3,2],[1,4,3],[2,4,4]],
    #[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    #[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    #[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    #[[-2,2,-2],[-1,3,-1],[0,2,-1],[1,4,-1]]
    #]

    #list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    #[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    #[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    #[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    #[[-2,3,-2],[-1,3,0],[0,3,2],[1,3,3]]
    #]

    init_trans = list_of_inits[s12_level+2]
    #init_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]] #prepare mp2
    #init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1
    #init_trans = [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]] #prepare m0
    #init_trans = [[-2,3,-1],[0,3,-1],[1,4,2],[2,4,3]] #prepare mn1
    #init_trans = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]] #prepare mn2

    init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
    init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    init_pulse_time = sum(init_times_array)

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
    if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
        setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"%0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us")

    PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
    if not "%s"%PulseTime_Dummy == "%s us"%probe_time:
        setGlobal("Shelving_Pulse_Time", probe_time, "us")

    Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
    if not "%s"%Init_PulseTime == init_pulse_time:
        setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)
    os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 0')

    pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"

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

    matlab_set_freq = matlab.double(set_freq)
    matlab_probe_pulse_time = matlab.double(pulse_time)
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

            
    def F1_pump_reps_scan(idx_dummy, F1PumpReps_list,threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        createTrace('1762 nm pi-time scan', 'Scan Data', xLabel=f'F1 Pump Reps')

        fluor_ave = []
        plot_point = 0
        for F1PumpReps in F1PumpReps_list:

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

            plotPoint(F1PumpReps, 1+PD, '1762 nm pi-time scan', plotStyle=2)
            #plotPoint(plot_point, PD, '1762 nm pi-time scan', plotStyle=2)
            plot_point = plot_point + 10
        combined_data = zip(F1PumpReps_list,fluor_ave)
        F1_pump_str = str(F1PumpTime).replace(',','p')
        s12_level_string = f"p{s12_level}" if s12_level >= 0 else f"n{-1*s12_level}"
        closeTrace('1762 nm pi-time scan')
        filename = f'Z:\\Lab Data\\Sessions\\{year}\\{year}_{month}\\{year}_{month}_{day}\\F1_pump_reps_scan_F1_pump_time_{F1_pump_str}us_100Exp_m{s12_level_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")

    idx_dummy = 0
    for F1PumpTime in F1PumpTime_list:

        F1_Pump_Time = getGlobal('F1_PumpTime')
        if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
            setGlobal("F1_PumpTime", F1PumpTime, "us")

        #att = F1_pump_attentuations[idx_dummy]
        #os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 {att}')


        setEvaluation('Eval3')

        F1_pump_reps_scan(idx_dummy, F1PumpReps_list, threshold, pulse_program, script_functions)

        setEvaluation('Eval2')
        idx_dummy = idx_dummy + 1
eng.quit()