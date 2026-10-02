#check_Ba138.py created 2026-07-31 10:33:32.269533

import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from Functions_Trap import * 
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

Set8GHzSideband(5.82,-10,"ON")
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", script_functions)