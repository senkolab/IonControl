#Shelving_Scan_Repump_Freq.py created 2022-09-23 18:32:14.350776

import numpy as np

freq_step =    0.00001
start_freq = 487.98868
stop_freq =  487.99068
#start_freq = 595.605
#stop_freq = 595.615

PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Ba137"

SetPulseTime = 155 #us

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq

while set_freq < stop_freq:
    if scriptIsStopped():
        break
    Repump_Freq = getGlobal("ShelvingRepumpFreq")
    if not "%s"%Repump_Freq == "%s THz"%set_freq:
        setGlobal("ShelvingRepumpFreq", np.round(set_freq, 6), "THz")
    time.sleep(10)
    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    set_freq = np.round(set_freq + freq_step, 6)