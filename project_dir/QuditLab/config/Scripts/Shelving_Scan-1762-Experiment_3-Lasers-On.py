#Scan_1762_Experiment_3LasersOn.py created 2022-01-25 14:17:06.187744

import numpy as np

startfreq = 621000000.0
endfreq = 650e6
freqinterval = 10e3

freq_array = np.arange(startfreq,endfreq,freqinterval)

for set_freq in freq_array:
    EOM_1762_freq = getGlobal("EOM_1762_Freq").magnitude
    os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%set_freq)
    if not "%s"%EOM_1762_freq == "%s Hz"%set_freq:
        setGlobal("EOM_1762_Freq", set_freq, "Hz")
    setScan("PMT_CheckCounts_For-Script_Fast_Even")
    startScan(globalOverrides=list(), wait=True)