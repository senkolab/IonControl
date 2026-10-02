#awg_quick_upload.py created 2026-02-27 15:36:32.474170

import sys

import numpy as np

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG_Upload import initialize_awg, make_multitone_waveform, upload_waveform_to_awg, send_awg_command

# SET FFREQUENCY HERE
set_frequency = 610.3892  # MHz

# define waveform and upload to awg
awg_frequency = getGlobal("AWG1_Frequency")
if not "%s"%awg_frequency == "%s MHz"%set_frequency:
    setGlobal("AWG1_Frequency", np.round(set_frequency, 6), "MHz")

# awg settings
max_amplitude = 1  # V
awg_voltage = 0.70  # V
sample_rate = 1e9  # Hz
set_frequency = set_frequency * 1e6
pulse_length = 100 / set_frequency  # n periods

initialize_awg(amplitude=max_amplitude)
#send_awg_command(":FREQ:RAST 2000000000")
signal, resample_rate = make_multitone_waveform([set_frequency], [awg_voltage], [0.0], pulse_length, sample_rate, max_amplitude)
upload_waveform_to_awg(signal, resample_rate)
