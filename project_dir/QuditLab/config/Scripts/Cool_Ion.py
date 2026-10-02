#Cool_Ion.py created 2022-07-26 19:52:40.587289
import sys
import time

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

WhichIon = int(getGlobal("WhichIon").magnitude)
time_wait = 120
time_wait = 1

(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs(f"Ba{WhichIon}", script_functions)
for i in range(200):
    if scriptIsStopped():
        break
    SweepCool493(Freq493, 3, script_functions)
    time.wait(time_wait)