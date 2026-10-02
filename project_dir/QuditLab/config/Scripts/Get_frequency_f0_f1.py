#New_Shelving_Calibration_ParamEstimated_Initialised.py created 2024-04-26 16:49:34.435318

#Shelving_Freq_PiTime_Calibration_PlotPD_ParamEstimated_Initialised.py created 2024-04-08 17:31:06.613195

import time
import matlab.engine

import sys
import os
import datetime
import glob
import numpy as np
import random
    
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)


f_offset = getGlobal('f_offset')
f_upper = getGlobal('f_upper')

pitime_n2 = getGlobal('pitime_n2') # [-2, 4, -4]
pitime_n1 = getGlobal('pitime_n1') # [-2, 3, -3]
pitime_0 = getGlobal('pitime_0') # [2, 4, 2]
pitime_p1 = getGlobal('pitime_p1') # [2, 4, 3]
pitime_p2 = getGlobal('pitime_p2') # [2, 4, 4]


freq = list(Get_1762_EOM_Freqs_an1an2([[2,4,3]],f_offset,f_upper))[0] + 1.527
print(freq)