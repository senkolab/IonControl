#Shelving_Rabi_B-Active_Compensation_Ba138.py created 2023-06-06 10:08:01.968350
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *
import time
import numpy as np

#Before starting this program, find the frequency of the transition, do Rabi pulse_time scan and find which peak you want to improve, and set frequency and pulse time accordingly
#Also, set the pulse_time_scan_even scan variable to dummy and set it to save the raw data with a meaningful name

PulseProgram = "Shelving_PulseTime_Scan_Even_Script_Compensation"

pulse_time = 355.0 #us
frequency = 732.404 # MHz

#What compensation amplitude on the DS345 to range over, and what phases
scan_amp_start = 0.55
scan_amp_stop = 2.5
scan_amp_step = 0.05
phases = np.arange(0,360,10)


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

ds345 = DS345_BCompensation_setOutput(0, 0)

createTrace('Rabi B-field Compensation', 'Script Data', xLabel=f'Comp. Amplitude (V) + Phase (deg decimals)')
setEvaluation('Eval3')
scan_amp = scan_amp_start
while scan_amp < scan_amp_stop:
    ds345.write("AMPL " + str(scan_amp) + "VP")
    time.sleep(1)
    j = 0
    for phase in phases:
        j += scan_amp_step/len(phases)
        print(f'amp:{scan_amp} V, phase:{phase} degrees')
        ds345.write("PHSE "+str(phase))#Sets Phase
        time.sleep(2)
        setScan(PulseProgram)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

        data = getAllData()['PMT Count']
        ydata = data[1]
        data_counts_ave = np.mean(np.array(ydata))
        plotPoint(scan_amp+j, data_counts_ave, 'Rabi B-field Compensation', plotStyle=0)
    scan_amp += scan_amp_step
ds345.close()

closeTrace('Rabi B-field Compensation')
setEvaluation('Eval2')