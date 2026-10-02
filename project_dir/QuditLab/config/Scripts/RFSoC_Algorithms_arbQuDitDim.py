#RFSoC_Algorithms_arbQuDitDim.py created 2026-03-30 19:07:49.353541


import json
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"

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
from Functions_RFSoC_FastBussed_calibration import *
from Functions_Measurement import *
from Functions_LineSignalCompensation import *
from Functions_Algorithm import compile_algorithm_pulses

script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"
def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
Side_band_cooling_reps = 0


do_calibrations = False
Short_U1_flag = True
LT_comp = True


#8, 9, 10, 11, 12, 
#dimension_list = [8]#[7, 6, 5, 4, 3, 2]
dimension_list = [2]#[4,3,2]
#dimension_list = [13, 14, 15]
repeat_experiments = 1

for dim in dimension_list:

    algorithm_name = "BVA"
    dimension = dim
    hidden_values = range(dimension)

    #hidden_values = [0, 1, 8]#[5, 6, 7, 8, 9, 10]

    mappings = {
        0: '0',
        1: '[4, -2]',
        2: '[3, 1]',
        3: '[4, -1]',
        4: '[3, 0]',
        5: '[3, 2]',
        6: '[4, 0]',
        7: '[2, -2]',
        8: '[2, 0]',
        9: '[2, 2]',
        10: '[4, 1]',
        11: '[3, -1]',
        12: '[1, 1]',
        13: '[2, -1]',
        14: '[1, -1]',
        15: '[2, 1]',
    }
    trans_list = [[int(mappings[0])] + eval(mappings[i]) for i in range(1, 16)]
    probe_trans = trans_list[:dimension-1]
    if dim == 16:
        initial_state = [[0, 4, -2]]
    else:
        initial_state = [trans_list[dimension-1]]
    
    #initial_state = [[0,4,-2]]

    center = 0
    tol = 1e-10
    minimize_gamma = False
    initial_frame = None
    initial_state_index = 0

    for hidden_val in hidden_values:

        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))

        pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
        pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
        pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
        pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
        pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]


        list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
        [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
        [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
        ]
        algorithm_kwargs = {"hidden_value": hidden_val}
        pulse_train_list, pulse_angle_list, pulse_phases_list, compile_metadata = compile_algorithm_pulses(
            mappings,
            dimension,
            algorithm_name,
            center=center,
            tol=tol,
            minimize_gamma=False,
            initial_frame=initial_frame,
            return_metadata=True,
            use_short_U1=Short_U1_flag,
            **algorithm_kwargs,
        )

        pulse_train = pulse_train_list
        phase_shifts = pulse_phases_list
        angles = pulse_angle_list
        print(pulse_train)
        #phases_180Hz,_ = compute_phase_and_detuning_180Hz(pulse_train, angles, [pitime_n2, pitime_n1, pitime_0, pitime_p1, pitime_p2])
        #print(phases_180Hz)


        print(phase_shifts)


        s12_level = initial_state[0][0]

        F1PumpTime = 0.5 #us
        F1PumpReps = 20


        set_global_value("F1_PumpTime", F1PumpTime, "us", script_functions)

        set_global_value("F1_PumpReps", F1PumpReps, "", script_functions)



        threshold = 11

        pulse_program = "PolyQubit_BVA_pulse_program"
                
        def findPiTime_withfit_plotPD(threshold ,pulse_program, script_functions):
            getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions

            BVA_dummy = 0
            file_names_list_all = []
            file_names_list = []
            while BVA_dummy<1:
                BVA_dummy += 2

                if scriptIsStopped():
                    eng.quit()
                    break
        
                print('1')
                setEvaluation('Eval2')

                if do_calibrations:
                    delta = 0
                    #ramsey_real_wait_time = 200
                    #freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                    #freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,4,-2],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                
                    freq_offset, freq_upper = Fast_Bussed_Calibration(script_functions)

                setEvaluation('Eval3')
        
                f_offset = float(getGlobal('f_offset'))
                f_upper = float(getGlobal('f_upper'))
        
                pitime_n2 = float(getGlobal('pitime_n2')) # [0, 4, -2]
                pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
                pitime_0 = float(getGlobal('pitime_0')) # [0, 2, 0]
                pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
                pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]
        
                ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]
                init_trans = list_of_inits[s12_level+2]
                init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
                init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
                init_pulse_time = sum(init_times_array) 
        
                probe_freq_list = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
        
                initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))

                set_global_value("Init_Shelving_Pulse_Time", init_pulse_time, "us", script_functions)

                pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))

                fractions = []
                # convert set_angles to fractions?
                for ang_idx, ang in enumerate(angles):
                    fractions.append(np.sin(ang / 2)**2)
                print('Fractions = ', fractions)
                if LT_comp:
                    detuning_line = compute_detuning_from_line_fit(
                        pulse_train, fractions, ref_pitimes)  #, param_file = None)
                    pulse_train_frequencies = list(
                        np.array(pulse_train_frequencies) - np.array(detuning_line))
                print('Detunings: ', detuning_line)
                print('Freqs:', pulse_train_frequencies)
                pi_time_initial_state = list(get_pi_times(initial_state,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
                pi_time_pulse_train = list(get_pi_times(pulse_train,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
                pi_times_probe_trans = list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        
                print(pulse_train)
        
                corrected_pulse_train_times = []

                for i,angle in enumerate(angles):
                    corrected_pulse_time = pi_time_pulse_train[i]*angle/np.pi
                    corrected_pulse_train_times.append(corrected_pulse_time)
                print(corrected_pulse_train_times)
                corrected_pulse_train_times = list(corrected_pulse_train_times)
                set_global_value("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us", script_functions)
                print('2')
        
        # Phase Calculations ===================================================================

                set_phases = list(np.array(phase_shifts)) #------------------------------------------------------------

                if LT_comp:
                    full_phases = list(
                        np.array(set_phases) + np.array(
                            compute_phases_from_line_signal(
                                pulse_train, fractions,
                                pi_t=ref_pitimes)))  #, param_file = None)))
                #print(np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))
                else:
                    full_phases = list(np.array(set_phases))
                print('Phases_corr: ', np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes, t_ref="start")))
                print('Phases:', full_phases)
        #=======================================================================================
                #print(garbage)
                init_row1 = [1,init_freqs_array, [0]*len(init_freqs_array),init_times_array, [0]*len(init_freqs_array),0]
                dummy_row2 = [2, [800],[0], [0.1], [0], 0]
                
                herald_shelve_row3 = [3, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
                dummy_row4 = [4, [800],[0], [0.1], [0], 0]

                herald_deshelve_row5 = [5, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
                dummy_row6 = [6, [800],[0], [0.1], [0], 0]

                BVA_row7 = [7, pulse_train_frequencies, full_phases, corrected_pulse_train_times, [1]*len(pulse_train_frequencies), 1]
                
                print('BVA row = ', BVA_row7)

                dummy_row8 = [8, [800],[0], [0.1], [0], 0]   
                    
                rows = [init_row1, 
                        dummy_row2, 
                        herald_shelve_row3, 
                        dummy_row4, 
                        herald_deshelve_row5, 
                        dummy_row6, 
                        BVA_row7, 
                        dummy_row8]
                
                row_number = 8
      
                for idx, freq in enumerate(probe_freq_list):
                    row_number = row_number + 1
                    readout_row = [row_number, [freq], [0], [pi_times_probe_trans[idx]], [0], 1]  
                    rows.append(readout_row)
                    row_number = row_number + 1
                    dummy_row = [row_number, [800],[0], [0.1], [0], 0]
                    rows.append(dummy_row)
                    print(row_number,[freq],[pi_times_probe_trans[idx]])
        
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
                ket3_data = data['PMT Index 3'][1]
                print(ket3_data)
                ket4_data = data['PMT Index 4'][1]
                print(ket4_data)
                ket5_data = data['PMT Index 5'][1]
                print(ket5_data)
                arrays = []
                for idx,herald_outcome in enumerate(herald_data):
                    if herald_outcome < threshold:# and ket1_data[idx] < threshold:
                        if ket1_data[idx] > threshold or ket2_data[idx] > threshold or ket3_data[idx] > threshold or ket4_data[idx] > threshold or ket5_data[idx] > threshold: 
                            arrays.append([ket1_data[idx],ket2_data[idx],ket3_data[idx],ket4_data[idx],ket5_data[idx]])
                mean_value = np.mean(np.array(arrays)>threshold , axis = 0)
        
        #--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

                year = datetime.datetime.now().strftime("%Y")
                month = datetime.datetime.now().strftime("%m")
                day = datetime.datetime.now().strftime("%d")

                file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                destination_today = f'Z:\\Lab Data\\Algorithms\\QuDit_{algorithm_name}\\\IonControl_raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
                pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\BVA_2_polyqubit_*'
                soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\BVA_2_polyqubit'

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
                
                
                PD = mean_value
                print("PD is", PD)

                #filename = f'Z:\\Lab Data\\Algorithms\\Polyqubit_BVA\\RFSoC_BVA_logs\\BVA_{int(np.log2(sub_dim))}_polyqubit_LT_comp_{LT_comp}_hiddenstring_{hidden_string}_{dt_string}.txt'
                filename = f'Z:\\Lab Data\\Algorithms\\QuDit_{algorithm_name}\\BVA_logs\\BVA_{dimension}_quDit_LT_comp_{LT_comp}_hiddenval_{hidden_val}_{dt_string}.txt'
                
                with open(filename,'w') as file:

                    file.write(f"{PD}\n")
                    file.write(f"{pulse_train}\n")
                    file.write(f"{[f_offset,f_upper]}\n")
                    file.write(f"{ref_pitimes}")
                    file.write(f"{pi_time_pulse_train}\n")
                    file.write(f"{corrected_pulse_train_times}\n")
                    file.write(f"{probe_trans}\n")
                    file.write(f"{phase_shifts}\n")
                    file.write(f"{copied_file}")



        print('this worked')
        setEvaluation('Eval3')
        pi_time = findPiTime_withfit_plotPD(threshold, pulse_program, script_functions)
        print(pi_time)
        setEvaluation('Eval2')
