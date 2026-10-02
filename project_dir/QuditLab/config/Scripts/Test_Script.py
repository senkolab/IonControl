#Test_Script.py created 2022-07-15 21:18:16.276025
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
import numpy as np
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *

ydata = []

PulseProgram = 'Shelving_Freq_Cal_Ba137'
setScan(PulseProgram)
startScan(globalOverrides=list(), wait=True)
stopScan()
data = getAllData()['PMT Count']
ydata.append(data[1])

setScan(PulseProgram)
startScan(globalOverrides=list(), wait=True)
stopScan()
data = getAllData()['PMT Count']
ydata.append(data[1])

threshold = getShelvingThreshold(ydata)

print('ydata is')
print(ydata)

print('ydata size is')
print(np.shape(ydata))

print('threshold is')
print(threshold)