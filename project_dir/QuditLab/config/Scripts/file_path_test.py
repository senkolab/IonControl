#file_path_test.py created 2023-10-16 12:32:10.553899
import datetime
dt_string = datetime.datetime.now().strftime("%d%m%Y_%H%M")
input_file = r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\2023\2023_10\2023_10_16\Calibration_files\calibration_input_F2P2.txt'
with open(input_file,'r'):
    pass
output_file = r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\2023\2023_10\2023_10_16\Calibration_files\Calibration_scan_peak_freqs_F2P2_%s.txt'%dt_string
with open(output_file,'w'):
    pass