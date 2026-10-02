#AWG_test.py created 2025-09-07 10:26:24.474231

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

eng.SendAWGCommand("RES", nargout=0)
time.sleep(5)
eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
time.sleep(0.1)
eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

seg_num = 1
fs = 4e9
matlab_initial_state_freq = matlab.double([100,200,300,400,500])
matlab_initial_state_pulse_time = matlab.double([3,3,3,3,3])
matlab_initial_state_phases = matlab.double([0,0,0,0,0])
eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)
seg_num = seg_num + 1 
eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 
seg_num = seg_num + 1 
eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0)
seg_num = seg_num + 1 
eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) 

eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,0", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,1", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 4,2,1,1", nargout=0)
eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
