#RFSoC_NBOP_RepsSweep.py created 2025-09-27 19:24:16.283256
import time
import json
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

import sys
import os
import datetime
import glob
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
#from Functions_Data import *
#from Functions_AWG import *
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
#from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

Side_band_cooling_reps = 0

s12_levels = [-2,-1,0,1,2]
#s12_levels = [0]


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

    probe_trans = list_of_probes[s12_level+2]

    set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    pulse_time = list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

    probe_time = sum(pulse_time)
    F1_pump_attentuations = [0]

    F1PumpTime_list = [1.5] #us
 
    F1PumpReps_list = [1, 3, 5, 7, 11, 15, 17, 20, 25,30, 40]
    #F1PumpReps_list = [20,30,40]
    InitReps = 0
    fs = 4e9
    threshold = 10

    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    init_trans = list_of_inits[s12_level+2]
 

    init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
    init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
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

    pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"


    init_row1 = [1, init_freqs_array, [0]*len(init_freqs_array), init_times_array, [0]*len(init_freqs_array), 0]
    dummy_row2 = [2, [800], [0], [0.01], [0], 0]

    probe_row3 = [3, set_freq, [0]*len(set_freq), pulse_time, [1]*len(set_freq), 1]
    dummy_row4 = [4, [800], [0], [0.01], [0], 0]
    rows = [init_row1,
            dummy_row2,
            probe_row3,
            dummy_row4]

    resp = upload_rows(rows, time_unit="us")
    print(json.dumps(resp, indent=2))  
            
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

            plotPoint(F1PumpReps, 1-PD, '1762 nm pi-time scan', plotStyle=2)

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
