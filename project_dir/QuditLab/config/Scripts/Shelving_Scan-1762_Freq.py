#Scan_1762_Freq.py created 2021-12-15 17:20:52.986197

import numpy as np

startfreq = 500e6
endfreq = 610e6
freqinterval = 100e3
wait_time = 0.01

freq_array = np.arange(startfreq,endfreq,freqinterval)

for set_freq in freq_array:
    EOM_1762_freq = getGlobal("EOM_1762_Freq").magnitude
    os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%set_freq)
    if not "%s"%EOM_1762_freq == "%s Hz"%set_freq:
        setGlobal("EOM_1762_Freq", set_freq, "Hz")
    time.sleep(wait_time)