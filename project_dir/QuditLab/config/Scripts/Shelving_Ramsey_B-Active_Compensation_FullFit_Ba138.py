#Shelving_Ramsey_B-Active_Compensation_FullFit_Ba138.py created 2023-06-07 19:00:19.992799
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *
import time
import numpy as np

#Before starting this program, find the frequency of the transition, do Rabi pulse_time scan and find the pi/2 time then
# set frequency and pi/2 pulse time accordingly
#Also, set the pulse program to scan over the pulse_time variable with whatever time step is desired

frequency_resonance = 753.808 # MHz
detuning = 0.004 #MHz
frequency = frequency_resonance - detuning
pulse_time = 27.5 #us

sweep_type = 'phase'

#What compensation amplitude on the DS345, and what phases to range over
#For phase scanning
if sweep_type == 'phase':
    scan_amp = 0.3
    phases = np.arange(20,40,2)
elif sweep_type == 'amp':
#For amplitude scanning
    scan_amps = np.arange(0.0,0.5,0.025)
    phase = 8.0

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

#fun=0 for sine wave, func=1 for square wave
#trigmode=4 by default, corres to AFG triggering by internal AC power line trigger, not an external trigger, trig_mode=2 is pos-in from external trigger
ds345 = DS345_BCompensation_setOutput(amp=0.35, phase=10.0, freq=180.1, func=0, offset=0, trig_mode=4, brst_count=3)

createTrace('Ramsey B-field Compensation', 'Script Data', xLabel=f'Comp. Amplitude (V) + Phase (deg decimals)')
setEvaluation('Eval3')

if sweep_type == 'phase':
    ds345.write("AMPL " + str(scan_amp) + "VP")
    time.sleep(1)
    for phase in phases:
        if scriptIsStopped():
            break
        print(f'amp:{scan_amp} V, phase:{phase} degrees')
        
        
        ds345.write("PHSE "+str(phase))#Sets Phase
        time.sleep(2)

        setScan(PulseProgram)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

elif sweep_type == 'amp':
    ds345.write("PHSE "+str(phase))#Sets Phase
    time.sleep(1)
    for scan_amp in scan_amps:
        if scriptIsStopped():
            break
        print(f'amp:{scan_amp} V, phase:{phase} degrees')
        
        ds345.write("AMPL " + str(scan_amp) + "VP")
        time.sleep(2)

        setScan(PulseProgram)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

#ds345.write("AMPL " + str(0.0) + "VP")
#ds345.write("PHSE "+str(0.0))
ds345.close()

closeTrace('Ramsey B-field Compensation')
setEvaluation('Eval2')