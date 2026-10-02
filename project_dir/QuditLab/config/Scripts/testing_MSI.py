#testing_MSI.py created 2023-12-21 12:21:43.691665

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
pulse_program = "Shelving_InitScheme_Comparison_Ba137"
date = datetime.datetime.now().strftime("%d%m%Y")
dt_string = datetime.datetime.now().strftime("%d%m%Y_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

m_lvl = "F2P2"
threshold = 7
SetInitPulseTime = 450 # us

# which populations to probe. 0 is mp2, 4 is mn2
indices = [4]
use_pi_times = True
set_comparisons= 5

set_zero_F1pumpTime = 0 #us
set_F1pumpTime = 30 #us
set_F1pumpTime_repeated = 0 #us
set_F1pumpTime_repeated_1f1 = 30 # us

set_initReps_zero = 0
set_initReps_repeated = 0
set_F1PumpReps = 0
set_F1PumpReps_zero = 0

no_f1_flag = False
f1_flag = False
rep_no_f1_flag = False
rep_f1_flag = True

# frequencies read from txt for readout pulse
input_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1s12_f2_freqs_file_output_{date}_PLL_{m_lvl}.txt'
output_file = fr'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\{year}\{year}_{month}\{year}_{month}_{day}\1S12_F2_PD_std_file_{dt_string}_{m_lvl}_{set_F1pumpTime_repeated_1f1}us{set_F1PumpReps}xF1_{set_initReps_repeated}xS_POP.txt'



att_PLL = 0
AWG_mode = 0
AWG_Power_dBm = 3
#SetPulseTime = [3000,3000,3000,3000,3000] #us

InitPulseTime = getGlobal("Init_Shelving_Pulse_Time")
if not "%s"%InitPulseTime == "%s us"%SetInitPulseTime:
    setGlobal("Init_Shelving_Pulse_Time", SetInitPulseTime, "us")

AWG_Power_dBm_global = getGlobal('AWG1_Power_dBm').magnitude
if not "%s"%AWG_Power_dBm_global == AWG_Power_dBm:
    setGlobal("AWG1_Power_dBm", AWG_Power_dBm, "")

os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%att_PLL)

AWG_mode_curr = getGlobal("AWG1_Mode").magnitude
if not int(AWG_mode_curr) == AWG_mode: #Set global variable storing this transition's freq.
    setGlobal("AWG1_Mode", AWG_mode, "")

pulse_program = "Shelving_InitScheme_Comparison_Ba137"

sum_array = np.zeros(4)
m_values = [2,1,0,-1,-2]
def find_std(x, set_comparisons):
    return np.sqrt((x*(1-x)/(300*set_comparisons)))

with open(output_file,'w'):
    pass
with open(input_file,'r') as freq_file:
    freq_pi_list = []
    for l in freq_file:
        tuple = l.strip().split(' ')
        freq_pi_list.append(tuple)


    for k in indices:
        freq = float(freq_pi_list[k][0])
        os.system('ssh pi@192.168.168.101 python ~/pll-evalboard-synthesizer/src/Control-Programs/rf1.py 6 %s'%freq)
        EOM_1762_sideband1_freq = getGlobal("EOM_1762_Sideband3_Freq").magnitude
        if not "%s"%EOM_1762_sideband1_freq == "%s MHz"%freq:
            setGlobal("EOM_1762_Sideband3_Freq", freq, "MHz")

        if use_pi_times:
            PulseTime = getGlobal("Shelving_Pulse_Time")
            if not "%s"%PulseTime == "%s us"%float(freq_pi_list[k][1]):
                setGlobal("Shelving_Pulse_Time", float(freq_pi_list[k][1]), "us")
        elif not use_pi_times:
            PulseTime = getGlobal("Shelving_Pulse_Time")
            if not "%s"%PulseTime == "%s us"%3000:
                setGlobal("Shelving_Pulse_Time", 3000, "us")

        time.sleep(0.2)
        
        createTrace('PlotPD No F1 Pump', 'Script Data', xLabel=f'Data Points')
        createTrace('PlotPD F1 Pump Only', 'Script Data', xLabel=f'Data Points')
        createTrace('PlotPD Repeated F1 Pump and Shelving', 'Script Data', xLabel=f'Data Points')
        createTrace('PlotPD Repeated F1 Pump and Shelving2', 'Script Data', xLabel=f'Data Points')
        No_F1_PD = []
        F1Only_PD = []
        F1_and_Shelving_PD = []
        F1_and_Shelving_PD2 = []

        #Loop 
        for j in range(set_comparisons):
            i = j + k*set_comparisons
            
            # NO F1 pumping 
            if no_f1_flag:
                F1_pumpTime = getGlobal('F1_PumpTime')
                if not "%s"%F1_pumpTime == "%s us"%set_zero_F1pumpTime:
                    setGlobal("F1_PumpTime", set_zero_F1pumpTime, "us")

                Init_reps_zero = getGlobal('InitialisationReps')
                if not "%s"%Init_reps_zero == set_initReps_zero:
                    setGlobal("InitialisationReps", set_initReps_zero, "")

                F1PumpReps = getGlobal('F1_PumpReps')
                if not "%s"%F1PumpReps == set_F1PumpReps_zero:
                    setGlobal("F1_PumpReps", set_F1PumpReps_zero, "")

                setEvaluation('Eval3')

                PD_no_F1 = find_and_plotPD_NoF1pump(i, freq, threshold, pulse_program, script_functions, AWG=True)
                No_F1_PD.append(PD_no_F1)
                setEvaluation('Eval2')
                #outfile.write(f'{round(np.mean(No_F1_PD),4)} || {round(find_std(np.mean(No_F1_PD), set_comparisons),4)}||')
        #First Part
            if f1_flag:
                F1_pumpTime = getGlobal('F1_PumpTime')
                if not "%s"%F1_pumpTime == "%s us"%set_F1pumpTime:
                    setGlobal("F1_PumpTime", set_F1pumpTime, "us")

                Init_reps_zero = getGlobal('InitialisationReps')
                if not "%s"%Init_reps_zero == set_initReps_zero:
                    setGlobal("InitialisationReps", set_initReps_zero, "")

                F1PumpReps = getGlobal('F1_PumpReps')
                if not "%s"%F1PumpReps == set_F1PumpReps_zero:
                    setGlobal("F1_PumpReps", set_F1PumpReps_zero, "")

                setEvaluation('Eval3')

                PD_F1_only = find_and_plotPD_F1pumpOnly(i, freq, threshold, pulse_program, script_functions, AWG=True)
                F1Only_PD.append(PD_F1_only)
                setEvaluation('Eval2')
                #outfile.write(f'{round(np.mean(F1Only_PD),4)} || {round(find_std(np.mean(F1Only_PD), set_comparisons),4)}||')
        #Second Part
            if rep_no_f1_flag:
                F1_pumpTime_repeated = getGlobal('F1_PumpTime')
                if not "%s"%F1_pumpTime_repeated == "%s us"%set_F1pumpTime_repeated:
                    setGlobal("F1_PumpTime", set_F1pumpTime_repeated, "us")

                Init_reps_repeated = getGlobal('InitialisationReps')
                if not "%s"%Init_reps_repeated == set_initReps_repeated+set_F1PumpReps:
                    setGlobal("InitialisationReps", set_initReps_repeated+set_F1PumpReps, "")

                F1PumpReps = getGlobal('F1_PumpReps')
                if not "%s"%F1PumpReps == set_F1PumpReps_zero:
                    setGlobal("F1_PumpReps", set_F1PumpReps_zero, "")

                setEvaluation('Eval3')

                PD_F1_and_Shelving_repeated = find_and_plotPD_repeatF1PumpandShelve(i, freq, threshold, pulse_program, script_functions, AWG=True)
                F1_and_Shelving_PD.append(PD_F1_and_Shelving_repeated)

                setEvaluation('Eval2')
                #outfile.write(f'{round(np.mean(F1_and_Shelving_PD),4)} || {round(find_std(np.mean(F1_and_Shelving_PD), set_comparisons),4)}||')
            #part 3


            if rep_f1_flag:
                F1_pumpTime_repeated = getGlobal('F1_PumpTime')
                if not "%s"%F1_pumpTime_repeated == "%s us"%set_F1pumpTime_repeated_1f1:
                    setGlobal("F1_PumpTime", set_F1pumpTime_repeated_1f1, "us")

                Init_reps_repeated = getGlobal('InitialisationReps')
                if not "%s"%Init_reps_repeated == set_initReps_repeated:
                    setGlobal("InitialisationReps", set_initReps_repeated, "")

                F1PumpReps = getGlobal('F1_PumpReps')
                if not "%s"%F1PumpReps == set_F1PumpReps:
                    setGlobal("F1_PumpReps", set_F1PumpReps, "")

                setEvaluation('Eval3')

                PD_F1_and_Shelving_repeated2 = find_and_plotPD_repeatF1PumpandShelve2(i, freq, threshold, pulse_program, script_functions, AWG=True)
                F1_and_Shelving_PD2.append(PD_F1_and_Shelving_repeated2)

                setEvaluation('Eval2')
                #outfile.write(f'{round(np.mean(F1_and_Shelving_PD2),4)} || {round(find_std(np.mean(F1_and_Shelving_PD2), set_comparisons),4)}\n|- \n')
        sum_array = sum_array + [np.mean(No_F1_PD), np.mean(F1Only_PD), np.mean(F1_and_Shelving_PD), np.mean(F1_and_Shelving_PD2)]

	
        with open(output_file,'a') as outfile:
            outfile.write(f'|F=2, m = {m_values[k]}||{round(freq,4)}||')
            if no_f1_flag:
                outfile.write(f'{round(np.mean(No_F1_PD),4)} || {round(find_std(np.mean(No_F1_PD), set_comparisons),4)}||')
            if f1_flag:
                outfile.write(f'{round(np.mean(F1Only_PD),4)} || {round(find_std(np.mean(F1Only_PD), set_comparisons),4)}||')
            if rep_no_f1_flag:
                outfile.write(f'{round(np.mean(F1_and_Shelving_PD),4)} || {round(find_std(np.mean(F1_and_Shelving_PD), set_comparisons),4)}||')
            if rep_f1_flag:
                outfile.write(f'{round(np.mean(F1_and_Shelving_PD2),4)} || {round(find_std(np.mean(F1_and_Shelving_PD2), set_comparisons),4)}\n|- \n')
  
        closeTrace('PlotPD No F1 Pump')
        closeTrace('PlotPD F1 Pump Only')
        closeTrace('PlotPD Repeated F1 Pump and Shelving')
        closeTrace('PlotPD Repeated F1 Pump and Shelving2')

    with open(output_file,'a') as outfile:
        outfile.write(f'!colspan="2" | Sum ||{round(sum_array[0],4)}|| ||{round(sum_array[1],4)}|| ||{round(sum_array[2],4)}|| ||{round(sum_array[3],4)} ||')