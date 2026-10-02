#Shelving_TwoStep_Find_Resonance_Freq.py created 2023-08-25 10:33:19.924023

import numpy as np

SaveData = False

freq_step = 0.0003
freq_range_factor = 10
range = freq_range_factor*freq_step

prep_set_freq = 609.172
SetPrepPulseTime = 250 #us

freq = 606.212
AWG_Power_dBm = 3
SetPulseTime = 3000 #us


# Setting the PLL controlled frequency for the shelving step in the prep phase of this two-step process

os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%prep_set_freq)
EOM_1762_sideband3_freq = getGlobal("EOM_1762_Sideband3_Freq").magnitude
if not "%s"%EOM_1762_sideband3_freq == "%s MHz"%prep_set_freq:
    setGlobal("EOM_1762_Sideband3_Freq", prep_set_freq, "MHz")

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", 0, "")

start_freq = freq-range
stop_freq = freq+range+freq_step
#start_freq = 595.605
#stop_freq = 595.615
AWG = True

PulseProgram = "Shelving_TwoStep_PulseGlobalShelvePulseTime_Ba137"

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

PrepPulseTime = getGlobal("Prep_Pulse_Time")
if not "%s"%PrepPulseTime == "%s us"%SetPrepPulseTime:
    setGlobal("Prep_Pulse_Time", SetPrepPulseTime, "us")

set_freq = start_freq

freq_min = set_freq
data_min = 100
createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
setEvaluation('Eval3')
while set_freq < stop_freq:
    if scriptIsStopped():
        break

    setGlobal('AWGClockRef',int(1),'')
    time.sleep(0.01)
    setGlobal('AWGClockRef',int(0),'')
    time.sleep(0.1)
    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%set_freq:
        setGlobal("AWG1_Frequency", np.round(set_freq, 6), "MHz")

    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()['PMT Count']
    ydata = data[1]
    data_counts_ave = np.mean(np.array(ydata))

    if data_counts_ave > data_min:
        data_min = data_counts_ave
        freq_max = set_freq
    #plotPoint(set_freq, np.mean(np.array(ydata)), 'Sideband1_data', plotStyle=1)
    plotPoint(set_freq, data_counts_ave, '1762 nm freq scan', plotStyle=0)
    set_freq = np.round(set_freq + freq_step, 6)
closeTrace('1762 nm freq scan')
setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_max:
    setGlobal("AWG1_Frequency", np.round(freq_max, 6), "MHz")