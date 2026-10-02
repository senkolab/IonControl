#FreqScanPMT_Ba138.py created 2020-12-16 13:43:59.066149

import numpy as np
import os
import glob
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

FreqSetTime = 5
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))

BaseFolder = r"Z:\Lab Data\Sessions"
addname = ""
filename = "PMTCount_Ba137_0MHz_DeltaDetune"
filename0, Filepath = GetDataFilePath(BaseFolder, filename, NewFile=False)

(Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba137", getGlobal, setGlobal)
Freq493Array = np.arange(Freq493 - 100e-6,Freq493 + 100e-6, 10e-6)
Freq650Array = np.arange(Freq650 - 100e-6,Freq650 + 100e-6, 10e-6)

print(Filepath)

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
        if not "%s"%RepumpFreq == "%s THz"%Freq650:
            setGlobal("RepumpFreq", Freq650, "THz")
        SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
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