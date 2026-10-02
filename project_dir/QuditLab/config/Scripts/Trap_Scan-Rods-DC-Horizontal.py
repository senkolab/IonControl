#Scan_Rods_DC_Horizontal.py created 2022-03-07 21:59:52.677305

import numpy as np
import time

StartVoltage = 0.15
EndVoltage = 0.25
VoltageStep = 0.001
WaitTime = 2

Push_Vertical_Down = 0.2
Push_Vertical_Up = 0
Squeeze_1_4_V = 0
Squeeze_2_3_V = 2

HorizontalVoltage = StartVoltage

setScan('Shelving_PulseTime_Scan_Even')
startScan(globalOverrides=list(), wait=False)    

while HorizontalVoltage < EndVoltage:
    if HorizontalVoltage < 0:
        Push_Horizontal_Down = -HorizontalVoltage
        Push_Horizontal_Up = 0
    else:
        Push_Horizontal_Down = 0
        Push_Horizontal_Up = HorizontalVoltage
    
    Rod_1_V = getGlobal("Rod_1_Voltage_V").magnitude
    Rod_2_V = getGlobal("Rod_2_Voltage_V").magnitude
    Rod_3_V = getGlobal("Rod_3_Voltage_V").magnitude
    Rod_4_V = getGlobal("Rod_4_Voltage_V").magnitude

    Rod_1_set_V = Push_Vertical_Down + Push_Horizontal_Up + Squeeze_1_4_V
    Rod_2_set_V = Push_Vertical_Up + Push_Horizontal_Up + Squeeze_2_3_V
    Rod_3_set_V = Push_Vertical_Down + Push_Horizontal_Down + Squeeze_2_3_V
    Rod_4_set_V = Push_Vertical_Up + Push_Horizontal_Down + Squeeze_1_4_V

    if not "%s"%Rod_1_V == "%s V"%Rod_1_set_V:
        setGlobal("Rod_1_Voltage_V", Rod_1_set_V, "V")

    if not "%s"%Rod_2_V == "%s V"%Rod_2_set_V:
        setGlobal("Rod_2_Voltage_V", Rod_2_set_V, "V")

    if not "%s"%Rod_3_V == "%s V"%Rod_3_set_V:
        setGlobal("Rod_3_Voltage_V", Rod_3_set_V, "V")

    if not "%s"%Rod_4_V == "%s V"%Rod_4_set_V:
        setGlobal("Rod_4_Voltage_V", Rod_4_set_V, "V")
    HorizontalVoltage = HorizontalVoltage + VoltageStep
    time.sleep(WaitTime)