#TestScript.py created 2020-02-18 14:59:36.434564
time.sleep(3)

setScan("PulseAblation_For-Script_Nat")
startScan(globalOverrides=list(), wait=True)
stopScan()

time.sleep(3)

setScan("PulseAblation_For-Script_Rad")
startScan(globalOverrides=list(), wait=True)
stopScan()