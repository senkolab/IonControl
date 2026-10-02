#Test_AWG_fit.py created 2024-04-15 15:24:17.987960

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
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

f_offset = 545.277190
f_upper = 623.095702

pitime_n2 = 21.031 # [-2, 4, -4]
pitime_n1 = 61.661 # [-2, 3, -3]
pitime_0 = 23.058 # [2, 4, 2]
pitime_p1 = 42.94 # [2, 4, 3]
pitime_p2 = 77.398 # [2, 4, 4]

num_comp = 10
F1PumpTime = 1 #us
F1PumpReps = 20
InitReps = 0
fs = 4e9
threshold = 12

#init_trans = [[-2,2,-1],[-1,3,0],[0,3,2],[1,4,2]] #prepare mp2
init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1
#init_trans = [[-2,3,-1],[-1,3,0],[1,3,2],[2,4,0]] #prepare m0
#init_trans = [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]] #prepare mn1
#init_trans = [[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]] #prepare mn2
init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) #us

#probe_trans = [
#[[-2,3,-1],[-2,2,0],[-2,4,-4],[-2,3,-3],[-2,3,-2],[-2,2,-1]],
#[[-1,3,0],[-1,3,-2],[-1,2,0],[-1,4,-2],[-1,4,-3],[-1,3,-1]],
#[[0,4,1],[0,4,-2],[0,4,-1],[0,4,0],[0,3,0],[0,3,1]],
#[[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]],
#[[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]]]

probe_trans = [[[-2,3,-1]],
[[-1,3,0]],
[[0,4,-2]],
[[1,4,3]],
[[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]]]

freq_num_list = [4] # select the frequencies you want to probe from 0-5 

Probe_freqs = [
[0],
list(Get_1762_EOM_Freqs(probe_trans[0],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[1],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[2],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[3],f_offset,f_upper)),
list(Get_1762_EOM_Freqs(probe_trans[4],f_offset,f_upper))]
Probe_times = [
[70],
list(Get_1762_PiTimes(probe_trans[0],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[1],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[2],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[3],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)),
list(Get_1762_PiTimes(probe_trans[4],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))]

print(Probe_freqs)
print(Probe_times)