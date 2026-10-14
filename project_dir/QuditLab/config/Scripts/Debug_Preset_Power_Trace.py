#Debug_Preset_Power_Trace.py created 2026-10-07
#Diagnostic for Measure_Laser_Powers.py: prints the CRM meter power against time while each preset runs and after stopScan,
#to show when the beam state changes (scan start, program exit, stopScan). Mirrors go to the meters and are put back on exit.
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from thorlabs_opm_controller import open_meter
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

METER = dict(model="PM16-120", serial="190927111")   #CRM
WAVELENGTH_NM = 493.0
PRESETS = ["All_CW_beams_off", "Keep_493_on_only", "Keep_650_on_only"]
MIRROR_TOGGLE_PRESET = "Toggle_Beam_Samplers"
SAMPLE_S = 0.25
AFTER_START_S = 5.0     #how long to sample after startScan(wait=False)
AFTER_STOP_S = 2.0      #how long to sample after stopScan

def run_preset(name):
    setScan(name)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

def sample(pm, t0, seconds, tag):
    end = time.time() + seconds
    while time.time() < end:
        consolePrint(f"{time.time() - t0:6.2f} s  {pm.read() * 1e6:10.3f} uW  {tag}")
        time.sleep(SAMPLE_S)

toggled = 0
try:
    run_preset(MIRROR_TOGGLE_PRESET)
    toggled += 1
    with open_meter(**METER) as pm:
        pm.set_wavelength(WAVELENGTH_NM)
        for name in PRESETS:
            consolePrint(f"--- {name}")
            t0 = time.time()
            sample(pm, t0, 1.0, "before start (idle/default state)")
            setScan(name)
            startScan(globalOverrides=list(), wait=False)
            sample(pm, t0, AFTER_START_S, "scan running or finished")
            stopScan()
            sample(pm, t0, AFTER_STOP_S, "after stopScan")
finally:
    while toggled % 2:
        run_preset(MIRROR_TOGGLE_PRESET)
        toggled += 1
