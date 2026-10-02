#New_micro-motion_compensation_script.py created 2026-09-29 00:49:52.964749

# Shelving_Auto_Micromotion_Compensation.py

import time
import numpy as np
import sys

sys.path.append(
    r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts'
)

from Functions_Trap import *
from Functions_Data import *

script_functions = (
    getGlobal,
    setGlobal,
    setScan,
    startScan,
    stopScan,
    getAllData,
)


# ============================================================
# User settings
# ============================================================

SCAN_NAME = "Shelving_PulseTime_MM_Compensation_Odd"
TRACE_NAME = "Micromotion Compensation"

# Camera-null operating point:
#
# SetDCVoltages(0.0, 0.17, 0.0, 3.0, ...)
#
# should produce approximately:
#
# [Rod 1, Rod 2, Rod 3, Rod 4]
# [0.17,  3.0,   3.17,  0.0]
#
CAMERA_NULL_HORIZONTAL_V = 0.0
CAMERA_NULL_VERTICAL_V = -0.17

SQUEEZE_1_4_V = 0.17
SQUEEZE_2_3_V = 3.17

# Scan an additional correction u about the camera-null point.
CORRECTION_START_V = -0.15
CORRECTION_STOP_V = 0.15
CORRECTION_STEP_V = 0.02

# Camera-null correction direction:
#
# H = H0 + u
# V = V0 + CAMERA_NULL_DV_DH * u
#
# Use 0.0 only if scanning HorizontalVoltage while holding
# VerticalVoltage = 0.17 preserves the camera displacement null.
#
# If the measured camera-null line is
#
#     V_camera_null(H) = 0.17 + slope * H
#
# put that slope here.
#
CAMERA_NULL_DV_DH = 0.0

# Allow the trap voltages to settle before starting spectroscopy.
VOLTAGE_SETTLE_TIME_S = 0.25

# Number of shortest-pulse points used to establish the bright baseline.
BASELINE_POINTS = 2


# ============================================================
# Micromotion metric
# ============================================================

def micromotion_flatness_metric(
        pulse_time,
        pmt_counts,
        baseline_points=2,
):
    """
    Measure the RMS deviation from the short-pulse bright baseline.

    Small metric:
        Flat trace at the bright-state level.

    Large metric:
        Rabi oscillation, shelving, or a flat trace displaced from
        the bright-state level.
    """

    t = np.asarray(pulse_time, dtype=float)
    y = np.asarray(pmt_counts, dtype=float)

    valid = np.isfinite(t) & np.isfinite(y)
    t = t[valid]
    y = y[valid]

    if len(y) <= baseline_points:
        raise ValueError(
            "Not enough valid points to calculate the micromotion metric."
        )

    order = np.argsort(t)
    t = t[order]
    y = y[order]

    bright_baseline = np.median(y[:baseline_points])

    deviations = y[baseline_points:] - bright_baseline

    metric = np.sqrt(np.mean(deviations**2))

    return float(metric)


# ============================================================
# Voltage parameterization
# ============================================================

def voltages_on_camera_null(correction_v):
    """
    Return HorizontalVoltage and VerticalVoltage while moving
    along the measured camera-null line.
    """

    horizontal_voltage = (
        CAMERA_NULL_HORIZONTAL_V + correction_v
    )

    vertical_voltage = (
        CAMERA_NULL_VERTICAL_V
        + CAMERA_NULL_DV_DH * correction_v
    )

    return horizontal_voltage, vertical_voltage


def apply_compensation_voltages(horizontal_voltage, vertical_voltage):
    SetDCVoltages(
        horizontal_voltage,
        vertical_voltage,
        SQUEEZE_1_4_V,
        SQUEEZE_2_3_V,
        script_functions,
    )


def restore_camera_null():
    apply_compensation_voltages(
        CAMERA_NULL_HORIZONTAL_V,
        CAMERA_NULL_VERTICAL_V,
    )


# ============================================================
# Main scan
# ============================================================

correction_values = np.arange(
    CORRECTION_START_V,
    CORRECTION_STOP_V + 0.5 * CORRECTION_STEP_V,
    CORRECTION_STEP_V,
)

measured_corrections = []
micromotion_metrics = []

trace_open = False
scan_completed = False

# Always begin at the known camera-null point.
restore_camera_null()
time.sleep(VOLTAGE_SETTLE_TIME_S)

try:
    createTrace(
        TRACE_NAME,
        "Script Data",
        xLabel="Correction coordinate u (V)",
    )
    trace_open = True

    for correction_v in correction_values:
        horizontal_voltage, vertical_voltage = (
            voltages_on_camera_null(correction_v)
        )

        apply_compensation_voltages(
            horizontal_voltage,
            vertical_voltage,
        )

        time.sleep(VOLTAGE_SETTLE_TIME_S)

        setScan(SCAN_NAME)
        startScan(
            globalOverrides=list(),
            wait=True,
        )

        trace_data = getAllData()["PMT Count"]

        pulse_time = np.asarray(
            trace_data[0],
            dtype=float,
        )

        pmt_counts = np.asarray(
            trace_data[1],
            dtype=float,
        )

        metric = micromotion_flatness_metric(
            pulse_time,
            pmt_counts,
            baseline_points=BASELINE_POINTS,
        )

        measured_corrections.append(correction_v)
        micromotion_metrics.append(metric)

        plotPoint(
            correction_v,
            metric,
            TRACE_NAME,
            plotStyle=1,
        )

        print(
            f"u={correction_v:+.4f} V, "
            f"H={horizontal_voltage:+.4f} V, "
            f"V={vertical_voltage:+.4f} V, "
            f"metric={metric:.6g}"
        )

    scan_completed = True

finally:
    if trace_open:
        closeTrace(TRACE_NAME)

    # If the script fails or is interrupted, return to the known
    # camera-null condition rather than leaving an arbitrary scan voltage.
    if not scan_completed:
        restore_camera_null()
        print("Scan interrupted: restored the camera-null voltages.")


# ============================================================
# Select and apply the best compensation
# ============================================================

metric_array = np.asarray(
    micromotion_metrics,
    dtype=float,
)

if not np.any(np.isfinite(metric_array)):
    restore_camera_null()
    raise RuntimeError(
        "No valid micromotion measurements were obtained."
    )

best_index = int(np.nanargmin(metric_array))

best_correction_v = measured_corrections[best_index]
best_metric = micromotion_metrics[best_index]

best_horizontal_voltage, best_vertical_voltage = (
    voltages_on_camera_null(best_correction_v)
)

apply_compensation_voltages(
    best_horizontal_voltage,
    best_vertical_voltage,
)

print("")
print("Micromotion compensation finished.")
print(f"Best correction u: {best_correction_v:+.4f} V")
print(f"HorizontalVoltage: {best_horizontal_voltage:+.4f} V")
print(f"VerticalVoltage: {best_vertical_voltage:+.4f} V")
print(f"Micromotion metric: {best_metric:.6g}")
print(
    "Verify the final point by reducing the RF amplitude "
    "and checking the camera displacement."
)