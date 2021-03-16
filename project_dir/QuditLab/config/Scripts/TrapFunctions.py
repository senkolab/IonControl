#Functions/TrapFunctions.py created 2020-08-30 17:15:52.614551
import numpy as np
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\scripting')
from Script import *

FreqSetTime = 3
CountsProgramBa137 = "PMT_CheckCounts_For-Script_Ba137"
CountsProgramEven = "PMT_CheckCounts_For-Script_Even"

def IsotopeFreqs(Isotope):
    #Ba138 Freqs
    Freq493_Ba138 = 607.42601
    Freq650_Ba138 = 461.31207
    Freq553_Ba138 = 541.433040
    #Ba137 Freqs
    #Ba137Offset493 = 5852.47e-6
    Ba137Offset493 = 1833.6e-6
    Freq493_Ba137 = round(Freq493_Ba138 + Ba137Offset493, 5)
    Ba137Offset650 = 105e-6
    Freq650_Ba137 = round(Freq650_Ba138 + Ba137Offset650, 5)
    Ba137Offset553 = 275e-6
    Freq553_Ba137 = round(Freq553_Ba138 + Ba137Offset553, 5)
    #Ba133 Freqs
    Ba133Offset493 = 0
    Freq493_Ba133 = round(Freq493_Ba138 + Ba133Offset493, 5)
    Ba133Offset650 = 500e-6
    Freq650_Ba133 = round(Freq650_Ba138 + Ba133Offset650, 5)
    Ba133Offset553 = 390e-6
    Freq553_Ba133 = round(Freq553_Ba138 + Ba133Offset553, 5)
    #Ba134 Freqs
    Ba134Offset493 = 222.6e-6
    Freq493_Ba134 = round(Freq493_Ba138 + Ba134Offset493, 5)
    Ba134Offset650 = 174.5e-6
    Freq650_Ba134 = round(Freq650_Ba138 + Ba134Offset650, 5)
    Ba134Offset553 = 142.8e-6
    Freq553_Ba134 = round(Freq553_Ba138 + Ba134Offset553, 5)
    #Ba136 Freqs
    Ba136Offset493 = 179.4e-6
    Freq493_Ba136 = round(Freq493_Ba138 + Ba136Offset493, 5)
    Ba136Offset650 = 68e-6
    Freq650_Ba136 = round(Freq650_Ba138 + Ba136Offset650, 5)
    Ba136Offset553 = 128.02e-6
    Freq553_Ba136 = round(Freq553_Ba138 + Ba136Offset553, 5)
    if Isotope == "Ba138":
        Freqs = (Freq493_Ba138, Freq650_Ba138, Freq553_Ba138)
    elif Isotope == "Ba137":
        Freqs = (Freq493_Ba137, Freq650_Ba137, Freq553_Ba137)
    elif Isotope == "Ba133":
        Freqs = (Freq493_Ba133, Freq650_Ba133, Freq553_Ba133)
    elif Isotope == "Ba134":
        Freqs = (Freq493_Ba134, Freq650_Ba134, Freq553_Ba134)
    elif Isotope == "Ba136":
        Freqs = (Freq493_Ba136, Freq650_Ba136, Freq553_Ba136)
    return Freqs

def GetPMTCounts(CountProgram, setScan, startScan, stopScan, getAllData):
    setScan(CountProgram)
    startScan(globalOverrides=list(), wait=True)
    time.sleep(0.05)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    ydataAvg = np.mean(np.array(ydata))
    ydataStD = np.std(np.array(ydata))
    stopScan()   
    return (ydataAvg, ydataStD)
    
def FlushTrapRF(setScan, startScan, stopScan):
    setScan("FlushTrap")
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    
def SetGlobalLaserFreqs(Isotope, getGlobal, setGlobal):
    CoolingFreq, RepumpFreq, IonizationFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), getGlobal("IonizationFreq"))
    (Freq493, Freq650, Freq553) = IsotopeFreqs(Isotope)
    if not "%s"%CoolingFreq == "%s THz"%Freq493:
        setGlobal("CoolingFreq", Freq493, "THz")
        time.sleep(FreqSetTime)
    if not "%s"%RepumpFreq == "%s THz"%Freq650:
        setGlobal("RepumpFreq", Freq650, "THz")
        time.sleep(FreqSetTime)
    if not "%s"%IonizationFreq == "%s THz"%Freq553:
        setGlobal("IonizationFreq", Freq553, "THz")
        time.sleep(FreqSetTime)
    return (Freq493, Freq650, Freq553)
        
def SetCoolLaserFreqs(Isotope, getGlobal, setGlobal):
    CoolingFreq, RepumpFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"))
    (Freq493, Freq650, Freq553) = IsotopeFreqs(Isotope)
    if not "%s"%getGlobal("CoolingFreq") == "%s THz"%Freq493:
        setGlobal("CoolingFreq", Freq493, "THz")
        time.sleep(FreqSetTime)
    if not "%s"%getGlobal("RepumpFreq") == "%s THz"%Freq650:
        setGlobal("RepumpFreq", Freq650, "THz")
        time.sleep(FreqSetTime)
    return (Freq493, Freq650, Freq553)
        
def SweepCool493(Freq, CoolSweepsNum, getGlobal, setGlobal):
    TimeSwitchFreq = getGlobal("TimeSwitchLaserFreqWM")
    TimeCool = getGlobal("TimeCoolBeforeCheck")
    FreqMove1 = Freq - 0.00001
    FreqMove2 = Freq
    FreqChange = FreqMove1
    for i in range(0, CoolSweepsNum):
        cmd = "i=%i, FreqChange=%f"%tuple([i, FreqChange])
        os.system(cmd)
        setGlobal("CoolingFreq",FreqChange,"THz")
        time.sleep(TimeSwitchFreq)
        if i%2 == 1:
            FreqChange = FreqMove1
        else:
            FreqChange = FreqMove2
    if not "%s"%getGlobal("CoolingFreq") == "%s THz"%Freq:
        setGlobal("CoolingFreq", Freq, "THz")
        time.sleep(FreqSetTime)
    time.sleep(TimeCool)
    
def CheckIonIsotopeSelectivity(BGyAvg, BGyStD, BGNumStDevs, getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=True):
    Isotopes = ["Ba137", "Ba134", "Ba136", "Ba138"]
    IonTrapped = False
    for Isotope in Isotopes:    
        if Isotope == "Ba137":
            CountsProgram = CountsProgramBa137
            PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba137"
        else:
            CountsProgram = CountsProgramEven
            PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        (Freq493, Freq650, Freq553) = SetCoolLaserFreqs(Isotope, getGlobal, setGlobal)
        stopScan()
        (yAvg, yStD) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)
        WithinBackground = (BGyAvg - BGNumStDevs*BGyStD < yAvg < BGyAvg + BGNumStDevs*BGyStD)
        print("")
        if not WithinBackground :
            IonTrapped = True
        if Isotope == "Ba137":
            Ba137Avg = yAvg
            Ba137StD = yStD
            if WithinBackground:
                Ba137Trapped = False
            else:
                Ba137Trapped = True
        elif Isotope == "Ba134":
            Ba134Avg = yAvg
            Ba134StD = yStD
            if WithinBackground:
                Ba134Trapped = False
            else:
                Ba134Trapped = True
        elif Isotope == "Ba136":
            Ba136Avg = yAvg
            Ba136StD = yStD
            if WithinBackground:
                Ba136Trapped = False
            else:
                Ba136Trapped = True
        elif Isotope == "Ba138":
            Ba138Avg = yAvg
            Ba138StD = yStD
            if WithinBackground:
                Ba138Trapped = False
            else:
                Ba138Trapped = True
    Ba137 = [Ba137Avg, Ba137StD, Ba137Trapped]
    Ba134 = [Ba134Avg, Ba134StD, Ba134Trapped]
    Ba136 = [Ba136Avg, Ba136StD, Ba136Trapped]
    Ba138 = [Ba138Avg, Ba138StD, Ba138Trapped]
    return (IonTrapped, Ba137, Ba134, Ba136, Ba138)
    
def CheckIonTrapped(BGyAvg, BGyStDev, yAvg, Count, Isotope, getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=True):
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (BGyAvg - BGNumStDevs*BGyStDev < yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        if Isotope == "Ba138":
            IonTrapped = True
            if Comm:
                os.system("C:/Users/ions/Documents/Beep.bat")
                #cmd = "start cmd wait /k echo Ion trapped, with %f counts average. Total ablation pulses: %i"%tuple([yAvg, Count])
                #os.system(cmd)
        elif Isotope == "Ba137" or Isotope == "Ba133":
            #Move cooling freqs to Ba138 freqs
            (Freq493_Ba138, Freq650_Ba138, Freq553_Ba138) = SetCoolLaserFreqs("Ba138", getGlobal, setGlobal)
            #Get counts with Ba138 freqs, and EOMs turned off
            (yAvg_Ba138, yStD_Ba138) = GetPMTCounts("PMT_CheckCounts_For-Script_Even", setScan, startScan, stopScan, getAllData)
            
            if (BGyAvg - BGNumStDevs*BGyStDev < yAvg_Ba138 < BGyAvg + BGNumStDevs*BGyStDev):
                #Return to Isotope Freqs
                if Isotope == "Ba137":
                    (Freq493_Ba137, Freq650_Ba137, Freq553_Ba137) = SetCoolLaserFreqs("Ba137", getGlobal, setGlobal)
                else:
                    (Freq493_Ba133, Freq650_Ba133, Freq553_Ba133) = SetCoolLaserFreqs("Ba133", getGlobal, setGlobal)
            IonTrapped = True
            if Comm:
                os.system("C:/Users/ions/Documents/Beep.bat")
    else:
        IonTrapped = False
    return IonTrapped

def CheckIonTrappedNoIsotopeCycle(BGyAvg, BGyStDev, yAvg, Count, Isotope, getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=True):
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (BGyAvg - BGNumStDevs*BGyStDev < yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        IonTrapped = True
        if Comm:
            os.system("C:/Users/ions/Documents/Beep.bat")
            cmd = "start /wait cmd /k echo Ion trapped, with %f counts average. Total ablation pulses: %i."%tuple([yAvg, Count])
            os.system(cmd)
    else:
        IonTrapped = False
    return IonTrapped

def ResetAblation():
    os.system('ssh pi@192.168.168.122 cd Documents; python press_stop_button.py')
    time.sleep(4)
    os.system('ssh pi@192.168.168.122 cd Documents; python press_start_button.py')

def SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData):
    (BGydataAvg1, BGydataStD1) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

    setScan("Toggle_Beam_Samplers")
    startScan(globalOverrides=list(), wait=True)

    (BGydataAvg2, BGydataStD2) = GetPMTCounts(CountsProgram, setScan, startScan, stopScan, getAllData)

    if BGydataAvg2 < BGydataAvg1:
        setScan("Toggle_Beam_Samplers")
        startScan(globalOverrides=list(), wait=True)