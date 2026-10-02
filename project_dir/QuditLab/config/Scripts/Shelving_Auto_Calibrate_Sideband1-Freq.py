#Calibrate_Shelving_Sideband_Freqs.py created 2022-04-20 22:05:36.475635

import numpy as np

start_freq_sideband1 = 743.4
stop_freq_sideband1 = 743.6
freq_step_sideband1 = 0.01

SetPulseTime = 200

PulseTime = getGlobal("Shelving_Pulse_Time")

if not "%s"%PulseTime == "%s us"%PulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq_sideband1
PMTdata = []

createTrace('1762 nm freq scan - sb1', 'Script Data', xLabel=f'Freq (MHz)')
while set_freq < stop_freq_sideband1:
    os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 4 %s'%set_freq)
    EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband1_Freq")
    if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%set_freq:
        setGlobal("EOM_1762_Sideband1_Freq", set_freq, "MHz")
    setScan("Shelving_PulseGlobalShelvePulseTime_Sideband1")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    data_counts_ave = np.mean(np.array(ydata))
    PMTdata.append(data_counts_ave)
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    set_freq = set_freq + freq_step_sideband1
    plotPoint(set_freq, data_counts_ave, '1762 nm freq scan - sb1', plotStyle=1)
closeTrace('1762 nm freq scan - sb1')
set_freq = start_freq_sideband1 + freq_step_sideband1*PMTdata.index(min(PMTdata))
os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 4 %s'%set_freq)
EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband1_Freq")
if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%set_freq:
    setGlobal("EOM_1762_Sideband1_Freq", set_freq, "MHz")