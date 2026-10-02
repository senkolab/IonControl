#Shelving_Find-Target-Resonance_Freq_PLL.py created 2023-08-28 22:46:43.441001

import numpy as np

SaveData = False

#fine = False
freq_step = 0.001
freq_range_factor = 15
#if fine:
#    freq_step *= 0.1
range = freq_range_factor*freq_step

freq = 619.591
#AWG_Power_dBm = 3
SetPulseTime = 3000
#AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
#if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
#    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

#AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
#if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
#    setGlobal("AWG1_Mode", 0, "")

start_freq = freq-range
stop_freq = freq+range+freq_step
#start_freq = 595.605
#stop_freq = 595.615
AWG = False

PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Ba137_UsePLL"

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
        os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%set_freq)
        EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband3_Freq").magnitude
        if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%set_freq:
            setGlobal("EOM_1762_Sideband3_Freq", set_freq, "MHz")
#        EOM_1762_sideband2_freq = getGlobal("EOM_1762_Sideband2_Freq").magnitude
#        os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%set_freq)
#        if not "%s"%EOM_1762_sideband2_freq == "%s MHz"%set_freq:
#            setGlobal("EOM_1762_Sideband2_Freq", set_freq, "MHz")
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

os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%freq_min)
EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband3_Freq").magnitude
if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%freq_min:
    setGlobal("EOM_1762_Sideband3_Freq", freq_min, "MHz")