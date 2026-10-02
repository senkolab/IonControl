import numpy as np

def compute_phase_and_detuning_180Hz(pulse_train, fractions, pi_t = [21.46,36.91,45.20,32.07,44.55]):

    def line_signal(t, 
                    A1=0.000273203217587317, phi1=-0.7165710705760902,
                    A2=6.842623973133531e-05, phi2=-7.7358413871655065,
                    offset=0.0002890819550014299):
        return (
            2*np.pi*A1 * np.sin(2 * np.pi * 60 * t + phi1) +
            2*np.pi*A2 * np.sin(2 * np.pi * 180 * t + phi2) +
            offset
        ) - (
            2*np.pi*A1 * np.sin(2 * np.pi * 60 * 0 + phi1) +
            2*np.pi*A2 * np.sin(2 * np.pi * 180 * 0 + phi2) +
            offset
        )
    
    
    def analytical_integral(T, 
                    A1=0.000273203217587317, phi1=-0.7165710705760902,
                    A2=6.842623973133531e-05, phi2=-7.7358413871655065,
                    offset=0.0002890819550014299):
    
        int_60 = (A1 / 60) * (np.cos(phi1) - np.cos(2 * np.pi * 60 * T + phi1))
    
        int_180 = (A2 / 180) * (np.cos(phi2) - np.cos(2 * np.pi * 180 * T + phi2))
    
        t0 = (2 * np.pi * A1 * np.sin(2 * np.pi * 60 * 0 + phi1) +
              2 * np.pi * A2 * np.sin(2 * np.pi * 180 * 0 + phi2) +
              offset)
    
        int_offset = (offset - t0) * T
        return int_60 + int_180 + int_offset

    def compute_pi_times(pi_t):
        transition_strengths = np.loadtxt(
            'Z:\\Lab Data\\Phase_and_freq_correction_180Hz\\Transition_strengths_4p216.txt', delimiter=','
        )
        transition_strengths[transition_strengths == 0] = np.nan
    
        # pi_t = np.array([19.470, 35.554, 41.166, 30.108, 39.326])
        strengths = np.array([
            transition_strengths[23, 0], transition_strengths[14, 0],
            transition_strengths[17, 4], transition_strengths[16, 4], transition_strengths[15, 4]
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

    def get_pi_times(transitions,matrix):
        pi_times_list = []
        col_labels = [-2, -1, 0, 1, 2]
        for transition in transitions:
            row_label = [transition[1],transition[2]]
            Fs = [1,2,3,4]
            states = []
            for i in Fs:
                for j in range(2*i+1):
                    mF = i-j
                    states.append([i,mF])
        
            row_labels = states
        
            col_label = transition[0]
        
            # Find the index of the row label
            row_index = next((i for i, label in enumerate(row_labels) if label == row_label), None)
            # Find the index of the column label
            col_index = col_labels.index(col_label)
            
            if row_index is not None and col_index in range(len(col_labels)):
                pi_times_list.append(matrix[row_index, col_index])
            else:
                pi_times_list.append(np.nan)
    
        return pi_times_list
    
    def get_pulse_schedule(rabi_freqs, fractions):
        if len(rabi_freqs) != len(fractions):
            raise ValueError(f"rabi_freqs {len(rabi_freqs)} and fractions {len(fractions)} must have the same length.")
        times = []
        t_current = 0.0  # start time in microseconds
        for Omega, frac in zip(rabi_freqs, fractions):
            # if not 0 <= frac <= 1:
            #     raise ValueError(f"Fraction must be between 0 and 1, got {frac}.")
            # Calculate the rotation angle and pulse duration (in microseconds)
            # theta = 2.0 * np.arcsin(np.sqrt(frac))
            theta = np.pi*frac
            t_pulse = theta / Omega if Omega > 0 else 0.0
            t_start = t_current
            t_end = t_current + t_pulse
            times.append((t_start, t_end))
            t_current = t_end
        return times
    
    pi_times_train = get_pi_times(pulse_train,compute_pi_times(pi_t))
    rabi_frequencis_list = np.pi/np.array(pi_times_train)

    sens_matrix = np.loadtxt('Z:\Lab Data\Phase_and_freq_correction_180Hz\sensitivities_4p216.txt',delimiter=',')
    sens_list = get_pi_times(pulse_train, sens_matrix)
    
    schedule = get_pulse_schedule(rabi_frequencis_list, fractions)
    # print(schedule)
    pulses_sec = [(start * 1e-6, end * 1e-6) for (start, end) in schedule]
    
    integrated_values = []
    detuning_values = []

    # For each pulse, compute the analytical integration and instantaneous detuning at the pulse start.
    for (start_s, _) in pulses_sec:
        integ = analytical_integral(start_s)
        integrated_values.append(integ)
        det = line_signal(start_s)
        detuning_values.append(det)
    
    # Convert to numpy arrays for vectorized operations.
    # print(integrated_values)
    integrated_values = np.array(integrated_values)
    detuning_values = np.array(detuning_values)
    sens_array = np.array(sens_list)
    
    # Compute phase (scaled integrated detuning) and instantaneous detuning.
    phase_180Hz = integrated_values * 1e6 * sens_array
    detuning_180Hz = detuning_values * sens_array
    
    return phase_180Hz, detuning_180Hz
