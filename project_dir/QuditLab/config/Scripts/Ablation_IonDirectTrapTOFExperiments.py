#IonDirectTrapTOFExperiments.py created 2020-10-06 14:10:14.698057

TotalExperiments = 100
ExperimentCount = 0

while ExperimentCount < TotalExperiments:
    if scriptIsStopped():
        break
    setScan("Ion-Direct Trap")
    startScan(globalOverrides=list(), wait=True)
    if scriptIsStopped():
        break
    ExperimentCount += 1