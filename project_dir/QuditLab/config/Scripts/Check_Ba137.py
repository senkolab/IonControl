#Check_Ba137.py created 2026-07-31 10:38:44.123428

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from Functions_Trap import * 
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

Set8GHzSideband(8.101,-20,"ON")
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)