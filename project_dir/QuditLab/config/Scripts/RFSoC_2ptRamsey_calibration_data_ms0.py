#RFSoC_FastRamsey_calibration_data.py created 2025-11-18 15:10:17.876421

import time
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


import sys
import os
import datetime
import glob
import numpy as np
import random
    
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
from Functions_RFSoC_RamseyCalibration import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

# get latest 545 and 623 freqs
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

Ramsey_wait_time = 400
line_trigger = True
run_rough_calibration= False

# get latest pitimes for all delta-m transition types
pitime_n2 = getGlobal('pitime_n2') # [-2, 4, -4]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [2, 4, 2]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]

ref_pitimes_input = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]


f_offset_index = [0,2,0]
f_upper_index = [-1,4,-3]
f_upper_new_index = [0, 4, -2]

#scan_indices =[[-2,3,-1],[-1,3,0],[1,4,2],[1,3,2],[2,4,0],[1,4,0], \
#            [-1,3,-2],[-2,2,0], [-1,2,0],[1,2,2],[1,4,-1],[0,2,2],[-1,4,-2], \
#            [-2,4,-4],[-1,4,-3], [0,4,-1],[0,4,0],[0,4,1],[2,4,2],[2,4,3], \
#            [2,4,4],[-2,3,-3],[-2,3,-2], [-1,3,-1],[0,3,0],[0,3,1],[0,3,2], \
#            [1,3,3],[-2,2,-2],[-2,2,-1],[2,2,1],[2,2,2],[-1,1,-1],[-2,1,0], \
#            [1,1,1],[-1,1,1], [2, 2, 0],[-2, 1, -1],[2, 4, 1],[0, 1, 1]]

scan_indices =[[-1,3,0],[1,4,2],[1,3,2],[2,4,0],[1,4,0], \
             [-1,3,-2],[-2,2,0], \
             [-1,2,0],[1,2,2],[1,4,-1],[0,2,2],[-1,4,-2],[-2,4,-4],[-1,4,-3], \
             [0,4,-1],[0,4,0],[0,4,1],[2,4,2],[2,4,3],[2,4,4],[-2,3,-3],[-2,3,-2], \
             [-1,3,-1],[0,3,0],[0,3,1],[0,3,2],[1,3,3],[-2,2,-2],[-2,2,-1],[2,2,1], \
             [2,2,2],[-1,1,-1],[-2,1,0],[1,1,1],[-1,1,1], \
             [2, 2, 0],[-2, 1, -1],[2, 4, 1],[0, 1, 1], \
             [-2,3,-1],]
scan_indices = scan_indices + scan_indices + scan_indices
#scan_indices = [[1,4,1],[1,3,-1],[-1,2,-2],[0,3,-1]]

# the remaining 3 transitions not explicitly calibrated are below
#scan_indices = [[0,2,-2],[1,2,-1],[2,1,0]]

#random.shuffle(scan_indices)
#scan_indices = [[0,3,-1]]*100

pitime_ref_index = [[-1,4,-3],[-2,3,-3],[0,2,0],[2,4,3],[2,4,4]]

if run_rough_calibration:
    f_offset_cal = run_fast_calibration(script_functions, 0, 50,target_transition=f_offset_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
    f_offset_dummy = getGlobal('f_offset')
    if not "%s"%f_offset_dummy == f_offset_cal:
        setGlobal("f_offset", f_offset_cal, "")

    f_upper_cal = run_fast_calibration(script_functions, 0, 50,target_transition=f_upper_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
    f_upper_dummy = getGlobal('f_upper')
    if not "%s"%f_upper_dummy == f_upper_cal:
        setGlobal("f_upper", f_upper_cal, "")

for i in range(10):
    for scan_index in scan_indices:
            dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")


            f_upper_cal = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=f_upper_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            f_upper_dummy = getGlobal('f_upper')
            if not "%s"%f_upper_dummy == f_upper_cal:
                setGlobal("f_upper", f_upper_cal, "")
            
            f_offset_cal = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=f_offset_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            f_offset_dummy = getGlobal('f_offset')
            if not "%s"%f_offset_dummy == f_offset_cal:
                setGlobal("f_offset", f_offset_cal, "")

            f_upper_new = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=f_upper_new_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)

            f_target = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=scan_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            print('f_target is', f_target)
            filename_freq = str(np.round(f_target,5)).replace('.','p')
            
            output_file = fr'Z:\\Lab Data\\D52_Calibration_Ba137\\RFSoC_2ptRamsey_calibration_data_ms0\\ramsey_calibration_triplet_{filename_freq}_Wait{Ramsey_wait_time}_Shots250_{dt_string}.txt'
            with open(output_file,'w') as file:
                file.write(f"[{f_offset_cal},{f_upper_new},{f_target}]\n")
                file.write(f"[{f_offset_index},{f_upper_new_index},{scan_index}]\n")
                file.write(f"We measure [-1,4,-3] so we know what frequencies to guess. It's value was: [{f_upper_cal}]\n")