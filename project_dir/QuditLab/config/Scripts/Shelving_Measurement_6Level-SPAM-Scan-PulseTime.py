#D52_6Level_SPAM_Scan_PulseTime.py created 2022-06-03 15:49:43.550154

import sys
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint)

WhichIon = getGlobal("WhichIon").magnitude
if WhichIon == 138:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Even"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses"
elif WhichIon == 137:
    pulse_program_findres = "Shelving_PulseGlobalShelvePulseTime_Ba137"
    pulse_program_findpi = "Auto_Calibrate_Pi_Pulses_Ba137"

measurement_scan = "Shelving_Measurement_Ba138_6Level_Qudit_SPAM_Exp"
dict_states = 
    {0:"Fp2_DM_zero", 1:"Fp2_DM_n1", 2:"Fp2_DM_n2", 
    3:"Fp4_DM_p2", 4:"Fp4_DM_p1", 5:"Fp3_DM_n1"
    6:"Fp4_DM_zero", 7:"Fp2_DM_n1", 8:"Fp3_DM_n2"
    9:"Fp4_DM_n1", 10:"Fp4_DM_n2"}

    




time_step = 0.1

start_time = 27
stop_time = 32

StartState = 3
StartStateGUI = getGlobal("Shelving_Measurement_StartState")
if not "%s"%StartStateGUI == "%s"%int(StartState):
    setGlobal("Shelving_Measurement_StartState", int(StartState), "")

startstate_string1 = "Ba138_Shelving_N12_DM"
startstate_string2 = dict_startstate[StartState]
    
set_time = start_time

#Try for different pulse times to find the optimal measurement pulse-time
while set_time < stop_time:
    PulseTimeString = f"{startstate_string1}_{startstate_string2}_Pi_Time"
    PulseTime = getGlobal()
    if not "%s"%PulseTime == "%s us"%set_time:
        setGlobal(PulseTimeString, set_time, "us")
    setScan(measurement_scan)
    startScan(globalOverrides=list(), wait=True)
    set_time = set_time + time_step