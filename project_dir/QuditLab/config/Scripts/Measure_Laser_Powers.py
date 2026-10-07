#Measure_Laser_Powers.py created 2026-10-07
#Measures the CW laser powers (390/493/553/614/650 nm) on the two Thorlabs PM16-120 meters.
#Both flip mirrors (CRM and PI/UV) are flipped by one Toggle_Beam_Samplers pulse, which sends the whole beam to the meters.
#Each beam is isolated with its Keep_*_on_only scan preset, read, and dark-subtracted. The trap state is restored on exit.
#Needs the presets Keep_614_on_only and All_CW_beams_off made in the GUI, and the thorlabs_opm_controller package installed.
import sys
import time
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import GetDataFilePath, SaveDataToTextFile
from thorlabs_opm_controller import open_meter, OpmError
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

#Config: the only thing to edit when the optics change. Acceptable ranges are from Collin (2026-10-07); max None means as high as possible.
METERS = {"CRM": dict(model="PM16-120", serial="190927111"),
          "UV":  dict(model="PM16-120", serial="200707115")}  #PI/UV: 390 + 614
MIRROR_TOGGLE_PRESET = "Toggle_Beam_Samplers"
BEAMS = [  #label, wavelength_nm, meter, preset, min_uW, max_uW
    ("493", 493.0, "CRM", "Keep_493_on_only", 50.0, 60.0),
    ("553", 553.0, "CRM", "Keep_553_on_only", 8.0, 14.0),
    ("650", 650.0, "CRM", "Keep_650_on_only", 250.0, 260.0),
    ("390", 390.0, "UV",  "Keep_405_on_only", 1600.0, None),  #390 replaced 405; clamps to 400 nm
    ("614", 614.0, "UV",  "Keep_614_on_only", 7.0, None)]
DARK_PRESET = "All_CW_beams_off"
NORMAL_PRESET = "PMT_CheckCounts_For-Script_Even"  #re-enables all CW AOMs through its InitializeShutters
SETTLE_S = 1.0
COUNT = 20
ROUTING_FACTOR = 10.0   #first beam must read at least this many times the dark reading
MIN_SIGNAL_UW = 0.1     #floor on the dark reading used for the routing check, so a ~0 dark can't pass noise
TRACE_PLOT = "Scan Data"

#Mirror bookkeeping: there is no state readback, so count toggles in total and since the routing check last confirmed the beams on a meter
mirrors = dict(total=0, since_verified=0, verified=False, retried=False)

#Function run_preset: select a scan preset and run it to completion; the pulser holds its TTL state after the program exits
def run_preset(name):
    setScan(name)
    startScan(globalOverrides=list(), wait=True)
    stopScan()

#Function toggle_mirrors: flip both flip mirrors and count it
def toggle_mirrors():
    run_preset(MIRROR_TOGGLE_PRESET)
    mirrors["total"] += 1
    mirrors["since_verified"] += 1

#Function restore_mirrors: send the beams back to the trap. After a verified meter reading that is one toggle from the verified state,
#otherwise (never verified) restore the starting state, assumed to be the trap
def restore_mirrors():
    if mirrors["verified"]:
        while mirrors["since_verified"] % 2 == 0:
            toggle_mirrors()
    else:
        while mirrors["total"] % 2 == 1:
            toggle_mirrors()

#Function read_uW: read the meter at a wavelength. Returns (Reading, power_uW, stdev_uW)
def read_uW(pm, wavelength_nm):
    r = pm.read_at(wavelength_nm, count=COUNT)
    if r.unit != "W":
        raise OpmError(f"Expected meter unit W, got {r.unit}")
    stdev_uW = r.stdev * 1e6 if r.stdev is not None else float("nan")
    return r, r.value * 1e6, stdev_uW

#Functions range_hi, range_text: format a beam's acceptable range, where a max of None means no upper limit
def range_hi(row):
    return "none" if row["max_uW"] is None else f"{row['max_uW']:0.1f}"

def range_text(row):
    return f"> {row['min_uW']:0.0f}" if row["max_uW"] is None else f"{row['min_uW']:0.0f}-{row['max_uW']:0.0f}"

#Function measure_beam: isolate one beam, wait, read. Returns a row dict with the raw (not dark-subtracted) power
def measure_beam(pm, beam):
    label, wavelength, meter, preset, lo, hi = beam
    run_preset(preset)
    time.sleep(SETTLE_S)
    r, raw, stdev = read_uW(pm, wavelength)
    return dict(timestamp=r.timestamp, label=label, lambda_req=r.wavelength_requested, lambda_used=r.wavelength,
                clamped=r.clamped, raw_uW=raw, stdev_uW=stdev, min_uW=lo, max_uW=hi)

#Function measure_meter: dark reading, routing check on the first beam, then the remaining beams. Returns the rows
def measure_meter(pm, key, beams):
    run_preset(DARK_PRESET)
    time.sleep(SETTLE_S)
    r, dark, dark_stdev = read_uW(pm, beams[0][1])
    consolePrint(f"{key}: dark = {dark:0.3f} uW (stdev {dark_stdev:0.3f})")
    row = measure_beam(pm, beams[0])
    threshold = ROUTING_FACTOR * max(dark, MIN_SIGNAL_UW)
    if row["raw_uW"] < threshold:
        consolePrint(f"{key}: {beams[0][0]} nm reads {row['raw_uW']:0.3f} uW, below {threshold:0.3f} uW; mirrors probably the wrong way round, toggling", error=True)
        mirrors["retried"] = True
        toggle_mirrors()
        row = measure_beam(pm, beams[0])
        if row["raw_uW"] < threshold:
            consolePrint(f"{key}: {beams[0][0]} nm still reads {row['raw_uW']:0.3f} uW; aborting", error=True)
            raise RuntimeError(f"{key} meter routing check failed")
    mirrors["verified"] = True
    mirrors["since_verified"] = 0
    rows = [row]
    for beam in beams[1:]:
        if scriptIsStopped():
            break
        rows.append(measure_beam(pm, beam))
    for row in rows:
        row["dark_uW"] = dark
        row["power_uW"] = row["raw_uW"] - dark
        row["in_tol"] = row["power_uW"] >= row["min_uW"] and (row["max_uW"] is None or row["power_uW"] <= row["max_uW"])
    return rows

path, folder = GetDataFilePath(f"Laser_Powers_{time.strftime('%H%M')}_*.txt")
SaveDataToTextFile(path, "timestamp, label, lambda_req_nm, lambda_used_nm, clamped, power_uW, stdev_uW, dark_uW, min_uW, max_uW, in_tol")
createTrace("Laser power (uW)", TRACE_PLOT, xLabel="Wavelength (nm)")
all_rows = []
try:
    toggle_mirrors()
    for key in METERS:
        if scriptIsStopped():
            break
        beams = [b for b in BEAMS if b[2] == key]
        try:
            with open_meter(**METERS[key]) as pm:
                rows = measure_meter(pm, key, beams)
        except OpmError as err:
            consolePrint(f"{key}: meter failed, skipping its beams: {err}", error=True)
            continue
        for row in rows:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["timestamp"]))
            SaveDataToTextFile(path, f"{stamp}, {row['label']}, {row['lambda_req']:0.1f}, {row['lambda_used']:0.1f}, {row['clamped']}, "
                                     f"{row['power_uW']:0.3f}, {row['stdev_uW']:0.3f}, {row['dark_uW']:0.3f}, {row['min_uW']:0.1f}, {range_hi(row)}, {row['in_tol']}")
            consolePrint(f"{row['label']} nm: {row['power_uW']:0.2f} uW (want {range_text(row)})", error=not row["in_tol"])
            plotPoint(row["lambda_req"], row["power_uW"], "Laser power (uW)", plotStyle=2)
        all_rows.extend(rows)
finally:
    #Send the beams back to the trap, then re-enable all CW AOMs
    restore_mirrors()
    run_preset(NORMAL_PRESET)
    closeTrace("Laser power (uW)")

if mirrors["retried"]:
    consolePrint("The mirrors were not where the script assumed; the two flip mirrors toggle together and may be out of step, so check the PMT counts", error=True)
consolePrint("| Laser (nm) | Power (µW) | Notes |")
consolePrint("|---|---|---|")
for row in all_rows:
    notes = []
    if row["clamped"]:
        notes.append(f"read at {row['lambda_used']:0.0f} nm")
    if not row["in_tol"]:
        notes.append(f"outside {range_text(row)} µW")
    consolePrint(f"| {row['label']} | {row['power_uW']:0.1f} | {'; '.join(notes)} |")
consolePrint(f"Saved to {path}")
