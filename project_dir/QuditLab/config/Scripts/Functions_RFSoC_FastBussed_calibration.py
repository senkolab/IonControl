import json
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
 
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
#from Functions_RFSoC_RamseyCalibration import *
from Functions_RFSoC_2ptRamseyCalibration_ms0 import *
from Functions_RFSoC_bussed_ramsey_detuning_fitter import *
from Functions_Measurement import *

#list_of_transitions = [[0, 4, 1], [0,3,-1]]*10
#list_of_ramsey_times = [2000, 2500]*10
#det_values = np.array([-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100])
def Fast_Bussed_Calibration(script_functions, qubit_transition = [0, 4, -2], bussed_waitTime = 800, direct_ramsey_calibration = True, direct_Ramsey_wait_time=250, update_ref_pitimes=False):

    #BOOK KEEPING ==============================================================================================================================
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    #script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    day = datetime.datetime.now().strftime("%d")
    pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"
    def insert(x,p):
        return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
    Side_band_cooling_reps = 0

    full_phase_scan = False

    f_offset = float(getGlobal('f_offset'))
    f_upper = float(getGlobal('f_upper'))

    pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
    pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
    pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
    pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
    pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]

    F1PumpTime = 0.5 #us
    F1PumpReps = 20
    InitReps = 0
    threshold = 10

    set_global_value("F1_PumpTime", F1PumpTime, "us", script_functions)

    set_global_value("InitialisationReps", InitReps, "", script_functions)

    set_global_value("F1_PumpReps", F1PumpReps, "", script_functions)

    set_global_value("LineTriggerWait_Global", 0, "us", script_functions)
    #END BOOK KEEPING=======================================================================================================================================================================

    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    pair = [qubit_transition, [0, 2, 0]]
    wtr = bussed_waitTime
    do_calibrations = direct_ramsey_calibration
    #f1_frequency_correction = 0
    transition_list = []
    transition_frequency_list = []
    detunings_list = []
    rough_freqs = []

    print('IN THE FOR LOOP')
    wait_trans_piTime = list(get_pi_times([[0,0,0]],[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))[0]

    print(wait_trans_piTime)
    #for wtr in waitTime_list:
    num_repeat = 0


    qubit_trans = pair[0]
    bus_trans = pair[1]

    initial_state = [qubit_trans]

    pulse_train_U1 = [qubit_trans, bus_trans, [0, 0, 0]]
    fractions_U1 = [0.5, 1,(np.sin((wtr/wait_trans_piTime)*(np.pi/2)))**2]
    simulated_phase_mask_U1 = [0, 0, 0]
    fixed_phase_mask_U1 = [1, 0, 0]

    pulse_train_U2 = [bus_trans, qubit_trans]
    fractions_U2 = [1, 0.5]
    simulated_phase_mask_U2 = [0, 1]
    fixed_phase_mask_U2 = [1, 0]

    s12_state_shelvings = []

    probe_trans = [qubit_trans, bus_trans]

    dimension = len(probe_trans)
    ############################### Just make sure s12 state is dealt with (this is shared for all dimensions)
    pulse_train_U2 = pulse_train_U2 + s12_state_shelvings
    fractions_U2 = fractions_U2 #+ s12_state_fractions
    fixed_phase_mask_U2 = fixed_phase_mask_U2 #+ s12_state_fixed_phases
    simulated_phase_mask_U2 = simulated_phase_mask_U2 #+ s12_state_simulated_phases

    ############################### Finished define the pulse sequence for a given dimension

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

    s12_level = initial_state[0][0]

    periodicity = 100 #us
    start_time = 0
    if full_phase_scan:
        # for full phase scans
        phases = np.linspace(0, 2, 11)
    else:
        phases = [0.5, 1, 1.5]

    pulse_program = "Qudit_ramsey_experiment_bused_ket0_in_D52"

    def bussed_ramsey_for_calibration(ramsey_wait, phases, threshold, pulse_program, script_functions):
        getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
        #createTrace('Qudit Ramsey, 0 state', 'Scan Data', xLabel=f'Pulse Time (us)')
       
        file_names_list_all = []

        fluor_ave = []
        phase_list = []
        file_names_list = []

        file_names_list_U1 = []
        phase_index = 0
        while phase_index <= len(phases)-1:

            fractions = fractions_U1 + fractions_U2
            print('not at scriptisstopped yet')
            if scriptIsStopped():

                break
            print('past scriptisstopped')

            #for waiter in [50]*10:
            #    freq_upper = run_fast_calibration(script_functions,0,waiter,target_transition=[0,4,-2],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = True)


            print('1')
            setEvaluation('Eval2')
            if phase_index == 0:
                if do_calibrations:
                    delta = 0
                    ramsey_real_wait_time = direct_Ramsey_wait_time
                    freq_offset = run_fast_calibration(script_functions,0,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                    freq_upper = run_fast_calibration(script_functions,0,ramsey_real_wait_time,target_transition=[0,4,-2],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = True, update_ref_pitimes=update_ref_pitimes)

            setEvaluation('Eval3')

            f_offset = float(getGlobal('f_offset'))
            f_upper = float(getGlobal('f_upper'))

            pitime_n2 = float(getGlobal('pitime_n2')) # [0, 4, -2]
            pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
            pitime_0 = float(getGlobal('pitime_0')) # [0, 2, 0]
            pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
            pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]


            init_trans = list_of_inits[s12_level+2]
            init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
            init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
            init_pulse_time = sum(init_times_array) 

            ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

            set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))

            initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))

            pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))
            
            pi_time_initial_state = list(get_pi_times(initial_state,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

            pi_time_pulse_train = list(get_pi_times(pulse_train,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

            pi_times_probe_trans = list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
            #if pair[0] != [0, 4, -2]:
            #if not do_calibrations:
            #    det = det_values[det_index]*1e-6
            #    pulse_train_frequencies = list(np.array(pulse_train_frequencies) - np.array([det, 0, 0, 0, det]))
            #else:
            pulse_train_frequencies = list(np.array(pulse_train_frequencies))

            print(pulse_train)

            set_global_value("Init_Shelving_Pulse_Time", init_pulse_time, "us", script_functions)

            corrected_pulse_train_times = []

            for i,_ in enumerate(fixed_phase_mask):
                if np.isnan(_):
                    corrected_pulse_train_times.append(ramsey_wait)
                else:
                    frac = fractions[i]
                    corrected_pulse_train_times.append(2*pi_time_pulse_train[i]*np.arcsin(np.sqrt(frac))/np.pi)

            print(corrected_pulse_train_times)


            

            set_global_value("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us", script_functions)

            set_global_value("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us", script_functions)
            print('2')

    # Phase Calculations ===================================================================

            phases_bussed_ramsey = []
            for i,_ in enumerate(fixed_phase_mask):
                if np.isnan(_):
                    phases_bussed_ramsey.append(0)
                else:
                    pi_phase = fixed_phase_mask[i]
                    real_phase = simulated_phase_mask[i]
                    x = (np.pi * phases[phase_index] * real_phase)
                    y = pi_phase*np.pi
                    print(i,x,y)
                    phases_bussed_ramsey.append(x + y)

            full_phases = list(np.array(phases_bussed_ramsey))
    #=======================================================================================


            init_row1 = [1,init_freqs_array, [0]*len(init_freqs_array),init_times_array, [0]*len(init_freqs_array),0]
            dummy_row2 = [2, [800],[0], [0.1], [0], 0]

            herald_row3 = [3, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
            dummy_row4 = [4, [800],[0], [0.1], [0], 0]
            
            ramsey_row5 = [5, pulse_train_frequencies, full_phases, corrected_pulse_train_times, [1]*len(pulse_train_frequencies), 1]
            dummy_row6 = [6, [800],[0], [0.1], [0], 0]   
            
            rows = [init_row1, dummy_row2, herald_row3, dummy_row4, ramsey_row5, dummy_row6]
            row_number = 6
            '''
            for idx, freq in enumerate(set_freq):
                row_number = row_number + 1
                readout_row = [row_number, [freq], [0], [pi_times_probe_trans[idx]], [0], 1]  
                rows.append(readout_row)
                row_number = row_number + 1
                dummy_row = [row_number, [800],[0], [0.1], [0], 0]
                rows.append(dummy_row)
                print(row_number,[freq],[pi_times_probe_trans[idx]])
            '''

            set_global_value("Table_length", row_number, "", script_functions)

            resp = upload_rows(rows, time_unit="us")
            print(json.dumps(resp, indent=2))


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
                if herald_outcome < threshold:
                    arrays.append(ket1_data[idx])
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

            fluor_ave.append(PD)
            

            phase_list.append(phases[phase_index])
            

            #plotPoint(phases[phase_index], PD,'Qudit Ramsey, 0 state', plotStyle=2)
            #print('point plotted')

            freq_string = str(round(set_freq[0],3)).replace('.','p')

            combined_data = zip(phase_list,fluor_ave)
            
            # for bussed qudit Ramsey contrasts
            #filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qudit_WaitTime{ramsey_wait}us_d={dimension_string}_Cal_{do_calibrations_0}_U1only_{U1_only}_{repeat_ind}_{dt_string}.txt'
            # for bussed qubit Ramsey measurements

            phase_index = phase_index + 1
            
        #closeTrace('Qudit Ramsey, 0 state')
        filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\RFSoC_bussed_ramsey_individual_scans\\\Ramsey_experiment_{pulse_train_U1[:-1]}_{np.round(wtr)}_us_{num_repeat}_{dt_string}.txt'
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
            file.write(f"{file_names_list}\n")

        return phase_list, fluor_ave, pulse_train_frequencies, f_offset, f_upper, ref_pitimes
        
    print('this worked')
    
    for _ in range(3):    
        setEvaluation('Eval2')
        phase_list, ket_data, pulse_train_frequencies, f_offset, f_upper, ref_pitimes = bussed_ramsey_for_calibration(wtr, phases, threshold, pulse_program, script_functions)
        setEvaluation('Eval3')
        
        detuning, err_detuning = fit_detuning_for_bussed_ramsey(ket_data,
                                 phase_list,
                                 pair,
                                 wtr,
                                 pi_time_refs = ref_pitimes,
                                 initial_delta_guess=-2 * np.pi * 0, consider_line = True)
                                 
        if detuning != None:
            break
            
    if detuning is None:
        raise Exception("Stopping script due to 1762 lock or ion issues.")

    rough_freqs.append(pulse_train_frequencies[0])
    fitted_frequency = pulse_train_frequencies[0] - detuning*(1e-6)/(2*np.pi)

    if pair[0] == [0, 4, -2]:
        #fitted_frequency = fitted_frequency + det_values[det_index]*1e-6
        set_global_value("f_upper", fitted_frequency, "", script_functions)

    detunings_list.append(detuning*(1e-6)/(2*np.pi))
    transition_frequency_list.append(fitted_frequency)
    

    f0_f1_fn_detunings = [0] + detunings_list
    f0_f1_fn_rough_freqs = [f_offset] + rough_freqs
    f0_f1_fn_freqs = [f_offset] + transition_frequency_list
    f0_f1_fn_triplets = [[0, 2, 0], pair[0]]
    filename = f'Z:\\Lab Data\\D52_Calibration_Ba137\\RFSoC_Fast_bussed_Ramsey_daily_calibrations\\\Ramsey_experiment_{pair[0]}_{np.round(wtr)}_us_{dt_string}.txt'
    with open(filename,'w') as file:
        file.write(f"{f0_f1_fn_freqs}\n")
        file.write(f"{f0_f1_fn_triplets}\n")
        file.write(f"{f0_f1_fn_rough_freqs}\n")
        file.write(f"{f0_f1_fn_detunings}\n")

    return f_offset, fitted_frequency
#if __name__ == "__main__":
#f_offset, f_upper = Fast_Bussed_Calibration()