#Check_Ba137.py created 2026-07-31 10:38:44.123428

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from Functions_Trap import * 
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

eom_493_frequency = getGlobal("Ba137_CoolingFreq_EOM").magnitude / 1000 # MHz to GHz
print(eom_493_frequency)
Set8GHzSideband(eom_493_frequency, -20, "ON")
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)