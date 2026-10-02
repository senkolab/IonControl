#Find_Shelving_Target_Resonance_Freq_Ramsey.py created 2022-05-04 20:46:22.361698

import numpy as np

start_freq = 497.39
stop_freq = 497.41
freq_step = 0.001

SetPulseTime = 19

PulseTime = getGlobal("Shelving_Pulse_Time")

if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq
PMTdata = []

while set_freq < stop_freq:
    AWG1_Freq = getGlobal("AWG1_Freq")
    if not "%s"%AWG1_Freq == "%s MHz"%set_freq:
        setGlobal("AWG1_Freq", set_freq, "MHz")
    setScan("Shelving_RamseyTime_Scan_Find_Target_Resonance")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    PMTdata.append(np.mean(np.array(ydata)))
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    set_freq = set_freq + freq_step

set_freq = start_freq + freq_step*PMTdata.index(min(PMTdata))
AWG1_Freq = getGlobal("AWG1_Freq")
if not "%s"%AWG1_Freq == "%s MHz"%set_freq:
    setGlobal("AWG1_Freq", set_freq, "MHz")