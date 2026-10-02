#Set_rod_voltages_test.py created 2026-09-29 11:04:44.253123
#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)
    
Push_Vertical_Down = -0.00
Push_Vertical_Up = 0.08
Push_Horizontal_Up = 0.07
Push_Horizontal_Down = -0.07
Squeeze_1_4_V = 0.0
Squeeze_2_3_V = 3.0

Rod_1_set_V = Push_Vertical_Down + Push_Horizontal_Up + Squeeze_1_4_V
Rod_2_set_V = Push_Vertical_Up + Push_Horizontal_Up + Squeeze_2_3_V
Rod_3_set_V = Push_Vertical_Down + Push_Horizontal_Down + Squeeze_2_3_V
Rod_4_set_V = Push_Vertical_Up + Push_Horizontal_Down + Squeeze_1_4_V


Rod_1_V = getGlobal("Rod_1_Voltage_V")
Rod_2_V = getGlobal("Rod_2_Voltage_V")
Rod_3_V = getGlobal("Rod_3_Voltage_V")
Rod_4_V = getGlobal("Rod_4_Voltage_V")

if not "%s"%Rod_1_V == "%s V"%Rod_1_set_V:
    setGlobal("Rod_1_Voltage_V", Rod_1_set_V, "V")

if not "%s"%Rod_2_V == "%s V"%Rod_2_set_V:
    setGlobal("Rod_2_Voltage_V", Rod_2_set_V, "V")

if not "%s"%Rod_3_V == "%s V"%Rod_3_set_V:
    setGlobal("Rod_3_Voltage_V", Rod_3_set_V, "V")

if not "%s"%Rod_4_V == "%s V"%Rod_4_set_V:
    setGlobal("Rod_4_Voltage_V", Rod_4_set_V, "V")

consolePrint([Rod_1_set_V, Rod_2_set_V, Rod_3_set_V, Rod_4_set_V])