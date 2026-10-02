#Ba138_Selectivity_Ion_Chain.py created 2021-09-08 00:40:37.523797

import numpy as np
from PIL import Image
import glob
import os
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *

PulseEnergy = 145
IonizationPower = 4

#setScan("LoadTargetNIons")
#BaseFolder = r"Z:\Lab Data\Sessions"
#addname = "7o24x_6o08y"
#filename0 = f"Ba138_Selectivity_Chain_{PulseEnergy:0.0f}uJ_{IonizationPower:0.0f}uW{addname}_*.txt"
#filename0, base_folder = GetDataFilePath(BaseFolder, filename0, NewFile=True)

BaseFolder = r"Z:\Lab Data\Sessions"
filename0 = f"Ba138 AI {time.strftime('%d%m', time.localtime())}.txt"
filenameNC = f"Ba138 AI Neutral {time.strftime('%d%m', time.localtime())}.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)
filenameNC, base_folder = GetDataFilePath(filenameNC, NewFile=False)

TargetNIons = getGlobal("TargetNIons")
CycleLimit = 30000
Count = 0
#xmin = 110; xmax = 170; ymin = 90; ymax = 120
multiplier = 5
number_of_ions = 0
GUINumberofIons = getGlobal("NumberofIons")
GUILoadAttempts = getGlobal("LoadAttempts")

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Even_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPer = int(getGlobal("AblationPulsesPer"))
WindowStart = 160
WindowWidth = 55
NumberofExperiments = 20
NumberofRepumps = 100

BGNumStDevs = getGlobal("BGCheckNumStDevs")
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))

ResetAblationAndLasers = bool(getGlobal("LasersReset"))

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

WriteString = f"Metadata,Ionization Freq.:{Freq553:0.6f}:THz,Cooling Freq.:{Freq493:0.6f}:THz,\
Repump Freq.:{Freq650:0.6f}:THz,Window Start:{WindowStart:0.3f}:us,Window Width:{WindowWidth:0.3f}:us,\
Cooling Sweeps Num:{CoolSweepsNum}:,Pulses Per Attempt:{PulsesPer}"
WriteString += ""#Extra metadata from Ba137 trapping
if PulsesPer > 1:
    WriteStringNeutral = "\tNeutralCounts\tNeutralCounts_std"
else:
    WriteStringNeutral = "\tNeutralCounts"
WriteString += f"\nh,Time\tExpNum\tAttemptNum{WriteStringNeutral}\tNumIons\tPeakPos"
SaveDataToTextFile(filename0, WriteString)


if ResetAblationAndLasers:
    print("Reseting lasers")
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)

images_filename = f"BG_Ion-Image.bmp"
filepath_image = base_folder + "\\" + images_filename

BG_img,Success,Sucess_data = acquireBlackflyFrame(filepath_image)
BG_img = BG_img.astype(float)

ZeroNeutralCount = 0
for h in range(NumberofExperiments):
    if scriptIsStopped():
        break
    if ZeroNeutralCount < 10:
        FlushTrapRF(setScan, startScan, stopScan)
        ResetAblation(setScan, startScan, stopScan)
    filepath_image = base_folder + "\\" + images_filename
    number_of_ions = 0
    Count = 0
    while number_of_ions < TargetNIons and Count < CycleLimit and ZeroNeutralCount <10:
        if scriptIsStopped():
            break
    
        setScan(PulseAblationProgram)
        startScan(globalOverrides=list(), wait=True)
        neutraldata = getAllData()['PMT Count'] #Returns all data associated with scan.
        NeutralCounts = neutraldata[1]
        stopScan()

        print("\nNeutral counts is:")
        print(np.mean(NeutralCounts))
        print(NeutralCounts)
        print("\n")
        if NeutralCounts[0] < 0:
            ZeroNeutralCount += 1
        else:
            ZeroNeutralCount = 0
        
        setScan(PulseAblationDummyProgram)
        startScan(globalOverrides=list(), wait=False)
        SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
        stopScan()

        Data_img,Success,Sucess_data = acquireBlackflyFrame(filepath_image)
        Data_img = Data_img.astype(float)
    
        A = Data_img - BG_img
    
        number_of_ions,peak_positions_th = GetNumberOfIons(A,multiplier)
    
        if number_of_ions != GUINumberofIons:
            setGlobal("NumberofIons",number_of_ions,"")
            GUINumberofIons = getGlobal("NumberofIons")
        Count += 1
        if Count != GUILoadAttempts:
            setGlobal("LoadAttempts",Count,"")
            GUILoadAttempts = getGlobal("LoadAttempts")
        if len(NeutralCounts) > 1:
            NeutralString = f"\t{np.mean(NeutralCounts):0.1f}\t{np.std(NeutralCounts):0.1f}"
        else:
            NeutralString = f"\t{NeutralCounts[0]:0.1f}"
        #WriteString = f"{time.time()}\t{h}\t{Count}{NeutralString}\t{number_of_ions}\t{peak_positions_th:0.3f}"
        WriteString = f"{time.time()}\t{h}\t{Count}{NeutralString}\t{number_of_ions}"
        SaveDataToTextFile(filename0, WriteString)
    if ZeroNeutralCount < 10:
        for hh in range(NumberofRepumps):
            if scriptIsStopped():
                break
            h_str = str(h).zfill(2)
            hh_str = str(hh).zfill(2)
            images_filename = f"Ion-Image_{h_str}_{hh_str}.bmp"
            filepath_image = base_folder + "\\" + images_filename
            setScan("Toggle_repump")
            startScan(globalOverrides=list(), wait=True)
            time.sleep(1)
            acquireBlackflyFrame(filepath_image)
    else:
        print("Spot not producing fluorescence")