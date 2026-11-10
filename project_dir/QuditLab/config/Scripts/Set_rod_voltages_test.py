#Set_rod_voltages_test.py created 2026-09-29 11:04:44.253123
#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
import numpy as np
comm_voltage = 0.47


#1762nm Coupling Co-ords for MMC
Push_Vertical_Down = -0.04
Push_Vertical_Up = 0.04

# Camera Position Co-ords fpor MMC
Push_Horizontal_Up = 0.07
Push_Horizontal_Down = -0.07


Squeeze_1_4_V = 0.5
Squeeze_2_3_V = 3.5

Rod_1_set_V = Push_Vertical_Down + Push_Horizontal_Up + Squeeze_1_4_V - comm_voltage
Rod_2_set_V = Push_Vertical_Up + Push_Horizontal_Up + Squeeze_2_3_V - comm_voltage
Rod_3_set_V = Push_Vertical_Down + Push_Horizontal_Down + Squeeze_2_3_V - comm_voltage
Rod_4_set_V = Push_Vertical_Up + Push_Horizontal_Down + Squeeze_1_4_V - comm_voltage


Rod_1_V = getGlobal("Rod_1_Voltage_V")
Rod_2_V = getGlobal("Rod_2_Voltage_V")
Rod_3_V = getGlobal("Rod_3_Voltage_V")
Rod_4_V = getGlobal("Rod_4_Voltage_V")

if not "%s"%Rod_1_V == "%s V"%Rod_1_set_V:
    setGlobal("Rod_1_Voltage_V", np.round(Rod_1_set_V,3), "V")

if not "%s"%Rod_2_V == "%s V"%Rod_2_set_V:
    setGlobal("Rod_2_Voltage_V", np.round(Rod_2_set_V,3), "V")

if not "%s"%Rod_3_V == "%s V"%Rod_3_set_V:
    setGlobal("Rod_3_Voltage_V", np.round(Rod_3_set_V,3), "V")

if not "%s"%Rod_4_V == "%s V"%Rod_4_set_V:
    setGlobal("Rod_4_Voltage_V", np.round(Rod_4_set_V,3), "V")

consolePrint([Rod_1_set_V, Rod_2_set_V, Rod_3_set_V, Rod_4_set_V])