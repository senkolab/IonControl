"""Importable control for two KDC101/Z812 motors on the ablation target.

From another script:
    from Functions_AblationMotorControl import move_to_location
    move_to_location(7.12, 6.07, x_serial="27253859", y_serial="27255860")
"""

import math
import os
import struct
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path


KINESIS_DIR = Path(r"C:\Program Files\Thorlabs\Kinesis")
REQUIRED_KINESIS_DLLS = (
    "Thorlabs.MotionControl.DeviceManagerCLI.dll",
    "Thorlabs.MotionControl.GenericMotorCLI.dll",
    "Thorlabs.MotionControl.KCube.DCServoCLI.dll",
)
SERIALS = {
    "X": "PASTE_8_DIGIT_SERIAL_FOR_MAP_X_7.xx",
    "Y": "PASTE_8_DIGIT_SERIAL_FOR_MAP_Y_6.xx",
}
TRAVEL_MM = 12.0  # Z812 actuator travel; this is not the mirror angle.

# The active x_data (6.xx) and y_data (7.xx) in the supplied map script were
# fitted with that script's centered rotation and de-warping transformation.
# Map X is source y_data; map Y is source x_data. The fit values below use
# exactly those 22 paired samples, including the [::-1] on both arrays.
MAP_DATE = "2026-09-01_21"
RAW_X_CENTER = 6.132636363636363  # source x_data / plotted map Y
RAW_Y_CENTER = 7.140113636363637  # source y_data / plotted map X
FIT_B = 2.856083421527065
FIT_C = -2.8442773551192535e-8
FIT_THETA = -1.019993411878558
FIT_RADIUS = 0.077780320263169
EDGE_MARGIN_FRACTION = 0.10  # Keep 10% of the fitted radius inside the edge.


def target_radius_fraction(map_x_mm, map_y_mm):
    """Return 0 at target center; 1 at the fitted map circle boundary."""
    dx = map_y_mm - RAW_X_CENTER
    dy = map_x_mm - RAW_Y_CENTER
    u = dx * math.cos(FIT_THETA) + dy * math.sin(FIT_THETA)
    v = -dx * math.sin(FIT_THETA) + dy * math.cos(FIT_THETA)
    x_prime = u + FIT_C * v
    y_prime = v / FIT_B
    return math.hypot(x_prime, y_prime) / FIT_RADIUS


def inside_target(map_x_mm, map_y_mm):
    return target_radius_fraction(map_x_mm, map_y_mm) <= 1 - EDGE_MARGIN_FRACTION


def find_kinesis_dir():
    """Return the folder containing the required Kinesis DLLs."""
    candidates = []
    if KINESIS_DIR:
        candidates.append(Path(KINESIS_DIR))
    if os.environ.get("THORLABS_KINESIS_DIR"):
        candidates.append(Path(os.environ["THORLABS_KINESIS_DIR"]))

    candidates.append(Path(__file__).resolve().parent)
    program_folders = [
        os.environ.get("ProgramW6432"),
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        r"C:\Program Files",
        r"C:\Program Files (x86)",
    ]
    for folder in program_folders:
        if folder:
            candidates.append(Path(folder) / "Thorlabs" / "Kinesis")

    checked = []
    for candidate in candidates:
        candidate = candidate.expanduser()
        name = str(candidate)
        if name in checked:
            continue
        checked.append(name)
        if candidate.is_dir() and all(
            (candidate / dll).is_file() for dll in REQUIRED_KINESIS_DLLS
        ):
            return candidate

    raise RuntimeError(
        "Kinesis DLL folder was not found. Checked:\n  "
        + "\n  ".join(checked)
        + "\nSet KINESIS_DIR in this file to the folder containing "
        + REQUIRED_KINESIS_DLLS[0]
    )


def load_kinesis():
    kinesis_dir = find_kinesis_dir()
    python_bits = struct.calcsize("P") * 8
    if "program files (x86)" in str(kinesis_dir).lower() and python_bits != 32:
        raise RuntimeError(
            f"Architecture mismatch: Python is {python_bits}-bit, but Kinesis at "
            f"{kinesis_dir} is 32-bit. Install 64-bit Kinesis or use 32-bit Python."
        )

    # Help Windows resolve DLL dependencies. add_dll_directory is available
    # on Python 3.8+; the fallback supports the Python 3.6 IonControl env.
    if hasattr(os, "add_dll_directory"):
        dll_directory = os.add_dll_directory(str(kinesis_dir))
    else:
        os.environ["PATH"] = str(kinesis_dir) + os.pathsep + os.environ.get("PATH", "")
        import ctypes

        set_dll_directory = ctypes.windll.kernel32.SetDllDirectoryW
        set_dll_directory.argtypes = [ctypes.c_wchar_p]
        set_dll_directory.restype = ctypes.c_bool
        if not set_dll_directory(str(kinesis_dir)):
            raise RuntimeError(f"Windows could not add the Kinesis DLL folder: {kinesis_dir}")
        dll_directory = None
    import clr

    for dll in REQUIRED_KINESIS_DLLS:
        clr.AddReference(str(kinesis_dir / dll))

    from System import Decimal
    from Thorlabs.MotionControl.DeviceManagerCLI import (
        DeviceConfiguration,
        DeviceManagerCLI,
    )
    from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo

    return dll_directory, Decimal, DeviceManagerCLI, DeviceConfiguration, KCubeDCServo


def serial_for(axis, override=None):
    serial = str(override) if override is not None else SERIALS[axis]
    if len(serial) != 8 or not serial.isdigit():
        raise ValueError(f"Set the 8-digit KDC101 serial number for map {axis} in SERIALS")
    return serial


def list_devices():
    """Return serial numbers currently available through Kinesis; no movement."""
    dll_directory, Decimal, DeviceManagerCLI, DeviceConfiguration, KCubeDCServo = load_kinesis()
    DeviceManagerCLI.BuildDeviceList()
    return tuple(str(serial) for serial in DeviceManagerCLI.GetDeviceList())


@contextmanager
def connected_motor(serial, DeviceConfiguration, KCubeDCServo):
    motor = KCubeDCServo.CreateKCubeDCServo(serial)
    connected = False
    polling = False
    try:
        motor.Connect(serial)
        connected = True
        if not motor.IsSettingsInitialized():
            motor.WaitForSettingsInitialized(10000)
        if not motor.IsSettingsInitialized():
            raise RuntimeError(f"Settings did not initialize for {serial}")

        # Initialize the converter used by Position and MoveTo for millimetres.
        config = motor.LoadMotorConfiguration(
            serial, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings
        )
        motor.StartPolling(250)
        polling = True
        time.sleep(0.3)
        motor.EnableDevice()
        time.sleep(0.5)
        yield motor, str(config.DeviceSettingsName)
    finally:
        if polling:
            motor.StopPolling()
        if connected:
            motor.Disconnect()


def _plan_segment(start, end):
    """Find sequential single-axis moves whose endpoints stay in the map."""
    for subdivisions in (1, 2, 4, 8, 16, 32, 64, 128):
        for order in (("X", "Y"), ("Y", "X")):
            position = start.copy()
            moves = []
            valid = True
            for step in range(1, subdivisions + 1):
                waypoint = {
                    axis: start[axis] + (end[axis] - start[axis]) * step / subdivisions
                    for axis in ("X", "Y")
                }
                for axis in order:
                    if abs(waypoint[axis] - position[axis]) < 1e-10:
                        continue
                    position[axis] = waypoint[axis]
                    if not inside_target(position["X"], position["Y"]):
                        valid = False
                        break
                    moves.append((axis, waypoint[axis]))
                if not valid:
                    break
            if valid:
                return moves
    return None


def _plan_moves(start, end):
    direct = _plan_segment(start, end)
    if direct is not None:
        return direct
    center = {"X": RAW_Y_CENTER, "Y": RAW_X_CENTER}
    to_center = _plan_segment(start, center)
    from_center = _plan_segment(center, end)
    if to_center is None or from_center is None:
        raise RuntimeError("Could not plan a target-contained path to the requested location")
    return to_center + from_center


def move_to_location(
    x_mm,
    y_mm,
    *,
    x_serial=None,
    y_serial=None,
):
    """Move to map X/Y in mm and return the actual reported (X, Y) positions.

    Pass x_serial/y_serial or set SERIALS first. The motors must already be
    homed. A target pair outside the fitted circle, or a current pair outside
    it, is rejected before moving.
    """
    x_mm, y_mm = float(x_mm), float(y_mm)
    if not all(math.isfinite(v) and 0 <= v <= TRAVEL_MM for v in (x_mm, y_mm)):
        raise ValueError(f"X and Y must each be between 0 and {TRAVEL_MM} mm")
    if not inside_target(x_mm, y_mm):
        raise ValueError(
            f"Requested X={x_mm:.5f}, Y={y_mm:.5f} is outside the "
            f"target map (radius fraction {target_radius_fraction(x_mm, y_mm):.3f})"
        )

    serials = {
        "X": serial_for("X", x_serial),
        "Y": serial_for("Y", y_serial),
    }
    if serials["X"] == serials["Y"]:
        raise ValueError("X and Y must have different controller serial numbers")

    dll_directory, Decimal, DeviceManagerCLI, DeviceConfiguration, KCubeDCServo = load_kinesis()
    DeviceManagerCLI.BuildDeviceList()
    found = {str(serial) for serial in DeviceManagerCLI.GetDeviceList()}
    missing = [f"{axis} ({serial})" for axis, serial in serials.items() if serial not in found]
    if missing:
        raise RuntimeError(
            "Not detected: "
            + ", ".join(missing)
            + ". Kinesis detected: "
            + (", ".join(sorted(found)) if found else "no devices")
        )

    with ExitStack() as stack:
        motors = {}
        for axis in ("X", "Y"):
            motor, stage = stack.enter_context(
                connected_motor(serials[axis], DeviceConfiguration, KCubeDCServo)
            )
            if "Z812" not in stage.upper():
                raise RuntimeError(f"{axis} is configured as {stage!r}, not Z812")
            if not motor.Status.IsHomed:
                raise RuntimeError(f"{axis} is not homed")
            motors[axis] = motor

        def read_position():
            return {
                axis: float(Decimal.ToDouble(motors[axis].Position))
                for axis in ("X", "Y")
            }

        current = read_position()
        if not inside_target(current["X"], current["Y"]):
            raise RuntimeError(
                f"Current X={current['X']:.5f}, Y={current['Y']:.5f} "
                "is outside the target; move refused"
            )
        planned = _plan_moves(current, {"X": x_mm, "Y": y_mm})
        for axis, goal in planned:
            # Recheck live positions so manual movement or a prior position
            # error cannot make the next command leave the target.
            current = read_position()
            proposed = current.copy()
            proposed[axis] = goal
            if not inside_target(current["X"], current["Y"]) or not inside_target(
                proposed["X"], proposed["Y"]
            ):
                raise RuntimeError("Motor position changed; next move would leave the target")
            motors[axis].MoveTo(Decimal(goal), 60000)
            current = read_position()
            if not inside_target(current["X"], current["Y"]):
                raise RuntimeError("Reported motor position moved outside the target")
        return current["X"], current["Y"]


