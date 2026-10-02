#Swt_1762_Freq.py created 2022-01-14 17:33:43.157058



#OBSOLETE, can just change the global variable now



import numpy as np

set_freq = 20

EOM_1762_freq = getGlobal("PDH_EOM_1762_Freq").magnitude
#os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%(set_freq*1e6))
if not "%s"%EOM_1762_freq == "%s MHz"%set_freq:
    setGlobal("PDH_EOM_1762_Freq", set_freq, "MHz")