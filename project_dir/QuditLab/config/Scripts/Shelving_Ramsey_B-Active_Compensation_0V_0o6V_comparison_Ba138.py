#Shelving_Ramsey_B-Active_Compensation_0V_0o3V_comparison_Ba138.py created 2023-06-16 13:01:42.589472

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *
import time
import numpy as np

#Before starting this program, find the frequency of the transition, do Rabi pulse_time scan and find the pi/2 time then
# set frequency and pi/2 pulse time accordingly
#Also, set the pulse program to scan over the pulse_time variable with whatever time step is desired

frequency_resonance = 739.525 # MHz
detuning = 0.004 #MHz
frequency = frequency_resonance + detuning
pulse_time = 15 #us

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

PulseProgram = "Shelving_RamseyTime_Scan_Script_FullFit_Compensation"

ds345 = DS345_BCompensation_setOutput(0, 0)

createTrace('Ramsey B-field Compensation', 'Script Data', xLabel=f'Comp. Amplitude (V) + Phase (deg decimals)')
setEvaluation('Eval3')

dummy_var=0
scan_amp = 0.0
phase = 110.0
ds345.write("AMPL " + str(scan_amp) + "VP")
ds345.write("PHSE "+str(phase))
time.sleep(1)

while dummy_var < 120:
    if scriptIsStopped():
        break
    print(f'amp:{scan_amp} V, phase:{phase} degrees')

    if dummy_var % 2:
        scan_amp = 0.0
        ds345.write("AMPL " + str(scan_amp) + "VP")
        time.sleep(1)
    else:
        scan_amp = 0.6
        ds345.write("AMPL " + str(scan_amp) + "VP")
        time.sleep(1)

    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    dummy_var += 1

ds345.write("AMPL " + str(0.0) + "VP")
ds345.write("PHSE "+str(0.0))
ds345.close()

closeTrace('Ramsey B-field Compensation')
setEvaluation('Eval2')