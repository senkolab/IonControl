#AWG_programming_tests,py.py created 2024-03-06 10:32:51.139898


centre_freq = [620.400]
freq_step = 0.004
freq_range_factor = 4

# for signal generation
SetPulseTime = [1000] #us
# for probing pulse
power_factor = 1
SetProbeTime = 400

F1PumpTime = 20 #us
F1PumpReps = 20
InitReps = 10
AWG_Power = 3

fs = 1.92192e9
# mp2
#init_freqs_array = [602.458321,600.575041,594.505,606.552242]
#init_times_array = [100,67,140,74] #us

# mp1
init_freqs_array = [602.460,600.573,594.535,603.676]
init_times_array = [100,65,125,46] #us

#Shelving_Find_Target_Resonance_Freq_PlotPD_Initialised.py created 2024-02-02 11:22:42.353979
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)



#eng.SendAWGCommand("SOUR:FUNC:MODE USER", nargout=0)
eng.SendAWGCommand('SOUR:SEQ:DEL:ALL',nargout = 0)
eng.SendAWGCommand('TRAC:DEL:ALL',nargout = 0)

AWG_Power = 3
eng.SendAWGCommand("SOUR:POW:LEV:AMPL "+str(AWG_Power),nargout = 0)
eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
#eng.SendAWGCommand("INIT:CONT:ENAB ARM",nargout = 0)
#eng.SendAWGCommand("OUTP:STAT 1", nargout=0)

matlab_init_freqs = matlab.double(init_freqs_array)
matlab_init_times = matlab.double(init_times_array)

matlab_dummy_freq = matlab.double([1921])

#eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,0", nargout=0)


#eng.SendAWGCommand("SYST:STOR:CLE", nargout=0)
#eng.SendAWGCommand("*RST", nargout=0)
#eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)\

eng.SendAWGCommand("SOUR:FUNC:MODE FIX",nargout = 0)
eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
eng.SendAWGCommand("SOUR:ROSC:EXT:FREQ 10e6", nargout=0)
#time.sleep(1)
#eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

matlab_init_freqs = matlab.double([610])
matlab_init_times = matlab.double([300])
        
matlab_set_freq = matlab.double([620])

matlab_dummy_freq = matlab.double([630])
matlab_probe_pulse_time = matlab.double([300])
power_factor = matlab.double([1])
power_factor_dbm = matlab.double([1])

eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,power_factor,nargout = 0)

eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,power_factor_dbm,nargout = 0)

eng.Pulse_upload(matlab_dummy_freq,matlab_probe_pulse_time,fs,3,power_factor,nargout = 0) # Dummy 3rd sequence

eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1000,0", nargout=0)
#eng.SendAWGCommand("SOUR:SEQ:SEL 2", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
#eng.SendAWGCommand("SOUR:SEQ:SEL 3", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1000,0", nargout=0)
eng.SendAWGCommand("SOUR:SEQ:DEF 4,2,1,1", nargout=0)

eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        
#eng.SendAWGCommand("SEQ:ONCE:COUN 1",nargout = 0)
#eng.SendAWGCommand("ARM:SEQ:SLOP POS",nargout = 0)
#eng.SendAWGCommand("INIT:CONT:ENAB ARM",nargout = 0)
#eng.SendAWGCommand("INIT:STAT OFF",nargout = 0)

eng.quit()