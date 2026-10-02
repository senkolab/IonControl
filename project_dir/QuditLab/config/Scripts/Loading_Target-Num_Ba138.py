#LoadTargteNumIons.py created 2020-02-19 18:07:50.097868

import numpy as np
import os
import sys
import glob
from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

ResetAblationAndLasers = True

BGCountsProgram = "PMT_CheckCounts_For-Script_BG"
CountsProgram = "PMT_CheckCounts_For-Script_Even"
PulseAblationProgram = "PulseAblation_For-Script_Meas_Even_Nat"
PulseAblationDummyProgram = "PulseAblation_For-Script_Dummy_Ba138"
WindowStart = 160
WindowWidth = 55
CoolSweepsNum = int(getGlobal("NumCoolSweeps"))
PulsesPer = int(getGlobal("AblationPulsesPer"))

(Freq493, Freq650, Freq553) = SetGlobalLaserFreqs("Ba138", getGlobal, setGlobal)
if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
    setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
    setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")

if ResetAblationAndLasers:
    SendLasersToTrap(CountsProgram,setScan,startScan,stopScan,getAllData)
    ResetAblation(setScan, startScan, stopScan)

Filepath = "Z:/Lab Data/IonImageFolder"
filepath_image = Filepath + '/' + 'BG_Ion_image.bmp'
TargetNIons = getGlobal("TargetNIons")
CycleLimit = 100
Count = 0
multiplier = 5
number_of_ions = 0
GUINumberofIons = getGlobal("NumberofIons")
GUILoadAttempts = getGlobal("LoadAttempts")

BG_img,Success,Sucess_data = acquireBlackflyFrame(filepath_image)
BG_img = BG_img.astype(float)

filepath_image = Filepath + '/' + 'Data_Ion_image.bmp'

while number_of_ions < TargetNIons and Count < CycleLimit:
    if scriptIsStopped():
        break
    #files = glob.glob(Filepath + "IonImage*.Bmp")
    #InitFileLen = len(files)
    #startScan(globalOverrides=list(), wait=False)
    #files = glob.glob(Filepath + "IonImage*.Bmp")
    #while len(files) <= InitFileLen:
    #    if scriptIsStopped():
    #        break
    #    time.sleep(0.2)
    #    files = glob.glob(Filepath + "IonImage*.Bmp")
    #stopScan()
    #files = glob.glob(Filepath + "IonImage*.Bmp")
    
    setScan(PulseAblationProgram)
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    NeutralCounts = data[1]
    stopScan()

    setScan(PulseAblationDummyProgram)
    startScan(globalOverrides=list(), wait=False)
    SweepCool493(Freq493, CoolSweepsNum, getGlobal, setGlobal)
    stopScan()

    Data_img,Success,Sucess_data = acquireBlackflyFrame(filepath_image)
    Data_img = Data_img.astype(float)

    #im = Image.open(files[-1])
    #A = np.array(im)
    
    A = Data_img - BG_img
    #print(A[50,:])

    number_of_ions,peak_positions_th = GetNumberOfIons(A,multiplier)

    #threshold = np.percentile(A,50) + multiplier*(np.percentile(A,95)-np.percentile(A,50))
    #[max_y_ind,max_x_ind]=np.where(A == np.amax(A[ymin:ymax,xmin:xmax]))
    #[peak_positions,local_peaks] = find_peaks(A[int(max_y_ind[0]),xmin:xmax])
    #peak_positions_th = peak_positions[local_peaks > threshold]
    #peak_positions_th = peak_positions_th.astype(float)
    #if len(peak_positions_th) > 1:
    #    peak_positions_th_diff = peak_positions_th[1:]-peak_positions_th[0:-1]
    #    peak_positions_th_diff_end0 = np.append(peak_positions_th_diff,0)
    #    peak_positions_th_diff_start0 = np.append(0,peak_positions_th_diff)
    #    peak_positions_th[peak_positions_th_diff_end0 == 1] = peak_positions_th[peak_positions_th_diff_end0 == 1] + 0.5
    #    index = np.asarray(range(0,len(peak_positions_th)))
    #    peak_positions_th = np.delete(peak_positions_th,index[peak_positions_th_diff_start0 == 1])
    #number_of_ions = len(peak_positions_th)
    if number_of_ions != GUINumberofIons:
        setGlobal("NumberofIons",number_of_ions,"")
        GUINumberofIons = getGlobal("NumberofIons")
    #im.close()
    #for h in range(0,len(files)-1):
    #    os.remove(files[h])
    Count += 1
    if Count != GUILoadAttempts:
        setGlobal("LoadAttempts",Count,"")
        GUILoadAttempts = getGlobal("LoadAttempts")