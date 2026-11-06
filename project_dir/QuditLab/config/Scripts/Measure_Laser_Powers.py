# Measure_Laser_Powers.py created 2026-10-07
# Measures the CW laser powers (390/493/554/614/650 nm) on the two Thorlabs PM16-120 meters.
# Both flip mirrors (CRM and PI/UV) are flipped by one Toggle_Beam_Samplers pulse, which sends the whole beam to the meters.
# Each beam is isolated with its Keep_*_on_only scan preset, read, and dark-subtracted. The trap state is restored on exit.
# Needs the presets Keep_614_on_only and All_CW_beams_off made in the GUI, and the thorlabs_opm_controller package installed.
# Revised 2026-11-05: 10 s preset hold, end-of-reading check with one retry, held_s and valid columns, per-meter skips with one
# "Not measured:" summary, and the results table printed even if an IonControl call fails.
# If stopped by hand: the beams may still be on the meters. Run Toggle_Beam_Samplers until the PMT counts come back, then run
# PMT_CheckCounts_For-Script_Even to re-enable all CW AOMs.
import sys
import time
from contextlib import contextmanager

sys.path.append(r"C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts")
from Functions_Data import GetDataFilePath, SaveDataToTextFile, makeRelativeDirectory
from thorlabs_opm_controller import open_meter, OpmError

script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

# Config: the only thing to edit when the optics change. max None means as high as possible.
METERS = {
    "CRM": dict(model="PM16-120", serial="190927111"),
    "UV": dict(model="PM16-120", serial="200707115"),
}  # PI/UV: 390 + 614
MIRROR_TOGGLE_PRESET = "Toggle_Beam_Samplers"
BEAMS = [  # label, wavelength_nm, meter, preset, min_uW, max_uW
    ("493", 493.0, "CRM", "Keep_493_on_only", 50.0, 60.0),
    ("554", 554.0, "CRM", "Keep_554_on_only", 8.0, 14.0),
    ("650", 650.0, "CRM", "Keep_650_on_only", 250.0, 260.0),
    ("390", 390.0, "UV", "Keep_405_on_only", 1600.0, None),  # 390 replaced 405; clamps to 400 nm
    ("614", 614.0, "UV", "Keep_614_on_only", 7.0, None),
]
DARK_PRESET = "All_CW_beams_off"
NORMAL_PRESET = "PMT_CheckCounts_For-Script_Even"  # re-enables all CW AOMs through its InitializeShutters
SETTLE_S = 1.0  # after startScan, let the preset take effect (the trace shows ~0.3-0.6 s of latency) before polling the meter
# A preset's beam state lasts only as long as its program runs. RFWait of All_CW_beams_off and every Keep_* preset is bound to the global
# LaserPowerMeasurementWait, which the script sets to WAIT_S. A reading longer than PRESET_HOLD_S only warns: the end-of-reading check is what
# catches a program that ended mid-reading (rework plan approved by Collin 2026-11-05)
WAIT_GLOBAL = "LaserPowerMeasurementWait"
WAIT_S = 10.0
PRESET_HOLD_S = WAIT_S - 2.0
COUNT = 20  # host-side samples averaged per reading (saved as n_samples)
MS_PER_AVERAGE = 3.0  # nominal integration time of one meter sample per unit of hardware averaging on the PM16 (thorlabs_opm_controller docs/usage.md)
SETTLE_POLL_S = 0.25  # after a preset starts, poll the meter until the last SETTLE_WINDOW readings agree, then average
SETTLE_MAX_S = 10.0
SETTLE_WINDOW = 4
SETTLE_REL = 0.03  # readings agree when their spread is within this fraction of their mean plus SETTLE_ABS_UW; 0.01 never settled on 1% flicker
SETTLE_ABS_UW = 0.05
ROUTING_FACTOR = 10.0  # first beam must read at least this many times the dark reading
MAX_DARK_UW = 1.0  # a dark reading above this means light is reaching the meter with every CW beam supposedly off; abort rather than misreport routing
MIN_SIGNAL_UW = 0.001  # floor on the dark reading used for the routing check, so a ~0 dark can't pass noise
TRACE_PLOT = "Scan Data"
RESULTS_SUBFOLDER = "Laser Powers"  # inside today's Sessions folder, so the results files do not clutter it

# Mirror bookkeeping: there is no state readback, so count toggles in total and since the routing check last confirmed the beams on a meter
mirrors = dict(total=0, since_verified=0, verified=False, retried=False)


# Raised to skip one meter's beams for a reason the script found itself (the reason is the message); the other meter still runs
class MeterSkipped(Exception):
    pass


# Function run_preset: select a scan preset and run it to completion, then stop. Fine for the mirror toggle (a mechanical flip), but beam states
# do not survive the program: the apparatus drops back to its default (mirrors out, 493/650/614 on, 554/390 off), see preset_held
def run_preset(name):
    setScan(name)
    startScan(globalOverrides=list(), wait=True)
    stopScan()


# Function preset_held: start a preset without waiting and keep it open, so its beam state is applied inside the with block; stopScan on exit.
# The beam state only lasts while the preset's program runs (RFWait); when it exits the apparatus returns to its default state at once, so the
# block should finish within PRESET_HOLD_S. Yields a dict whose "s" is set to the time held, in s, when the block ends
@contextmanager
def preset_held(name):
    setScan(name)
    startScan(globalOverrides=list(), wait=False)
    started = time.time()
    hold = dict(s=float("nan"))
    try:
        yield hold
        hold["s"] = time.time() - started
        if hold["s"] > PRESET_HOLD_S:
            consolePrint(
                f"{name}: reading took {hold['s']:0.1f} s, within {WAIT_S - hold['s']:0.1f} s of the {WAIT_S:0.0f} s the preset's program runs; raise WAIT_S, "
                f"and check this preset's RFWait is bound to {WAIT_GLOBAL}",
                error=True,
            )
    finally:
        stopScan()


# Function toggle_mirrors: flip both flip mirrors and count it
def toggle_mirrors():
    run_preset(MIRROR_TOGGLE_PRESET)
    mirrors["total"] += 1
    mirrors["since_verified"] += 1


# Function restore_mirrors: send the beams back to the trap. After a verified meter reading that is one toggle from the verified state,
# otherwise (never verified) restore the starting state, assumed to be the trap
def restore_mirrors():
    if mirrors["verified"]:
        while mirrors["since_verified"] % 2 == 0:
            toggle_mirrors()
    else:
        while mirrors["total"] % 2 == 1:
            toggle_mirrors()


# Function read_uW: read the meter at a wavelength. Returns (Reading, power_uW, stdev_uW)
def read_uW(pm, wavelength_nm):
    r = pm.read_at(wavelength_nm, count=COUNT)
    if r.unit != "W":
        raise OpmError(f"Expected meter unit W, got {r.unit}")
    stdev_uW = r.stdev * 1e6 if r.stdev is not None else float("nan")
    return r, r.value * 1e6, stdev_uW


# Function tolerance_uW: how far apart two readings near mean_uW may be and still count as the same light, in uW
def tolerance_uW(mean_uW):
    return SETTLE_REL * abs(mean_uW) + SETTLE_ABS_UW


# Function wait_stable: poll the meter until the last SETTLE_WINDOW readings agree, so the average is not taken while the beams or the meter are
# still changing. Warns and carries on if it never settles within SETTLE_MAX_S. Returns True if it settled
def wait_stable(pm, wavelength_nm, what):
    pm.set_wavelength(wavelength_nm)
    recent = []
    for i in range(int(SETTLE_MAX_S / SETTLE_POLL_S)):
        recent.append(pm.read() * 1e6)
        recent = recent[-SETTLE_WINDOW:]
        if len(recent) == SETTLE_WINDOW:
            mean = sum(recent) / SETTLE_WINDOW
            if max(recent) - min(recent) <= tolerance_uW(mean):
                return True
        time.sleep(SETTLE_POLL_S)
    consolePrint(
        f"{what}: reading still changing after {SETTLE_MAX_S:0.0f} s (last {recent[0]:0.3f} to {recent[-1]:0.3f} uW), averaging anyway", error=True
    )
    return False


# Functions range_hi, range_text: format a beam's acceptable range, where a max of None means no upper limit
def range_hi(row):
    return "none" if row["max_uW"] is None else f"{row['max_uW']:0.1f}"


def range_text(row):
    return f"> {row['min_uW']:0.0f}" if row["max_uW"] is None else f"{row['min_uW']:0.0f}-{row['max_uW']:0.0f}"


# Function read_held: run a preset, wait for the meter to settle, average, then read once more inside the preset. If that last read disagrees
# with the average, the preset's program probably ended mid-reading (the apparatus snaps back to its default beams), so run the preset once more.
# Returns (Reading, power_uW, stdev_uW, held_s, valid); valid is False if the retry also failed or the script was stopped before it
def read_held(pm, preset, wavelength_nm, what):
    for attempt in (1, 2):
        with preset_held(preset) as hold:
            time.sleep(SETTLE_S)
            wait_stable(pm, wavelength_nm, what)
            r, value, stdev = read_uW(pm, wavelength_nm)
            check = pm.read() * 1e6
        if abs(check - value) <= tolerance_uW(value):
            return r, value, stdev, hold["s"], True
        if attempt == 1 and not scriptIsStopped():
            consolePrint(
                f"{what}: read {check:0.3f} uW at the end against an average of {value:0.3f} uW, so {preset}'s program probably ended mid-reading; retrying",
                error=True,
            )
        else:
            break
    consolePrint(f"{what}: reading still not steady to the end of {preset} ({check:0.3f} against {value:0.3f} uW); marking it invalid", error=True)
    return r, value, stdev, hold["s"], False


# Function measure_beam: isolate one beam, wait, read. Returns a row dict with the raw (not dark-subtracted) power, nan if the reading is invalid
def measure_beam(pm, beam):
    label, wavelength, meter, preset, lo, hi = beam
    r, raw, stdev, held, valid = read_held(pm, preset, wavelength, f"{meter} {label} nm")
    return dict(
        timestamp=r.timestamp,
        label=label,
        lambda_req=r.wavelength_requested,
        lambda_used=r.wavelength,
        clamped=r.clamped,
        raw_uW=raw if valid else float("nan"),
        stdev_uW=stdev if valid else float("nan"),
        n_samples=COUNT,
        integration_ms=integration_ms(pm),
        held_s=held,
        valid=valid,
        min_uW=lo,
        max_uW=hi,
    )


# Function integration_ms: nominal integration time of one sample, in ms. The PM16-120 rejects SENS:AVER:COUN? with -113 (lab PC, 2026-10-14)
# and the driver's retry leaves two errors queued that fail the next command, so the meter is never asked: this assumes hardware averaging of 1
def integration_ms(pm):
    return MS_PER_AVERAGE


# Function summarize: one-line list of the raw readings of some rows
def summarize(rows):
    return ", ".join("%s nm %0.3f uW" % (row["label"], row["raw_uW"]) for row in rows)


# Function reaches_meter: whether any valid reading among the rows clears the routing threshold
def reaches_meter(rows, threshold):
    return any(row["valid"] and row["raw_uW"] >= threshold for row in rows)


# Function measure_beams: measure each beam of a meter in turn, stopping early if the script is stopped. Returns the rows
def measure_beams(pm, beams):
    rows = []
    for beam in beams:
        if scriptIsStopped():
            break
        rows.append(measure_beam(pm, beam))
    return rows


# Function measure_meter: dark reading, then every beam of this meter. The routing check is that at least one beam clears ROUTING_FACTOR x dark: if
# none does, the mirrors are probably the wrong way round, so toggle and measure again. If some do and others don't, the mirrors are right and the
# dark-level beams are off or blocked, which is reported per beam rather than aborting. Raises MeterSkipped to skip this meter. Returns the rows
def measure_meter(pm, key, beams):
    r, dark, dark_stdev, held, valid = read_held(pm, DARK_PRESET, beams[0][1], f"{key} dark")
    if not valid:
        raise MeterSkipped("dark reading unreliable")
    consolePrint(f"{key}: dark = {dark:0.3f} uW (stdev {dark_stdev:0.3f}), held {held:0.1f} s of {WAIT_S:0.0f} s")
    if dark > MAX_DARK_UW:
        consolePrint(
            f"{key}: dark reading {dark:0.1f} uW is above {MAX_DARK_UW:0.1f} uW, so something is still lighting this meter with {DARK_PRESET} running "
            f"(a beam the preset does not close, or stray light); skipping this meter",
            error=True,
        )
        raise MeterSkipped("dark reading too high")
    threshold = ROUTING_FACTOR * max(dark, MIN_SIGNAL_UW)
    rows = measure_beams(pm, beams)
    if rows and not reaches_meter(rows, threshold):
        consolePrint(
            f"{key}: no beam reaches the meter (all below {threshold:0.3f} uW: {summarize(rows)}); mirrors probably the wrong way round, toggling",
            error=True,
        )
        mirrors["retried"] = True
        toggle_mirrors()
        rows = measure_beams(pm, beams)
        if rows and not reaches_meter(rows, threshold):
            consolePrint(f"{key}: still no beam reaches the meter after toggling the mirrors ({summarize(rows)}); skipping this meter", error=True)
            raise MeterSkipped("routing check failed")
    if reaches_meter(rows, threshold):
        mirrors["verified"] = True
        mirrors["since_verified"] = 0
    for row in rows:
        if row["valid"] and row["raw_uW"] < threshold and mirrors["verified"]:
            consolePrint(
                f"{key}: {row['label']} nm reads {row['raw_uW']:0.3f} uW, at the dark level although other beams reach the meter, so this beam is off or "
                f"blocked: check its preset and path",
                error=True,
            )
        row["dark_uW"] = dark
        row["power_uW"] = row["raw_uW"] - dark
        row["in_tol"] = row["valid"] and row["power_uW"] >= row["min_uW"] and (row["max_uW"] is None or row["power_uW"] <= row["max_uW"])
    return rows


# Function print_summary: mirror warning, results table, what was not measured, and where the file went. Called from the finally block so the
# readings already taken are reported even when an IonControl call fails
def print_summary():
    if mirrors["retried"]:
        consolePrint(
            "The mirrors were not where the script assumed; the two flip mirrors toggle together and may be out of step, so check the PMT counts",
            error=True,
        )
    # The table is printed as one consolePrint so IonControl's per-statement "Executing ..." echo lines can't get between its rows
    table = ["| Laser (nm) | Power (\u00b5W) | Notes |", "|---|---|---|"]  # \u00b5 escape: IonControl reads scripts in the Windows codepage, keep the source ASCII
    for row in all_rows:
        notes = []
        if not row["valid"]:
            notes.append("invalid reading")
        else:
            if row["clamped"]:
                notes.append(f"read at {row['lambda_used']:0.0f} nm")
            if not row["in_tol"]:
                notes.append(f"outside {range_text(row)} \u00b5W")
        table.append(f"| {row['label']} | {row['power_uW']:0.1f} | {'; '.join(notes) or '-'} |")
    # Blank lines either side: Markdown only starts a table after a blank line and a following non-table line becomes one of its rows, so the
    # copied block carries its own separation from whatever surrounds it in the note
    consolePrint("\n" + "\n".join(table) + "\n")
    if not_measured:
        consolePrint("Not measured: " + "; ".join(not_measured), error=True)
    consolePrint(f"Saved to {path}")


# The first call makes sure today's Sessions folder exists and returns it; the file is then numbered inside the results subfolder
day_folder = GetDataFilePath("Laser_Powers_*.txt", NewFile=False)[1]
makeRelativeDirectory(day_folder, RESULTS_SUBFOLDER)
path, folder = GetDataFilePath(RESULTS_SUBFOLDER + "\\" + f"Laser_Powers_{time.strftime('%H%M')}_*.txt")
SaveDataToTextFile(
    path,
    "timestamp, label, lambda_req_nm, lambda_used_nm, clamped, power_uW, stdev_uW, n_samples, integration_ms, held_s, valid, dark_uW, min_uW, max_uW, "
    "in_tol",
)
setGlobal(WAIT_GLOBAL, WAIT_S, "s")  # raises if the global does not exist, before anything moves
createTrace("Laser power (uW)", TRACE_PLOT, xLabel="Wavelength (nm)")
all_rows = []
not_measured = []  # "<meter> (<reason>)" or "<label> nm (invalid reading)", printed as one line at the end
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
            not_measured.append(f"{key} (meter failed: {err})")
            continue
        except MeterSkipped as err:
            not_measured.append(f"{key} ({err})")
            continue
        for row in rows:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["timestamp"]))
            SaveDataToTextFile(
                path,
                f"{stamp}, {row['label']}, {row['lambda_req']:0.1f}, {row['lambda_used']:0.1f}, {row['clamped']}, "
                f"{row['power_uW']:0.3f}, {row['stdev_uW']:0.3f}, {row['n_samples']}, {row['integration_ms']:0.1f}, {row['held_s']:0.1f}, {row['valid']}, "
                f"{row['dark_uW']:0.3f}, {row['min_uW']:0.1f}, {range_hi(row)}, {row['in_tol']}",
            )
            if not row["valid"]:
                consolePrint(f"{row['label']} nm: invalid reading, not plotted (held {row['held_s']:0.1f} s of {WAIT_S:0.0f} s)", error=True)
                not_measured.append(f"{row['label']} nm (invalid reading)")
                continue
            consolePrint(
                f"{row['label']} nm: {row['power_uW']:0.2f} uW (want {range_text(row)}), held {row['held_s']:0.1f} s of {WAIT_S:0.0f} s",
                error=not row["in_tol"],
            )
            plotPoint(row["lambda_req"], row["power_uW"], "Laser power (uW)", plotStyle=2)
        all_rows.extend(rows)
finally:
    try:
        # Send the beams back to the trap, then re-enable all CW AOMs
        restore_mirrors()
        run_preset(NORMAL_PRESET)
        closeTrace("Laser power (uW)")
    finally:
        print_summary()
