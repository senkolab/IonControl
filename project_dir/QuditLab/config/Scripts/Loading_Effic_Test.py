#LoadingEfficiencyTest.py created 2020-03-10 15:25:07.267850

TotalExperiments = 500
ExperimentCount = 0
NumofSweeps = 5
while ExperimentCount < TotalExperiments:
    if scriptIsStopped():
        break
    setScan("LoadingEfficiencyTestPt1")
    startScan(globalOverrides=list(), wait=True)
    if scriptIsStopped():
        break
    setScan("LoadingEfficiencyDummyPulse")
    if scriptIsStopped():
        break
    startScan(globalOverrides=list(), wait=False)
    for h in range(0,NumofSweeps):
        if scriptIsStopped():
            break
        setGlobal("CoolingFreq",607.42596,"THz")
        time.sleep(0.1)
        setGlobal("CoolingFreq",607.42597,"THz")
        time.sleep(2)
    stopScan()
    time.sleep(0.2)
    setScan("LoadingEfficiencyTestPt2")
    time.sleep(0.2)
    startScan(globalOverrides=list(), wait=True)
    ExperimentCount += 1