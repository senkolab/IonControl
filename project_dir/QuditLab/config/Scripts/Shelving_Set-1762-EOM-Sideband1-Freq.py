#Set_1762_EOM_Sideband1_Freq.py created 2022-04-20 21:50:56.490396

import numpy as np

set_freq = 100

os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 4 %s'%set_freq)

EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband1_Freq").magnitude
if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%set_freq:
    setGlobal("EOM_1762_Sideband1_Freq", set_freq, "MHz")