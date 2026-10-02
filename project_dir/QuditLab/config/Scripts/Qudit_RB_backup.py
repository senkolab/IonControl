#PolyQubit_BVA.py created 2025-03-24 17:41:40.347163

#D52_Qudit_heralded_Ramsey.py created 2024-09-26 15:04:20.886427

# First, the variables we will actually change ######################
import numpy as np
# single qubit with [0,2,0] transition - this defines the initial state as well

# d=2
#mappings = {0: '0', 1: '[2, 0]'}
#mappings = {0: '0', 1: '[2, 2]'}
#mappings = {0: '1', 1: '[1, -1]'}
mappings = {0: '0', 1: '[3, -1]'}
'''
# d=3
mappings = {0: '-2', 1: '[4, -4]', 2: '[3, -3]'}
# d=4
mappings = {0: '-2', 1: '[4, -4]', 2: '[3, -3]', 3: '[3, -2]'}
# d=5
mappings = {0: '-1', 1: '[4, -3]', 2: '[3, -1]', 3: '[3, -2]', 4: '[3, 0]'}
# d=6
mappings = {0: '1', 1: '[4, 0]', 2: '[4, -1]', 3: '[4, 1]', 4: '[4, 2]', 5: '[2, -1]'}
# d=7
mappings = {0: '1', 1: '[4, 0]', 2: '[4, -1]', 3: '[4, 1]', 4: '[4, 2]', 5: '[2, -1]', 6: '[3, 2]'}

# d=8
mappings = {0: '1', 1: '[4, 0]', 2: '[4, -1]', 3: '[4, 1]', 4: '[4, 2]', 5: '[2, -1]', 6: '[3, 2]', 7: '[3, 3]'}
'''

do_calibrations = True
LT_comp=False
#num_unitaries_list = np.linspace(1, 50, 10).astype(int)1,2,3,4,6,8,10,12,14,16,
num_unitaries_list = [20,26,34,50,65,85,120,150,195,240] #
#num_unitaries_list = [1,2] #
#num_unitaries_list = [20,26,34,50,65,85,120,150,195,240] #
num_unitary_sets = 10 # we do each num_unitaries above N times
pulse_program = "Qudit_heralded_RB"
#print(num_unitaries_list)

F1PumpTime = 0.5  #us
F1PumpReps = 20
InitReps = 0  # never changed
threshold = 12
#####################################################################
# Start of script.

import ast
import datetime
import glob
import json
import os
import shutil
import sys
import urllib.request

from scipy.optimize import curve_fit

sys.path.append(
    r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from Functions_Data import Get_1762_PiTimes, Get_1762_EOM_Freqs_an1an2
from Functions_Gates import build_transitions_list
from Functions_RFSoC_RamseyCalibration import run_fast_calibration
from Functions_RandomisedBenchmarking import (_concatenate_pulse_sequences,
                                              _decompose_inverse,
                                              generate_haar_unitary)
from Functions_LineSignalCompensation import *
from Functions_RFSoC_FastBussed_calibration import *

def _encode(obj):
    # If it's a matrix/array, encode as JSON-friendly
    if isinstance(obj, np.ndarray):
        if np.iscomplexobj(obj):
            data = [[[float(z.real), float(z.imag)] for z in row] for row in obj]
            return {"__ndarray__": True, "dtype": "complex", "data": data}
        else:
            data = [[float(x) for x in row] for row in obj]
            return {"__ndarray__": True, "dtype": "float", "data": data}

    # If it's a list/tuple, recurse
    if isinstance(obj, (list, tuple)):
        return [_encode(x) for x in obj]

    # Otherwise, try to store it directly (numbers, strings, etc.)
    return obj


def save_unitaries_json(path, unitaries):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_encode(unitaries), f)

'''
def _decode(obj):
    # If it's an encoded ndarray
    if isinstance(obj, dict) and obj.get("__ndarray__"):
        data = obj["data"]
        if obj["dtype"] == "complex":
            return np.array([[complex(z[0], z[1]) for z in row] for row in data], dtype=complex)
        return np.array(data, dtype=float)

    # If it's a list, recurse
    if isinstance(obj, list):
        return [_decode(x) for x in obj]

    return obj

def load_unitaries_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return _decode(json.load(f))
'''
dimension = len(mappings)
num_unitary = 1


# generate a new random sequence of unitaries
seq_unitaries = generate_haar_unitary(dimension, int(num_unitary),seed=42)
print(seq_unitaries)
print(dimension)
print(mappings)
print(len(mappings))
print(num_unitary)

(cat_couplings, cat_angles, cat_phases, cat_diag_phases,
 combined_unitary) = _concatenate_pulse_sequences(dimension, seq_unitaries)

inv_couplings, inv_angles, inv_phases, inv_diag_phases = _decompose_inverse(
    dimension, combined_unitary, cat_diag_phases)

set_couplings = inv_couplings + cat_couplings
angles = inv_angles + cat_angles
phases = inv_phases + cat_phases

print(angles)
print(phases)

# need to do some cleanup of angles and phases
angles = np.array(angles)
phases = np.array(phases)
mask = angles > 0  # Create a mask of negative angles
angles[mask] = -angles[mask]  # Flip signs where mask is True
phases[mask] += np.pi  # Add pi to phases where mask is True

# angles are already <=pi always, but phases are unconstrained, so for
# ease of checking take them mod 2pi
angles = -angles
phases = -phases % (2 * np.pi)
print(angles)
print(phases)



script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan,
                    getAllData, createTrace, closeTrace, plotPoint,
                    scriptIsStopped, setEvaluation)
dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
pattern = "Z:\Lab Data\Qudit_RB_raw_data\Raw_data\qudit_RB_scan_*"

# RFSoC configuration/connection
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL = f"http://{HOST}:{PORT}/upload_rows"

def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL,
                                 data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

list_of_inits = [[[-1, 3, -2], [0, 4, -2], [1, 4, 0], [2, 4, 2]],
                 [[-2, 3, -1], [0, 3, 0], [1, 4, 0], [2, 4, 3]],
                 [[-2, 2, -1], [-1, 3, 0], [1, 3, 2], [2, 4, 2]],
                 [[-2, 3, -1], [-1, 3, 0], [0, 3, 2], [2, 4, 3]],
                 [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 3, 3]]]

# defining the system parameters
dimension = len(mappings)
initial_state = [[int(mappings[0]),
    ast.literal_eval(mappings[1])[0],
    ast.literal_eval(mappings[1])[1]
]]
s12_level = initial_state[0][0]
probe_trans = initial_state  # only for qubits

F1_Pump_Time = getGlobal('F1_PumpTime')
if not "%s" % F1_Pump_Time == "%s us" % F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s" % Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s" % F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

def run_RB_measurement(num_unitary, threshold, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    createTrace('Qudit RB, 0 state', 'Scan Data', xLabel=f'Number of unitary gates in set')
        
    sets_num_counter = 0
    file_names_list_all = []
    file_names_list = []
    fluor_ave = []
    unique_sets_list = []
    
    all_couplings = []
    all_angles = []
    all_phases = []
    all_unitaries = []
    
    all_pulse_trains = []
    all_corrected_pulse_train_times = []
    
    while sets_num_counter < num_unitary_sets:
        
        if scriptIsStopped():
            break
        
        # generate a new random sequence of unitaries
        seq_unitaries = generate_haar_unitary(dimension, int(num_unitary))
        print(seq_unitaries)
        print(dimension)
        print(mappings)
        print(len(mappings))
        print(num_unitary)

        (cat_couplings, cat_angles, cat_phases, cat_diag_phases,
         combined_unitary) = _concatenate_pulse_sequences(dimension, seq_unitaries)

        inv_couplings, inv_angles, inv_phases, inv_diag_phases = _decompose_inverse(
            dimension, combined_unitary, cat_diag_phases)

        seq_unitaries.append(combined_unitary) # add combined unitary to what we save

        set_couplings = inv_couplings + cat_couplings
        set_angles = inv_angles + cat_angles
        set_phases = inv_phases + cat_phases
        print('RB angles and phases')
        print(set_angles)
        print(set_phases)
        # need to do some cleanup of angles and phases
        set_angles = np.array(set_angles)
        set_phases = np.array(set_phases)
        mask = set_angles > 0  # Create a mask of negative angles
        set_angles[mask] = -set_angles[mask]  # Flip signs where mask is True
        set_phases[mask] += np.pi  # Add pi to set_phases where mask is True

        # set_angles are already <=pi always, but set_phases are unconstrained, so for
        # ease of checking take them mod 2pi
        set_angles = -set_angles # set_angles in radians here
        set_phases = -set_phases % (2 * np.pi) # set_phases are already in radians here
        print('RB angles and phases - fixed')
        print(set_angles)
        print(set_phases)
        set_angles = list(set_angles)
        set_phases = list(set_phases)
        
        fractions = []
        # convert set_angles to fractions?
        for ang_idx, ang in enumerate(set_angles):
            fractions.append(np.sin(ang/2)**2)
        
        pulse_train = build_transitions_list(mappings, set_couplings)
        print(pulse_train)

        print('1')
        # setEvaluation('Eval2')

        if (do_calibrations and sets_num_counter%10==0):
            #delta = 0
            #ramsey_real_wait_time = 100
            freq_offset, freq_upper = Fast_Bussed_Calibration(script_functions)
            '''
            freq_offset = run_fast_calibration(script_functions,
                                               delta,
                                               ramsey_real_wait_time,
                                               target_transition=[0, 2, 0],
                                               f_offset_input=None,
                                               f_upper_input=None,
                                               ref_pitimes=None)
            freq_upper = run_fast_calibration(
                script_functions,
                delta,
                ramsey_real_wait_time,
                target_transition=[0, 4, -2],
                f_offset_input=None,
                f_upper_input=None,
                ref_pitimes=None)
        setEvaluation('Eval3')
        '''

        f_offset = float(getGlobal('f_offset'))
        f_upper = float(getGlobal('f_upper'))

        pitime_n2 = float(getGlobal('pitime_n2'))  # [0, 4, -2]
        pitime_n1 = float(getGlobal('pitime_n1'))  # [-2, 3, -3]
        pitime_0 = float(getGlobal('pitime_0'))  # [0, 2, 0]
        pitime_p1 = float(getGlobal('pitime_p1'))  # [2, 4, 3]
        pitime_p2 = float(getGlobal('pitime_p2'))  # [2, 4, 4]
        ref_pitimes = [pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2]
        
        # NBOP initialisation #########################################
        init_trans = list_of_inits[s12_level + 2]
        init_freqs_array = list(
            Get_1762_EOM_Freqs_an1an2(init_trans, f_offset, f_upper))
        init_times_array = list(
            Get_1762_PiTimes(init_trans, pitime_n2, pitime_n1, pitime_0,
                             pitime_p1, pitime_p2))
        init_pulse_time = sum(init_times_array)


        # heralding #########################################
        initial_state_frequency = list(
            Get_1762_EOM_Freqs_an1an2(initial_state, f_offset, f_upper))

        pi_time_initial_state = list(
            Get_1762_PiTimes(initial_state, pitime_n2, pitime_n1, pitime_0, pitime_p1, pitime_p2))


        # gates #########################################
        pulse_train_frequencies = list(
            Get_1762_EOM_Freqs_an1an2(pulse_train, f_offset, f_upper))
            
        if LT_comp:
            detuning_line = compute_detuning_from_line_fit(pulse_train, fractions, ref_pitimes)#, param_file = None)
            pulse_train_frequencies = list(np.array(pulse_train_frequencies) - np.array(detuning_line))

        pi_time_pulse_train = list(
            Get_1762_PiTimes(pulse_train, pitime_n2, pitime_n1, pitime_0, pitime_p1, pitime_p2))


        # readout pulses #########################################
        probe_freq_list = list(
            Get_1762_EOM_Freqs_an1an2(probe_trans, f_offset, f_upper))

        pi_times_probe_trans = list(
            Get_1762_PiTimes(probe_trans, pitime_n2, pitime_n1, pitime_0,
                             pitime_p1, pitime_p2))

        print(pulse_train)

        Init_PulseTime = getGlobal('Init_Shelving_Pulse_Time')
        if not "%s" % Init_PulseTime == init_pulse_time:
            setGlobal("Init_Shelving_Pulse_Time", init_pulse_time, "us")

        corrected_pulse_train_times = []

        for i, angle in enumerate(set_angles):
            corrected_pulse_time = pi_time_pulse_train[i] * angle/np.pi # convert angle in radians to pulse times
            corrected_pulse_train_times.append(corrected_pulse_time)
        print(corrected_pulse_train_times)

        AOM_ON_time = getGlobal('Shelving_Pulse_Time')
        if not "%s" % AOM_ON_time == "%s us" % sum(
                corrected_pulse_train_times):
            setGlobal("Shelving_Pulse_Time",
                      sum(corrected_pulse_train_times), "us")

        herald_pulse_on_time = getGlobal('Hareld_pulse_time')
        if not "%s" % herald_pulse_on_time == "%s us" % pi_time_initial_state[0]:
            setGlobal("Hareld_pulse_time", pi_time_initial_state[0], "us")

        print('2')

        # Phase Calculations ===================================================================

        if LT_comp:
            full_phases = list(np.array(set_phases) + np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))#, param_file = None)))
        #print(np.array(compute_phases_from_line_signal(pulse_train, fractions, pi_t = ref_pitimes)))
        else:
            full_phases = list(np.array(set_phases))
            
        print(full_phases)

#=======================================================================================

        # NBOP
        init_row1 = [1,init_freqs_array, [0]*len(init_freqs_array), init_times_array, [0]*len(init_freqs_array),0]
        dummy_row2 = [2, [800],[0], [0.01], [0], 0]

        # heralding
        herald_row3 = [3, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
        dummy_row4 = [4, [800],[0], [0.01], [0], 0]
        
        # HERALDING READOUT OCCURS HERE ############################
        
        # deshelve after herald
        deshelve_row5 = [3, initial_state_frequency, [0], pi_time_initial_state, [0], 1]
        dummy_row6 = [4, [800],[0], [0.01], [0], 0]

        # pulse train for RB
        pulse_train_row7 = [5, pulse_train_frequencies, full_phases, corrected_pulse_train_times, [1]*len(pulse_train_frequencies), 1]
        dummy_row8 = [6, [800],[0], [0.01], [0], 0]   
        
        rows = [
        init_row1, 
        dummy_row2, 
        herald_row3, 
        dummy_row4, 
        deshelve_row5, 
        dummy_row6,
        pulse_train_row7, 
        dummy_row8]
        
        row_number = 8
        # uploading the deshelving pulses for readout
        for idx, freq in enumerate(probe_freq_list):
            row_number = row_number + 1
            readout_row = [row_number, [freq], [0], [pi_times_probe_trans[idx]], [0], 1]  
            rows.append(readout_row)
            row_number = row_number + 1
            dummy_row = [row_number, [800],[0], [0.01], [0], 0]
            rows.append(dummy_row)
            print(row_number,[freq],[pi_times_probe_trans[idx]])
        
        Table_length_dummy =  getGlobal('Table_length')
        if not "%s"%Table_length_dummy == row_number:
            setGlobal("Table_length", row_number, "")

        resp = upload_rows(rows, time_unit="us")
        print(json.dumps(resp, indent=2))

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()

        data = getAllData()
        herald_data = data['PMT Index 0'][1]
        print(herald_data)
        
        # mostly we will be interested in the |0> population only
        ket1_data = data['PMT Index 1'][1]
        print(ket1_data)
        #ket2_data = data['PMT Index 2'][1]
        #print(ket2_data)

        arrays = []
        for idx,herald_outcome in enumerate(herald_data):
            if herald_outcome < threshold:
                arrays.append(ket1_data[idx])
        mean_value = np.mean(np.array(arrays)<threshold)

#--------------------------------------------------------Raw_data_file_saving-----------------------------------------------------------------------------------------------

        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        
        # TODO fix these names for correct file paths
        file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
        destination_today = f'Z:\\Lab Data\\Qudit_RB\\Raw_PMT_Counts\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
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
        unique_sets_list.append(num_unitary)
        plotPoint(num_unitary+(sets_num_counter/num_unitary_sets), PD,'Qudit RB, 0 state', plotStyle=2)
        combined_data = zip(unique_sets_list,fluor_ave)
        
        all_couplings.append(set_couplings)
        all_angles.append(set_angles)
        all_phases.append(set_phases)
        
        all_pulse_trains.append(pulse_train)
        all_corrected_pulse_train_times.append(corrected_pulse_train_times)
        
        all_unitaries.append(list(seq_unitaries))
        

        filename = f'Z:\\Lab Data\\Qudit_RB\\Raw_data_PD\\\RBExperiment_Dim{dimension}_Init{probe_trans[0]}_NumUnitaries{num_unitary}_LTComp_{LT_comp}_NumSets{num_unitary_sets}_{dt_string}.txt'
        '''
        with open(filename,'w') as file:
            for x,y in combined_data:
                file.write(f"{x},{y}\n")
            file.write(f"{pulse_train}\n")
            file.write(f"{[f_offset,f_upper]}\n")
            file.write(f"{pi_time_pulse_train}\n")
            file.write(f"{corrected_pulse_train_times}\n")
            file.write(f"{probe_trans}\n")
            file.write(f"{phases}\n")

            file.write(f"{file_names_list}\n")
        '''        
        sets_num_counter += 1
        # END OF WHILE LOOP OVER DIFFERENT UNITARY SETS
        
    with open(filename,'w') as file:
        for x,y in combined_data:
            file.write(f"{x},{y}\n")
        file.write(f"{pulse_train}\n")
        file.write(f"{[f_offset,f_upper]}\n")
        file.write(f"{ref_pitimes}\n")
        file.write(f"{probe_trans}\n")
        
        file.write(f"{all_pulse_trains}\n")
        file.write(f"{all_corrected_pulse_train_times}\n")
        
        file.write(f"{all_couplings}\n")
        file.write(f"{all_angles}\n")
        file.write(f"{all_phases}\n")
        
        file.write(f"{file_names_list}\n")

    unitaries_filename = f'Z:\\Lab Data\\Qudit_RB\\Generated_unitaries\\\RBExperiment_Dim{dimension}_Init{probe_trans[0]}_NumUnitaries{num_unitary}_LTComp_{LT_comp}_NumSets{num_unitary_sets}_{dt_string}.txt'
    #with open(unitaries_filename,'w') as file:
    #    file.write(f"{all_unitaries}\n")

    save_unitaries_json(unitaries_filename, all_unitaries)

    closeTrace('Qudit RB, 0 state')


for num_unitary in num_unitaries_list:

    print('this worked')
    setEvaluation('Eval3')
    run_RB_measurement(num_unitary, threshold, pulse_program, script_functions)
    setEvaluation('Eval2')






