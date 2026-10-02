#Scan_614_Experiment_fast.py created 2022-02-14 15:30:38.331955
import sys
import numpy as np
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *

#(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
Freq614 = 487.98988

Scan614Start = getGlobal("Repump614ScanBeginning").magnitude*1e-6
Scan614End = getGlobal("Repump614ScanEnd").magnitude*1e-6
Scan614Res = getGlobal("Repump614ScanRes").magnitude*1e-6

freq_array = np.arange(Scan614Start,Scan614End,Scan614Res)
freq_array += Freq614
offset_freq = 487.989
freq_array = np.round(freq_array, 6)

createTrace('614spectrum_data', 'Script Data', xLabel=f'Freq (MHz) + {offset_freq} THz')
for set_freq in freq_array:
    Repump_614_freq = getGlobal("ShelvingRepumpFreq").magnitude
    if not "%s"%Repump_614_freq == "%s THz"%set_freq:
        setGlobal("ShelvingRepumpFreq", set_freq, "THz")
        time.sleep(10)
    setScan("Repump_Shelve_Scan_Even")
    startScan(globalOverrides=list(), wait=True)
    freq_MHz = (set_freq - offset_freq)*1e6
    data = getAllData()["PMT Count"]
    datamean = np.mean(data[1])
    plotPoint(freq_MHz, datamean, '614spectrum_data', plotStyle=1)
closeTrace('614spectrum_data')