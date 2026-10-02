#Auto_Micromotion_Compensation_Even.py created 2022-05-04 10:56:13.901787

import numpy as np
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

start_VerticalVoltage = -0.005
stop_VerticalVoltage = 0.005
step_VerticalVoltage = 0.001

Squeeze_1_4_V = 0
Squeeze_2_3_V = 3

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
    setScan("Shelving_PulseTime_MM_Compensation_Even")
    startScan(globalOverrides=list(), wait=True)
    data = getAllData()['PMT Count']
    ydata = data[1]
    data_ave = np.mean(np.array(ydata))
    PMTdata.append(data_ave)
    set_VerticalVoltage = set_VerticalVoltage + step_VerticalVoltage
    plotPoint(set_VerticalVoltage, data_ave, 'Micromotion Vertical Compensation', plotStyle=1)
closeTrace('Micromotion Vertical Compensation')

set_VerticalVoltage = start_VerticalVoltage + step_VerticalVoltage*PMTdata.index(max(PMTdata))
SetDCVoltages(set_HorizontalVoltage,set_VerticalVoltage,Squeeze_1_4_V,Squeeze_2_3_V,script_functions)