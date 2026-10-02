#Repeat_PP_N_Times.py created 2022-03-01 03:26:52.979687

ExperimentCount = 5

PP_Name = "Shelving_PulseTime_Scan_Ba137"

setScan(PP_Name)
Count = 0

PP_Repeat_Count = getGlobal("PP_Repeat_Count").magnitude

while Count<ExperimentCount:
    if not "%s"%PP_Repeat_Count == "%s"%Count:
        setGlobal("PP_Repeat_Count", Count, "")
        PP_Repeat_Count = Count
    if scriptIsStopped():
        break
    startScan(globalOverrides=list(), wait=True)
    Count = Count+1
    