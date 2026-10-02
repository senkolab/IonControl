#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

import json
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
 
import sys
import os
import datetime
import glob
import json
import numpy as np
import shutil
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_RFSoC_RamseyCalibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"
def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
Side_band_cooling_reps = 0

import numpy as np

import numpy as np
import io

def compute_phases_from_line_signal(
    pulse_train,
    fractions,
    pi_t=(23.76, 36.54, 106.33, 32.755, 39.168),
    B0=0.2289,
    A60=-0.2791,
    phi60=1.0002,
    A180=-0.0774,
    phi180=-0.2650,
    param_file="Z:\Lab Data\Line_signal_fitted_params\line_signal_fit_params.txt",
    t_ref="mid",  # "mid", "start", or "end"
    transition_strengths_path=r"Z:\Lab Data\Phase_and_freq_correction_180Hz\Transition_strengths_4p216.txt",
    sensitivities_path=r"Z:\Lab Data\Phase_and_freq_correction_180Hz\sensitivities_4p216.txt",
):
    """
    Single-function version of your entire pipeline.

    Computes per-pulse phase corrections using:
        A(t) = t*B(t) - ?_0^t B(t') dt'
    with B(t) = B_rel_G(t) (Gauss), so A(t) is in G*s.

    Phase per pulse i:
        phi_i = 2? * 1e6 * sens_i * A(t_i)

    Returns:
        phases_per_pulse (list[float]): same length as pulse_train
    """

    # -----------------------------
    # Helpers (nested)
    # -----------------------------
    def load_line_fit_parameters(filename):
        B0_fit = None
        B0_err = None
        harmonic_lines = []
        with open(filename, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if B0_fit is None:
                    vals = np.fromstring(stripped, sep=" ")
                    B0_fit, B0_err = vals[0], vals[1]
                else:
                    harmonic_lines.append(stripped)
        harmonics = np.loadtxt(io.StringIO("\n".join(harmonic_lines)))
        if harmonics.ndim == 1:
            harmonics = harmonics[None, :]
        freqs = harmonics[:, 0]
        A_vals = harmonics[:, 1]
        A_errs = harmonics[:, 2]
        phi_vals = harmonics[:, 3]
        phi_errs = harmonics[:, 4]
        return B0_fit, B0_err, freqs, A_vals, A_errs, phi_vals, phi_errs

    def _get_line_params(param_file, B0, A60, phi60, A180, phi180):
        if param_file is not None:
            B0_fit, B0_err, freqs, A_vals, A_errs, phi_vals, phi_errs = load_line_fit_parameters(param_file)
            return B0_fit, freqs, A_vals, phi_vals
        freqs = np.array([60.0, 180.0], dtype=float)
        A_vals = np.array([A60, A180], dtype=float)
        phi_vals = np.array([phi60, phi180], dtype=float)
        return B0, freqs, A_vals, phi_vals

    def B_line_mG(t, B0, A60, phi60, A180, phi180, param_file):
        B0_use, freqs, A_vals, phi_vals = _get_line_params(param_file, B0, A60, phi60, A180, phi180)
        t_arr = np.asarray(t, dtype=float)
        y = np.full_like(t_arr, B0_use, dtype=float)
        for f, A, phi in zip(freqs, A_vals, phi_vals):
            y = y + A * np.cos(2.0 * np.pi * f * t_arr + phi)
        return y

    def B_rel_G(t, B0, A60, phi60, A180, phi180, param_file):
        return (
            B_line_mG(t, B0, A60, phi60, A180, phi180, param_file=param_file)
            - B_line_mG(0.0, B0, A60, phi60, A180, phi180, param_file=param_file)
        ) * 1e-3

    def primitive_B_rel_G(t, B0, A60, phi60, A180, phi180, param_file):
        B0_use, freqs, A_vals, phi_vals = _get_line_params(param_file, B0, A60, phi60, A180, phi180)
        t_arr = np.asarray(t, dtype=float)
        t_arr_1d = np.atleast_1d(t_arr)
        omega = 2.0 * np.pi * freqs

        B_line_0 = B0_use + np.sum(A_vals * np.cos(phi_vals))
        const_term = (B0_use - B_line_0) * t_arr_1d
        sin_terms = (A_vals / omega)[:, None] * np.sin(omega[:, None] * t_arr_1d[None, :] + phi_vals[:, None])

        F_mG = const_term + np.sum(sin_terms, axis=0)
        F_Gs = 1e-3 * F_mG
        if np.isscalar(t):
            return float(F_Gs[0])
        return F_Gs

    def integral_B_rel_G(t_start, t_end, B0, A60, phi60, A180, phi180, param_file):
        F_end = primitive_B_rel_G(t_end, B0, A60, phi60, A180, phi180, param_file=param_file)
        F_start = primitive_B_rel_G(t_start, B0, A60, phi60, A180, phi180, param_file=param_file)
        return F_end - F_start

    def compute_pi_times(pi_t):
        transition_strengths = np.loadtxt(transition_strengths_path, delimiter=",")
        transition_strengths[transition_strengths == 0] = np.nan
        strengths = np.array(
            [
                transition_strengths[22, 1],
                transition_strengths[14, 0],
                transition_strengths[5, 2],
                transition_strengths[16, 4],
                transition_strengths[15, 4],
            ]
        )
        factors = np.array(pi_t, dtype=float) * strengths

        Fs = [1, 2, 3, 4]
        row_labels = [[i, i - j] for i in Fs for j in range(2 * i + 1)]
        col_labels = [-2, -1, 0, 1, 2]

        pi_times = np.zeros((24, 5), dtype=float)
        for i in range(transition_strengths.shape[0]):
            for j in range(transition_strengths.shape[1]):
                if not np.isnan(transition_strengths[i, j]):
                    delta_m = (row_labels[i][1] - col_labels[j]) + 2
                    pi_times[i, j] = factors[delta_m] / transition_strengths[i, j]
        return pi_times

    def get_pi_times_from_matrix(transitions, matrix):
        Fs = [1, 2, 3, 4]
        states = []
        for i in Fs:
            for j in range(2 * i + 1):
                mF = i - j
                states.append([i, mF])
        row_labels = states
        col_labels = [-2, -1, 0, 1, 2]

        out = []
        for transition in transitions:
            row_label = [transition[1], transition[2]]
            col_label = transition[0]
            row_index = next((k for k, label in enumerate(row_labels) if label == row_label), None)
            col_index = col_labels.index(col_label) if col_label in col_labels else None
            if row_index is not None and col_index is not None:
                out.append(matrix[row_index, col_index])
            else:
                out.append(np.nan)
        return out

    def get_pulse_schedule(rabi_freqs, fractions):
        if len(rabi_freqs) != len(fractions):
            raise ValueError(
                f"rabi_freqs {len(rabi_freqs)} and fractions {len(fractions)} must have the same length."
            )
        times = []
        t_current = 0.0
        for Omega, frac in zip(rabi_freqs, fractions):
            if not 0 <= frac <= 1:
                raise ValueError(f"Fraction must be between 0 and 1, got {frac}.")
            theta = 2.0 * np.arcsin(np.sqrt(frac))
            t_pulse = theta / Omega if Omega > 0 else 0.0
            t_start = t_current
            t_end = t_current + t_pulse
            times.append((t_start, t_end))
            t_current = t_end
        return times

    # -----------------------------
    # Main logic (formerly top-level)
    # -----------------------------
    pulse_train = [tuple(tr) for tr in pulse_train]

    # Build pulse schedule from pi-times
    pi_times_matrix = compute_pi_times(pi_t)
    pi_times_train = get_pi_times_from_matrix(pulse_train, pi_times_matrix)

    # Free placeholder: effectively no pulse
    for i, tr in enumerate(pulse_train):
        if tr == (0, 0, 0):
            pi_times_train[i] = 1e6

    rabi_frequencies_list = np.pi / np.array(pi_times_train, dtype=float)
    schedule_us = get_pulse_schedule(rabi_frequencies_list, fractions)
    pulses_sec = [(start * 1e-6, end * 1e-6) for (start, end) in schedule_us]

    # Sensitivities
    sens_matrix = np.loadtxt(sensitivities_path, delimiter=",")
    sens_list = get_pi_times_from_matrix(pulse_train, sens_matrix)
    for i, tr in enumerate(pulse_train):
        if tr == (0, 0, 0):
            sens_list[i] = 0.0
    sens_array = np.array(sens_list, dtype=float)

    # Reference time per pulse
    t_refs = np.zeros(len(pulse_train), dtype=float)
    for i, (t_start, t_end) in enumerate(pulses_sec):
        if t_ref == "start":
            t_refs[i] = t_start
        elif t_ref == "end":
            t_refs[i] = t_end
        else:  # "mid"
            t_refs[i] = 0.5 * (t_start + t_end)

    # Compute phases
    phases_per_pulse = np.zeros(len(pulse_train), dtype=float)
    for i, tr in enumerate(pulse_train):
        if tr == (0, 0, 0) or sens_array[i] == 0.0:
            phases_per_pulse[i] = 0.0
            continue

        ti = float(t_refs[i])
        Bt = B_rel_G(ti, B0, A60, phi60, A180, phi180, param_file=param_file)
        I0t = integral_B_rel_G(0.0, ti, B0, A60, phi60, A180, phi180, param_file=param_file)
        area_Gs = ti * Bt - I0t #+ 0.115e-3*ti

        phases_per_pulse[i] = 2.0 * np.pi * 1e6 * sens_array[i] * area_Gs

    return phases_per_pulse.tolist()




import numpy as np

def load_line_fit_parameters(filename):
    B0_line = np.loadtxt(filename, comments='#', max_rows=1)
    B0_fit, B0_err = B0_line
    harmonics = np.loadtxt(filename, comments='#', skiprows=2)
    if harmonics.ndim == 1:
        harmonics = harmonics[None, :]
    freqs = harmonics[:, 0]
    A = harmonics[:, 1]
    A_err = harmonics[:, 2]
    phi = harmonics[:, 3]
    phi_err = harmonics[:, 4]
    return B0_fit, B0_err, freqs, A, A_err, phi, phi_err

def compute_detuning_from_line_fit(
    pulse_train,
    fractions,
    pi_t=[23.76, 36.54, 106.33, 32.755, 39.168],
    B0=0.2289,
    A60=-0.2791,
    phi60=1.0002,
    A180=-0.0774,
    phi180=-0.2650,
    param_file="Z:\\Lab Data\\Line_signal_fitted_params\\line_signal_fit_params.txt"
):
    if param_file is not None:
        B0_fit, B0_err, freqs, A_vals, A_errs, phi_vals, phi_errs = load_line_fit_parameters(param_file)
        # print(B0_fit, B0_err, freqs, A_vals, A_errs, phi_vals, phi_errs)
        def B_line_mG(t):
            t = np.asarray(t)
            y = B0_fit
            for f, A, phi in zip(freqs, A_vals, phi_vals):
                y = y + A * np.cos(2 * np.pi * f * t + phi)
            return y
    else:
        def B_line_mG(t, B0=B0, A60=A60, phi60=phi60, A180=A180, phi180=phi180):
            return B0 + A60 * np.cos(2 * np.pi * 60 * t + phi60) + A180 * np.cos(2 * np.pi * 180 * t + phi180)

    def B_rel_G(t):
        return (B_line_mG(t) - B_line_mG(0.0)) * 1e-3

    def compute_pi_times(pi_t):
        transition_strengths = np.loadtxt(
            'Z:\\Lab Data\\Phase_and_freq_correction_180Hz\\Transition_strengths_4p216.txt',
            delimiter=','
        )
        transition_strengths[transition_strengths == 0] = np.nan
        strengths = np.array([
            transition_strengths[22, 1],
            transition_strengths[14, 0],
            transition_strengths[5, 2],
            transition_strengths[16, 4],
            transition_strengths[15, 4]
        ])
        factors = np.array(pi_t) * strengths
        Fs = [1, 2, 3, 4]
        row_labels = [[i, i - j] for i in Fs for j in range(2 * i + 1)]
        col_labels = [-2, -1, 0, 1, 2]
        pi_times = np.zeros((24, 5))
        for i in range(np.shape(transition_strengths)[0]):
            for j in range(np.shape(transition_strengths)[1]):
                if not np.isnan(transition_strengths[i, j]):
                    delta_m = (row_labels[i][1] - col_labels[j]) + 2
                    pi_times[i, j] = factors[delta_m] / transition_strengths[i, j]
        return pi_times

    def get_pi_times(transitions, matrix):
        Fs = [1, 2, 3, 4]
        states = []
        for i in Fs:
            for j in range(2 * i + 1):
                mF = i - j
                states.append([i, mF])
        row_labels = states
        col_labels = [-2, -1, 0, 1, 2]
        pi_times_list = []
        for transition in transitions:
            row_label = [transition[1], transition[2]]
            col_label = transition[0]
            row_index = next((k for k, label in enumerate(row_labels) if label == row_label), None)
            col_index = col_labels.index(col_label) if col_label in col_labels else None
            if row_index is not None and col_index is not None:
                pi_times_list.append(matrix[row_index, col_index])
            else:
                pi_times_list.append(np.nan)
        return pi_times_list

    def get_pulse_schedule(rabi_freqs, fractions):
        if len(rabi_freqs) != len(fractions):
            raise ValueError(f"rabi_freqs {len(rabi_freqs)} and fractions {len(fractions)} must have the same length.")
        times = []
        t_current = 0.0
        for Omega, frac in zip(rabi_freqs, fractions):
            if not 0 <= frac <= 1:
                raise ValueError(f"Fraction must be between 0 and 1, got {frac}.")
            theta = 2.0 * np.arcsin(np.sqrt(frac))
            t_pulse = theta / Omega if Omega > 0 else 0.0
            t_start = t_current
            t_end = t_current + t_pulse
            times.append((t_start, t_end))
            t_current = t_end
        return times

    pi_times_matrix = compute_pi_times(pi_t)
    pi_times_train = get_pi_times(pulse_train, pi_times_matrix)
    for i, tr in enumerate(pulse_train):
        if tr[0] == 0 and tr[1] == 0 and tr[2] == 0:
            pi_times_train[i] = 1e6
    rabi_frequencies_list = np.pi / np.array(pi_times_train)

    sens_matrix = np.loadtxt(
        'Z:\\Lab Data\\Phase_and_freq_correction_180Hz\\sensitivities_4p216.txt',
        delimiter=','
    )
    sens_list = get_pi_times(pulse_train, sens_matrix)
    for i, tr in enumerate(pulse_train):
        if tr[0] == 0 and tr[1] == 0 and tr[2] == 0:
            sens_list[i] = 0.0
    sens_array = np.array(sens_list)
    print(sens_array)
    schedule = get_pulse_schedule(rabi_frequencies_list, fractions)
    pulses_sec = [(start * 1e-6, end * 1e-6) for (start, end) in schedule]
    print(pulses_sec)
    detuning_values_MHz = []
    for i, (start_s, _) in enumerate(pulses_sec):
        B_here_G = B_rel_G(start_s)
        det_here_MHz = B_here_G * sens_array[i]
        detuning_values_MHz.append(det_here_MHz)

    detuning_values_MHz = np.array(detuning_values_MHz, dtype=float)
    return detuning_values_MHz


#initial_state = [[0,2,2]]

do_calibrations_0 = True
do_calibration_qubit = False
Measure_U1_only = False
full_phase_scan = True
LT_comp = False


#ramsey_wait_times = np.arange(0,5100,500)
repeat_experiments = 1
ramsey_wait_times = [1]
f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

F1PumpTime = 0.5 #us
F1PumpReps = 60
InitReps = 0
threshold = 10

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

LT_wait_dummy = getGlobal('LineTriggerWait_Global')
if not "%s"%LT_wait_dummy == 0:
    setGlobal("LineTriggerWait_Global", 0, "us")

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")


#waitTime_list  = [1,10,300,400,500,600,700,800,900,100,350,450,550,650,750,850,950,200]
#waitTime_list = [1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500]
waitTime_list = np.arange(16000.1,32000.1,2000)
wait_trans_piTime = list(get_pi_times([[0,0,0]],[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))[0]
print(wait_trans_piTime)
for wtr in waitTime_list:
    num_repeat = 0
     

    qubit_trans = [0,4,1]
    bus_trans = [0,3,-1]

    initial_state = [qubit_trans]

    pulse_train_U1 = [qubit_trans, bus_trans, [0, 0, 0]]
    fractions_U1 = [0.5, 1,(np.sin((wtr/wait_trans_piTime)*(np.pi/2)))**2]
    simulated_phase_mask_U1 = [0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 0]

    pulse_train_U2 = [bus_trans, qubit_trans]
    fractions_U2 = [1, 0.5]
    simulated_phase_mask_U2 = [0, 1]
    fixed_phase_mask_U2 = [1, 0]

    s12_state_shelvings = []

    probe_trans = [qubit_trans, bus_trans]



    '''
    #pair for line signal phase accumulation


    initial_state = [[-2, 2, -1]]

    pulse_train_U1 = [[-2, 2, -1], [-2, 3, -2], [0, 0, 0]]
    fractions_U1 = [0.5, 1,(np.sin((wtr/wait_trans_piTime)*(np.pi/2)))**2]
    simulated_phase_mask_U1 = [0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 0]

    pulse_train_U2 = [[-2, 3, -2], [-2, 2, -1]]
    fractions_U2 = [1, 0.5]
    simulated_phase_mask_U2 = [0, 1]
    fixed_phase_mask_U2 = [1, 0]

    s12_state_shelvings = []

    probe_trans = [[-2, 2, -1], [-2, 3, -2]]
    

    #pair for insensitive pair

    initial_state = [[0, 2, 2]]

    pulse_train_U1 = [[0, 2, 2], [0, 3, 2], [0, 0, 0]]
    fractions_U1 = [0.5, 1,(np.sin((wtr/wait_trans_piTime)*(np.pi/2)))**2]
    simulated_phase_mask_U1 = [0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 0]

    pulse_train_U2 = [[0, 3, 2], [0, 2, 2]]
    fractions_U2 = [1, 0.5]
    simulated_phase_mask_U2 = [0, 1]
    fixed_phase_mask_U2 = [1, 0]

    s12_state_shelvings = []

    probe_trans = [[0, 2, 2], [0, 3, 2]]
    '''
    dimension = len(probe_trans)
############################### Just make sure s12 state is dealt with (this is shared for all dimensions)
    pulse_train_U2 = pulse_train_U2 + s12_state_shelvings
    fractions_U2 = fractions_U2 #+ s12_state_fractions
    fixed_phase_mask_U2 = fixed_phase_mask_U2 #+ s12_state_fixed_phases
    simulated_phase_mask_U2 = simulated_phase_mask_U2 #+ s12_state_simulated_phases

############################### Finished define the pulse sequence for a given dimension

    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    pulse_train = pulse_train_U1 + pulse_train_U2
    simulated_phase_mask = simulated_phase_mask_U1 + simulated_phase_mask_U2
    fixed_phase_mask = fixed_phase_mask_U1 + fixed_phase_mask_U2

    phase_shifts = zip(simulated_phase_mask,fixed_phase_mask)
    detunings = np.zeros(len(probe_trans))
    s12_level = initial_state[0][0]

    periodicity = 100 #us
    start_time = 0
    if full_phase_scan:
        # for full phase scans
        stop_time = 101
        start_time = 0
        time_step = 100/10
    else:
        # take just two points for a contrast measurement
        if dimension%2==0:
            time_step = (dimension)*100/(2*dimension)
            stop_time = 1+(dimension)*100/(2*dimension)
        else:
            time_step = (dimension+1)*100/(2*dimension)
            stop_time = 1+(dimension+1)*100/(2*dimension)



    pulse_program = "Qudit_ramsey_experiment_bused_ket0_in_D52"


    def findPiTime_withfit_plotPD(ramsey_wait,stop_time,start_time, time_step, threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
        createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')
        
        if Measure_U1_only:
            U1_only_bool_list = [False, True]
        else:
            U1_only_bool_list = [False]
        
        pulse_time = start_time

        file_names_list_all = []

        fluor_ave = []
        pulse_time_list = []
        file_names_list = []
        fluor_ave_U1 = []
        pulse_time_list_U1 = []
        file_names_list_U1 = []
        while pulse_time <= stop_time:
            for U1_only in U1_only_bool_list:
                if U1_only:
                    fractions = fractions_U1 + list(np.zeros(np.size(fractions_U2)))
                    do_calibrations = False
                else:
                    fractions = fractions_U1 + fractions_U2
                    do_calibrations = do_calibrations_0

                if scriptIsStopped():

                    break
        
                print('1')
                setEvaluation('Eval2')
                if pulse_time == 0:
                #if 1 == 1:
                    if do_calibrations:
                        delta = 0
                        ramsey_real_wait_time = 100
                        freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                        freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = False)
                        
                    if do_calibration_qubit:
                            delta = 0
                            ramsey_real_wait_time = 100
                            print('calibrating explicitly')
                            freq_qubit_trans = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition = qubit_trans,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                            freq_bus_trans = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition = bus_trans,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                setEvaluation('Eval3')
        
                f_offset = float(getGlobal('f_offset'))
                f_upper = float(getGlobal('f_upper'))
        
                pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
                pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
                pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
                pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
                pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]
        
        
                init_trans = list_of_inits[s12_level+2]
                init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
                init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
                init_pulse_time = sum(init_times_array) 

                ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

                set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        
                initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))
        
                det = 0#-11.2e-6
                #freq_qubit_trans = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition = qubit_trans,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                #freq_bus_trans = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition = bus_trans,f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                if do_calibration_qubit:
                    print('calibrating explicitly')
                    pulse_train_frequencies = [freq_qubit_trans, freq_bus_trans, 800, freq_bus_trans, freq_qubit_trans]
                else:
                    pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))
                    pulse_train_frequencies = list(np.array(pulse_train_frequencies) + np.array([det, -det, 0, -det, det]))
                
                #pulse_train_frequencies = [609.269758, 546.100823, 800, 546.100823, 609.269758]
                if LT_comp:
                    detuning_line = compute_detuning_from_line_fit(pulse_train, fractions, ref_pitimes)#, param_file = None)

                    pulse_train_frequencies = list(np.array(pulse_train_frequencies) - np.array(detuning_line))

                for idx, delta in enumerate(detunings):
                    set_freq[idx] = set_freq[idx] + delta
        
                
        
                pi_time_initial_state = list(get_pi_times(initial_state,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
                pi_time_pulse_train = list(get_pi_times(pulse_train,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
                pi_times_probe_trans = list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
        
        
                print(pulse_train)
       

                Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
                if not "%s"%Init_PulseTime == init_pulse_time:
                    setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")
        
                corrected_pulse_train_times = []
        
                for i,_ in enumerate(fixed_phase_mask):
                    if np.isnan(_):
                        corrected_pulse_train_times.append(ramsey_wait)
                    else:
                        frac = fractions[i]
                        corrected_pulse_train_times.append(2*pi_time_pulse_train[i]*np.arcsin(np.sqrt(frac))/np.pi)
        
                print(corrected_pulse_train_times)


                

                Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
                if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(corrected_pulse_train_times):
                    setGlobal("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us")
        
                half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
                if not "%s"%half_pi_time_dummy == "%s us"%sum(corrected_pulse_train_times):
                    setGlobal("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us")
                print('2')
        
        # Phase Calculations ===================================================================
        
                phases = []
                for i,_ in enumerate(fixed_phase_mask):
                    if np.isnan(_):
                        phases.append(0)
                    else:
                        pi_phase = fixed_phase_mask[i]
                        real_phase = simulated_phase_mask[i]
                        x = (2 * np.pi * pulse_time * real_phase / periodicity)
                        y = pi_phase*np.pi
                        print(i,x,y)
                        phases.append(x + y)
                if LT_comp:
                    full_phases = list(np.array(phases) + np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))#, param_file = None)))
                #print(np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))
                else:
                    full_phases = list(np.array(phases))
                print(full_phases)
        #=======================================================================================


                init_row1 = [1,init_freqs_array, [0]*len(init_freqs_array),init_times_array, [0]*len(init_freqs_array),0]
                dummy_row2 = [2, [800],[0], [0.1], [0], 0]

                herald_row3 = [3, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
                dummy_row4 = [4, [800],[0], [0.1], [0], 0]
                
                ramsey_row5 = [5, pulse_train_frequencies, full_phases, corrected_pulse_train_times, [1]*len(pulse_train_frequencies), 1]
                dummy_row6 = [6, [800],[0], [0.1], [0], 0]   
                
                rows = [init_row1, dummy_row2, herald_row3, dummy_row4, ramsey_row5, dummy_row6]
                
                row_number = 6
                for idx, freq in enumerate(set_freq):
                    row_number = row_number + 1
                    readout_row = [row_number, [freq], [0], [pi_times_probe_trans[idx]], [0], 1]  
                    rows.append(readout_row)
                    row_number = row_number + 1
                    dummy_row = [row_number, [800],[0], [0.1], [0], 0]
                    rows.append(dummy_row)
                    print(row_number,[freq],[pi_times_probe_trans[idx]])


                
                Table_length_dummy =  getGlobal('Table_length')
                if not "%s"%Table_length_dummy == row_number:
                    setGlobal("Table_length", row_number, "")

                resp = upload_rows(rows, time_unit="us")
                print(json.dumps(resp, indent=2))
  
        
                setScan(pulse_program)
                startScan(globalOverrides=list(), wait=True)
                stopScan()
        
                data = getAllData()
                herald_data = data['PMT Index 0'][1]
                print(herald_data)
                ket1_data = data['PMT Index 1'][1]
                print(ket1_data)
                ket2_data = data['PMT Index 2'][1]
                print(ket2_data)
        
                arrays = []
                for idx,herald_outcome in enumerate(herald_data):
                    if herald_outcome < threshold:
                        arrays.append(ket1_data[idx])
                mean_value = np.mean(np.array(arrays)<threshold)

#--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

                year = datetime.datetime.now().strftime("%Y")
                month = datetime.datetime.now().strftime("%m")
                day = datetime.datetime.now().strftime("%d")

                file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                destination_today = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan_*'
                soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan'

                def copy_file(src_file, dest_path):
                 
                    if not os.path.isfile(src_file):
                        print(f"Source file does not exist: {src_file}")
                        return
                 
                    dest_folder = os.path.dirname(dest_path)
                 
                    if not os.path.exists(dest_folder):
                        os.makedirs(dest_folder)
                        print(f"Created destination folder: {dest_folder}")
                 
                    shutil.copy2(src_file, dest_path)
                    print(f"File copied from {src_file} to {dest_path}")

                #if not file_names_list_all:
                matching_files = glob.glob(pattern)
                matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
                file_path = matching_files[-1]
                chunks = file_path.split('\\')
                print(chunks[:-1])        
                fname = chunks[-1]
                file_names_list_all.append(destination_today+fname)
                file_names_list.append(destination_today+fname)
                source_file = file_path_today + fname
                copied_file = destination_today + fname
                copy_file(source_file,copied_file)

                if np.isnan(mean_value):
                    mean_value = 1
                PD = mean_value
                print("PD is", PD)
                
                if U1_only:
                    fluor_ave_U1.append(PD)
                else:
                    fluor_ave.append(PD)
                
                if U1_only:
                    pulse_time_list_U1.append(pulse_time)
                else:
                    pulse_time_list.append(pulse_time)
                
                if not U1_only:
                    plotPoint(pulse_time, PD,'Qudit Ramsey, 0 state', plotStyle=2)
        
                freq_string = str(round(set_freq[0],3)).replace('.','p')
                if U1_only:
                    combined_data = zip(pulse_time_list_U1,fluor_ave_U1)
                else:
                    combined_data = zip(pulse_time_list,fluor_ave)
                
                # for bussed qudit Ramsey contrasts
                #filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qudit_WaitTime{ramsey_wait}us_d={dimension_string}_Cal_{do_calibrations_0}_U1only_{U1_only}_{repeat_ind}_{dt_string}.txt'
                # for bussed qubit Ramsey measurements
                filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_{pulse_train_U1[:-1]}_{np.round(wtr)}_us_{num_repeat}_{dt_string}.txt'
                with open(filename,'w') as file:
                    for x,y in combined_data:
                        file.write(f"{x},{y}\n")
                    file.write(f"{pulse_train}\n")
                    file.write(f"{[f_offset,f_upper]}\n")
                    file.write(f"{pi_time_pulse_train}\n")
                    file.write(f"{corrected_pulse_train_times}\n")
                    file.write(f"{fractions_U1}\n")
                    file.write(f"{fractions_U2}\n")
                    file.write(f"{probe_trans}\n")
                    file.write(f"{phases}\n")
                    if U1_only:
                        file.write(f"{file_names_list_U1}\n")
                    else:
                        file.write(f"{file_names_list}\n")
            pulse_time = pulse_time + time_step
        closeTrace('Qudit Ramsey, 0 state')


    # looping over different wait times
    for repeat_ind in range(repeat_experiments):
        for wait_time in ramsey_wait_times:
            print('this worked')
            setEvaluation('Eval3')
            pi_time = findPiTime_withfit_plotPD(wait_time,stop_time,start_time, time_step, threshold, pulse_program, script_functions)
            print(pi_time)
            setEvaluation('Eval2')
            #with open(output_file_pitimes,'a') as outfile:
            #    outfile.write(f'{pi_time}\n')

