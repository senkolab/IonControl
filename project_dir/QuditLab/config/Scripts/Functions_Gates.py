import numpy as np
#=====================HELPER_FUNCTIONS=============================
def fix_couplings_and_phases(couplings, fixed_phase_flags, Virtual_Z=False, Z_gate_states=None):
    new_couplings = []
    new_fixed_phase_flags = []
    for (cpl, phase_flag) in zip(couplings, fixed_phase_flags):
        i, j = cpl
        if i != 0 and j == 0:
            cpl_fixed = (0, i)
            phase_flag_fixed = phase_flag + 1.0
        else:
            cpl_fixed = cpl
            phase_flag_fixed = phase_flag

        if Virtual_Z and Z_gate_states is not None:
            if i in Z_gate_states or j in Z_gate_states:
                phase_flag_fixed += 1.0
        new_couplings.append(cpl_fixed)
        new_fixed_phase_flags.append(phase_flag_fixed)
    return new_couplings, new_fixed_phase_flags


def parse_string_to_int_list(s):
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        inside = s[1:-1].strip()
        parts = inside.split(',')
        return [int(x) for x in parts]
    else:
        return [int(s)]

def build_transitions_list(index_to_str_map, couplings):
    transitions_list = []
    for (start_idx, end_idx) in couplings:
        left_list  = parse_string_to_int_list(index_to_str_map[start_idx])
        right_list = parse_string_to_int_list(index_to_str_map[end_idx])
        transitions_list.append(left_list + right_list)
    return transitions_list

transition_strengths = np.loadtxt(
    'Z:\\Lab Data\\Phase_and_freq_correction_180Hz\\Transition_strengths_4p209.txt', delimiter=','
)

def compute_pi_times(pi_t, ref_transitions = np.array([
        transition_strengths[23, 0], transition_strengths[14, 0],
        transition_strengths[17, 4], transition_strengths[16, 4], transition_strengths[15, 4]
    ])):
    transition_strengths = np.loadtxt(
        'Z:\\Lab Data\\Phase_and_freq_correction_180Hz\\Transition_strengths_4p209.txt', delimiter=','
    )
    transition_strengths[transition_strengths == 0] = np.nan

    # pi_t = np.array([19.470, 35.554, 41.166, 30.108, 39.326])
    strengths = ref_transitions

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

def get_pi_times(transitions, pi_t,ref_transitions = np.array([
        transition_strengths[21, 2], transition_strengths[14, 0],
        transition_strengths[5, 2], transition_strengths[16, 4], transition_strengths[15, 4]
    ])):
    matrix = compute_pi_times(pi_t, ref_transitions)
    pi_times_list = []
    col_labels = [-2, -1, 0, 1, 2]
    for transition in transitions:
        if transition[1] == 0 and transition[2] == 0:
            pi_times_list.append(1e6)
            continue
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
            pi_times_list.append(1e6)

    return pi_times_list

def pulse_duration_for_fraction(f, pi_times):
    Omega = np.pi/np.array(pi_times)
    # if not (0 <= f <= 1):
    #     raise ValueError("Fraction f must be between 0 and 1.")
    theta = np.pi*f # 2.0 * np.arcsin(np.sqrt(f))
    return theta / Omega 

#=====================GATE_FUNCTIONS=============================

def Bussed_PolyQubit_Hadamard(dim, mappings,pi_t = [23.172,40.114,47.954,34.418,46.591], U1 = False, Virtual_Z = False, Z_gate_state = None):
    if dim == 2:
        # couplings = [(2,0),(0,1),(2,0)] + [(4,0),(3,0)]  + [(0,1),(3,0)] + [(0,2),(4,0)] 
        # theta = [1,1/2,1] + [1,1/2]  + [1/2,1] + [1/2,1]      
        # fixed_phase_flags = [0.5,0.5,0.5] + [0.5,0.5]  + [0.5,0.5] + [0.5,0.5]
        #couplings = [(0, 2), (3, 0), (0, 1), (4, 0), (0, 1), (3, 0), (2, 0)]
        #theta = [1, 0.5, 2.0 * np.arcsin(np.sqrt(1/3))/np.pi, 2/3, 2.0 * np.arcsin(np.sqrt(1/3))/np.pi, 0.5, 1]
        #fixed_phase_flags = [1,0,0,0,0,0,0,0]
        
        couplings = [(0, 3), (0, 1), (0, 2), (0, 1), (0, 3)]
        theta = [0.5, 2.0 * np.arcsin(np.sqrt(1/3))/np.pi, 4/3, 2.0 * np.arcsin(np.sqrt(2/3))/np.pi + 1, 0.5]
        fixed_phase_flags = [1.5, 0.5, 1.5, 0.5, 0.5]
        couplings, fixed_phase_flags = fix_couplings_and_phases(couplings, fixed_phase_flags,Virtual_Z = Virtual_Z, Z_gate_states = Z_gate_state)
        probe_couplings = [(0,1),(0,2),(0,3)]
    if dim == 3:
        if U1:
            couplings = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]
            theta = [2*np.arcsin(np.sqrt(1/8))/np.pi, 2*np.arcsin(np.sqrt(1/7))/np.pi, 2*np.arcsin(np.sqrt(1/6))/np.pi, 2*np.arcsin(np.sqrt(1/5))/np.pi, 2*np.arcsin(np.sqrt(1/4))/np.pi, 2*np.arcsin(np.sqrt(1/3))/np.pi, 2*np.arcsin(np.sqrt(1/2))/np.pi+1]
            fixed_phase_flags = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
            
        else:
        #    couplings =  [(0, 6), (0, 1), (0, 3), (0, 5), (0, 4), (0, 2), (0, 4), (0, 5), (0, 7), (0, 3), (0, 1), (0, 2), (0, 4), (0, 7), (0, 1), (0, 5), (0, 3), (0, 6), (0, 7), (0, 1), (0, 6)]
        #    theta =  [1.5, 1, 1., 1.5, 2.0 * np.arcsin(np.sqrt(1/3))/np.pi, 2/3, 1 + 2.0 * np.arcsin(np.sqrt(1/3))/np.pi, 1, 1, 0.5, 0.5, 0.5, 1.0, 1.5, 1.0, 1.5, 1, 1.5, 1.5, 1, 1.5]
        #    fixed_phase_flags =  [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 1.5, 1.5]
        
            couplings =  [(0, 1), (0, 2), (0, 1), (0, 3), (0, 2), (0, 1), (0, 4), (0, 3), (0, 2), (0, 1), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1)]

            theta =  list(np.array([4.620092044196028, 3.5168131512264633, 2.3548480564370933, 2.785864459061643, 0.8639124026416288, 5.198616121616511, 3.825845252433758, 0.9425459222203657, 0.6083957794979428, 2.0983340514170985, 2.4243024175517407, 0.4936972077721923, 0.8368416712087451, 1.6870607234979087, 1.1566698096636743, 2.474646309086129, 0.8446406808207161, 0.751348182467907, 1.0684520891358287, 0.8632118900695411, 4.436162349621098, 3.8643269014032087, 0.7751933733103614, 0.8410686705679304, 0.9272952180016122, 1.0471975511965979, 1.2309594173407745, 1.5707963267948966])/np.pi)

            fixed_phase_flags =  list(np.array([4.71238898038469, 1.5707963267948966, 4.71238898038469, 1.5707963267948966, 1.5707963267948966, 4.71238898038469, 1.5707963267948966, 4.71238898038469, 4.71238898038469, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 4.71238898038469, 4.71238898038469, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 4.71238898038469, 1.5707963267948966, 4.71238898038469, 4.71238898038469, 1.5707963267948966, 4.71238898038469, 1.5707963267948966, 1.5707963267948966])/np.pi)
        
        #couplings = [(2,0),(0,1),(2,0)] + [(4,0),(3,0)]  + [(0,1),(3,0)] + [(0,2),(4,0)]\
        #          + [(6,0),(0,5),(6,0)] + [(8,0),(7,0)]  + [(0,5),(7,0)] + [(6,0)]\
        #          + [(0,2),(6,0)] + [(5,0),(0,1),(5,0)] + [(7,0),(0,3),(7,0)] + [(0,4),(8,0)]
        #theta = [1,1/2,1] + [1,1/2]  + [1/2,1] + [1/2,1]\
        #          + [1,1/2,1] + [1,1/2]  + [1/2,1] + [1/2]\
        #          + [1/2,1] + [1,1/2,1] + [1,1/2,1] + [1/2,1]
        #fixed_phase_flags = [0.5,0.5,0.5] + [0.5,0.5]  + [0.5,0.5] + [0.5,0.5]\
        #                   +[0.5,0.5,0.5] + [0.5,0.5]  + [0.5,0.5] + [0.5]\
        #                   + [0.5,0.5] + [0.5,0.5,0.5] + [0.5,0.5,0.5] + [0.5,0.5]
        couplings, fixed_phase_flags = fix_couplings_and_phases(couplings, fixed_phase_flags,Virtual_Z = Virtual_Z, Z_gate_states = Z_gate_state)
        probe_couplings = [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7)]
    Hadamard_trans = build_transitions_list(mappings,couplings)
    Hadamard_pitimes = list(pulse_duration_for_fraction(np.array(theta),get_pi_times(Hadamard_trans,pi_t)))
    probe_trans = build_transitions_list(mappings,probe_couplings)
    return Hadamard_trans, Hadamard_pitimes,fixed_phase_flags, theta, probe_trans

def PolyQubit_Toffoli(dim, mappings,pi_t = [23.172,40.114,47.954,34.418,46.591]):
    if dim == 4:
        couplings = [(0,1)]
        theta =  [1]
        fixed_phase_flags =  [0]
        couplings, fixed_phase_flags = fix_couplings_and_phases(couplings, fixed_phase_flags,Virtual_Z = False, Z_gate_states = None)
        probe_couplings = [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),(0,11),(0,12),(0,13),(0,14),(0,15)]
    trans = build_transitions_list(mappings,couplings)
    pitimes = list(pulse_duration_for_fraction(np.array(theta),get_pi_times(trans,pi_t)))
    probe_trans = build_transitions_list(mappings,probe_couplings)
    return trans, pitimes,fixed_phase_flags, theta, probe_trans

#if __name__ == "__main__":

#mappings = {0: '-2', 1: '[2, -1]', 2: '[3, -2]', 3: '[4, -4]', 4: '[3, -3]'}
#mappings = {0: '1', 1: '[2, -1]', 2: '[3, 2]', 3: '[4, 2]', 4: '[4, 0]', 5: '[3, 3]', 6: '[4, 1]', 7: '[4, -1]'}

#print(Bussed_PolyQubit_Hadamard(2,mappings))
    