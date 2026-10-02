#Auto_Calibrate_Pi_Pulses.py created 2022-06-07 09:18:38.439015

import numpy as np
import glob
import pandas as pd
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
#from Functions_NeutralFluor import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

WhichIon = getGlobal("WhichIon").magnitude
if WhichIon == 138:
    PulseProgram = "Auto_Calibrate_Pi_Pulses"
elif WhichIon == 137:
    PulseProgram = "Auto_Calibrate_Pi_Pulses_Ba137"

start_time = 50
stop_time = 58
time_step = 1

filename = "Pi_Pulse_Calibration_PulseTime_Scan_Raw"


setGlobalPulseTimeScan(start_time, stop_time, time_step, script_functions)

setScan(PulseProgram)
startScan(globalOverrides=list(), wait=True)
stopScan()

Filepath = GetRawDataFolder()
files0 = f'{Filepath}\\{filename}*'

files0 = np.array(glob.glob(files0))
data_indfirst = 4
data_indlast = -20
data = pd.read_csv(files0[-1], delimiter = "\[|\]|,|\"", engine='python',header=None).values
data = data2[:, data_indfirst:data_indlast+1]

threshold = getShelvingThreshold(data2)
fluor_bool = data2 < threshold
fluor_ave = np.mean(fluor_bool, 1)
fluor_std = np.std(fluor_bool, 1)
fluor_ave_max_index = np.argmax(fluor_ave)
optimal_time = start_time + time_step*fluor_ave_max_index







start_time = optimal_time - 2
stop_time = optimal_time + 2
time_step = 0.1

setGlobalPulseTimeScan(start_time, stop_time, time_step, script_functions)

setScan(PulseProgram)
startScan(globalOverrides=list(), wait=True)
stopScan()

Filepath = GetRawDataFolder()
files0 = f'{Filepath}\\{filename}*'

files0 = np.array(glob.glob(files0))
data_indfirst = 4
data_indlast = -20
data = pd.read_csv(files0[-1], delimiter = "\[|\]|,|\"", engine='python',header=None).values
data = data2[:, data_indfirst:data_indlast+1]

threshold = getShelvingThreshold(data2)
fluor_bool = data2 < threshold
fluor_ave = np.mean(fluor_bool, 1)
fluor_std = np.std(fluor_bool, 1)
fluor_ave_max_index = np.argmax(fluor_ave)
optimal_time = start_time + time_step*fluor_ave_max_index

print(optimal_time)
print(max(Pumped_Probability))