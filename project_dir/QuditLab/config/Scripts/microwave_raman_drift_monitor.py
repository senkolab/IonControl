# microwave_raman_drift_monitor.py created 2026-11-23, copied from microwave_light_shift_vs_raman_power.py
#
# Repeatedly probes one M1 line, [S, 2, 2, S, 1, 1], at fixed frequencies on the sides of the line, alternating the
# Raman beam off and on. Off tracks the magnetic field drift; (on - off) tracks the Raman intensity drift.
# Two-sided (default): each condition probes centre -/+ half_detuning_khz, and P(+) - P(-) is the error signal.
# One-sided fallback (two_sided = False): each condition probes only centre + one_sided_sign * half_detuning_khz.
#
# Presets: Microwave_Calibration_NBOP_Ba137 (probe), PMT_CheckCounts_For-Script_Ba137 (ion check), Eval3.
# Packages: dsi_sg_controller (Raman SG6000L through the NUC bridge), DSI_12000PRO_connet (microwave source).
# If stopped: the finally block parks the Raman SG6000L at -21 dBm, output on (it talks to the bridge directly, so Stop
# does not block it). After Stop the script ends with a TypeError from getAllData, as the light-shift script does; points
# already taken are saved. If the bridge is unreachable, park the SG6000L by hand at -21 dBm, output on.

import time
import json
import urllib.request

HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL = f"http://{HOST}:{PORT}/upload_rows"


def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


import sys
import os
import datetime
import numpy as np

sys.path.append(r"C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts")
from Functions_Data import *
from Functions_Measurement import *
from Functions_RFSoC import upload_dac0
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
from Functions_Microwave import *
from Functions_Trap import GetPMTCounts, CheckIonTrappedHeadless
from DSI_12000PRO_connet import set_DSI12000PRO


script_functions = (
    getGlobal,
    setGlobal,
    setScan,
    startScan,
    stopScan,
    getAllData,
    createTrace,
    closeTrace,
    plotPoint,
    scriptIsStopped,
)
run_time = datetime.datetime.now()
dt_string = run_time.strftime("%Y%m%d_%H%M%S_%f")

transition = ["S", 2, 2, "S", 1, 1]  # probe transition (Collin, 2026-11-23)
MicrowavePulseTime = 19  # us, Collin's pi time for this line (pi_time_overrides_us, 2026-11-19)

# Line centres in MHz. Defaults from the lapidary Rabi-model fits of the 2026-11-13 to 11-20 runs
# (lightshift-analysis-2026-11/results/2026-11-23/lapidary_mw_all_rabi/results.csv):
# off = mean of the ten 11-19/11-20 Raman-off references (spread 5.0 kHz);
# on = off + 29.3 kHz, the mean -5 dBm shift of three sessions (17.7 to 35.7 kHz). Re-measure both after realignment.
f_center_off_mhz = 8046.4680
f_center_on_mhz = 8046.4990
half_detuning_khz = 21.0  # half-maximum point for a 19 us pi pulse (raman-drift-monitor/halfpoint.py)

two_sided = True  # False = one-sided fallback
one_sided_sign = +1  # side probed when two_sided is False: +1 = above the centre, -1 = below

n_cycles = 1000  # one cycle = Raman off then Raman on; press Stop to end early

drive_power = 0

from dsi_sg_controller import open_generator, PowerLimits

# Raman SG6000L through the NUC bridge. Off = RF output off, power left at raman_on_dbm.
raman_on_dbm = -5
raman_park_dbm = -21
raman_settle_s = 0.5

if not -21 <= raman_on_dbm <= -5:
    raise ValueError(f"Raman power {raman_on_dbm} dBm is outside -21 to -5 dBm")


def open_raman():
    # one connection per use: the NUC bridge drops clients idle for more than its --idle-timeout
    return open_generator(
        model="SG6000L",
        serial="488",
        host="192.168.168.47",
        tcp_port=10001,
        limits={1: PowerLimits(min_dbm=-21, max_dbm=-5, max_step_db=2)},
    )


line_trigger = True

pulse_program = "Microwave_Calibration_NBOP_Ba137"

threshold = 11
F1PumpTime = 1.5
F1PumpReps = 35
InitReps = 0

# Shelving transitions are indexed by the F=2 mF plus two.
list_of_shelving = [
    [[-2, 4, -4], [-2, 3, -3], [-2, 3, -2]],
    [[-1, 4, -3], [-1, 3, 0], [-1, 3, -1]],
    [[0, 2, 0], [0, 4, -2], [0, 3, 2]],
    [[1, 4, 1], [1, 4, -1], [1, 3, 3]],
    [[2, 4, 2], [2, 4, 3], [2, 4, 4]],
]

list_of_inits = [
    [[-1, 3, -2], [0, 4, -2], [1, 4, 0], [2, 4, 2]],
    [[-2, 3, -1], [0, 3, 0], [1, 4, 0], [2, 4, 3]],
    [[-2, 2, -1], [-1, 3, 0], [1, 3, 2], [2, 4, 2]],
    [[-2, 3, -1], [-1, 3, 0], [0, 3, 2], [2, 4, 3]],
    [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 3, 3]],
]

output_root = r"Z:\Lab Data\MicrowaveLightShiftMeasurements"


def measure_point(set_freq):
    # body of the frequency-scan loop in microwave_light_shift_vs_raman_power.py, for one frequency
    Microwave_Freq = getGlobal("Microwave_Frequency")
    if not "%s" % Microwave_Freq == "%s MHz" % set_freq:
        setGlobal("Microwave_Frequency", np.round(set_freq, 6), "MHz")

    set_DSI12000PRO(set_freq, drive_power, True)

    setScan(pulse_program)
    startScan(globalOverrides=list(), wait=True)
    stopScan()
    data = getAllData()["PMT Count"]
    ydata = data[1]
    fluor_bool = np.array(ydata) < threshold

    PD = 1 - np.mean(fluor_bool)
    return PD, np.asarray(ydata).tolist()


f_offset = float(getGlobal("f_offset"))
f_upper = float(getGlobal("f_upper"))

pitime_n2 = float(getGlobal("pitime_n2"))
pitime_n1 = float(getGlobal("pitime_n1"))
pitime_0 = float(getGlobal("pitime_0"))
pitime_p1 = float(getGlobal("pitime_p1"))
pitime_p2 = float(getGlobal("pitime_p2"))
ref_pitimes_list = [pitime_n2, pitime_n1, pitime_0, pitime_p1, pitime_p2]

LT_dummy = getGlobal("LineTriggerBoolean")
if not "%s" % LT_dummy == int(line_trigger):
    setGlobal("LineTriggerBoolean", int(line_trigger), "")

F1_pumpTime = getGlobal("F1_PumpTime")
if not "%s" % F1_pumpTime == "%s us" % F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

OptPumpTime = getGlobal("OpticalPumpTimeGlobal")
if not "%s" % OptPumpTime == "%s us" % 0:
    setGlobal("OpticalPumpTimeGlobal", 0, "us")  # type: ignore

Init_reps = getGlobal("InitialisationReps")
if not "%s" % Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal("F1_PumpReps")
if not "%s" % F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

# RFSoC rows and pulse-time globals, set once (same rows as the light-shift script's frequency scan)
init_state = int(transition[2])
shelving_transition = list_of_shelving[init_state + 2]
init_trans = list_of_inits[init_state + 2]

init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans, f_offset, f_upper))
init_times_array = list(get_pi_times(init_trans, ref_pitimes_list))

shelving_freq = list(Get_1762_EOM_Freqs_an1an2(shelving_transition, f_offset, f_upper))
ShelvingPulseTime = list(get_pi_times(shelving_transition, ref_pitimes_list))

init_row1 = [1, init_freqs_array, [0] * len(init_freqs_array), init_times_array, [0] * len(init_times_array), 0]

tot_init_time = np.sum(init_times_array)
InitShelvingTime = getGlobal("Init_Shelving_Pulse_Time")
if not "%s" % InitShelvingTime == "%s us" % tot_init_time:
    setGlobal("Init_Shelving_Pulse_Time", tot_init_time, "us")

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s" % PulseTime == "%s us" % sum(ShelvingPulseTime):
    setGlobal("Shelving_Pulse_Time", sum(ShelvingPulseTime), "us")

Microwave_Pulse_Time_dummy = getGlobal("Microwave_Pulse_Time")
if not "%s" % Microwave_Pulse_Time_dummy == "%s us" % MicrowavePulseTime:
    setGlobal("Microwave_Pulse_Time", MicrowavePulseTime, "us")

dummy_row2 = [2, [800], [0], [0.01], [0], 0]
probe_row3 = [3, shelving_freq, [0] * len(shelving_freq), ShelvingPulseTime, [0] * len(shelving_freq), 1]
dummy_row4 = [4, [800], [0], [0.01], [0], 0]

rows = [init_row1, dummy_row2, probe_row3, dummy_row4]
resp = upload_rows(rows, time_unit="us")
print(json.dumps(resp, indent=2))

sides = [-1, +1] if two_sided else [one_sided_sign]
conditions = [None, raman_on_dbm]  # None = Raman RF output off

date_folders = (run_time.strftime("%Y_%m"), run_time.strftime("%d"))
drift_dir = os.path.join(output_root, "Drift_monitor", *date_folders)
os.makedirs(drift_dir, exist_ok=True)
points_path = os.path.join(drift_dir, f"{dt_string}_drift_monitor.tsv")
raw_data_path = os.path.join(drift_dir, f"{dt_string}_drift_monitor_each_exp.txt")  # line i = row i of the tsv
print(f"{transition}: off {f_center_off_mhz} MHz, on {f_center_on_mhz} MHz, sides {sides} x {half_detuning_khz} kHz")
print(f"Saving to {points_path}")

trace_names = {}
for raman_power in conditions:
    for side in sides:
        name = f"Raman {'off' if raman_power is None else 'on'} {'+' if side > 0 else '-'}"
        trace_names[(raman_power, side)] = name
        createTrace(name, "Script Data", xLabel="Time (min)")

setEvaluation("Eval3")
try:
    with open(points_path, "w") as points_file, open(raw_data_path, "w") as raw_file:
        points_file.write("stamp\tcycle\trequested_dbm\treadback_dbm\toutput\tside\tcentre_mhz\tfreq_mhz\tPD\n")
        for cycle in range(n_cycles):
            if scriptIsStopped():
                break

            yAvg, yStd = GetPMTCounts("PMT_CheckCounts_For-Script_Ba137", script_functions[:6], bg=False)
            if not CheckIonTrappedHeadless(yAvg, yStd, None, None, script_functions[:6]):
                print(f"Ion check failed before cycle {cycle} ({yAvg:.1f} counts). Stopping.")
                break

            for raman_power in conditions:
                if scriptIsStopped():
                    break
                with open_raman() as raman:
                    raman_ch = raman.channel(1)
                    if raman_power is None:
                        raman_ch.set_output(False)
                    else:
                        raman_ch.ramp_power_dbm(raman_power)
                        raman_ch.set_output(True)
                    readback_dbm = raman_ch.get_power_dbm()
                    output = raman_ch.get_output()
                time.sleep(raman_settle_s)

                centre_freq = f_center_off_mhz if raman_power is None else f_center_on_mhz
                for side in sides:
                    if scriptIsStopped():
                        break
                    set_freq = np.round(centre_freq + side * half_detuning_khz * 1e-3, 6)
                    PD, ydata = measure_point(set_freq)
                    stamp = datetime.datetime.now()
                    points_file.write(
                        f"{stamp.strftime('%Y%m%d_%H%M%S_%f')}\t{cycle}\t{raman_power}\t{readback_dbm}\t"
                        f"{output}\t{side}\t{centre_freq}\t{set_freq}\t{PD}\n"
                    )
                    raw_file.write(f"{set_freq},{ydata}\n")
                    points_file.flush()
                    raw_file.flush()
                    plotPoint(
                        (stamp - run_time).total_seconds() / 60, PD, trace_names[(raman_power, side)], plotStyle=0
                    )

finally:
    setEvaluation("Eval2")
    for name in trace_names.values():
        closeTrace(name)
    with open_raman() as raman:  # park at -21 dBm on finish, Stop, or error
        raman.channel(1).ramp_power_dbm(raman_park_dbm)
        raman.channel(1).set_output(True)
