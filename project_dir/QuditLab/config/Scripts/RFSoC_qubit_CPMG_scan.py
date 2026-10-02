#RFSoC_bussed_ramsey_detuning_calibration.py created 2026-01-30 13:37:44.434639

#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

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

script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"

def insert(x,p):
    return x[:int((len(x))/2)] + [p] +x[int((len(x))/2):]
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

Side_band_cooling_reps = 0

do_calibrations_0 = False
full_phase_scan = True
pts_for_full_phase_scan = 5


num_pi_pulses = 1

repeat_experiments = 1

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

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s"%F1_Pump_Time == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

LT_wait_dummy = getGlobal('LineTriggerWait_Global')
if not "%s"%LT_wait_dummy == 0:
    setGlobal("LineTriggerWait_Global", 0, "us")

SB_cooling_reps = getGlobal("Sideband_Cooling_Reps")
if not "%s"%SB_cooling_reps == Side_band_cooling_reps:
    setGlobal("Sideband_Cooling_Reps", Side_band_cooling_reps, "")
#1900, 1900, 3400, 1900, 2400, 25600, 10500,

list_of_pairs = [[[0, 3, -1], [0, 2, 0]]]
list_of_max_times = [4000]
list_of_step_size = [200]
LT_comp_flags_list = [False]
wait_start_index = [0]

def bussed_pi_pulse_sequence(qubit_trans, bus_trans, wtCPMG, num_pi_pulses):
    
    CPMG_pi_pulse_train = []
    CPMG_theta = []
    CPMG_phases = []
    pi_times_in_sequence = list(get_pi_times([[0,0,0], qubit_trans, bus_trans],[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

    wait_trans_piTime = pi_times_in_sequence[0]
    qubit_trans_piTime = pi_times_in_sequence[1]
    bus_trans_piTime = pi_times_in_sequence[2]

    total_pi_time = qubit_trans_piTime + 2*bus_trans_piTime

    CPMG_pi_pulse_train.append([0,0,0])
    CPMG_theta.append((wtCPMG - total_pi_time/2)/wait_trans_piTime)
    CPMG_phases.append(0)

    for i in range(num_pi_pulses):

        CPMG_pi_pulse_train.append(bus_trans)
        CPMG_pi_pulse_train.append(qubit_trans)
        CPMG_pi_pulse_train.append(bus_trans)
        CPMG_pi_pulse_train.append([0,0,0])


        CPMG_theta.append(1)
        CPMG_theta.append(1)
        CPMG_theta.append(1)
        CPMG_theta.append((wtCPMG - total_pi_time)/wait_trans_piTime)

        CPMG_phases.append(1)
        CPMG_phases.append(0)
        CPMG_phases.append(0)
        CPMG_phases.append(0)

    return CPMG_pi_pulse_train, CPMG_theta, CPMG_phases

for step_size, pair, max_time, LT_comp_flag, start_index_wtr in zip(list_of_step_size, list_of_pairs, list_of_max_times, LT_comp_flags_list, wait_start_index):
    LT_comp = LT_comp_flag
    dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    CPMG_freq = np.linspace(20,200,30)*1e-6
    waitTime_list = 1/(2*CPMG_freq)
    #waitTime_list = [0.1, 100, 1000, 3000, 5000, 7000, 9000]
    wait_trans_piTime = list(get_pi_times([[0,0,0]],[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))[0]
    
    
    print(wait_trans_piTime)

    for wtCPMG in waitTime_list[start_index_wtr:]:
        num_repeat = 0
        
        qubit_trans = pair[0]
        bus_trans = pair[1]

        initial_state = [qubit_trans]

        pulse_train_U1 = [qubit_trans, bus_trans]
        theta_U1 = [0.5, 1]
        fixed_phase_mask_U1 = [1, 0, 0]

        pulse_train_U2 = [bus_trans, qubit_trans]
        theta_U2 = [1, 0.5]
        fixed_phase_mask_U2 = [1, 0]

        probe_trans = [qubit_trans, bus_trans]

        dimension = len(probe_trans)

        CPMG_pi_pulse_train, CPMG_theta, CPMG_phase = bussed_pi_pulse_sequence(qubit_trans, bus_trans, wtCPMG, num_pi_pulses)

        pulse_train = pulse_train_U1 + CPMG_pi_pulse_train + pulse_train_U2
        rotation_angle_theta = theta_U1 + CPMG_theta + theta_U1
        phase_mask = fixed_phase_mask_U1 + CPMG_phase + fixed_phase_mask_U2

        phases = list(np.array(phase_mask)*np.pi)

        pi_time_initial_state = list(get_pi_times(initial_state,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

        pi_time_pulse_train = list(get_pi_times(pulse_train,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))

        pi_times_probe_trans = list(get_pi_times(probe_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
        print(pi_time_pulse_train)
        print(rotation_angle_theta)
        corrected_pulse_train_times = list(np.array(pi_time_pulse_train)*np.array(rotation_angle_theta))

    ############################### Finished define the pulse sequence for a given dimension

        list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
        [[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
        [[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
        [[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
        ]

        s12_level = initial_state[0][0]

        pulse_program = "Qudit_ramsey_experiment_bused_ket0_in_D52"

        def findPiTime_withfit_plotPD(wtCPMG, threshold, pulse_program, script_functions):
            getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
            createTrace('CPMG Scan, 0 state', 'Scan Data', xLabel=f'Freq (Hz)')
           

            file_names_list_all = []

            fluor_ave = []

            file_names_list = []

            file_names_list_U1 = []

            do_calibrations = do_calibrations_0

    
            print('1')
            #setEvaluation('Eval2')
            if wtCPMG:
                if do_calibrations:
                    delta = 0
                    #ramsey_real_wait_time = 400
                    #freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
                    #freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,4,-2],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = False)
                    #freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None, check_3pt_coherence = False)
                    freq_offset, freq_upper = Fast_Bussed_Calibration(script_functions)
            #setEvaluation('Eval3')
    
            f_offset = float(getGlobal('f_offset'))
            f_upper = float(getGlobal('f_upper'))
    
            init_trans = list_of_inits[s12_level+2]
            init_freqs_array = list(Get_1762_EOM_Freqs_an1an2(init_trans,f_offset,f_upper))
            init_times_array = list(get_pi_times(init_trans,[pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]))
            init_pulse_time = sum(init_times_array) 

            ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]

            set_freq = list(Get_1762_EOM_Freqs_an1an2(probe_trans,f_offset,f_upper))
    
            initial_state_frequency = list(Get_1762_EOM_Freqs_an1an2(initial_state,f_offset,f_upper))

            pulse_train_frequencies = list(Get_1762_EOM_Freqs_an1an2(pulse_train,f_offset,f_upper))
            
            if LT_comp:
                detuning_line = compute_detuning_from_line_fit(pulse_train, fractions, ref_pitimes)#, param_file = None)
                pulse_train_frequencies = list(np.array(pulse_train_frequencies) - np.array(detuning_line) + np.array([det_offset, 0, 0, 0, det_offset]))
            

    
            #pulse_train_frequencies = list(np.array(pulse_train_frequencies))
    
            print(pulse_train)

            set_global_value("Init_Shelving_Pulse_Time", init_pulse_time, "us", script_functions)

            print('2')
    
            set_global_value("Shelving_Pulse_Time", sum(corrected_pulse_train_times), "us", script_functions)
            set_global_value("Ramsey_Wait_Time", sum(corrected_pulse_train_times), "us", script_functions)

    # Phase Calculations ===================================================================
    
            if LT_comp:
                full_phases = list(np.array(phases) + np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))#, param_file = None)))
            #print(np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))
            else:
                full_phases = list(np.array(phases))
            print(full_phases)
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
            destination_today = f'Z:\\Lab Data\\Qubit_CPMG\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
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

           
            plotPoint((1/(2*wtCPMG))*1e6, PD,'CPMG Scan, 0 state', plotStyle=2)
            print()
            
            # for bussed qudit Ramsey contrasts
            #filename = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_PD\\\Ramsey_qudit_WaitTime{ramsey_wait}us_d={dimension_string}_Cal_{do_calibrations_0}_U1only_{U1_only}_{repeat_ind}_{dt_string}.txt'
            # for bussed qubit Ramsey measurements

            closeTrace('CPMG Scan, 0 state')
            filename = f'Z:\\Lab Data\\Qubit_CPMG\\Raw_data_copied\\CPMG_experiment_{pulse_train_U1}_{np.round(wtCPMG)}_us_LT_comp_{LT_comp}_{dt_string}.txt'
            with open(filename,'w') as file:

                file.write(f"{wtCPMG},{PD}\n")
                file.write(f"{[f_offset,f_upper]}\n")
                file.write(f"{ref_pitimes}\n")
                file.write(f"{pulse_train}\n")
                file.write(f"{pi_time_pulse_train}\n")
                file.write(f"{corrected_pulse_train_times}\n")
                file.write(f"{full_phases}\n")
                file.write(f"{probe_trans}\n")
                file.write(f"{file_names_list}\n")

        print('this worked')
        setEvaluation('Eval3')
        pi_time = findPiTime_withfit_plotPD(wtCPMG, threshold, pulse_program, script_functions)
        print(pi_time)
        setEvaluation('Eval2')


