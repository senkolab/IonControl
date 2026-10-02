#AWG_Control_Test.py created 2024-01-30 16:03:01.049279
import sys

import numpy as np
#import matplotlib.pyplot as plt
import math
import time
import pyvisa as visa
from struct import pack
from struct import unpack

import matlab.engine

freqs_list = [605]
time_list = [30]
freq = [600]
time = [30]
def upload(freqs_list,time_list):
# Start the MATLAB engine for Python
    #try:
    #sharedEngine = matlab.engine.find_matlab()
    print(matlab.engine.find_matlab()[0])
    eng = matlab.engine.connect_matlab(matlab.engine.find_matlab()[0])
    #except:
    eng = matlab.engine.start_matlab()

    eng.matlab.engine.shareEngine('SharedEngine',nargout = 0)

    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
    #try: 
    # Call a MATLAB function
        #matlab_array_freqs = matlab.double(freqs_list)
        #matlab_array_times = matlab.double(time_list)
        #matlab_freq = matlab.double(freq)
        #matlab_time = matlab.double(time)  
        #eng.SendAWGCommand('SOUR:SEQ:DEL:ALL',nargout = 0)
        #eng.SendAWGCommand('TRAC:DEL:ALL',nargout = 0)
        #eng.SendAWGCommand("SOUR:FUNC:MODE SEQ")
        #flag = eng.Pulse_upload(matlab_array_freqs,matlab_array_times,1.92192e9,1)
        #flag1 = eng.Pulse_upload(matlab_freq,matlab_time,1.92192e9,2)
        #eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        #eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,0",nargout = 0)
        #eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,0",nargout = 0)
    #eng.SendAWGCommand("SOUR:FUNC:MODE FIX",nargout = 0)
    #time.sleep(1)
    #eng.SendAWGCommand("SOUR:FUNC:MODE USER", nargout = 0)
    #time.sleep(1)
    #eng.SendAWGCommand("SOUR:FUNC:MODE SEQ", nargout = 0)
    #ime.sleep(1)
    #eng.SendAWGCommand("SOUR:FUNC:MODE FIX", nargout = 0)
    #time.sleep(1)
    return None

#   finally: 
#        eng.quit()


upload(freqs_list,time_list)



