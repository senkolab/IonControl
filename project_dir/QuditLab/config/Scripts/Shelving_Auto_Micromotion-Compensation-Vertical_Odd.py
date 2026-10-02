#Shelving_Auto_Micromotion-Compensation-Vertical_Odd.py created 2022-11-27 23:02:57.994342

import numpy as np
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)


start_VerticalVoltage = -0.1
stop_VerticalVoltage = 0.1
step_VerticalVoltage = 0.01

Squeeze_1_4_V = 0.0
Squeeze_2_3_V = 3.0

Rod_1_V = getGlobal("Rod_1_Voltage_V").magnitude
Rod_2_V = getGlobal("Rod_2_Voltage_V").magnitude
Rod_3_V = getGlobal("Rod_3_Voltage_V").magnitude
Rod_4_V = getGlobal("Rod_4_Voltage_V").magnitude

set_HorizontalVoltage = (Rod_1_V + Rod_2_V - Rod_3_V - Rod_4_V)/2

set_VerticalVoltage = start_VerticalVoltage
PMTdata = []

createTrace('Micromotion Vertical Compensation', 'Script Data', xLabel=f'Rod Voltage offset (V)')
while set_VerticalVoltage < stop_VerticalVoltage:
    SetDCVoltages(set_HorizontalVoltage,set_VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V,script_functions)
    setScan("Shelving_PulseTime_MM_Compensation_Odd")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    #data_ave = np.mean(np.array(ydata))

    data_rms = np.sqrt(np.mean(np.array(ydata)**2))
    data_std = np.std(np.array(ydata))
    data_ave = data_rms
    PMTdata.append(data_ave)

    plotPoint(set_VerticalVoltage, data_ave, 'Micromotion Vertical Compensation', plotStyle=1)
    set_VerticalVoltage = set_VerticalVoltage + step_VerticalVoltage
closeTrace('Micromotion Vertical Compensation')

set_VerticalVoltage = start_VerticalVoltage + step_VerticalVoltage*PMTdata.index(max(PMTdata))
SetDCVoltages(set_HorizontalVoltage,set_VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V,script_functions)