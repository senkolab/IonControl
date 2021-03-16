#FreqScanPMT_Ba138.py created 2020-12-16 13:43:59.066149

import numpy as np
import os
import glob
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *

Default493Freq = 607.42787
Default650Freq = 461.31221
FreqSetTime = 5
CoolSweepsNum = 2

Filepath = r"Z:\Lab Data\Sessions\2021\2021_02\2021_02_16\FreqScan"
filename = "PMTCount_Ba137"

if not os.path.exists(os.path.abspath(Filepath)):
    os.mkdir(os.path.abspath(Filepath))

Freq493Array = np.arange(607.42765,607.42805,0.00002)
Freq650Array = np.arange(461.31175,461.31275,0.00002)

savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_493WL.txt"),'w+')
savetextfile.write(str(Freq493Array))
savetextfile.close()

savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_650WL.txt"),'w+')
savetextfile.write(str(Freq650Array))
savetextfile.close()

CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Ba137"

for h493 in Freq493Array:
    for h650 in Freq650Array:
        (BGydataAvg, BGydataStD) = GetPMTCounts(BGCountsProgram, setScan, startScan, stopScan, getAllData)
        
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"),'a+')
        savetextfile.write(str(BGydataAvg) + "\t")
        savetextfile.close()
        
        CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))
        if not "%s"%RepumpFreq == "%s THz"%Default650Freq:
            setGlobal("RepumpFreq", Default650Freq, "THz")
        SweepCool493(Default493Freq, CoolSweepsNum, getGlobal, setGlobal)
        time.sleep(FreqSetTime)

        (ydatadefAvg, ydatadefStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_default.txt"))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_default.txt"),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_default.txt"),'a+')
        savetextfile.write(str(ydatadefAvg) + "\t")
        savetextfile.close()
        
        CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))
        if not "%s"%CoolingFreq == "%s THz"%h493:
            setGlobal("CoolingFreq", h493, "THz")
        if not "%s"%RepumpFreq == "%s THz"%h650:
            setGlobal("RepumpFreq", h650, "THz")
            time.sleep(FreqSetTime)
        
        (ydataAvg, ydataStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        
        save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"))
        if not save_file:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"),'w+')
        else:
            savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"),'a+')
        savetextfile.write(str(ydataAvg) + "\t")
        savetextfile.close()
    
    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"))
    if not save_file:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"),'w+')
    else:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_BG.txt"),'a+')
    savetextfile.write("\n")
    savetextfile.close()
    
    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_default.txt"))
    if not save_file:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_default.txt"),'w+')
    else:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_default.txt"),'a+')
    savetextfile.write("\n")
    savetextfile.close()

    save_file = glob.glob(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"))
    if not save_file:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"),'w+')
    else:
        savetextfile = open(os.path.abspath(Filepath + "\\" + filename + "_FreqScan.txt"),'a+')
    savetextfile.write("\n")
    savetextfile.close()