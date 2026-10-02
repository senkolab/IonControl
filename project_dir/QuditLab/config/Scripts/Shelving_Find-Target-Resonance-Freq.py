#Find_Shelving_Target_Resonance_Freq.py created 2022-04-21 01:35:44.954235

import numpy as np

SaveData = True

#fine = False
freq_step = 0.001
freq_range_factor = 5
#if fine:
#    freq_step *= 0.1
range = freq_range_factor*freq_step

freq = 609.37
AWG_Power_dBm = -10
AWG_mode = 0
SetPulseTime = 3000 #us

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == AWG_mode: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", AWG_mode, "")

start_freq = freq-range
stop_freq = freq+range+freq_step
#start_freq = 614.466
#stop_freq = 614.614
AWG = True

WhichIon = getGlobal("WhichIon").magnitude
if WhichIon == 138:
    PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Even"
elif WhichIon == 137:
    if SaveData:
        PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Ba137_SaveData"
    else:
        PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Ba137"

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq

freq_min = set_freq
data_min = 100
createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
setEvaluation('Eval3')
while set_freq < stop_freq:
    if scriptIsStopped():
        break
    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        time.sleep(0.01)
        setGlobal('AWGClockRef',int(0),'')
        time.sleep(0.1)
        AWG1_Freq = getGlobal("AWG1_Frequency")
        if not "%s"%AWG1_Freq == "%s MHz"%set_freq:
            setGlobal("AWG1_Frequency", np.round(set_freq, 6), "MHz")
    else:
        EOM_1762_freq_glob = getGlobal("PDH_EOM_1762_Freq").magnitude
        if not "%s"%EOM_1762_freq_glob == "%s MHz"%set_freq:
            setGlobal("PDH_EOM_1762_Freq", set_freq, "MHz")
        time.sleep(0.2)
    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    data_counts_ave = np.mean(np.array(ydata))

    if data_counts_ave < data_min:
        data_min = data_counts_ave
        freq_min = set_freq
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    plotPoint(set_freq, data_counts_ave, '1762 nm freq scan', plotStyle=0)
    set_freq = np.round(set_freq + freq_step, 6)
closeTrace('1762 nm freq scan')
setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_min:
    setGlobal("AWG1_Frequency", np.round(freq_min, 6), "MHz")