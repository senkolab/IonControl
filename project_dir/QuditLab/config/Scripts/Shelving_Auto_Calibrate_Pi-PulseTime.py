#Find_Shelving_Optimal_Pi_PulseTime.py created 2022-05-11 20:01:34.115433

import numpy as np

start_time = 47
stop_time = 49
time_step = 0.1

set_time = start_time
PMTdata = []

while set_time < stop_time:
    Pulse_Time = getGlobal("Shelving_Pulse_Time")
    if not "%s"%Pulse_Time == "%s us"%set_time:
        setGlobal("Shelving_Pulse_Time", set_time, "us")
    setScan("Shelving_PulseGlobalShelvePulseTime")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    PMTdata.append(np.mean(ydata))
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    set_time = set_time + time_step

print(PMTdata)
set_time = start_time + time_step*PMTdata.index(min(PMTdata))
Pulse_Time = getGlobal("Shelving_Pulse_Time")
if not "%s"%Pulse_Time == "%s us"%set_time:
    setGlobal("Shelving_Pulse_Time", set_time, "us")