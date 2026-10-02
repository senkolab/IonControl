#Shelving_Find_Target_Resonance_Freq_PlotPD_Initialised.py created 2024-02-02 11:22:42.353979
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)

import sys
import os
import datetime
import glob
import numpy as np
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")

#centre_freq = [603.76473]
#s12_level = -2
#centre_freq = [463.7295]

f_offset = 545.50996
f_upper = 623.31181

pitime_n2 = 24.4 # [-2, 4, -4]
pitime_n1 = 55.435 # [-2, 3, -3]
pitime_0 = 50 # [2, 4, 2]
pitime_p1 = 35 # [2, 4, 3]
pitime_p2 = 46 # [2, 4, 4]

#pitime_ref_index = [[-2,4,-4],[-2,3,-3],[2,4,2],[2,4,3],[2,4,4]]
#[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2] = Get_1762_Latest_PiTimes(pitime_ref_index)

#f_offset_index = [0,2,0]
#f_upper_index = [-1,4,-3]
#[f_offset,f_upper] = Get_1762_Latest_EOM_Freqs([f_offset_index,f_upper_index])



probe_trans = [[0,2,0]]
s12_level = probe_trans[0][0]

#sideband_freqs = [+1.354]

# for signal generation
#SetPulseTime = list(Get_1762_Latest_PiTimes(probe_trans))
SetPulseTime = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
SetPulseTime = [131]
centre_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
centre_freq = [545.50996]
# regular scans
freq_step = 0.002
freq_range_factor = 20
power_factor_dbm = matlab.double([1])
SetProbeTime = SetPulseTime[0]

# low power scans
#freq_step = 0.0001
#freq_range_factor = 12
#scale_factor = 1500/SetPulseTime[0]
#scale_factor = 1
#power_factor_dbm = matlab.double([1/scale_factor])
#SetProbeTime = SetPulseTime[0]*scale_factor*0.6

threshold = 12
 
F1PumpTime = 1 #us
F1PumpReps = 50
InitReps = 0
fs = 4e9
F1_pump_attentuations = 0
os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 {F1_pump_attentuations}')



list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

init_trans = list_of_inits[s12_level+2]
init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
init_pulse_time = sum(init_times_array) #us

#init_freqs_array = init_freqs_array_full[init_s12+2]
#eng.SendAWGCommand("SOUR:FUNC:MODE USER", nargout=0)
#eng.SendAWGCommand('SOUR:SEQ:DEL:ALL',nargout = 0)
#eng.SendAWGCommand('TRAC:DEL:ALL',nargout = 0)

#centre_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))

#centre_freq = [603.80428+20.763]
#eng.SendAWGCommand("SOUR:POW:LEV:AMPL "+str(AWG_Power),nargout = 0)
eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode
eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
print(init_freqs_array)
matlab_init_freqs = matlab.double(init_freqs_array)
matlab_init_times = matlab.double(init_times_array)




#matlab_dummy_freq = matlab.double([1921])

#eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,0", nargout=0)





PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == SetProbeTime:
    setGlobal("Shelving_Pulse_Time", SetProbeTime, "us")

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
if not "%s"%Init_PulseTime == init_pulse_time:
    setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%10)
#os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)

pulse_program_findres = "Shelving_InitScheme_Comparison_AWGOnly_Ba137"

range = freq_range_factor*freq_step
freq_start = centre_freq[0]-range
freq_stop = centre_freq[0]+range+freq_step

for i in [1]:

    def findResonance_withfit_plotPD(start_freq, stop_freq, freq_step, dt_string , threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped = script_functions
        set_freq = start_freq
        createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
        flour_exp = []
        fluor_ave = []
        freq_list = []
        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(1)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

        eng.SendAWGCommand("INIT:CONT 1", nargout=0) #0 sets AWG to externally triggered mode
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        

        while set_freq <= stop_freq:
            if scriptIsStopped():
                eng.quit()
                break

            eng.SendAWGCommand("RES", nargout=0)
            time.sleep(1)
            eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
            eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)

            eng.SendAWGCommand("INIT:CONT 1", nargout=0) #0 sets AWG to externally triggered mode
            eng.SendAWGCommand("OUTP:STAT 1", nargout=0)

            #eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
            #eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
            #eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 2",nargout = 0)
            #eng.SendAWGCommand("SOUR:POW:LEV:AMPL 0",nargout = 0)    
            #time.sleep(1)    
            #eng.SendAWGCommand("SOUR:POW:LEV:AMPL 10",nargout = 0)    
            #eng.SendAWGCommand("SOUR:POW:LEV:AMPL "+str(AWG_Power),nargout = 0)
            #eng.SendAWGCommand("INIT:CONT 0", nargout=0) #0 sets AWG to externally triggered mode

            #eng.SendAWGCommand("SYST:STOR:CLE", nargout=0)
            #eng.SendAWGCommand("*RST", nargout=0)
            #eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)
            #eng.SendAWGCommand("SEQ:ADV ONCE",nargout = 0)
            eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)
            print('0')
            eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
            #eng.SendAWGCommand("SOUR:ROSC:EXT:FREQ 10e6", nargout=0)
            time.sleep(0.1)
            eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
            print('1')
            eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
            eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
            print('2')


            if scriptIsStopped():
                eng.quit()
                break

            print(set_freq,SetProbeTime)
            print(init_freqs_array,init_times_array)
            matlab_set_freq = matlab.double([set_freq])
            #matlab_dummy_freq = matlab.double([1921])
            matlab_probe_pulse_time = matlab.double([SetProbeTime])
            power_factor = matlab.double([1])


            #eng.Pulse_upload(matlab_sideband_cool_freq,matlab_sideband_cool_pulse_time,fs,1,power_factor,nargout = 0)

            #eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,1,1,nargout = 0)
            #eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,2,nargout = 0)


            eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,1,power_factor,nargout = 0)
            #eng.Pulse_upload_single(matlab_set_freq,fs,2,power_factor_dbm,nargout = 0)
            if scriptIsStopped():
                eng.quit()
                break
            eng.Pulse_upload_dummy(fs,2,nargout = 0) 
            eng.Pulse_upload(matlab_set_freq,matlab_probe_pulse_time,fs,3,power_factor_dbm,nargout = 0)
            if scriptIsStopped():
                eng.quit()
                break
            print('3')
            eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
            eng.SendAWGCommand("SOUR:SEQ:DEF 4,2,1,1", nargout=0)
            print('4')
            eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
            print('5')
            eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
            eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
            eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)

            if scriptIsStopped():
                eng.quit()
                break

            setScan(pulse_program)
            startScan(globalOverrides=list(), wait=True)
            stopScan()
            data = getAllData()['PMT Count']
            ydata = data[1]
            #threshold = getShelvingThreshold2(ydata)
            fluor_bool = np.array(ydata) < threshold

            PD = np.mean(fluor_bool)
            flour_exp.append(fluor_bool)


            fluor_ave.append(PD)
            freq_list.append(set_freq)

            plotPoint(set_freq, PD, '1762 nm freq scan', plotStyle=2)
            set_freq = set_freq + freq_step
        closeTrace('1762 nm freq scan')
        #print(fluor_ave)
        #print(getShelvingThreshold2(ydata))

        def Lorentzian_1D(x, centre, width, amp, bg):
            return amp/(1+((x-centre)/width)**2) + bg
        #def Lorentzian_1D(x, centre, width, amp, bg):
        #    return -amp/(1+((x-centre)/width)**2) + bg
        #freq_guess = (start_freq+stop_freq)/2
        freq_guess = freq_list[np.argmax(fluor_ave)]
        guess = np.array([freq_guess,0.001,0.5,0])
        #freq_guess = freq_list[np.argmax(fluor_data)]
        #guess = np.array([freq_guess,0.001,10,30])
        popt, pcov = curve_fit(Lorentzian_1D, freq_list, fluor_ave, guess, maxfev = 10000)
        freq_res = popt[0]
        uncertainty = np.sqrt(pcov[0][0])
        print(f'freqs covered: {freq_list}')
        print(f'fluor ave: {fluor_ave}')
        print(f'{freq_res}, amp={popt[2]}, width={popt[1]}, bg={popt[3]}')
        #Sving Raw data for the plots
        freq_string = str(round(freq_res,4)).replace('.','p')
        combined_data = zip(freq_list,fluor_ave)
        filename = f'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration_Raw_data\D52_calibration_{freq_string}_{dt_string}.txt'
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{freq_res},{uncertainty}")

        filename = f'Z:\Lab Data\D52_Calibration_Ba137\Complete_Calibration\D52_calibration_{dt_string}.txt'
        with open(filename,'w') as file:
            file.write(f"{freq_res},{SetProbeTime}")
        #Saving Raw data of each Experiment
    #        combined_data = zip(freq_list,flour_exp)
    #    filename = f'Z:\Lab Data\D52_Calibration_Ba137\Calibration_experiments_raw_data_of_each_experiment\D52_calibration_each_exp_raw_data_{freq_string}_{dt_string}.txt'
    #    with open(filename,'w') as file:
    #        for x,y in combined_data:
    #            file.write(f"{x},{y}\n")
    #        file.write(f"{uncertainty}")
        return freq_res


    setEvaluation('Eval3')

    freq_peak = findResonance_withfit_plotPD(freq_start, freq_stop,  freq_step, dt_string , threshold, pulse_program_findres, script_functions)
    print(freq_peak)
    setEvaluation('Eval2')

eng.quit()