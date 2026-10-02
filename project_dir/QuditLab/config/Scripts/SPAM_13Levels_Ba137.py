#SPAM_13Levels_Ba137.py created 2023-04-10 12:47:08.898142
import time

PP_Name = "Shelving_Measurement_DLevel_Qudit_SPAM_Exp_Ba137"
StartState_list = [0,1,2,3,4,5,6,7,8,9,10,11,12]
StartState_trans_list = [0,1,2,3,4,5,7,8,9,10,11,12,14]
setScan(PP_Name)

for ind in range(13):
    StartState_trans_set = StartState_trans_list[ind]
    StartState_set = StartState_list[ind]
    
    AWG_Mode = getGlobal("AWG1_Mode").magnitude
    if not AWG_Mode == 0:
        setGlobal("AWG1_Mode", 0, "")   
    time.sleep(0.1)

    AWG_Mode = getGlobal("AWG1_Mode").magnitude
    if not AWG_Mode == 2:
        setGlobal("AWG1_Mode", 2, "")
    time.sleep(0.1)

    StartState_trans = getGlobal("StartState_Overall_trans").magnitude
    if not "%s"%StartState_trans == "%s"%StartState_trans_set:
        setGlobal("StartState_Overall_trans", StartState_trans_set, "")

    StartState = getGlobal("StartState_Which_d").magnitude
    if not "%s"%StartState == "%s"%StartState_set:
        setGlobal("StartState_Which_d", StartState_set, "")

    startScan(globalOverrides=list(), wait=True)