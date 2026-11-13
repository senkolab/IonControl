#RFSoC_FastFive_Calibration.py created 2025-11-20 08:55:23.023898

#New_Shelving_Calibration_ParamEstimated_Initialised.py created 2024-04-26 16:49:34.435318

#Shelving_Freq_PiTime_Calibration_PlotPD_ParamEstimated_Initialised.py created 2024-04-08 17:31:06.613195

do_pi_time_calibration = True
line_trigger = True
check_3pt_coherence = True
do_rough_scan = True
steps_per_pi_time = 4

import time
import sys
import os
import datetime
import glob
import numpy as np
import random
    
import json, urllib.request
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

from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
#from Functions_RFSoC_RamseyCalibration import *
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

# set pulse program for pi-time scans
pulse_program = "Hareld_pulse_time_scan"
#pulse_program = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

pitime_n2 = getGlobal('pitime_n2') # [-1, 4, -3]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [0, 2, 0]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]
ref_pitimes_list = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

threshold = 9

F1PumpTime = 0.5 #us
F1PumpReps = 20
InitReps = 0
#fs = 4e9

Side_band_cooling_reps = 0

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")

f_offset_index = [0,2,0]
f_upper_index = [0,4,-2]

# do frequency references first
#pitime_ref_index = [[0,2,0],[-1,4,-3],[-2,3,-3],[2,4,3],[2,4,4]]
#list_var_names = ['pitime_0','pitime_n2','pitime_n1','pitime_p1','pitime_p2']

pitime_ref_index = [[0,2,0],[0,4,-2],[-2,3,-3],[2,4,3],[2,4,4]]
list_var_names = ['pitime_0','pitime_n2','pitime_n1','pitime_p1','pitime_p2']

#pitime_ref_index = [[2,4,4]]
#list_var_names = ['pitime_p2']
#pitime_ref_index = [[0,2,0]]

init_n2_index = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]]
init_n1_index = [[-2,3,-1],[0,3,0],[1,4,2],[2,4,3]]
init_0_index = [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]]
init_p1_index = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]]
init_p2_index = [[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

init_freqs_n2 = list(Get_1762_EOM_Freqs_an1an2(init_n2_index,f_offset,f_upper))
init_freqs_n1 = list(Get_1762_EOM_Freqs_an1an2(init_n1_index,f_offset,f_upper))
init_freqs_0 = list(Get_1762_EOM_Freqs_an1an2(init_0_index,f_offset,f_upper))
init_freqs_p1 = list(Get_1762_EOM_Freqs_an1an2(init_p1_index,f_offset,f_upper))
init_freqs_p2 = list(Get_1762_EOM_Freqs_an1an2(init_p2_index,f_offset,f_upper))

init_times_n2 = list(get_pi_times(init_n2_index,ref_pitimes_list))
init_times_n1 = list(get_pi_times(init_n1_index,ref_pitimes_list))
init_times_0 = list(get_pi_times(init_0_index,ref_pitimes_list))
init_times_p1 = list(get_pi_times(init_p1_index,ref_pitimes_list))
init_times_p2 = list(get_pi_times(init_p2_index,ref_pitimes_list))

init_freqs_array = [init_freqs_n2,init_freqs_n1,init_freqs_0,init_freqs_p1,init_freqs_p2]
init_times_array = [init_times_n2,init_times_n1,init_times_0,init_times_p1,init_times_p2]

LT_dummy = getGlobal('LineTriggerBoolean')
if not "%s"%LT_dummy == int(line_trigger):
    setGlobal("LineTriggerBoolean", int(line_trigger), "")

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

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == 0:
    setGlobal("Sideband_Cooling_Reps", 0, "")

if do_rough_scan:
    freq_offset = run_fast_calibration(script_functions,0,25,target_transition=f_offset_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=False)
    [pi_time] = get_pi_times([f_offset_index],ref_pitimes_list)
    f_offset_dummy = getGlobal('f_offset')
    if not "%s"%f_offset_dummy == freq_offset:
        setGlobal("f_offset", freq_offset, "")
    print('020 pi time', pi_time)    

    freq_upper = run_fast_calibration(script_functions,0,25,target_transition=f_upper_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=True)
    [pi_time] = get_pi_times([f_upper_index],ref_pitimes_list)
    f_upper_dummy = getGlobal('f_upper')
    if not "%s"%f_upper_dummy == freq_upper:
        setGlobal("f_upper", freq_upper, "")


def find_freq_target(index, dt_string, threshold, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped,setEvaluation = script_functions

    real_wait_time = 200
    delta = 0
    

    #with open(output_file_freqs,'a') as outfile:
        
    freq_offset = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=f_offset_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=check_3pt_coherence)
    #[pi_time] = get_pi_times([[0,2,0]],ref_pitimes_list)
    #outfile.write(f'{np.round(freq_offset,6)}, {np.round(pi_time,3)}, {[0,2,0]}\n')
    f_offset_dummy = getGlobal('f_offset')
    if not "%s"%f_offset_dummy == freq_offset:
        setGlobal("f_offset", freq_offset, "")
    freq_target = freq_offset
    

    #with open(output_file_freqs,'a') as outfile:
    freq_upper = run_fast_calibration(script_functions,delta,real_wait_time,target_transition=f_upper_index,f_offset_input=None,f_upper_input=None,ref_pitimes=None,check_3pt_coherence=check_3pt_coherence)
    #[pi_time] = get_pi_times([[-1,4,-3]],ref_pitimes_list)
    #outfile.write(f'{np.round(freq_upper,6)}, {np.round(pi_time,3)}, {[-1,4,-3]}\n')
    f_upper_dummy = getGlobal('f_upper')
    if not "%s"%f_upper_dummy == freq_upper:
        setGlobal("f_upper", freq_upper, "")
    freq_target = freq_upper
        
    return freq_offset, freq_upper


setEvaluation('Eval3')

#find_f0_f1_fast_cal(dt_string, threshold, script_functions)

#setEvaluation('Eval2')

for i in range(1000):

    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_file_freqs = fr'Z:\\Lab Data\\Magnetic_field_measurement\\Magnetic_field_measurement_{dt_string}.txt'

    freq_offset, freq_upper = find_freq_target(i,dt_string, threshold, script_functions)
    
    with open(output_file_freqs,'w') as outfile:
        outfile.write(f'{f_offset_index}, {f_upper_index} \n')
        outfile.write(f'{freq_offset}, {freq_upper}')

