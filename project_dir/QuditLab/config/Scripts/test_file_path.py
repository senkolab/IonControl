#test_file_path.py created 2025-01-23 13:20:27.571280

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

year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")
file_path_today = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
destination_today = f'Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_copied\\{year}\\{year}_{month}\\{year}_{month}_{day}\\'
pattern = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan_*'
soruce_file_path = f'C:\\Users\\ions\\Documents\\IonControl\\project_dir\\QuditLab\\{year}\\{year}_{month}\\{year}_{month}_{day}\\qudit_ramsey_scan_'
file_names_list = ['Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_copied\\2025\\2025_01\\2025_01_23\\qudit_ramsey_scan_bused_126']
file_names_list_all = ['Z:\\Lab Data\\Qudit_Ramsey_raw_data\\Raw_data_copied\\2025\\2025_01\\2025_01_23\\qudit_ramsey_scan_bused_126']
U1_only = False

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



if not file_names_list_all:
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
else: 
    filename = file_names_list_all[-1]
    parts = filename.split('_')
    original_number_str = parts[-1]
    num_digits = len(original_number_str)
    number = int(original_number_str) + 1
    new_number_str = str(number).zfill(num_digits)
    new_filename = '_'.join(parts[:-1]) + f'_{new_number_str}'
    file_names_list_all.append(new_filename)
    if U1_only:
        file_names_list_U1.append(new_filename)
    else:
        file_names_list.append(new_filename)

print(file_names_list,file_names_list_all)