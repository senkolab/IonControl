#TestScript.py created 2020-02-18 14:59:36.434564

setScan("Shelving_PulseTime_MM_Compensation_Even")
startScan(globalOverrides=list(), wait=True)
data = getAllData()['PMT Count']
ydata = data[1]
print(ydata)