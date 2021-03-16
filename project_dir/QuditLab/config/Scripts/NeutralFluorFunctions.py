#NeutralFluorFunctions.py created 2021-03-04 14:00:54.455223
import numpy as np
import time

def NeutralFluoresencePulse(NeutProgram, setScan, startScan, stopScan, getAllData):
    setScan(NeutProgram)
    startScan(globalOverrides=list(), wait=True)
    time.sleep(0.05)
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    if len(ydata) > 1:
        ydataAvg = np.mean(np.array(ydata))
        ydataStd = np.std(np.array(ydata))
    else:
        ydataAvg = ydata[0]
        ydataStd = None
    stopScan()   
    return (ydata, ydataAvg, ydataStd)

def setNeutralParameters(WindowStart, WindowWidth, Freq, getGlobal, setGlobal):
    if not "%s"%getGlobal("NeutralFluorescenceWindowStart") == "%s us"%WindowStart:
        setGlobal("NeutralFluorescenceWindowStart", WindowStart, "us")
    if not "%s"%getGlobal("NeutralFluorescenceWindowWidth") == "%s us"%WindowWidth:
        setGlobal("NeutralFluorescenceWindowWidth", WindowWidth, "us")
    if not "%s"%getGlobal("IonizationFreq") == "%s THz"%Freq:
        setGlobal("IonizationFreq", Freq, "THz")