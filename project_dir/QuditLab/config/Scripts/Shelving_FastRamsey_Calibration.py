#Shelving_FastRamsey_Calibration.py created 2024-08-06 09:20:07.289105
#New_Shelving_Calibration_ParamEstimated_Initialised.py created 2024-04-26 16:49:34.435318
#Shelving_Freq_PiTime_Calibration_PlotPD_ParamEstimated_Initialised.py created 2024-04-08 17:31:06.613195

import time
#import matlab.engine
#eng = matlab.engine.start_matlab()
#eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
#eng.SendAWGCommand("RES", nargout=0)
#time.sleep(1)

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
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

# get latest 545 and 623 freqs
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

Ramsey_wait_time = 400
line_trigger = True
run_rough_calibration=True

# get latest pitimes for all delta-m transition types
pitime_n2 = getGlobal('pitime_n2') # [-2, 4, -4]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [2, 4, 2]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]

ref_pitimes_input = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]


f_offset_index = [0,2,0]
f_upper_index = [-1,4,-3]

scan_indices =[[-2,3,-1],[-1,3,0],[1,4,2],[1,3,2],[2,4,0],[1,4,0],[-1,3,-2],[-2,2,0], \
             [-1,2,0],[1,2,2],[1,4,-1],[0,2,2],[-1,4,-2],[-2,4,-4],[0,4,-2], \
             [0,4,-1],[0,4,0],[0,4,1],[2,4,2],[2,4,3],[2,4,4],[-2,3,-3],[-2,3,-2], \
             [-1,3,-1],[0,3,0],[0,3,1],[0,3,2],[1,3,3],[-2,2,-2],[-2,2,-1],[2,2,1], \
             [2,2,2],[-1,1,-1],[-2,1,0],[1,1,1],[-1,1,1], \
             [2, 2, 0],[-2, 1, -1],[2, 4, 1],[0, 1, 1]]
scan_indices = scan_indices + scan_indices + scan_indices
#scan_indices = [[1,4,1],[1,3,-1],[-1,2,-2],[0,3,-1]]

# the remaining 3 transitions not explicitly calibrated are below
#scan_indices = [[0,2,-2],[1,2,-1],[2,1,0]]

random.shuffle(scan_indices)
#scan_indices = [[-1,4,-2]]

pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]

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
            
            f_offset_cal = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=f_offset_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            f_offset_dummy = getGlobal('f_offset')
            if not "%s"%f_offset_dummy == f_offset_cal:
                setGlobal("f_offset", f_offset_cal, "")

            f_upper_cal = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=f_upper_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            f_upper_dummy = getGlobal('f_upper')
            if not "%s"%f_upper_dummy == f_upper_cal:
                setGlobal("f_upper", f_upper_cal, "")

            f_target = run_fast_calibration(script_functions, 0, Ramsey_wait_time,target_transition=scan_index,f_offset_input=None, f_upper_input=None,ref_pitimes=ref_pitimes_input)
            print('f_target is', f_target)
            filename_freq = str(np.round(f_target,5)).replace('.','p')
            
            output_file = fr'Z:\Lab Data\D52_Calibration_Ba137\Fast_Ramsey_calibrations\ramsey_calibration_triplet_{filename_freq}_Wait{Ramsey_wait_time}_Shots250_{dt_string}.txt'
            with open(output_file,'w') as file:
                file.write(f"[{f_offset_cal},{f_upper_cal},{f_target}]\n")
                file.write(f"[{f_offset_index},{f_upper_index},{scan_index}]\n")