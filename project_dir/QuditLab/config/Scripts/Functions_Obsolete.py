#Functions_Obsolete.py created 2022-08-09 18:44:05.990071
#Function CheckIonIsotopeSelectivity: Inputs BGyAvg, bGyStD, BGNumStDevs, getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, Comm=True: whether to run cmd when trapped
def CheckIonIsotopeSelectivity(BGyAvg, BGyStD, BGNumStDevs, script_functions, Comm=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
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
        (Freq493, Freq650, Freq553) = SetCoolLaserFreqs(Isotope, script_functions)
        stopScan()
        (yAvg, yStD) = GetPMTCounts(CountsProgram, script_functions)
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
    
#Function CheckIonTrapped: Check if an ion was trapped. Input BGyAvg: average BG, BGyStDev: std BG, yAvg: counts from PMT, Isotope: Which isotope to check for, getGlobal, segGlobal, Comm=True: whether to run cmd when trapped
#Returns IonTrapped boolean
def CheckIonTrapped(yAvg, Count, Isotope, script_functions, Comm=True):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    PMT_GlobalIntBG = "PMT_Integration_Time_BG"
    BGyInt = getGlobal("PMT_Integration_Time_BG").magnitude #ms
    BGyAvg = getGlobal("PMT_CurrentBG").magnitude
    BGyStD = getGlobal("PMT_CurrentBGStD").magnitude
    yInt = getGlobal("PMT_Integration_Time").magnitude #ms
    #Scale yAvg to same scale as BG measurement
    yAvg *= BGyInt/yInt
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
            (Freq493_Ba138, Freq650_Ba138, Freq553_Ba138) = SetCoolLaserFreqs("Ba138", script_functions)
            #Get counts with Ba138 freqs, and EOMs turned off
            (yAvg_Ba138, yStD_Ba138) = GetPMTCounts("PMT_CheckCounts_For-Script_Even", script_functions)
            
            if (BGyAvg - BGNumStDevs*BGyStDev < yAvg_Ba138 < BGyAvg + BGNumStDevs*BGyStDev):
                #Return to Isotope Freqs
                if Isotope == "Ba137":
                    (Freq493_Ba137, Freq650_Ba137, Freq553_Ba137) = SetCoolLaserFreqs("Ba137", script_functions)
                else:
                    (Freq493_Ba133, Freq650_Ba133, Freq553_Ba133) = SetCoolLaserFreqs("Ba133", script_functions)
            IonTrapped = True
            if Comm:
                os.system("C:/Users/ions/Documents/Beep.bat")
    else:
        IonTrapped = False
    return IonTrapped