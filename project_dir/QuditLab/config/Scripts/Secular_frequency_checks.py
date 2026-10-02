#Secular_frequency_checks.py created 2025-04-22 11:43:54.814181

#Shelving_Find_Target_Resonance_Freq_PlotPD.py created 2023-10-06 14:50:31.111782
import sys
import os
import datetime
import glob
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

F1PumpTimes = [0]
f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')
transition = [[2,4,2]]

cent_freq = list(Get_1762_EOM_Freqs_an1an2(transition,f_offset,f_upper))
print(cent_freq)

threshold = 9

# set this mode to 1 if you want to do a plot PD when initialising in any state in S1/2 F=2
AWG_mode = 0
AWG_RunMode = 1 # 0 for triggered mode, 1 for continuous mode
use_AWG = True # this must be set to False when AWG_mode = 1
AWG_Power_dBm = 1.5
# below is the pulse time for the PLL pulse when AWG_mode = 1, the AWG pulse time (for prep) is set via Init_Pulse_Time
def perform_frequency_scan(type="carrier"):
    # type can be "carrier", "x-sec", or "y-sec"


    if type=="carrier":
        freq_step = 0.004
        freq_range_factor = 10
        SetPulseTime = 40 #us
        centre_freq = cent_freq[0]

    elif type=="x_sec":
        freq_step = 0.002
        freq_range_factor = 15
        SetPulseTime = 3000 #us
        #centre_freq = cent_freq[0] + 0.215 # axial z-frequency
        centre_freq = cent_freq[0] + 1.259#1.259 # x-secular frequency
        #centre_freq = cent_freq[0] + 1.455 # y-secular frequency

    elif type=="y_sec":
        freq_step = 0.002
        freq_range_factor = 15
        SetPulseTime = 3000 #us
        #centre_freq = cent_freq[0] + 0.215 # axial z-frequency
        #centre_freq = cent_freq[0] + 1.259#1.259 # x-secular frequency
        centre_freq = cent_freq[0] + 1.455 # y-secular frequency
    '''
    #micromotion
    freq_step = 0.001
    freq_range_factor = 15
    SetPulseTime = 3000 #us
    centre_freq = cent_freq[0] + 20.771 # y-secular frequency
    '''

    PulseTime = getGlobal("Shelving_Pulse_Time")
    if not "%s"%PulseTime == "%s us"%SetPulseTime:
        setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

    OptPumpTime = getGlobal("OpticalPumpTimeGlobal")
    if not "%s"%OptPumpTime == "%s us"%1000:
        setGlobal("OpticalPumpTimeGlobal", 1000, "us")

    AWG_Flag = getGlobal("UseAWG_Flag")
    if not "%s"%AWG_Flag == "%s us"%use_AWG:
        setGlobal("UseAWG_Flag", use_AWG, "")

    AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
    if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
        setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

    AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
    if not int(AWG_mode_curr) == AWG_mode:
        setGlobal("AWG1_Mode", AWG_mode, "")

    AWG_runmode_curr = getGlobal("AWG1_Trig_Cont_Run_Mode").magnitude
    if not int(AWG_runmode_curr) == AWG_RunMode:
        setGlobal("AWG1_Trig_Cont_Run_Mode", int(AWG_RunMode), "")

    Init_reps_zero = getGlobal('InitialisationReps')
    if not "%s"%Init_reps_zero == 0:
        setGlobal("InitialisationReps", 0, "")

    os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
    os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)


    if AWG_mode==1:
        InitReps = 20
        F1PumpReps = 5

        Init_reps_dummy = getGlobal('InitialisationReps')
        if not "%s"%Init_reps_dummy == InitReps:
            setGlobal("InitialisationReps", InitReps, "")

        F1PumpReps_dummy = getGlobal('F1_PumpReps')
        if not "%s"%F1PumpReps_dummy == F1PumpReps:
            setGlobal("F1_PumpReps", F1PumpReps, "")

    pulse_program_findres = "Shelving_Freq_Cal_Ba137"

    range = freq_range_factor*freq_step
    freq_start = centre_freq-range
    freq_stop = centre_freq+range+freq_step

    for F1PumpTime in F1PumpTimes:
        AOMWait_global = getGlobal('F1_PumpTime')
        if not "%s"%AOMWait_global == "%s us"%F1PumpTime:
            setGlobal("F1_PumpTime", F1PumpTime, "us")
        setEvaluation('Eval3')

        freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop, freq_step, dt_string, threshold, pulse_program_findres, script_functions, AWG=use_AWG)

        setEvaluation('Eval2')

    AWG1_Freq = getGlobal("AWG1_Frequency")
    if not "%s"%AWG1_Freq == "%s MHz"%freq_peak:
        setGlobal("AWG1_Frequency", np.round(freq_peak, 6), "MHz")

    return freq_peak

filename = f'Z:\\Lab Data\\25lvl_SPAM\\Secular_freqs_check\\Seculars_{dt_string}.txt'


for iterate in np.arange(0,100):
    carrier = perform_frequency_scan(type="carrier")

    x_sec = perform_frequency_scan(type="x_sec")
    y_sec = perform_frequency_scan(type="y_sec")

    x_diff = x_sec - carrier
    y_diff = y_sec - carrier

    with open(filename,'a') as file:
        dt_string_run = datetime.datetime.now().strftime("%Y%m%d_%H%M")     
        file.write(f"{dt_string_run},{np.round(carrier,6)},{np.round(x_sec,6)},{np.round(y_sec,6)},{np.round(x_diff,6)},{np.round(y_diff,6)}\n")
        #file.write(f"{carrier}\n")
        
    