#Functions_RandomisedBenchmarking.py created 2025-12-15 13:57:49.152518

import numpy as np


def generate_haar_unitary(d, number=1, seed=None):
    """
    Generate one or more Haar random unitary matrices of dimension d.

    Parameters:
    -----------
    d : int
        Dimension of the unitary matrix.
    number : int, optional
        Number of Haar random unitaries to generate (default is 1).
    seed : int or None, optional
        Random seed for reproducibility (default is None).

    Returns:
    --------
    np.ndarray or list of np.ndarray
        A single dxd Haar random unitary matrix if number=1,
        otherwise a list of such matrices.
    """
    if not isinstance(d, int) or d <= 0:
        raise ValueError("Dimension d must be a positive integer.")
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Number must be a positive integer.")

    if seed is not None:
        np.random.seed(seed)

    def single_haar():
        # Generate a random complex Gaussian matrix
        z = (np.random.randn(d, d) + 1j * np.random.randn(d, d)) / np.sqrt(2)
        q, r = np.linalg.qr(z)
        # Normalize phases to ensure Haar measure
        diag = np.diag(r)
        lam = diag / np.abs(diag)
        return q * lam

    if number == 1:
        return [single_haar()]
    else:
        return [single_haar() for _ in range(number)]


def givens_rotation(d, i, j, theta, phi):
    """
    Create a d-dimensional Givens rotation matrix acting on subspace (i,j)
    with angles theta and phi.
    """
    G = np.eye(d, dtype=complex)
    c = np.cos(theta / 2)
    s = np.sin(theta / 2) * np.exp(1j * (phi))
    G[i, i] = c
    G[j, j] = c
    G[i, j] = -s
    G[j, i] = np.conj(s)

    # c = np.cos(theta / 2)
    # s = np.sin(theta / 2)
    # exp_phi = np.exp(1j * ((np.pi / 2) - phi))

    # G[i, i] = c
    # G[j, j] = c
    # G[i, j] = -s * exp_phi
    # G[j, i] = s * np.conj(exp_phi)

    return G


def gate_fidelity(U_target, U_decomposed):
    """
    Compute gate fidelity: |tr(U_target^dagger U_decomposed)|^2 / d^2
    Handles the cases where U_target and U_decomposed may be one entry lists.
    """
    if isinstance(U_target, list) and len(U_target) == 1:
        U_target = U_target[0]
    if isinstance(U_decomposed, list) and len(U_decomposed) == 1:
        U_decomposed = U_decomposed[0]
    d = U_target.shape[0]
    fid = np.abs(np.trace(U_target.conj().T @ U_decomposed))**2 / (d**2)
    return fid


def star_topology_decomposition_scheme(d):
    """
    Generate correct decomposition scheme for d-level star topology.

    For row r (from d-1 down to 1):
      - Eliminate columns 1..r-1 with pivot 0
      - Then eliminate column 0 with pivot r
    """
    scheme = []

    for row_idx in range(d - 1, 0, -1):
        z_list = []
        p_list = []

        # First: eliminate columns 1 to row_idx-1 with pivot 0
        for col in range(1, row_idx):
            z_list.append(col)
            p_list.append(0)

        # Last: eliminate column 0 with pivot row_idx
        z_list.append(0)
        p_list.append(row_idx)

        scheme.append({'row': row_idx, 'z': z_list, 'p': p_list})

    return scheme


def decompose_unitary_star_topology(U, tol=1e-10):
    """
    Decompose arbitrary d-dimensional unitary with star topology.
    Uses the transition-aware decomposition scheme from Drozhzhin et al. 2025.
    """
    d = U.shape[0]
    U_current = U.copy()
    pulse_sequence = []

    # Generate the decomposition scheme for this dimension
    scheme = star_topology_decomposition_scheme(d)

    # Apply the scheme
    for step_idx, step in enumerate(scheme):
        row = step['row']
        z_indices = step['z']  # Columns to zero
        p_indices = step['p']  # Pivots for each column

        for z_idx, p_idx in zip(z_indices, p_indices):
            # Compute Givens rotation to zero U[row, z_idx]
            # using U[p_idx, z_idx]
            x = U_current[p_idx, row]
            y = U_current[z_idx, row]

            r = np.hypot(np.abs(x), np.abs(y))
            if r < tol:
                continue

            theta = 2 * np.arctan2(np.abs(y), np.abs(x))
            phi = np.angle(x) - np.angle(y)

            if theta > 1e-8:
                # Apply Givens rotation R_{p_idx, z_idx}
                G = givens_rotation(d, p_idx, z_idx, theta, phi)
                U_current = G.conj().T @ U_current
                pulse_sequence.append(((p_idx, z_idx), theta, phi))

    # Extract diagonal phases
    diagonal_phases = np.angle(np.diag(U_current))

    # Fix the
    fixed_sequence = []

    for (i, j), theta, phi in pulse_sequence:
        if i > j:
            # Swap indices and adjust angles
            i, j = j, i
            theta = -theta
            phi = -phi

        fixed_sequence.append(((i, j), theta, phi))

    # Reconstruct from fixed sequence
    # d = U.shape[0]
    # U_pulses = np.diag(np.exp(1j * diagonal_phases))
    U_pulses = np.eye(d, dtype=complex)
    for (i, j), theta, phi in reversed(fixed_sequence):
        G = givens_rotation(d, i, j, theta, phi)
        U_pulses = G @ U_pulses

    # Calculate and print fidelity
    # fidelity = gate_fidelity(U,
    #                          U_pulses @ np.diag(
    #                          np.exp(1j * diagonal_phases)))
    # print(f"\nGate Fidelity: {fidelity:.8f}")

    # The TRUE unitary is U_pulses @ np.diag(np.exp(1j * diagonal_phases)) but
    # we are interested in inverting just the pulses later - because the phases
    # won't be measured anyway
    return fixed_sequence, U_pulses, diagonal_phases


def _concatenate_pulse_sequences(dimension, unitaries):
    """
    Decompose each unitary in order and concatenate pulse sequences.
    Returns concatenated sequence end-to-beginning (reverse order).
    """
    all_couplings = []
    all_angles = []
    all_phases = []
    all_diagonal_phases = []

    # Process each unitary in REVERSE order (so they concatenate correctly)
    diagonal_fixer = np.zeros(dimension)
    for idx, unitary in enumerate(reversed(unitaries)):
        # Decompose this unitary
        (pulse_sequence, U_pulses,
         diagonal_phases) = decompose_unitary_star_topology(unitary)

        diagonal_phases = diagonal_phases + diagonal_fixer
        # Extract and prepend to lists (since we're going in reverse)
        couplings = []
        angles = []
        fixed_phases = []
        # print(diagonal_phases)
        for (i, j), theta, phi in pulse_sequence:
            # print(i, j, theta, phi)
            # print(diagonal_phases[i], diagonal_phases[j])
            couplings.append((i, j))
            angles.append(theta)
            # phi's need special care for moving diagonal phase matrix to
            # the other end, which requires changing phases as we go
            fixed_phi = phi + diagonal_phases[i] - diagonal_phases[j]
            fixed_phases.append(fixed_phi)

        all_couplings = couplings + all_couplings
        all_angles = angles + all_angles
        all_phases = fixed_phases + all_phases

        # now the overall phase would be applied LAST
        all_diagonal_phases = diagonal_phases

        diagonal_fixer = diagonal_phases

    # combining all pulses, then implementing them from right to left
    combined_pulse_sequence = []
    for idx_coup, coup in enumerate(all_couplings):
        combined_pulse_sequence.append(
            (coup, all_angles[idx_coup], all_phases[idx_coup]))

    U_combined = np.eye(dimension, dtype=complex)
    for (i, j), theta, phi in reversed(combined_pulse_sequence):
        # print(i, j, theta, phi)
        G = givens_rotation(dimension, i, j, theta, phi)
        U_combined = G @ U_combined
    combined_unitary = U_combined

    return (all_couplings, all_angles, all_phases, diagonal_phases,
            combined_unitary)


def _decompose_inverse(dimension, unitary, propagated_phases):
    """Decompose the inverse of just the gate sequence (without diagonal
    phases).

    Since U = G_n G_{n-1} ... G_1 D, we need to find the inverse of G_n
    G_{n-1} ... G_1 which is (G_n G_{n-1} ... G_1)^? = G_1^? G_2^? ...
    G_n^?

    This is equivalent to decomposing U D^? (which removes the diagonal
    factor)

    """

    # Decompose the combined unitary - we will invert it manually very
    # easily in the next step
    (pulse_sequence, U_pulses,
     diagonal_phases) = decompose_unitary_star_topology(unitary)

    # this step JUST implements the reverse order phase flipping ie. for a
    # series of P_N @ ... P_1, the inverse is P_1^dag @ ... P_N^dag
    inverse_sequence = []
    for coupling, theta, phi in reversed(pulse_sequence):
        new_theta = theta
        flipped_phi = np.pi + phi
        inverse_sequence.append((coupling, new_theta, flipped_phi))

    # then we need to propagate through the diagonal matrix we had after
    # the combined unitary
    # diagonal_phases = propagated_phases

    # couplings = []
    # angles = []
    # fixed_phases = []
    # # print(diagonal_phases)
    # fixed_sequence = []
    # for (i, j), theta, phi in inverse_sequence:
    #     # print(i, j, theta, phi)
    #     # print(diagonal_phases[i], diagonal_phases[j])
    #     couplings.append((i, j))
    #     angles.append(theta)
    #     # phi's need special care for moving diagonal phase matrix to
    #     # the other end, which requires changing phases as we go
    #     fixed_phi = phi + propagated_phases[i] - propagated_phases[j]
    #     fixed_phases.append(fixed_phi)
    #     fixed_sequence.append(((i, j), theta, fixed_phi))

    # Extract parameters and flip order for inverse
    couplings = [trans for trans, _, _ in inverse_sequence]
    angles = [theta for _, theta, _ in inverse_sequence]
    phases = [phi for _, _, phi in inverse_sequence]

    U_pulses = np.eye(dimension, dtype=complex)
    # U_pulses = np.diag(np.exp(1j * diagonal_phases))
    for (i, j), theta, phi in reversed(pulse_sequence):
        # print(i, j, theta, phi)
        G = givens_rotation(dimension, i, j, theta, phi)
        U_pulses = G @ U_pulses

    # print('what U_pulses without phase correction is', U_pulses)

    U_inverted = np.eye(dimension, dtype=complex)
    for (i, j), theta, phi in reversed(inverse_sequence):
        # print(i, j, theta, phi)
        G = givens_rotation(dimension, i, j, theta, phi)
        U_inverted = G @ U_inverted
    # print('U^-1 (no phase correction, so D^-1 U^-1 U = I)\n', U_inverted)

    # print('this should be identity', U_inverted @ U_pulses)
    # check_inverse = np.allclose(U_inverted @ U_pulses,
    #                             np.eye(d, dtype=complex))

    # print(f"Is identity? {check_inverse}")
    return couplings, angles, phases, diagonal_phases

if __name__ == "__main__":

    # print(star_topology_decomposition_scheme(3))
    # breakpoint()

    d = 5
    U = generate_haar_unitary(d,1)

    # print(givens_rotation(4,0,1,np.pi/2,0))
    # define an arbitrary QFT for dimension d
    # omega = np.exp(2j * np.pi / d)
    # U = np.array([[omega**(j * k) / np.sqrt(d) for k in range(d)]
    #               for j in range(d)])

    # Using star topology (to start at least)
    allowed_transitions = [(0, i) for i in range(1, d)]

    # this takes a single unitary
    pulse_seq, U_pulses, diagonal_phases = decompose_unitary_star_topology(U[0])

    # this takes a list of unitaries and concatenates the pulse sequences
    (all_couplings, all_angles, all_phases, diag_phases,
     combined_unitary) = _concatenate_pulse_sequences(d, U)

    print("Couplings", all_couplings)
    # breakpoint()

    print("Target unitary U:")
    print(np.round(U, 3))

    print("\nPulse unitary:")
    print(np.round(U_pulses, 3))

    # need to get "real" unitary - so add back phase correction
    U_decomposed = U_pulses @ np.diag(np.exp(1j * diagonal_phases))

    print("\nPhase fixed unitary:")
    print(np.round(U_decomposed, 3))
    fidelity = gate_fidelity(U, U_decomposed)
    print(f"\nGate fidelity: {fidelity:.8f}")

    print("\nDiagonal phases (radians):")
    for i, phase in enumerate(diagonal_phases):
        print(f"{i}: {phase:.4f}")

    print("\nPulse sequence (transition, theta, phi):")
    for i, (trans, theta, phi) in enumerate(pulse_seq):
        print(rf"{i}: {trans}, {theta/np.pi:.4f}, {phi/np.pi:.4f}")
