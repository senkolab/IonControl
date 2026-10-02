#Shelving_ResonanceFrequency_LineTrigger_Ba138.py created 2023-07-27 14:28:01.230148

#Find_Shelving_Target_Resonance_Freq.py created 2022-04-21 01:35:44.954235

import numpy as np

SaveData = False

#fine = False

AWG_Power_dBm = -20
SetPulseTime = 1500 #us

AWG = True
start_freq = 753.803
stop_freq = 753.813
freq_step = 0.001

phase_delays = np.arange(0,17,0.5) #ms

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == 0: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", 0, "")

PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Even_LineTrigger"

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

set_freq = start_freq
freq_min = set_freq
data_min = 100

for phase in phase_delays:

    TrigDelay = getGlobal("Trigger_Delay_Time")
    if not "%s"%TrigDelay == "%s ms"%phase:
        setGlobal("Trigger_Delay_Time", phase, "ms")

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
    set_freq = start_freq

setEvaluation('Eval2')
AWG1_Freq = getGlobal("AWG1_Frequency")
if not "%s"%AWG1_Freq == "%s MHz"%freq_min:
    setGlobal("AWG1_Frequency", np.round(freq_min, 6), "MHz")