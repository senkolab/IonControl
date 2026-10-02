#test_2.py created 2025-05-14 14:15:27.390727
from Functions_Calibration import *
from Functions_phase_correction import *

pulse_train = [[-1,4,-3],[0,2,0],[-1,4,-3]]
fractions = [1,1,1]
phases_180Hz, _ = compute_phase_and_detuning_180Hz(pulse_train, fractions)

print(phases_180Hz)