#Auto_Micromotion_Compensation_Horizontal_Even.py created 2022-05-04 11:35:18.308236

import numpy as np
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

start_HorizontalVoltage = 0.11
stop_HorizontalVoltage = 0.13
step_HorizontalVoltage = 0.001

Squeeze_1_4_V = 0
Squeeze_2_3_V = 3

Rod_1_V = getGlobal("Rod_1_Voltage_V").magnitude
Rod_2_V = getGlobal("Rod_2_Voltage_V").magnitude
Rod_3_V = getGlobal("Rod_3_Voltage_V").magnitude
Rod_4_V = getGlobal("Rod_4_Voltage_V").magnitude

set_VerticalVoltage = (Rod_2_V + Rod_4_V - Rod_1_V - Rod_3_V)/2

set_HorizontalVoltage = start_HorizontalVoltage
PMTdata = []

createTrace('Micromotion Horizontal Compensation', 'Script Data', xLabel=f'Rod Voltage offset (V)')
while set_HorizontalVoltage < stop_HorizontalVoltage:
    SetDCVoltages(set_HorizontalVoltage,set_VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V,script_functions)
    setScan("Shelving_PulseTime_MM_Compensation_Even")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    data_mean = np.mean(np.array(ydata))
    PMTdata.append(data_mean)
    set_HorizontalVoltage = set_HorizontalVoltage + step_HorizontalVoltage
    plotPoint(set_HorizontalVoltage, data_mean, 'Micromotion Horizontal Compensation', plotStyle=1)
closeTrace('Micromotion Horizontal Compensation')

set_HorizontalVoltage = start_HorizontalVoltage + step_HorizontalVoltage*PMTdata.index(max(PMTdata))
SetDCVoltages(set_HorizontalVoltage,set_VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V,script_functions)