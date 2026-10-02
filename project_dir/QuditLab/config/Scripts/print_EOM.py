#print_EOM.py created 2024-04-05 10:37:10.392605
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

f_offset = 545.260879
f_upper = 623.078719

pitime_n2 = 20.3088
pitime_n1 = 59.5807
pitime_0 = 22.5572
pitime_p1 = 40.2741
pitime_p2 = 73.4768

probe_trans = [[2,4,2],[2,4,3],[2,4,4],[2,2,1],[2,2,2],[2,4,0]] #probe mp2
#probe_trans = [[1,4,2],[1,3,2],[1,4,0],[1,4,-1],[1,3,3],[1,2,2]] #probe mp1

Probe_freqs = list(Get_1762_EOM_Freqs(probe_trans,f_offset,f_upper))
Probe_times = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))

print(Probe_freqs)
print(Probe_times)

init_trans = [[-2,3,-3],[0,2,0],[-1,3,1],[1,2,2]] #prepare mp2
#init_trans = [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]] #prepare mp1

init_freqs_array = list(Get_1762_EOM_Freqs(init_trans,f_offset,f_upper))
print(init_freqs_array)