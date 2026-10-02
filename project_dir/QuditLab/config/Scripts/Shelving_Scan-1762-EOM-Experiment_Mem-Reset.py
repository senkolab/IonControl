#Scan_1762_EOM_Experiment_Mem_Reset.py created 2022-04-18 01:37:19.044306


import numpy as np
import gc
import sys
import glob
import pandas as pd
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

AWG = True
if AWG:
    Global_Freq_Set = "AWG1_Frequency"
else:
    Global_Freq_Set = "PDH_EOM_1762_Freq"

WhichIon = getGlobal("WhichIon").magnitude
if WhichIon == 138:
    PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Even"
    CountsProgram = "PMT_CheckCounts_For-Script_Even"
elif WhichIon == 137:
    PulseProgram = "Shelving_PulseGlobalShelvePulseTime_Ba137"
    CountsProgram = "PMT_CheckCounts_For-Script_Ba137"

filepath0 = GetRawDataFolder()
filename0 = "Shelving_PulseTime_Scan_Ba137_04_440-0o02-650MHzEOM_240MHzPDH_3dBm-AWGPower_1000usPulseTime_4A-BField_Raw"

bright_threshold = 4
plot = False

set_freq = getGlobal(Global_Freq_Set).magnitude
startfreq = 440
endfreq = 700
freqstep = 0.02

SetPulseTime = 1000 #us

#ShelvingPP = "Shelving_PulseTime_Scan_Even"
#ShelvingPP = "Shelving_PulseTime_Scan_Ba137"

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

ExperimentMax = 500
if set_freq == startfreq:
    set_freq = set_freq - freqstep


SendLasersToTrap(CountsProgram,script_functions)

ExperimentCount = 0

if plot:
    createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
while set_freq < endfreq and ExperimentCount < ExperimentMax:
    if scriptIsStopped():
        break
    set_freq = np.round(set_freq + freqstep, 6)
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
    #if Count >= Count_multiplier:
    setScan(PulseProgram)
    startScan(globalOverrides=list(), wait=True)
    setScan(PulseProgram)
    #stopScan()
    if plot:
        files = glob.glob(filepath0 + "\\" + filename0 + "*")
        data_indfirst = 4
        data_indlast = -20
        data = pd.read_csv(files[-1], delimiter = "\[|\]|,|\"", engine='python',header=None).values[0]
        data = data[data_indfirst:data_indlast+1]
        fluor_bool = data < bright_threshold
        fluor_ave = np.mean(fluor_bool)
        plotPoint(set_freq, fluor_ave, '1762 nm freq scan', plotStyle=1)
    ExperimentCount = ExperimentCount + 1
    gc.collect()
    #    Count = 0
    #Count = Count+1
if plot:
    closeTrace('1762 nm freq scan')