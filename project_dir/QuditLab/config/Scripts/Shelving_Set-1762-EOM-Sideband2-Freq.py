#Set_1762_EOM_Sideband2_Freq.py created 2022-04-20 21:54:13.673881

import numpy as np

set_freq = 603.517

EOM_1762_sideband2_freq = getGlobal("EOM_1762_Sideband2_Freq").magnitude
os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%set_freq)
if not "%s"%EOM_1762_sideband2_freq == "%s MHz"%set_freq:
    setGlobal("EOM_1762_Sideband2_Freq", set_freq, "MHz")