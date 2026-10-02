#Scan_EOM_micromotion.py created 2021-07-22 14:34:22.713784

import numpy as np
import os
import glob
import sys
import time

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

Default493Freq = 607.42421
Default650Freq = 461.31209
FreqSetTime = 5

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename0 = f"Micromotion_493EOM_Scan_10.txt"
filename0, Filepath = GetDataFilePath(BaseFolder, filename0, NewFile=False)

filename_freq, Filepath_freq = GetDataFilePath(BaseFolder, f"Micromotion_493EOM_freq_10.txt", NewFile=False)

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

EOM493Freqs = np.arange(1760,1820,1)

CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))

CountsProgram = "PMT_CheckCounts_For-Script_Even_withEOM"

ExperimentNumber = 3

CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))
if not "%s"%RepumpFreq == "%s THz"%Default650Freq:
    setGlobal("RepumpFreq", Default650Freq, "THz")
if not "%s"%CoolingFreq == "%s THz"%Default493Freq:
    setGlobal("CoolingFreq", Default493Freq, "THz")
time.sleep(FreqSetTime)

for hExpNum in range(ExperimentNumber):
    for hEOM in EOM493Freqs:
        EOM493Freq = hEOM
        os.system('ssh pi@192.168.168.103 python pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 14')
        time.sleep(0.1)
        os.system('ssh pi@192.168.168.103 python pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 1760')
        time.sleep(1)
        os.system('ssh pi@192.168.168.103 python pll-evalboard-synthesizer/src/Control-Programs/rf1.py 5 %s'%EOM493Freq)
        time.sleep(0.2)
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

        save_file = glob.glob(os.path.abspath(filename0))
        if not save_file:
            savetextfile = open(os.path.abspath(filename0),'w+')
        else:
            savetextfile = open(os.path.abspath(filename0),'a+')
        savetextfile.write(str(ydataAvg) + "\t")
        savetextfile.close()
        
        if hExpNum == 0:
            save_file = glob.glob(os.path.abspath(filename_freq))
            if not save_file:
                savetextfile = open(os.path.abspath(filename_freq),'w+')
            else:
                savetextfile = open(os.path.abspath(filename_freq),'a+')
            savetextfile.write(str(EOM493Freq) + "\t")
            savetextfile.close()
    
    save_file = glob.glob(os.path.abspath(filename0))
    if not save_file:
        savetextfile = open(os.path.abspath(filename0),'w+')
    else:
        savetextfile = open(os.path.abspath(filename0),'a+')
    savetextfile.write("\n")
    savetextfile.close()