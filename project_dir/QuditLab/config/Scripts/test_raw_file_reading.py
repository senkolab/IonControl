#D52_25_level_SPAM.py created 2024-03-01 16:24:43.974455

import time
import matlab.engine

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

use_an1_an2 = True



pattern = "Z:\Lab Data\Harelded_pulse_time_scans_raw_data\Raw_data\harelded_pulse_time_scan*"

matching_files = glob.glob(pattern)


matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
print(matching_files)

file_path = matching_files[-1]
chunks = file_path.split('\\')
print(chunks[-1])
print(file_path)
