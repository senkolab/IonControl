#Auto_Calibrate_Pi_Pulses_6Level.py created 2022-06-07 18:26:52.320510

import numpy as np
import glob
import pandas as pd
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
from Functions_Neutral-Fluor import *

filename = "Pi_Pulse_Calibration_PulseTime_Scan_Raw"

PulseTime_Strings = ["Ba138_Shelving_N12_DM_m2_Pi_Time","Ba138_Shelving_N12_DM_m1_Pi_Time","Ba138_Shelving_N12_DM_zero_Pi_Time","Ba138_Shelving_N12_DM_p1_Pi_Time","Ba138_Shelving_N12_DM_p2_Pi_Time"]

for hh in range(5):
    start_time = 20
    stop_time = 60
    time_step = 1

    setScan("TriggerAWGEvent")
    startScan(globalOverrides=list(), wait=True)

    StartTimeGUI = getGlobal("PulseTimeStart")
    if not "%s"%StartTimeGUI == "%s us"%start_time:
        setGlobal("PulseTimeStart", start_time, "us")

    StopTimeGUI = getGlobal("PulseTimeStop")
    if not "%s"%StopTimeGUI == "%s us"%stop_time:
        setGlobal("PulseTimeStop", stop_time, "us")

    TimeStepGUI = getGlobal("PulseTimeStep")
    if not "%s"%TimeStepGUI == "%s us"%time_step:
        setGlobal("PulseTimeStep", time_step, "us")

    Filepath = GetRawDataFolder()
    setScan("Auto_Calibrate_Pi_Pulses")
    startScan(globalOverrides=list(), wait=True)
    setScan("Auto_Calibrate_Pi_Pulses")
    files = glob.glob(Filepath + "\\" + filename + "*")
    data = pd.read_csv(files[-1])
    data = data.values.tolist()

    data_string = str(data[0])
    data_string = data_string.replace("'","")
    data_1D = data_string[data_string.index("[",data_string.index("{")):data_string.index("]",data_string.index("{"))+1]
    data_1D = eval(data_1D)
    data_1D = np.array(data_1D)

    data_2D = np.zeros((len(data),len(data_1D)))

    for h in range(len(data)):
        data_string = str(data[h])
        data_string = data_string.replace("'","")
        data_1D = data_string[data_string.index("[",data_string.index("{")):data_string.index("]",data_string.index("{"))+1]
        data_1D = eval(data_1D)
        data_1D = np.array(data_1D)
        data_2D[h,:] = data_1D

    data_2D = np.array(data_2D)

    Pumped_Indicator = GetPumpedIndicator(data_2D)
    Pumped_Probability = np.mean(Pumped_Indicator,1)
    Pumped_Probability_max_ind = np.where(Pumped_Probability == max(Pumped_Probability))
    Pumped_Probability_max_ind = Pumped_Probability_max_ind[0][int(np.size(Pumped_Probability_max_ind)/2)]
    optimal_time = start_time + time_step*Pumped_Probability_max_ind

    start_time = optimal_time - 2
    stop_time = optimal_time + 2
    time_step = 0.1

    StartTimeGUI = getGlobal("PulseTimeStart")
    if not "%s"%StartTimeGUI == "%s us"%start_time:
        setGlobal("PulseTimeStart", start_time, "us")

    StopTimeGUI = getGlobal("PulseTimeStop")
    if not "%s"%StopTimeGUI == "%s us"%stop_time:
        setGlobal("PulseTimeStop", stop_time, "us")

    TimeStepGUI = getGlobal("PulseTimeStep")
    if not "%s"%TimeStepGUI == "%s us"%time_step:
        setGlobal("PulseTimeStep", time_step, "us")

    Filepath = GetRawDataFolder()
    setScan("Auto_Calibrate_Pi_Pulses")
    startScan(globalOverrides=list(), wait=True)
    setScan("Auto_Calibrate_Pi_Pulses")
    files = glob.glob(Filepath + "\\" + filename + "*")
    data = pd.read_csv(files[-1])
    data = data.values.tolist()

    data_string = str(data[0])
    data_string = data_string.replace("'","")
    data_1D = data_string[data_string.index("[",data_string.index("{")):data_string.index("]",data_string.index("{"))+1]
    data_1D = eval(data_1D)
    data_1D = np.array(data_1D)

    data_2D = np.zeros((len(data),len(data_1D)))

    for h in range(len(data)):
        data_string = str(data[h])
        data_string = data_string.replace("'","")
        data_1D = data_string[data_string.index("[",data_string.index("{")):data_string.index("]",data_string.index("{"))+1]
        data_1D = eval(data_1D)
        data_1D = np.array(data_1D)
        data_2D[h,:] = data_1D

    data_2D = np.array(data_2D)

    Pumped_Indicator = GetPumpedIndicator(data_2D)
    Pumped_Probability = np.mean(Pumped_Indicator,1)
    Pumped_Probability_max_ind = np.where(Pumped_Probability == max(Pumped_Probability))
    Pumped_Probability_max_ind = Pumped_Probability_max_ind[0][int(np.size(Pumped_Probability_max_ind)/2)]
    optimal_time = start_time + time_step*Pumped_Probability_max_ind

    Pulse_Time = getGlobal(PulseTime_Strings[hh])
    if not "%s"%Pulse_Time == "%s us"%optimal_time:
        setGlobal(PulseTime_Strings[hh], optimal_time, "us")