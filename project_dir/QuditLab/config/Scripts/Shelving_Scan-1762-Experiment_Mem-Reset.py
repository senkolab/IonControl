#Scan_1762_Experiment_Mem_Reset.py created 2022-03-28 10:35:10.471807

import numpy as np
import gc
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

set_freq = getGlobal("PDH_EOM_1762_Freq").magnitude
startfreq = 588.4e6
endfreq = 592.4e6
freqstep = 1e3
ExperimentMax = 500
if set_freq == startfreq:
    set_freq = set_freq - freqstep

CountsProgram = "PMT_CheckCounts_For-Script_Even"
SendLasersToTrap(CountsProgram,script_functions)

setScan("Shelving_PulseTime_Scan_Even")
ExperimentCount = 0

while set_freq < endfreq and ExperimentCount < ExperimentMax:
    set_freq = set_freq + freqstep
    EOM_1762_freq = getGlobal("PDH_EOM_1762_Freq").magnitude
    os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%set_freq)
    if not "%s"%EOM_1762_freq == "%s Hz"%set_freq:
        setGlobal("PDH_EOM_1762_Freq", set_freq, "Hz")
    #if Count >= Count_multiplier:
    startScan(globalOverrides=list(), wait=True)
    ExperimentCount = ExperimentCount + 1
    gc.collect()
    #    Count = 0
    #Count = Count+1