#Shelving_Ramsey-B-Active-Compensation_Ba138.py created 2023-06-01 15:51:18.799130
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *
import time
import numpy as np

#Before starting this program, find the frequency of the transition, do Ramsey scan and find which peak you want to improve, and set frequency, pulse time, Ramsey wait time accordingly
#Also, set the Ramsey scan variable to dummy and set it to save the raw data with a meaningful name

PulseProgram = "Shelving_RamseyTime_Scan_Script-Compensation"

pulse_time = 12 #us
wait_time = 680 #us
frequency_resonance = 739.485 # MHz
detuning = 0.004 # MHz
frequency = frequency_resonance + detuning

scan_amp_start = 0.2
scan_amp_stop = 2
scan_amp_step = 0.05

phases = [0,45,90,135,180,225,270,315]
phases = np.arange(0,360,20)


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
wait_time_global = getGlobal('Ramsey_Wait_Time').magnitude
if not "%s"%wait_time_global == wait_time:
    setGlobal("Ramsey_Wait_Time", wait_time, "us")



ds345 = DS345_BCompensation_setOutput(0, 0)

createTrace('Ramsey B-field Compensation', 'Script Data', xLabel=f'Amplitude (V) + Phase (deg decimals)')
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
        plotPoint(scan_amp+j, data_counts_ave, 'Ramsey B-field Compensation', plotStyle=0)
    scan_amp += scan_amp_step
ds345.close()

closeTrace('Ramsey B-field Compensation')
setEvaluation('Eval2')