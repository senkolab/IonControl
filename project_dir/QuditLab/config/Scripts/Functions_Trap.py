#Functions/TrapFunctions.py created 2020-08-30 17:15:52.614551
import numpy as np
import sys
import time
import os
import serial
from serial.serialutil import SerialException
#Add the following line to package the script functions to easily send to these functions
#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

#FreqSetTime = 3
#FreqSetTime614 = 10
CountsProgramBa137 = "PMT_CheckCounts_For-Script_Ba137"
CountsProgramEven = "PMT_CheckCounts_For-Script_Even"

PulseAblationDummyProgramEven = "PulseAblation_For-Script_Dummy_Ba138"

#Function IsotopeFreqs: Gives optical laser frequencies of the transitions from lasers controlled by the wavemeter, for a specific isotope. Input Isotope (string i.e. "Ba138"),  getGlobal
#Returns Freqs=(Freq493, Freq650, Freq553, Freq614)
def IsotopeFreqs(Isotope, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    #Ba138 Freqs
    Freq493_Ba138_Opt = getGlobal("Ba138_CoolingFreq_Opt").magnitude
    Freq650_Ba138_Opt = getGlobal("Ba138_RepumpFreq_Opt").magnitude
    Freq553_Ba138_Opt = getGlobal("Ba138_IonizationFreq_Opt").magnitude
    Freq614_Ba138_Opt = getGlobal("Ba138_ShelvingRepumpFreq_Opt").magnitude
    Freq493_Ba138_Off = getGlobal("Ba138_CoolingFreq_Offset").magnitude*1e-6
    Freq650_Ba138_Off = getGlobal("Ba138_RepumpFreq_Offset").magnitude*1e-6
    Freq553_Ba138_Off = getGlobal("Ba138_IonizationFreq_Offset").magnitude*1e-6
    Freq614_Ba138_Off = getGlobal("Ba138_ShelvingRepumpFreq_Offset").magnitude
    Freq493_Ba138 = Freq493_Ba138_Opt + Freq493_Ba138_Off
    Freq650_Ba138 = Freq650_Ba138_Opt + Freq650_Ba138_Off
    Freq553_Ba138 = Freq553_Ba138_Opt + Freq553_Ba138_Off
    Freq614_Ba138 = Freq614_Ba138_Opt + Freq614_Ba138_Off
    #Ba137 Freqs
    #Ba137Offset493 = 5852.47e-6
    Ba137Offsetchange493 = getGlobal("Ba137_CoolingFreq_Offset_Change").magnitude*1e-6
    Ba137Offset493 = getGlobal("Ba137_CoolingFreq_Offset").magnitude*1e-6
    Ba137Offset493 += Ba137Offsetchange493
    Freq493_Ba137 = round(Freq493_Ba138_Opt + Ba137Offset493, 6)
    Ba137Offsetchange650 = getGlobal("Ba137_RepumpFreq_Offset_Change").magnitude*1e-6
    Ba137Offset650 = getGlobal("Ba137_RepumpFreq_Offset").magnitude*1e-6
    Ba137Offset650 += Ba137Offsetchange650
    Freq650_Ba137 = round(Freq650_Ba138_Opt + Ba137Offset650, 6)
    Ba137Offsetchange553 = getGlobal("Ba137_IonizationFreq_Offset").magnitude*1e-6
    Ba137Offset553 = 275e-6
    #Ba137Offset553 = 549.47e-6 #https://cdnsciencepub.com/doi/abs/10.1139/p95-069
    Ba137Offset553 += Ba137Offsetchange553
    Freq553_Ba137 = round(Freq553_Ba138_Opt + Ba137Offset553, 6)
    Ba137Offset614 = getGlobal("Ba137_ShelvingRepumpFreq_Offset").magnitude*1e-6
    Freq614_Ba137 = round(Freq614_Ba138_Opt + Ba137Offset614, 6)
    #Ba133 Freqs
    Ba133Offset493, Ba133Offset650, Ba133Offset553, Ba133Offset614 = 200e-6, 530e-6, 390e-6, 0
    Freq493_Ba133, Freq650_Ba133 = round(Freq493_Ba138 + Ba133Offset493, 6), round(Freq650_Ba138 + Ba133Offset650, 6)
    Freq553_Ba133, Freq614_Ba133 = round(Freq553_Ba138 + Ba133Offset553, 6), round(Freq614_Ba138 + Ba133Offset614, 6)
    #Ba134 Freqs
    Ba134Offset493, Ba134Offset650, Ba134Offset553, Ba134Offset614 = 222.6e-6, 174.5e-6, 142.8e-6, 194.7e-6
    Freq493_Ba134, Freq650_Ba134 = round(Freq493_Ba138 + Ba134Offset493, 6), round(Freq650_Ba138 + Ba134Offset650, 6)
    Freq553_Ba134, Freq614_Ba134 = round(Freq553_Ba138 + Ba134Offset553, 6), round(Freq614_Ba138 + Ba134Offset614, 6)
    #Ba136 Freqs
    Ba136Offset493, Ba136Offset650, Ba136Offset553, Ba136Offset614 = 179.4e-6, 68e-6, 128.02e-6, 80.3e-6
    Freq493_Ba136, Freq650_Ba136 = round(Freq493_Ba138 + Ba136Offset493, 6), round(Freq650_Ba138 + Ba136Offset650, 6)
    Freq553_Ba136, Freq614_Ba136 = round(Freq553_Ba138 + Ba136Offset553, 6), round(Freq614_Ba138 + Ba136Offset614, 6)
    #Ba132 Freqs
    Ba132Offset493, Ba132Offset650, Ba132Offset553, Ba132Offset614 = 278.9e-6, 292e-6, 167.9e-6, 311.4e-6
    Freq493_Ba132, Freq650_Ba132 = round(Freq493_Ba138 + Ba132Offset493, 6), round(Freq650_Ba138 + Ba132Offset650, 6)
    Freq553_Ba132, Freq614_Ba132 = round(Freq553_Ba138 + Ba132Offset553, 6), round(Freq614_Ba138 + Ba132Offset614, 6)
    #Ba130 Freqs
    Ba130Offset493, Ba130Offset650, Ba130Offset553, Ba130Offset614 = 355.3e-6, 394e-6, 207.3e-6, 426e-6
    Freq493_Ba130, Freq650_Ba130 = round(Freq493_Ba138 + Ba130Offset493, 6), round(Freq650_Ba138 + Ba130Offset650, 6)
    Freq553_Ba130, Freq614_Ba130 = round(Freq553_Ba138 + Ba130Offset553, 6), round(Freq614_Ba138 + Ba130Offset614, 6)
    if Isotope == "Ba138":
        Freqs = (Freq493_Ba138, Freq650_Ba138, Freq553_Ba138, Freq614_Ba138)
    elif Isotope == "Ba137":
        Freqs = (Freq493_Ba137, Freq650_Ba137, Freq553_Ba137, Freq614_Ba137)
    elif Isotope == "Ba133":
        Freqs = (Freq493_Ba133, Freq650_Ba133, Freq553_Ba133, Freq614_Ba133)
    elif Isotope == "Ba134":
        Freqs = (Freq493_Ba134, Freq650_Ba134, Freq553_Ba134, Freq614_Ba134)
    elif Isotope == "Ba136":
        Freqs = (Freq493_Ba136, Freq650_Ba136, Freq553_Ba136, Freq614_Ba136)
    elif Isotope == "Ba132":
        Freqs = (Freq493_Ba132, Freq650_Ba132, Freq553_Ba132, Freq614_Ba132)
    elif Isotope == "Ba130":
        Freqs = (Freq493_Ba130, Freq650_Ba130, Freq553_Ba130, Freq614_Ba130)
    return Freqs

#Function GetPMTCounts: Runs the PMT count scan to collect PMT counts. Input CountProgram: which scan to run, setScan, startScan, stopScan, getAllData
#ReturnsydataAvg: the average PMT counts from the scan, and ydataStD: the std of the PMT counts data
def GetPMTCounts(CountProgram, script_functions, bg=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    setScan(CountProgram)
    startScan(globalOverrides=list(), wait=True)
    time.sleep(0.01)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    print(ydata)
    ydataAvg = np.mean(np.array(ydata))
    ydataStD = np.std(np.array(ydata))
    
    stopScan()
    if bg:
        SetPMTBackground(ydataAvg, ydataStD, script_functions, bg=bg)
    return (ydataAvg, ydataStD)


#Function SetPMTBackground: sets the global variable that keeps track of the PMT background counts. Input ydataAvg: PMT measurement average of background, ydataStD: standard deviation of measurement, script_functions
def SetPMTBackground(ydataAvg, ydataStD, script_functions, bg=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    if bg:
        PMT_GlobalIntBG = "PMT_Integration_Time_BG"
        PMT_GlobalBG = "PMT_CurrentBG"
        PMT_GlobalBGStD = "PMT_CurrentBGStD"
    else:
        PMT_GlobalIntBG = "PMT_Integration_Time"
        PMT_GlobalBG = "IonBrightness"
        PMT_GlobalBGStD = "IonBrightness_StD"
    PMT_Integration_BG = getGlobal(PMT_GlobalIntBG).magnitude
    BG_Rate = 1000*ydataAvg/PMT_Integration_BG #Assumes ms units
    BG_Rate_std = 1000*ydataStD/PMT_Integration_BG
    BG_Current = getGlobal(PMT_GlobalBG)
    BG_CurrentStD = getGlobal(PMT_GlobalBGStD)
    if not "%s"%BG_Current == "%s Hz"%BG_Rate:
        setGlobal(PMT_GlobalBG, BG_Rate, "Hz")
    if not "%s"%BG_CurrentStD == "%s Hz"%BG_Rate_std:
        setGlobal(PMT_GlobalBGStD, BG_Rate_std, "Hz")
    
#Function FlushTrapRF: Runs the FlushTrap scan, which turns off the trap rf and turns it back on (only works if TTL switch setup on trap RF). Input setScan, startScan, stopScan
def FlushTrapRF(script_functions, TTL=False):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    if TTL:
        setScan("FlushTrap")
        startScan(globalOverrides=list(), wait=True)
        stopScan()
    else:
        trapRF_amp = getGlobal("TrapRFAmp")
        if not "%s"%trapRF_amp == "0 V":
            setGlobal("TrapRFAmp", 0, "V")
        time.sleep(0.1)
        setGlobal("TrapRFAmp", 4, "V")
    
#Function SetGlobalLaserFreqs: sets the wavemeter lasers to the frequencies needed for the isotope. Input Isotope: which isotope to set frequencies based on, getGlobal, setGlobal
#Returns the frequencies setpoints (Freq493, Freq650, Freq553, Freq614)
def SetGlobalLaserFreqs(Isotope, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    CoolingFreq, RepumpFreq, IonizationFreq, ShelvingRepumpFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"), \
        getGlobal("IonizationFreq"), getGlobal("ShelvingRepumpFreq"))
    Time_Cooling, Time_Repump, Time_Ionization, Time_ShelvingRepump = getGlobal("TimeSwitchFreqWM_Cooling").magnitude, \
        getGlobal("TimeSwitchFreqWM_Repump").magnitude, getGlobal("TimeSwitchFreqWM_Ionization").magnitude, \
        getGlobal("TimeSwitchFreqWM_ShelvingRepump").magnitude
    (Freq493, Freq650, Freq553, Freq614) = IsotopeFreqs(Isotope, script_functions)
    if not "%s"%CoolingFreq == "%s THz"%Freq493:
        setGlobal("CoolingFreq", Freq493, "THz")
        time.sleep(Time_Cooling)
    if not "%s"%RepumpFreq == "%s THz"%Freq650:
        setGlobal("RepumpFreq", Freq650, "THz")
        time.sleep(Time_Repump)
    if not "%s"%IonizationFreq == "%s THz"%Freq553:
        setGlobal("IonizationFreq", Freq553, "THz")
        time.sleep(Time_Ionization)
    if not "%s"%ShelvingRepumpFreq == "%s THz"%Freq614:
        setGlobal("ShelvingRepumpFreq", Freq614, "THz")
        time.sleep(Time_ShelvingRepump)
    return (Freq493, Freq650, Freq553, Freq614)

def SetPulsesPer(Isotope, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    pulsesPer_pp_var = "AblationPulsesPer"
    if Isotope == 138:
        pulsesPer_var = "AblationPulsesPer_Ba138"
    elif Isotope == 137:
        pulsesPer_var = "AblationPulsesPer_Ba137"
    PulsesPer = int(getGlobal(pulsesPer_var).magnitude)
    CurrPulsesPer = int(getGlobal(pulsesPer_pp_var).magnitude)
    if CurrPulsesPer != PulsesPer:
        setGlobal(pulsesPer_pp_var, PulsesPer, "")
    return PulsesPer

def SetNeutralFluorWindow(window_start, window_width, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%window_start:
        setGlobal("NeutralFluorescenceWindowStart", window_start, "us")
    if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%window_width:
        setGlobal("NeutralFluorescenceWindowWidth", window_width, "us")
        
#Function SetCoolLaserFreqs: Sets only the doppler cooling frequencies 493 and 650 nm. Input: Isotope, getGlobal, setGlobal
#Returns the frequency setpoints Freq493, Freq650, Freq553, Freq614)
def SetCoolLaserFreqs(Isotope, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    CoolingFreq, RepumpFreq = (getGlobal("CoolingFreq"), getGlobal("RepumpFreq"))
    Time_Cooling, Time_Repump = getGlobal("TimeSwitchFreqWM_Cooling").magnitude, \
        getGlobal("TimeSwitchFreqWM_Repump").magnitude
    (Freq493, Freq650, Freq553, Freq614) = IsotopeFreqs(Isotope, script_functions)
    if not "%s"%getGlobal("CoolingFreq") == "%s THz"%Freq493:
        setGlobal("CoolingFreq", Freq493, "THz")
        time.sleep(Time_Cooling)
    if not "%s"%getGlobal("RepumpFreq") == "%s THz"%Freq650:
        setGlobal("RepumpFreq", Freq650, "THz")
        time.sleep(Time_Repump)
    return (Freq493, Freq650, Freq553, Freq614)

#Function Set1762Offset: Sets the PDH EOM frequency. Input freq, getGlobal, setGlobal
def Set1762Offset(freq, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    EOM_1762_freq = getGlobal("EOM_1762_Freq").magnitude
    os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%(freq*1e6))
    if not "%s"%EOM_1762_freq == "%s MHz"%set_freq:
        setGlobal("EOM_1762_Freq", freq, "MHz")
        
#Function SweepCool493: Sweep the 493 nm laser frequency sevaral times to aid in crystallization. Input Freq: upper frequency of sweeping, CoolSweepsNum: number of sweeps to do, getGlobal, setGlobal
def SweepCool493(Freq, CoolSweepsNum, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    Time_Cooling = getGlobal("TimeSwitchFreqWM_Cooling").magnitude
    Time_Wait = getGlobal("TimeCoolBeforeCheck").magnitude
    #FreqMove1 = Freq - 0.00001
    FreqMove1 = np.round(Freq - 0.0002, 6)
    FreqMove2 = np.round(Freq, 6)
    FreqChange = FreqMove1
    for i in range(0, CoolSweepsNum):
        cmd = "i={0}, FreqChange={1}".format(int(i), float(FreqChange))
        #os.system(cmd)
        print(cmd)
        setGlobal("CoolingFreq",FreqChange,"THz")
        if i%2 == 1:
            FreqChange = FreqMove1
            time.sleep(Time_Cooling)
        else:
            FreqChange = FreqMove2
            time.sleep(0.5)
    if not "%s"%getGlobal("CoolingFreq") == "%s THz"%Freq:
        setGlobal("CoolingFreq", Freq, "THz")
        time.sleep(Time_Cooling)
    time.sleep(Time_Wait)
   
#Function SweepCool493: Sweep the 493 nm laser frequency sevaral times to aid in crystallization. Input Freq: upper frequency of sweeping, CoolSweepsNum: number of sweeps to do, getGlobal, setGlobal
def SweepCool493650(Freq, Freq650, CoolSweepsNum, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    Time_Cooling = getGlobal("TimeSwitchFreqWM_Cooling").magnitude
    Time_Wait = getGlobal("TimeCoolBeforeCheck").magnitude
    #FreqMove1 = Freq - 0.00001
    FreqMove1 = np.round(Freq - 0.0002, 6)
    FreqMove2 = np.round(Freq, 6)
    Freq650Move1 = np.round(Freq650 - 0.0002, 6)
    Freq650Move2 = np.round(Freq650, 6)
    FreqChange = FreqMove1
    Freq650Change = Freq650Move1
    for i in range(0, CoolSweepsNum):
        cmd = "i={0}, FreqChange={1}".format(int(i), float(FreqChange))
        #os.system(cmd)
        print(cmd)
        setGlobal("CoolingFreq",FreqChange,"THz")
        setGlobal("RepumpFreq",Freq650Change,"THz")
        if i%2 == 1:
            FreqChange = FreqMove1
            Freq650Change = Freq650Move1
            time.sleep(Time_Cooling)
        else:
            FreqChange = FreqMove2
            Freq650Change = Freq650Move2
            time.sleep(0.5)
    if not "%s"%getGlobal("CoolingFreq") == "%s THz"%Freq:
        setGlobal("CoolingFreq", Freq, "THz")
        setGlobal("RepumpFreq",Freq650,"THz")
        time.sleep(Time_Cooling)
    time.sleep(Time_Wait)

#Function CheckIonTrappedNoIsotopeCycle: Simpler check for trapped ion - don't check other isotopes. Input BGyAvg: average BG, BGyStDev: std BG, yAvg: counts from PMT, Isotope: Which isotope to check for, getGlobal, Comm=True: whether to run cmd when trapped
#Returns IonTrapped boolean
def CheckIonTrappedNoIsotopeCycle(yAvg, yStd, Count, Isotope, script_functions, Comm=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    PMT_GlobalIntBG = "PMT_Integration_Time_BG"
    BGyInt = getGlobal("PMT_Integration_Time_BG").magnitude #ms
    BGyAvg = getGlobal("PMT_CurrentBG").magnitude
    BGyStDev = getGlobal("PMT_CurrentBGStD").magnitude
    yInt = getGlobal("PMT_Integration_Time").magnitude #ms
    #print(f'yInt: {yInt}, yAvg:{yAvg}, yStd:{yStd}')
    #Scale BG to same scale as yAvg measurement
    BGyAvg = BGyAvg*yInt/1000
    BGyStDev = BGyStDev*yInt/1000
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        IonTrapped = True
        SetPMTBackground(yAvg, yStd, script_functions, bg=False)
        if Comm:
            os.system("C:/Users/ions/Documents/Beep.bat")
            cmd = "start /wait cmd /k echo Ion trapped, with %f counts average. Total ablation pulses: %i."%tuple([yAvg*1000/yInt, Count])
            os.system(cmd)
    else:
        IonTrapped = False
    return IonTrapped

def CheckIonTrappedNoIsotopeCycleNoCMD(yAvg, yStd, Count, Isotope, script_functions, Comm=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    PMT_GlobalIntBG = "PMT_Integration_Time_BG"
    BGyInt = getGlobal("PMT_Integration_Time_BG").magnitude #ms
    BGyAvg = getGlobal("PMT_CurrentBG").magnitude
    BGyStDev = getGlobal("PMT_CurrentBGStD").magnitude
    yInt = getGlobal("PMT_Integration_Time").magnitude #ms
    #print(f'yInt: {yInt}, yAvg:{yAvg}, yStd:{yStd}')
    #Scale BG to same scale as yAvg measurement
    BGyAvg = BGyAvg*yInt/1000
    BGyStDev = BGyStDev*yInt/1000
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        IonTrapped = True
        SetPMTBackground(yAvg, yStd, script_functions, bg=False)
    else:
        IonTrapped = False
    return IonTrapped

#Returns IonTrapped boolean
def CheckIonTrappedHeadless(yAvg, yStd, Count, Isotope, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    PMT_GlobalIntBG = "PMT_Integration_Time_BG"
    BGyInt = getGlobal("PMT_Integration_Time_BG").magnitude #ms
    BGyAvg = getGlobal("PMT_CurrentBG").magnitude
    BGyStDev = getGlobal("PMT_CurrentBGStD").magnitude
    yInt = getGlobal("PMT_Integration_Time").magnitude #ms
    #print(f'yInt: {yInt}, yAvg:{yAvg}, yStd:{yStd}')
    #Scale BG to same scale as yAvg measurement
    BGyAvg = BGyAvg*yInt/1000
    BGyStDev = BGyStDev*yInt/1000
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        IonTrapped = True
        SetPMTBackground(yAvg, yStd, script_functions, bg=False)
    else:
        IonTrapped = False
    return IonTrapped
    
def CheckIonTrappedWithBa138Check(yAvg, yStd, Count, Ba138Count, Isotope, script_functions, Comm=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    PMT_GlobalIntBG = "PMT_Integration_Time_BG"
    BGyInt = getGlobal("PMT_Integration_Time_BG").magnitude #ms
    BGyAvg = getGlobal("PMT_CurrentBG").magnitude
    BGyStDev = getGlobal("PMT_CurrentBGStD").magnitude
    yInt = getGlobal("PMT_Integration_Time").magnitude #ms
    #print(f'yInt: {yInt}, yAvg:{yAvg}, yStd:{yStd}')
    #Scale BG to same scale as yAvg measurement
    BGyAvg = BGyAvg*yInt/1000
    BGyStDev = BGyStDev*yInt/1000
    BGNumStDevs = getGlobal("BGCheckNumStDevs")
    if not (yAvg < BGyAvg + BGNumStDevs*BGyStDev):
        IonTrapped = True
        SetPMTBackground(yAvg, yStd, script_functions, bg=False)
        if Comm:
            os.system("C:/Users/ions/Documents/Beep.bat")
            cmd = "start /wait cmd /k echo Ion trapped, with %f counts average. Total ablation pulses: %i. Total Ba138 positive checks: %i."%tuple([np.round(yAvg*1000/yInt), Count, Ba138Count])
            os.system(cmd)
    else:
        IonTrapped = False
    return IonTrapped
    
def Check_Ba138_Present(PulseAblationDummyProgram, GHZ_Sideband, NumCoolSweeps, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    CoolSweepsNum = NumCoolSweeps
    BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
    CountsProgram = "PMT_CheckCounts_For-Script_Even"

    Set8GHzSideband(GHZ_Sideband,-5,"ON")

    (BGydataAvg, BGydataStd) = GetPMTCounts(BGCountsProgram, script_functions, bg=True) 

    (Freq493, Freq650, Freq553, Freq614) = SetGlobalLaserFreqs("Ba138", script_functions)
    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    #SweepCool493650(Freq493, Freq650, CoolSweepsNum, script_functions)
    SweepCool493(Freq493, CoolSweepsNum, script_functions)
    stopScan()
    
    (ydataAvg, ydataStd) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    Ba138_Present = CheckIonTrappedHeadless(ydataAvg, ydataStd, 0, "Ba138", script_functions)

    return Ba138_Present

#Function ResetAblation: resets the ablation laser by pressing the stop and start buttons using the stepper motors. Inputs setScan, startScan, stopScan
def ResetAblation(script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    os.system('ssh pi@192.168.168.122 cd Documents; python press_stop_button.py')
    time.sleep(2)
    #os.system('ssh pi@192.168.168.122 cd Documents; python press_start_button.py')
    setScan(PulseAblationDummyProgramEven)
    startScan(globalOverrides=list(), wait=False)
    time.sleep(0.5)
    stopScan()

#Function SendLasersToTrap: Check that the lasers are being sent to the trap, (flipper mirrors flip often when restarting program). Inputs setScan, startScan, stopScan, getAllData
def SendLasersToTrap(CountsProgram, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    (BGydataAvg1, BGydataStD1) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    setScan("Toggle_Beam_Samplers")
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    (BGydataAvg2, BGydataStD2) = GetPMTCounts(CountsProgram, script_functions, bg=False)
    if BGydataAvg2 < BGydataAvg1:
        setScan("Toggle_Beam_Samplers")
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        #SetPMTBackground(BGydataAvg1, BGydataStD1, script_functions, bg=True)
    #else:
        #SetPMTBackground(BGydataAvg2, BGydataStD2, script_functions, bg=True)
        

#Function SetDCVoltages: Sets the trap rod voltages. Input HorizontalVoltage, VerticalVoltage, Squeeze_1_4_V, Squeeze_2_3_V. Inputs getGlobal, setGlobal
def SetDCVoltages(HorizontalVoltage,VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    if HorizontalVoltage < 0:
        Push_Horizontal_Down = -HorizontalVoltage
        Push_Horizontal_Up = 0
    else:
        Push_Horizontal_Down = 0
        Push_Horizontal_Up = HorizontalVoltage
    if VerticalVoltage < 0:
        Push_Vertical_Down = -VerticalVoltage
        Push_Vertical_Up = 0
    else:
        Push_Vertical_Down = 0
        Push_Vertical_Up = VerticalVoltage
    
    Rod_1_V = getGlobal("Rod_1_Voltage_V")
    Rod_2_V = getGlobal("Rod_2_Voltage_V")
    Rod_3_V = getGlobal("Rod_3_Voltage_V")
    Rod_4_V = getGlobal("Rod_4_Voltage_V")

    Rod_1_set_V = Push_Vertical_Down + Push_Horizontal_Up + Squeeze_1_4_V
    Rod_2_set_V = Push_Vertical_Up + Push_Horizontal_Up + Squeeze_2_3_V
    Rod_3_set_V = Push_Vertical_Down + Push_Horizontal_Down + Squeeze_2_3_V
    Rod_4_set_V = Push_Vertical_Up + Push_Horizontal_Down + Squeeze_1_4_V

    if not "%s"%Rod_1_V == "%s V"%Rod_1_set_V:
        setGlobal("Rod_1_Voltage_V", Rod_1_set_V, "V")

    if not "%s"%Rod_2_V == "%s V"%Rod_2_set_V:
        setGlobal("Rod_2_Voltage_V", Rod_2_set_V, "V")

    if not "%s"%Rod_3_V == "%s V"%Rod_3_set_V:
        setGlobal("Rod_3_Voltage_V", Rod_3_set_V, "V")

    if not "%s"%Rod_4_V == "%s V"%Rod_4_set_V:
        setGlobal("Rod_4_Voltage_V", Rod_4_set_V, "V")

def Set8GHzSideband(freq,att_db,status = "ON", max_retries=3, retry_delay=1):

    #ser = serial.Serial(
    #port='COM6',        
    #baudrate=115200,     
    #bytesize=serial.EIGHTBITS,
    #stopbits=serial.STOPBITS_ONE,
    #parity=serial.PARITY_NONE,
    #timeout=1         )
    attempt = 0
    while attempt < max_retries:
        try:
            with serial.Serial(
                port="COM6",
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
               stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE,
                timeout=1,
            ) as ser:

                def send_command(command):
                    command+= '\n'
                    ser.write(command.encode())
                    time.sleep(0.1)
                    response = ser.readline().decode().strip()
                    return response

                send_command(f"POWER {att_db}")
                send_command(f"FREQ:CW {freq}GHz")
                send_command("OUTP:STAT "+status)
            return None
        except SerialException as e:
            attempt+=1
            time.sleep(retry_delay)
    return None