#Shalving_Ramsey_LineTrigger_Ba138.py created 2023-07-17 15:31:45.092645

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *
import time
import numpy as np

#Before starting this program, find the frequency of the transition, do Rabi pulse_time scan and find the pi/2 time then
# set frequency and pi/2 pulse time accordingly
#Also, set the pulse program to scan over the pulse_time variable with whatever time step is desired

frequency_resonance = 739.606 # MHz
detuning = 0.005 #MHz
frequency = frequency_resonance - detuning
pulse_time = 13.75 #us

# create the array of trigger delay times but for each time, make a reference 0 ms delay time to compare off of
initial_array = np.arange(0.0, 17.0, 0.25) #range of trigger delay times to check phase dependence on AC wall signal
zeros_array = np.zeros(len(initial_array))
delay_times = np.insert(initial_array, np.arange(0, len(initial_array), 1), zeros_array)

AWG_Power_dBm = 3
AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_Freq_global = getGlobal('AWG1_Frequency').magnitude
if not "%s"%AWG_Freq_global == frequency:
    setGlobal("AWG1_Frequency", frequency, "MHz")

pulse_time_global = getGlobal('Shelving_Pulse_Time').magnitude
if not "%s"%pulse_time_global == pulse_time:
    setGlobal("Shelving_Pulse_Time", pulse_time, "us")

PulseProgram = "Shelving_RamseyTime_Scan_Script_FullFit_LineTriggering"

createTrace('Ramsey Line Triggered', 'Script Data', xLabel=f'Delay Time (us)')
setEvaluation('Eval3')

for delay_time in delay_times:
    if scriptIsStopped():
        break

    trigger_delay_time_global = getGlobal('Trigger_Delay_Time').magnitude
    if not "%s"%trigger_delay_time_global == delay_time:
        setGlobal("Trigger_Delay_Time", delay_time, "ms")

    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

closeTrace('Ramsey Line Triggered')
setEvaluation('Eval2')