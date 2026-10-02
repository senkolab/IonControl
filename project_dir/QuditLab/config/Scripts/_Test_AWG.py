#AWG_test.py created 2022-06-14 13:04:30.916495

import numpy as np
import matplotlib.pyplot as plt
import math
import time
import pyvisa as visa

#                                       EXAMPLE
#               Setup for sending waveform
segment = 10
amplitude_dBm = 10
amplitude_W = 10**(amplitude_dBm/10)
    
clock = 4.6e9
num_points = 384
freq = 30e6
phase = 0

#               Create normalized waveform
Waveform1 = Waveform(clock, freq, timeQ=True)

#               Setup connection to AWG and send the waveform
AWG1 = AWG(connect=True, address=awg_visa_address)
AWG1.send_single_awseg(Waveform1, segment, amp_dBm=amplitude_dBm)