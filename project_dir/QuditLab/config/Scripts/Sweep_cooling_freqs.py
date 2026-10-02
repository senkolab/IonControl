#Sweep_cooling_freqs.py created 2026-09-17 16:19:06.532451
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
CoolSweepsNum = 50
(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", script_functions)


Set8GHzSideband(8.101,-20,"ON")
SweepCool493650(Freq493, Freq650, CoolSweepsNum, script_functions)