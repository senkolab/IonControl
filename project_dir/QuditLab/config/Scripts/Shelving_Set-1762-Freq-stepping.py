#Set_1762_Freq_stepping.py created 2022-04-03 18:52:22.599545

import numpy as np
import time



set_freq = 800
freq_step = 0.5

wait_time = 0.1

def change_freq(EOM_1762_freq, freq_step):
    EOM_1762_freq = np.round(EOM_1762_freq + freq_step, 6)
    EOM_1762_freq_glob = getGlobal("PDH_EOM_1762_Freq").magnitude
    if not "%s"%EOM_1762_freq_glob == "%s MHz"%EOM_1762_freq:
        setGlobal("PDH_EOM_1762_Freq", EOM_1762_freq, "MHz")
    time.sleep(wait_time)
    return EOM_1762_freq

EOM_1762_freq = getGlobal("PDH_EOM_1762_Freq").magnitude
if set_freq > EOM_1762_freq:
    freq_step = freq_step
    while EOM_1762_freq < set_freq:
        if scriptIsStopped():
            break
        EOM_1762_freq = change_freq(EOM_1762_freq, freq_step)   
else:
    freq_step = - freq_step
    while EOM_1762_freq > set_freq:
        if scriptIsStopped():
            break
        EOM_1762_freq = change_freq(EOM_1762_freq, freq_step)
