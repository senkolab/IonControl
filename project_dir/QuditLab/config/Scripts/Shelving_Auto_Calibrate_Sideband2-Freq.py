#Calibrate_Shelving_Sideband2_Freq.py created 2022-04-20 22:45:51.773989

import numpy as np

start_freq_sideband2 = 463.71
stop_freq_sideband2 = 463.73
freq_step_sideband2 = 0.001

SetPulseTime = 200

PulseTime = getGlobal("Shelving_Pulse_Time")

if not "%s"%PulseTime == "%s us"%PulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq_sideband2
PMTdata = []

while set_freq < stop_freq_sideband2:
    os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%set_freq)
    EOM_1762_sideband2_freq = getGlobal("EOM_1762_Sideband2_Freq")
    if not "%s"%EOM_1762_sideband2_freq == "%s MHz"%set_freq:
        setGlobal("EOM_1762_Sideband2_Freq", set_freq, "MHz")
    setScan("Shelving_PulseGlobalShelvePulseTime_Sideband2")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    PMTdata.append(np.mean(np.array(ydata)))
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    set_freq = set_freq + freq_step_sideband2

set_freq = start_freq_sideband2 + freq_step_sideband2*PMTdata.index(min(PMTdata))
os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%set_freq)
EOM_1762_sideband2_freq = getGlobal("EOM_1762_Sideband2_Freq")
if not "%s"%EOM_1762_sideband2_freq == "%s MHz"%set_freq:
    setGlobal("EOM_1762_Sideband2_Freq", set_freq, "MHz")