#Scan_Cooling_AOM_Switch_Freq.py created 2021-10-06 14:08:40.811863
import numpy as np

startfreq = 1145
endfreq = 1159
freqinterval = 0.5
wait_time = 0.5

freq_array = np.arange(startfreq,endfreq,freqinterval)

for set_freq in freq_array:
    AOM_switch_freq = getGlobal("Cooling_AOM_Switch_Freq").magnitude
    if not "%s"%AOM_switch_freq == "%s kHz"%set_freq:
        setGlobal("Cooling_AOM_Switch_Freq", set_freq, "kHz")
    time.sleep(wait_time)