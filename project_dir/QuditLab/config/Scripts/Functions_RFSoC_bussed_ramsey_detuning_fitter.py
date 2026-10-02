#Functions_RFSoC_bussed_ramsey_detuning_fitter.py created 2026-02-11 17:57:00.983278

import numpy as np
from scipy.linalg import expm
import io
from scipy.optimize import curve_fit

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


def B_line_mG(t, B0=0.2289, A60=-0.2791, phi60=1.0002, A180=-0.0774, phi180=-0.2650, param_file = 'Z:\Lab Data\Line_signal_fitted_params\line_signal_fit_params.txt'):
    B0_use, freqs, A_vals, phi_vals = _get_line_params(param_file, B0, A60, phi60, A180, phi180)
    t_arr = np.asarray(t, dtype=float)
    y = np.full_like(t_arr, B0_use, dtype=float)
    for f, A, phi in zip(freqs, A_vals, phi_vals):
        y = y + A * np.cos(2.0 * np.pi * f * t_arr + phi)
    return y

def B_rel_G(t, B0=0.2289, A60=-0.2791, phi60=1.0002, A180=-0.0774, phi180=-0.2650, param_file = 'Z:\Lab Data\Line_signal_fitted_params\line_signal_fit_params.txt'):
    return (
        B_line_mG(t, B0, A60, phi60, A180, phi180, param_file=param_file)
        - B_line_mG(0.0, B0, A60, phi60, A180, phi180, param_file=param_file)
    ) * 1e-3

def primitive_B_rel_G(t, B0=0.2289, A60=-0.2791, phi60=1.0002, A180=-0.0774, phi180=-0.2650, param_file = 'Z:\Lab Data\Line_signal_fitted_params\line_signal_fit_params.txt'):
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

def integral_B_rel_G(t_start, t_end, B0=0.2289, A60=-0.2791, phi60=1.0002, A180=-0.0774, phi180=-0.2650, param_file = 'Z:\Lab Data\Line_signal_fitted_params\line_signal_fit_params.txt'):
    F_end = primitive_B_rel_G(t_end, B0, A60, phi60, A180, phi180, param_file=param_file)
    F_start = primitive_B_rel_G(t_start, B0, A60, phi60, A180, phi180, param_file=param_file)
    return F_end - F_start

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

def compute_pi_times(pi_t = [26.374, 38.265, 118.144, 30.527, 38.734]):
    transition_strengths_path=r"Z:\Lab Data\Phase_and_freq_correction_180Hz\Transition_strengths_4p209.txt"
    transition_strengths = np.loadtxt(transition_strengths_path, delimiter=",")
    transition_strengths[transition_strengths == 0] = np.nan
    strengths = np.array(
        [
            transition_strengths[21, 2],
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

def bussed_ramsey_pop0(transition_pair, T, delta, ramsey_phase,  pi_time_refs = [26.374, 38.265, 118.144, 30.527, 38.734], consider_line = False):
    # get sensitivity table
    sensitivities_path=r"Z:\Lab Data\Phase_and_freq_correction_180Hz\sensitivities_4p209.txt" 
    sens_matrix = np.loadtxt(sensitivities_path, delimiter=",")
    sens_list = get_pi_times_from_matrix(transition_pair, sens_matrix)
    #get - pitimes
    pi_times = get_pi_times_from_matrix(transition_pair, compute_pi_times(pi_t = pi_time_refs))
    #get - sensitivities
    pair_sensitivities = get_pi_times_from_matrix(transition_pair, sens_matrix)

    pi_time_0b = pi_times[0]
    pi_time_b1 = pi_times[1]
    sens_0b = pair_sensitivities[0]
    sens_b1 = pair_sensitivities[1]
    # Rabi frequencies
    omega_0b = np.pi / (pi_time_0b * 1e-6)
    omega_b1 = np.pi / (pi_time_b1 * 1e-6)
    omega_dummy = np.pi/(1)
    t_pi2_0b = (pi_time_0b * 1e-6) / 2
    t_pi_b1 = (pi_time_b1 * 1e-6)

    Ramsey_wait = T * 1e-6
    # get - integral_values
    fractions = [1, 0.5, (np.sin((T/1e6)*(np.pi/2)))**2, 0.5, 1]
    rabi_freqs = [omega_0b, omega_b1, omega_dummy, omega_b1, omega_0b]
    times_seq_for_integral = get_pulse_schedule(rabi_freqs, fractions)
    # print(times_seq_for_integral)
    line_int_values = []
    for slots in times_seq_for_integral:
        if  consider_line:
            line_int_values.append(2.0 * np.pi * 1e6*integral_B_rel_G(slots[0], slots[1]))
        else:
            line_int_values.append(0)
    # print(line_int_values)

    def U_0b(omega, t, phase, delta, line_delta_eq = 0):
        H = np.array([
            [0, omega * np.exp(-1j * phase) / 2, 0],
            [omega * np.exp(1j * phase) / 2, delta + (sens_0b*line_delta_eq/t), 0],
            [0, 0, (sens_b1*line_delta_eq/t)]
        ], dtype=complex)
        return expm(-1j * H * t)

    def U_b1(omega, t, phase, delta, line_delta_eq = 0):
        H = np.array([
            [0, 0, omega * np.exp(-1j * phase) / 2],
            [0, delta + (sens_0b*line_delta_eq/t), 0],
            [omega * np.exp(1j * phase) / 2, 0, (sens_b1*line_delta_eq/t)]
        ], dtype=complex)
        return expm(-1j * H * t)

    def U_wait(t, delta, line_delta_eq = 0):
        H = np.array([
            [0, 0, 0],
            [0, delta + (sens_0b*line_delta_eq/t), 0],
            [0, 0, (sens_b1*line_delta_eq/t)]
        ], dtype=complex)
        return expm(-1j * H * t)

    # --- Pulse sequence ---
    U1 = U_0b(omega_0b, t_pi2_0b, phase=np.pi, delta=delta, line_delta_eq = line_int_values[0])
    U2 = U_b1(omega_b1, t_pi_b1, phase=0.0, delta = delta, line_delta_eq = line_int_values[1])
    Uw = U_wait(Ramsey_wait, delta, line_delta_eq = line_int_values[2])
    U3 = U_b1(omega_b1, t_pi_b1, phase=np.pi, delta = delta, line_delta_eq = line_int_values[3])
    U4 = U_0b(omega_0b, t_pi2_0b, phase=np.pi*ramsey_phase, delta=delta, line_delta_eq = line_int_values[4])

    U_total = U4 @ U3 @ Uw @ U2 @ U1

    # Initial state |0>
    ket0 = np.array([0, 1, 0], dtype=complex)

    final_state = U_total @ ket0
    pop0 = np.abs(final_state[1])**2

    return pop0


def fit_detuning_for_bussed_ramsey(ket_data,
                                 phase_list,
                                 transition_pair,
                                 T_wait_bussed_ramsey,
                                 pi_time_refs =  [26, 38.265, 118, 30.527, 38.734],
                                 initial_delta_guess=-2 * np.pi * 0, consider_line = True):
    ket_data = np.array(ket_data, dtype=float)

    phase_array = np.array(phase_list, dtype=float)

    if ket_data.shape[0] != phase_array.shape[0]:
        raise ValueError("ket_data and phase_list must have the same length.")



    def ramsey_model(phase_pi, delta):
        return np.array([
            bussed_ramsey_pop0(transition_pair, T_wait_bussed_ramsey, delta, ph, consider_line = True, pi_time_refs = pi_time_refs)
            for ph in phase_pi
        ])

    try:
        params, covariance = curve_fit(
            ramsey_model,
            phase_array,
            ket_data,
            p0=[initial_delta_guess],

            maxfev=50000
        )
        delta_opt = params[0]
        if covariance is not None:
            errors = np.sqrt(np.diag(covariance))
            delta_err = errors[0] if np.isfinite(errors[0]) else None
        else:
            delta_err = None
        return delta_opt, delta_err
    except RuntimeError:
        return None, None