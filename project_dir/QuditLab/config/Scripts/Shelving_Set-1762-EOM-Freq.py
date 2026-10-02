#Set_1762_EOM_Freq.py created 2022-04-18 01:14:10.755490

import numpy as np

set_freq = 471

EOM_1762_freq = getGlobal("EOM_1762_Target_Freq").magnitude
os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%set_freq)
if not "%s"%EOM_1762_freq == "%s MHz"%set_freq:
    setGlobal("EOM_1762_Target_Freq", set_freq, "MHz")