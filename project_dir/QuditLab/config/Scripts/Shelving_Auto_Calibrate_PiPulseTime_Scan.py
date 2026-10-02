#Find_Optimal_Shelving_PiPulseTime_Scan.py created 2022-05-26 17:38:26.206058

# Run over various pulse times 10x so can get the average error,
# Goal: find a precise pulse time  

import numpy as np

start_time = 35 # depending on the transition , determined empiracally 
stop_time = 37
time_step = 0.1

set_time = start_time
PMTdata = []

while set_time < stop_time:
    Pulse_Time = getGlobal("Shelving_Pulse_Time") # 43 us ,
    if not "%s"%Pulse_Time == "%s us"%set_time: #SANDIA , need to have these 2 values be different 
        setGlobal("Shelving_Pulse_Time", set_time, "us")
    setScan("Shelving_PulseGlobalShelvePulseTime_Iterative")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    PMTdata.append(np.mean(ydata))
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    set_time = set_time + time_step

print(PMTdata)
set_time = start_time + time_step*PMTdata.index(min(PMTdata)) # PMT data = list, index where the data is mimimum value = shevled successfully 
Pulse_Time = getGlobal("Shelving_Pulse_Time")
if not "%s"%Pulse_Time == "%s us"%set_time:
    setGlobal("Shelving_Pulse_Time", set_time, "us")