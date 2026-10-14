#Debug_Hang_Bisect.py created 2026-10-08
#Finds which part of Measure_Laser_Powers.py leaves IonControl in a state where the next PMT-counts call hangs.
#Restart IonControl, set MODE below, run this script, and see whether the PROBE at the end hangs (the console shows "probe: starting" but never
#"probe: done"; use Stop). Restart IonControl again before trying the next MODE.
#  "meter"        open the CRM meter, read it, close it. No presets run.
#  "abort"        run All_CW_beams_off and the Keep_* presets with wait=False and stopScan mid-run, like Measure_Laser_Powers.py. No meter.
#  "finish"       the same, but wait for each preset's program to end before stopScan. No meter.
#  "mirrors_only" toggle the mirrors out and back. Nothing else.
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

MODE = "mirrors_only"
METER = dict(model="PM16-120", serial="190927111")   #CRM
PRESETS = ["All_CW_beams_off", "Keep_493_on_only", "Keep_554_on_only", "Keep_650_on_only"]
MIRROR_TOGGLE_PRESET = "Toggle_Beam_Samplers"
COUNTS_PRESET = "PMT_CheckCounts_For-Script_Even"
WAIT_S = 6.0   #LaserPowerMeasurementWait, as in Measure_Laser_Powers.py
READ_S = 3.5   #how long Measure_Laser_Powers.py holds each preset before stopScan

def run_preset(name):
    setScan(name)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

def probe():
    #What a trapping script does on its first PMT call (Functions_Trap.GetPMTCounts)
    consolePrint("probe: starting")
    t0 = time.time()
    setScan(COUNTS_PRESET)
    startScan(globalOverrides=list(), wait=True)
    consolePrint(f"probe: startScan returned after {time.time() - t0:0.1f} s")
    data = getAllData()['PMT Count']
    stopScan()
    consolePrint(f"probe: done in {time.time() - t0:0.1f} s, mean counts {sum(data[1]) / len(data[1]):0.1f}")

consolePrint(f"MODE = {MODE}")
if MODE == "meter":
    from thorlabs_opm_controller import open_meter
    with open_meter(**METER) as pm:
        pm.set_wavelength(493.0)
        consolePrint(f"meter reads {pm.read() * 1e6:0.3f} uW")
elif MODE in ("abort", "finish"):
    setGlobal("LaserPowerMeasurementWait", WAIT_S, "s")
    run_preset(MIRROR_TOGGLE_PRESET)
    try:
        for name in PRESETS:
            setScan(name)
            startScan(globalOverrides=list(), wait=False)
            time.sleep(READ_S)
            if MODE == "finish":
                time.sleep(WAIT_S + 1.0 - READ_S)   #let the program run to its end before stopping it
            stopScan()
    finally:
        run_preset(MIRROR_TOGGLE_PRESET)
        run_preset(COUNTS_PRESET)
elif MODE == "mirrors_only":
    run_preset(MIRROR_TOGGLE_PRESET)
    run_preset(MIRROR_TOGGLE_PRESET)
else:
    raise ValueError(f"unknown MODE {MODE}")
probe()
