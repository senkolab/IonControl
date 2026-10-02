#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(1)

import sys
import os
import datetime
import glob
import json
import numpy as np
import shutil
from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"
def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
Side_band_cooling_reps = 0


#initial_state = [[0,2,2]]

do_calibrations_0 = False
Measure_U1_only = False
full_phase_scan = True

#ramsey_wait_times = np.arange(0,5100,500)
repeat_experiments = 1
ramsey_wait_times = [1]
f_offset = float(getGlobal('f_offset'))
f_upper = float(getGlobal('f_upper'))

pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]


#waitTime_list  = [1,10,300,400,500,600,700,800,900,100,350,450,550,650,750,850,950,200]
#waitTime_list = [1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500]
waitTime_list = [0]
wait_trans_piTime = list(Get_1762_PiTimes([[0,0,0]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))[0]
print(wait_trans_piTime)
for wtr in waitTime_list:
    num_repeat = 0

    '''
    #d=2 
    #, (np.sin((400/1013.667)*(np.pi/2)))**2, , [-2,4,-3]
    initial_state = [[0, 4, -2]]

    pulse_train_U1 = [[0, 4, -2], [0, 2, 2], [0,0,0]]
    fractions_U1 = [0.5, 1,(np.sin((wtr/wait_trans_piTime)*(np.pi/2)))**2]
    simulated_phase_mask_U1 = [0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 0]

    pulse_train_U2 = [[0, 2, 2], [0, 4, -2]]
    fractions_U2 = [1, 0.5]
    simulated_phase_mask_U2 = [0, 1]
    fixed_phase_mask_U2 = [1, 0]

    s12_state_shelvings = []

    probe_trans = [[0, 4, -2], [0, 2, 2]]


####################### DIMENSION = 10
    initial_state = [[0, 4, -1]]

    pulse_train_U1 = [[0, 4, -1], [0, 3, 0], [1, 4, -1], [1, 2, -1], [1, 4, -1], [1, 3, 2], [1, 4, -1], [1, 4, 2], [0, 4, -1], [0, 3, 1], [1, 4, -1], [1, 3, 3], [1, 4, -1], [1, 4, 0], [1, 4, -1], [1, 4, 1], [0, 4, -1], [0, 4, -2]]
    fractions_U1 = [0.1, 1, 0.1111111111111111, 1, 0.125, 1, 0.14285714285714285, 1, 0.16666666666666666, 1, 0.2, 1, 0.25, 1, 0.3333333333333333, 1, 0.5, 1]
    simulated_phase_mask_U1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

    pulse_train_U2 = [[0, 4, -2], [0, 4, -1], [0, 4, -2], [1, 4, 1], [1, 4, -1], [1, 4, 1], [1, 4, 0], [1, 4, -1], [1, 4, 0], [1, 3, 3], [1, 4, -1], [1, 3, 3], [0, 3, 1], [0, 4, -1], [0, 3, 1], [1, 4, 2], [1, 4, -1], [1, 4, 2], [1, 3, 2], [1, 4, -1], [1, 3, 2], [1, 2, -1], [1, 4, -1], [1, 2, -1], [0, 3, 0], [0, 4, -1], [0, 3, 0]]
    fractions_U2 = [1, 0.5, 1, 1, 0.3333333333333333, 1, 1, 0.25, 1, 1, 0.2, 1, 1, 0.16666666666666666, 1, 1, 0.14285714285714285, 1, 1, 0.125, 1, 1, 0.1111111111111111, 1, 1, 0.1, 1]
    simulated_phase_mask_U2 = [0, 9, 0, 0, 8, 0, 0, 7, 0, 0, 6, 0, 0, 5, 0, 0, 4, 0, 0, 3, 0, 0, 2, 0, 0, 1, 0]
    fixed_phase_mask_U2 = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]

    s12_state_shelvings = []
    s12_state_fractions = []
    s12_state_fixed_phases = []
    s12_state_simulated_phases = []

    probe_trans = [[1, 4, -1], [-1, 3, 0], [1, 2, -1], [1, 3, 2], [2, 4, 2], [0, 3, 1], [1, 3, 3], [1, 4, 0], [1, 4, 1], [0, 4, -2]]
    '''

    '''
    # TESTIGN WITH D=3 BUSSED
        initial_state = [[0, 4, -1]]

        pulse_train_U1 = [[0, 4, -1], [0, 3, 0], [1, 4, -1], [1, 2, -1]]
        fractions_U1 = [0.3333333333333333, 1, 0.5, 1]
        simulated_phase_mask_U1 = [0, 0, 0, 0]
        fixed_phase_mask_U1 = [1, 0, 1, 0]

        pulse_train_U2 = [[1, 2, -1], [1, 4, -1], [1, 2, -1], [0, 3, 0], [0, 4, -1], [0, 3, 0]]
        fractions_U2 = [1, 0.5, 1, 1, 0.3333333333333333, 1]
        simulated_phase_mask_U2 = [0, 2, 0, 0, 1, 0]
        fixed_phase_mask_U2 = [1, 0, 0, 1, 0, 0]

        s12_state_shelvings = []
        s12_state_fractions = []
        s12_state_fixed_phases = []
        s12_state_simulated_phases = []

        probe_trans = [[1, 4, -1], [-1, 3, 0], [1, 2, -1]]
    '''
    initial_state = [[-1, 3, -1]]
    pulse_train_U1 = [[-1, 3, -1], [-1, 2, -2], [-2, 3, -1], [-2, 2, -1], [-1, 3, -1], [-1, 4, -2], [-1, 3, -1], [-1, 3, -2], [0, 3, -1], [0, 4, -1], [0, 3, -1], [0, 4, 0], [-2, 3, -1], [-2, 3, -3]]
    fractions_U1 = [0.125, 1, 0.1428571428571429, 1, 0.16666666666666663, 1, 0.19999999999999996, 1, 0.25, 1, 0.33333333333333337, 1, 0.5, 1]
    simulated_phase_mask_U1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    pulse_train_U2 = [[-2, 3, -3], [-2, 3, -1], [-2, 3, -3], [0, 4, 0], [0, 3, -1], [0, 4, 0], [0, 4, -1], [0, 3, -1], [0, 4, -1], [-1, 3, -2], [-1, 3, -1], [-1, 3, -2], [-1, 4, -2], [-1, 3, -1], [-1, 4, -2], [-2, 2, -1], [-2, 3, -1], [-2, 2, -1], [-1, 2, -2], [-1, 3, -1], [-1, 2, -2]]
    fractions_U2 = [1, 0.5, 1, 1, 0.33333333333333337, 1, 1, 0.25, 1, 1, 0.19999999999999996, 1, 1, 0.16666666666666663, 1, 1, 0.1428571428571429, 1, 1, 0.125, 1]
    simulated_phase_mask_U2 = [0, 7, 0, 0, 6, 0, 0, 5, 0, 0, 4, 0, 0, 3, 0, 0, 2, 0, 0, 1, 0]
    fixed_phase_mask_U2 = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
    s12_state_shelvings = []
    probe_trans = [[-1, 3, -1], [0, 2, -2], [1, 2, -1], [0, 4, -2], [-2, 3, -2], [1, 4, -1], [1, 4, 0], [-2, 3, -3]]
     

############################### Just make sure s12 state is dealt with (this is shared for all dimensions)
    pulse_train_U2 = pulse_train_U2 + s12_state_shelvings
    fractions_U2 = fractions_U2 #+ s12_state_fractions
    fixed_phase_mask_U2 = fixed_phase_mask_U2 #+ s12_state_fixed_phases
    simulated_phase_mask_U2 = simulated_phase_mask_U2 #+ s12_state_simulated_phases

############################### Finished define the pulse sequence for a given dimension

    dimension = int(np.max(np.round(1/np.array(fractions_U1))))
    dimension_string = str(dimension)

    list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
    [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
    [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
    [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
    ]

    pulse_train = pulse_train_U1 + pulse_train_U2
    simulated_phase_mask = simulated_phase_mask_U1 + simulated_phase_mask_U2
    fixed_phase_mask = fixed_phase_mask_U1 + fixed_phase_mask_U2

    phase_shifts = zip(simulated_phase_mask,fixed_phase_mask)
    detunings = np.zeros(len(probe_trans))
    s12_level = initial_state[0][0]

    periodicity = 100 #us
    start_time = 0
    if full_phase_scan:
        # for full phase scans
        stop_time = 100
        start_time = 0
        time_step = 30*(1/dimension)
    else:
        # take just two points for a contrast measurement
        if dimension%2==0:
            time_step = (dimension)*100/(2*dimension)
            stop_time = 1+(dimension)*100/(2*dimension)
        else:
            time_step = (dimension+1)*100/(2*dimension)
            stop_time = 1+(dimension+1)*100/(2*dimension)

    F1PumpTime = 1.5 #us
    F1PumpReps = 60
    InitReps = 0
    fs = 2e9
    threshold = 10

    pulse_program = "Qudit_ramsey_experiment_bused_ket0_in_D52"


    def findPiTime_withfit_plotPD(ramsey_wait,stop_time,start_time, time_step, threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
        createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')
        
        if Measure_U1_only:
            U1_only_bool_list = [False, True]
        else:
            U1_only_bool_list = [False]
        
        pulse_time = start_time

        file_names_list_all = []

        fluor_ave = []
        pulse_time_list = []
        file_names_list = []
        fluor_ave_U1 = []
        pulse_time_list_U1 = []
        file_names_list_U1 = []
        while pulse_time <= stop_time:
            for U1_only in U1_only_bool_list:
                if U1_only:
                    fractions = fractions_U1 + list(np.zeros(np.size(fractions_U2)))
                    do_calibrations = False
                else:
                    fractions = fractions_U1 + fractions_U2
                    do_calibrations = do_calibrations_0

                if scriptIsStopped():
                    eng.quit()
                    break
        
                print('1')
                setEvaluation('Eval2')
                if pulse_time == 0:
                #if 1 == 1:
                    if do_calibrations:
                        delta = 0
                        ramsey_real_wait_time = 100
                        freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                        freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = True)
                setEvaluation('Eval3')
        
                f_offset = float(getGlobal('f_offset'))
                f_upper = float(getGlobal('f_upper'))
        
                pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
                pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
                pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
                pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
                pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]
        
        
                init_trans = list_of_inits[s12_level+2]
                init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
                init_times_array = list(Get_1762_PiTimes(init_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                init_pulse_time = sum(init_times_array) 
        
                set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        
                initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))
        
                pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))
        
                for idx, delta in enumerate(detunings):
                    set_freq[idx] = set_freq[idx] + delta
        
                for delta in detunings:
                    pulse_train_frequencies[0] = pulse_train_frequencies[0] + delta
        
                pi_time_initial_state = list(Get_1762_PiTimes(initial_state,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        
                pi_time_pulse_train = list(Get_1762_PiTimes(pulse_train,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        
                pi_times_probe_trans = list(Get_1762_PiTimes(probe_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
        
        
        
                print(pulse_train)
        
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
        
                SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
                if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
                    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")
        
                corrected_pulse_train_times = []
        
                for i,_ in enumerate(fixed_phase_mask):
                    if np.isnan(_):
                        corrected_pulse_train_times.append(ramsey_wait)
                    else:
                        frac = fractions[i]
                        corrected_pulse_train_times.append(2*pi_time_pulse_train[i]*np.arcsin(np.sqrt(frac))/np.pi)
        
                print(corrected_pulse_train_times)
        
                Ramsey_wait_time_dummy = getGlobal('Ramsey_Wait_Time')
                if not "%s"%Ramsey_wait_time_dummy == "%s us"%sum(corrected_pulse_train_times):
                    setGlobal("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us")
        
                half_pi_time_dummy = getGlobal('Shelving_Pulse_Time')
                if not "%s"%half_pi_time_dummy == "%s us"%sum(corrected_pulse_train_times):
                    setGlobal("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us")
                print('2')
        
        # Phase Calculations ===================================================================
        
                phases = []
                for i,_ in enumerate(fixed_phase_mask):
                    if np.isnan(_):
                        phases.append(0)
                    else:
                        pi_phase = fixed_phase_mask[i]
                        real_phase = simulated_phase_mask[i]
                        x = (2 * np.pi * pulse_time * real_phase / periodicity)
                        y = pi_phase*np.pi
                        print(i,x,y)
                        phases.append(x + y)
                    
                full_phases = phases
                print(full_phases)
        #=======================================================================================
        # AWG commands======================================================================================
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
        
                print('3')
        #---------------------------------------------------------------------------- S1/2 inits
                matlab_init_freqs = matlab.double(init_freqs_array)
                matlab_init_times = matlab.double(init_times_array)
        #---------------------------------------------------------------------------- D5/2 init pulse

                #initial_state_frequency = [0]
                #pi_time_initial_state = [21]

                print(initial_state_frequency)
                print(pi_time_initial_state)
                consolePrint(str(initial_state_frequency))
                consolePrint(str(pi_time_initial_state))
        
        
        
                matlab_initial_state_freq = matlab.double(initial_state_frequency)
                matlab_initial_state_pulse_time = matlab.double(pi_time_initial_state)
                matlab_initial_state_phases = matlab.double([0])
        #---------------------------------------------------------------------------------------------------------- pulse_train
                print(pulse_train_frequencies)
                print(corrected_pulse_train_times)
                matlab_pulse_train_freqs = matlab.double(pulse_train_frequencies)
                matlab_pulse_train_times = matlab.double(corrected_pulse_train_times)
                matlab_pulse_train_phases = matlab.double(full_phases)
        
                print(len(pulse_train_frequencies),len(corrected_pulse_train_times),len(full_phases))
        
                #for i in range(15):
                #    print(pulse_train_frequencies[i],corrected_pulse_train_times[i])
        
        #---------------------------------------------------------------------------- Uploading
    #=============================================Initialize a state=====================================================================================================
                
                power_factor = matlab.double([1])
                power_factor_dbm = matlab.double([1])
                print('4.5')
                seg_num = 1
                eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)  # S12 Initialization Pulses
                if scriptIsStopped():
                    eng.quit()
                    break
                
                seg_num = seg_num + 1 
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # dummy
                print('5')
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0) # Shelve to D52 
                
                seg_num = seg_num + 1 
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)  # dummy 

    #=========================================================================Herald here============================================================================================
                '''
                seg_num = seg_num + 1
                eng.Pulse_upload_with_phases(matlab_initial_state_freq,matlab_initial_state_pulse_time,matlab_initial_state_phases,fs,seg_num,nargout = 0) 
        
                if scriptIsStopped():
                    eng.quit()
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
                '''
                seg_num = seg_num + 1
        
                eng.Pulse_upload_with_phases(matlab_pulse_train_freqs,matlab_pulse_train_times,matlab_pulse_train_phases,fs,seg_num,nargout = 0)
                if scriptIsStopped():
                    eng.quit()
                    break
                seg_num = seg_num + 1
                eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
                print('6')
                # Readout pulses
                for idx, freq in enumerate(set_freq):
        
                    matlab_ro_freq = matlab.double([freq])
                    matlab_ro_time = matlab.double([pi_times_probe_trans[idx]])
                    print(seg_num,[freq],[pi_times_probe_trans[idx]])
                    seg_num = seg_num + 1
                    eng.Pulse_upload(matlab_ro_freq,matlab_ro_time,fs,seg_num,power_factor,nargout = 0)
                    if scriptIsStopped():
                        eng.quit()
                        break
                    seg_num = seg_num + 1
                    eng.Pulse_upload_dummy(fs,seg_num,nargout = 0) # Dummy 3rd sequence
        
        #-------------------------------------------------------------------------------------------------------------------------
                print('7')
        
                eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
                eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)

                seq_num = 6
        
                for idx, freq in enumerate(set_freq):
                    seq_num = seq_num + 1
                    string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,0"
                    eng.SendAWGCommand(string, nargout=0)
                    seq_num = seq_num + 1
                    string = f"SOUR:SEQ:DEF {seq_num}, {seq_num},1,1"
                    eng.SendAWGCommand(string, nargout=0)
        
                Table_length_dummy =  getGlobal('Table_length')
                if not "%s"%Table_length_dummy == seq_num:
                    setGlobal("Table_length", seq_num, "")
        
                eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)
        
                eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)
        
                eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
        
        
                #total_time = sum([piover2_time,pulse_time,piover2_time])+30
                #PulseTime_Dummy = getGlobal('Shelving_Pulse_Time').magnitude
                #if not "%s"%PulseTime_Dummy == "%s us"%total_time:
                #    setGlobal("Shelving_Pulse_Time", total_time, "us")
                #time.sleep(0.2)
        
                setScan(pulse_program)
                startScan(globalOverrides=list(), wait=True)
                stopScan()
        
                data = getAllData()
                herald_data = data['PMT Index 0'][1]
                print(herald_data)
                ket1_data = data['PMT Index 1'][1]
                print(ket1_data)
                ket2_data = data['PMT Index 2'][1]
                print(ket2_data)
        
                arrays = []
                for idx,herald_outcome in enumerate(herald_data):
                    if herald_outcome < threshold and ket1_data[idx] < threshold:
                        arrays.append(ket2_data[idx])
                mean_value = np.mean(np.array(arrays)<threshold)

#--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

                year = datetime.datetime.now().strftime("%Y")
                month = datetime.datetime.now().strftime("%m")
                day = datetime.datetime.now().strftime("%d")

                file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                destination_today = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan_*'
                soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan'

                def copy_file(src_file, dest_path):
                 
                    if not os.path.isfile(src_file):
                        print(f"Source file does not exist: {src_file}")
                        return
                 
                    dest_folder = os.path.dirname(dest_path)
                 
                    if not os.path.exists(dest_folder):
                        os.makedirs(dest_folder)
                        print(f"Created destination folder: {dest_folder}")
                 
                    shutil.copy2(src_file, dest_path)
                    print(f"File copied from {src_file} to {dest_path}")

                #if not file_names_list_all:
                matching_files = glob.glob(pattern)
                matching_files = sorted(matching_files, key=lambda t: os.stat(t).st_mtime)
                file_path = matching_files[-1]
                chunks = file_path.split('\\')
                print(chunks[:-1])        
                fname = chunks[-1]
                file_names_list_all.append(destination_today+fname)
                file_names_list.append(destination_today+fname)
                source_file = file_path_today + fname
                copied_file = destination_today + fname
                copy_file(source_file,copied_file)

                if np.isnan(mean_value):
                    mean_value = 1
                PD = mean_value
                print("PD is", PD)
                
                if U1_only:
                    fluor_ave_U1.append(PD)
                else:
                    fluor_ave.append(PD)
                
                if U1_only:
                    pulse_time_list_U1.append(pulse_time)
                else:
                    pulse_time_list.append(pulse_time)
                
                if not U1_only:
                    plotPoint(pulse_time, PD,'Qudit Ramsey, 0 state', plotStyle=2)
        
                freq_string = str(round(set_freq[0],3)).replace('.','p')
                if U1_only:
                    combined_data = zip(pulse_time_list_U1,fluor_ave_U1)
                else:
                    combined_data = zip(pulse_time_list,fluor_ave)
                
                # for bussed qudit Ramsey contrasts
                filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qudit_WaitTime{ramsey_wait}us_d={dimension_string}_Cal_{do_calibrations_0}_U1only_{U1_only}_{repeat_ind}_{dt_string}.txt'
                # for bussed qubit Ramsey measurements
                #filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_experiment_{pulse_train_U1[:-1]}_{wtr}_us_{num_repeat}_{dt_string}.txt'
                with open(filename,'w') as file:
                    for x,y in combined_data:
                        file.write(f"{x},{y}\n")
                    file.write(f"{pulse_train}\n")
                    file.write(f"{[f_offset,f_upper]}\n")
                    file.write(f"{pi_time_pulse_train}\n")
                    file.write(f"{corrected_pulse_train_times}\n")
                    file.write(f"{fractions_U1}\n")
                    file.write(f"{fractions_U2}\n")
                    file.write(f"{probe_trans}\n")
                    file.write(f"{phases}\n")
                    if U1_only:
                        file.write(f"{file_names_list_U1}\n")
                    else:
                        file.write(f"{file_names_list}\n")
            pulse_time = pulse_time + time_step
        closeTrace('Qudit Ramsey, 0 state')


    # looping over different wait times
    for repeat_ind in range(repeat_experiments):
        for wait_time in ramsey_wait_times:
            print('this worked')
            setEvaluation('Eval3')
            pi_time = findPiTime_withfit_plotPD(wait_time,stop_time,start_time, time_step, threshold, pulse_program, script_functions)
            print(pi_time)
            setEvaluation('Eval2')
            #with open(output_file_pitimes,'a') as outfile:
            #    outfile.write(f'{pi_time}\n')

eng.quit()