#Set_Rods_DC_Voltages.py created 2021-10-08 16:55:51.796521

import numpy as np

Push_Vertical_Down = 0.026
Push_Vertical_Up = 0.0
Push_Horizontal_Down = 0
Push_Horizontal_Up = 0.108
Squeeze_1_4_V = 0
Squeeze_2_3_V = 3

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