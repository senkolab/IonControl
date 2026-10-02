#NeutralFluorFunctions.py created 2021-03-04 14:00:54.455223
import numpy as np
import time
import pandas as pd
import math
import glob
from scipy.optimize import curve_fit
from Functions_Data import *
from Functions_Physics import *


amu_Conv = 1.660539040e-27
c = 2.99792458e8
k_B = 1.38064852e-23
h_bar = 1.0545718e-34
kelvin_Conv = 273.15

Lifetime = 8.36e-9
FreqNat = 1/Lifetime
FreqNatRad = FreqNat/(2*math.pi)
FreqNatRad *= 1e-6

#Function NeutralFluoresencePulse: for pulsing the ablation laser and collecting the neutral fluorescence. Input NeutProgram: the scan to run, script_functions
#Returns ydata, ydataAvg, ydataStd
def NeutralFluoresencePulse(NeutProgram, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    setScan(NeutProgram)
    startScan(globalOverrides=list(), wait=True)
    time.sleep(0.05)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    if len(ydata) > 1:
        ydataAvg = np.mean(np.array(ydata))
        ydataStd = np.std(np.array(ydata))
    else:
        ydataAvg = ydata[0]
        ydataStd = None
    stopScan()   
    return (ydata, ydataAvg, ydataStd)

#Function setNeutralParameters: Input WindowStart: the PMT counts collection start time (after ablation pulse), WindowWidth: window total collection time, Freq: 554 nm freq., script_functions
def setNeutralParameters(WindowStart, WindowWidth, Freq, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
        setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
    if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
        setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")
    if not "%s"%getGlobal("IonizationFreq") == "%s THz"%Freq:
        setGlobal("IonizationFreq", Freq, "THz")

#Function getData_553Spectrum: Get all the data from the 553 spectrum experiment after it's been run. Input data_path: string for the path to the data in project_dir
#Returns freq_datas, counts_datas 
def getData_553Spectrum(data_path):
    data_files = np.asarray(glob.glob(data_path))
    freq_datas = np.array([])
    counts_datas = np.array([])
    for i, data_file in enumerate(data_files):
        if i >= 0: # Get rid of a calibration point, to preserve which multiple the calibrations occur on
            freq_datas = freq_datas[:-1]
            counts_datas = counts_datas[:-1]
        data = np.asarray(pd.read_csv(data_file, delimiter = "[\]\[\t]", engine='python', skiprows=[0], header=None))
        data_header = []
        for j, data_row in enumerate(data):
            if data_row[0][0] == 'h':
                data_header = data_row
                break
        data = np.delete(data, j, axis=0)
        if data_header.size == 0:
            print("No data_header - assuming freq. in column 1, counts in column 2")
            freq_row = 1
            counts_row = 2
        else:
            freq_row = np.where(data_header == 'IonizationFreq')[0]
            counts_row = np.where(data_header == 'NeutralCounts')[0]
        freq_data = np.round(data[:,freq_row].astype(np.float), 6).flatten()
        counts_data = data[:,counts_row].astype(np.float).astype(np.int).flatten()
        freq_datas = np.hstack((freq_datas, freq_data))
        counts_datas = np.hstack((counts_datas, counts_data))
    return freq_datas, counts_datas

#Function calibrateData_553: calibrates the data based on drifting neutral fluorescence. Input freq_data, counts_data
#Returns calibrated data freqs, counts
def calibrateData_553(freq_data, counts_data):
    counts_calibration = counts_data[0::2]
    freqs = freq_data[1::2]
    counts = counts_data[1::2]
    for i, count in enumerate(counts):
        cal1 = counts_calibration[i]
        cal2 = counts_calibration[i+1]
        if cal1 < 15:
            cal1 = cal2
        if cal2 < 15:
            cal2 = cal1
        calibration = np.mean([cal1, cal2])
        counts[i] = counts[i]/calibration
    return freqs, counts

#Function aveData_553: averages the data. Inputs counts_cal, data_points_num
#Returns counts_cal_ave, counts_cal_std
def aveData_553(counts_cal, data_points_num):
    counts_cal_ave = np.array([])
    counts_cal_std = np.array([])
    for i in range(data_points_num):
        counts_cal_ave = np.append(counts_cal_ave, np.mean(counts_cal[i::data_points_num]))
        counts_cal_std = np.append(counts_cal_std, np.std(counts_cal[i::data_points_num]))
    return counts_cal_ave, counts_cal_std

#Function createFit_553Spectrum: finds the fit parameters to the data. Input freqs, counts
#Returns parameters (f0, s0, A0), perr
def createFit_553Spectrum(freqs, counts):
    f_init = 50
    f_lower = -20
    f_upper = 80
    s_init = 15
    s_lower = 5
    s_upper = 35
    amp_init = 7
    amp_lower = 0.1
    amp_upper = 15
    params0 = np.array([f_init, s_init, amp_init])
    lbound_array = np.array([f_lower, f_lower, amp_lower])
    ubound_array = np.array([f_upper, s_upper, amp_upper])
    pbounds = np.array([lbound_array, ubound_array])
    params, pcov = curve_fit(fitFunc_553Spectrum, freqs, counts, p0=params0, bounds=pbounds)
    perr = np.sqrt(np.diag(pcov))
    return params, perr

#Function fitFunc_553Spectrum: the function for the 553 nm transition lineshape. Inputs Freq, F0, Saturation, Amp
#Returns Lineshape array
def fitFunc_553Spectrum(Freq, F0, Saturation, Amp):
    #TransFreq = 541.43300e12
    #s = SaturationLevel(Power, Lifetime, TransFreq, BeamWaist)
    FWHM = FreqNatRad*math.sqrt(1+Saturation)
    Lineshape = 0
    i = 0
    for Isotope in Isotopes:
        TransStrength = get_TransStrength(Isotope)
        x = 2*(Freq - Isotope.freq_Off - F0)/FWHM
        Lineshape += Isotope.abund*TransStrength/(1 + np.square(x))
        i += 1
    Lineshape *= Amp
    return Lineshape