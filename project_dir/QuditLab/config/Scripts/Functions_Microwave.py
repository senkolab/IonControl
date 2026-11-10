import numpy as np
from pathlib import Path

def transition_matrix_value(matrix, transition):

    state_order = [ (x, y) for x in [1, 2] for y in range(x, -x-1, -1)] 

    matrix = np.asarray(matrix)

    if matrix.shape != (8, 8):
        raise ValueError(
            f"The matrix must have shape (8, 8); received {matrix.shape}."
        )

    if len(transition) != 6:
        raise ValueError(
            "The transition must have the format "
            "['S', final_F, final_mF, 'S', initial_F, initial_mF]."
        )

    (
        final_manifold,
        final_F,
        final_mF,
        initial_manifold,
        initial_F,
        initial_mF,
    ) = transition

    if (
        str(final_manifold).upper() != "S"
        or str(initial_manifold).upper() != "S"
    ):
        raise ValueError("Both states must belong to the S1/2 manifold.")

    final_state = (int(final_F), int(final_mF))
    initial_state = (int(initial_F), int(initial_mF))

    state_index = {
        state: index
        for index, state in enumerate(state_order)
    }

    if final_state not in state_index:
        raise ValueError(f"Invalid final state: {final_state}")

    if initial_state not in state_index:
        raise ValueError(f"Invalid initial state: {initial_state}")

    row = state_index[final_state]
    column = state_index[initial_state]

    return matrix[row, column].item()


def get_transition_frequency_MW(
    target_transition,
    fu = 8046.463,
    fl = 8029.027,
    f0 = 8037.750,
):

    state_order = [(x, y) for x in [1, 2] for y in range(x, -x-1, -1)]

    with np.load(r"Z:\Lab Data\Microwave_calibrations\Calibration_parameters\From_theory\S12_magnetic_sensitivity.npz", allow_pickle=False) as data:
        sensitivity_matrix = data["matrix"]
        sensitivity_state_order = [tuple(x) for x in data["state_order"]]

    with np.load(r"Z:\Lab Data\Microwave_calibrations\Calibration_parameters\From_theory\S12_an2.npz", allow_pickle=False) as data:
        an2_matrix = data["matrix"]
        an2_state_order = [tuple(x) for x in data["state_order"]]

    upper_transition = ['S', 2, +2, 'S', 1, +1]
    lower_transition = ['S', 2, -2, 'S', 1, -1]
    clock_transition = ['S', 2, 0, 'S', 1, 0]

    kfn = transition_matrix_value(sensitivity_matrix, target_transition)
    kfu = transition_matrix_value(sensitivity_matrix, upper_transition)
    kfl = transition_matrix_value(sensitivity_matrix, lower_transition)
    kf0 = transition_matrix_value(sensitivity_matrix, clock_transition)

    an2 = transition_matrix_value(an2_matrix, target_transition)

    fn = ((kfn - kf0) / (kfu - kfl) * (fu - fl) + f0 + an2)

    return float(fn)

def get_transition_frequencies_MW(frequency_list, fu = 8046.463, fl = 8029.027, f0 = 8037.750):
    return [get_transition_frequency_MW(transition, fu, fl, f0) for transition in frequency_list]  

def get_pi_time_MW(target_transition, pi_time_0 = 34, pi_time_u = 21, pi_time_l = 27):

    with np.load(r"Z:\Lab Data\Microwave_calibrations\Calibration_parameters\From_theory\S12_rabi_matrix.npz", allow_pickle=False) as data:
        rabi_matrix = data["matrix"]

    upper = ["S", 2, +2, "S", 1, +1]
    lower = ["S", 2, -2, "S", 1, -1]
    clock = ["S", 2, 0, "S", 1, 0]

    final_F, final_mF = int(target_transition[1]), int(target_transition[2])
    initial_F, initial_mF = int(target_transition[4]), int(target_transition[5])

    if final_F != 2 or initial_F != 1: raise ValueError("Target must be an F=1 -> F=2 transition.")

    q = final_mF - initial_mF
    calibration = {0: (clock, pi_time_0), +1: (upper, pi_time_u), -1: (lower, pi_time_l)}

    if q not in calibration: raise ValueError(f"Transition has unsupported delta_mF={q}.")

    calibration_transition, calibration_pi_time = calibration[q]
    target_rabi = abs(transition_matrix_value(rabi_matrix, target_transition))
    calibration_rabi = abs(transition_matrix_value(rabi_matrix, calibration_transition))

    if not np.isfinite(target_rabi) or target_rabi == 0: raise ValueError("Target transition has an invalid Rabi frequency.")
    if not np.isfinite(calibration_rabi) or calibration_rabi == 0: raise ValueError("Calibration transition has an invalid Rabi frequency.")

    return float(calibration_pi_time * calibration_rabi / target_rabi)
