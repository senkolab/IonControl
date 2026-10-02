#fastcaltest.py created 2024-07-29 10:50:09.592377

import glob
pattern = "Z:\\Lab Data\\D52_Calibration_Ba137\\Fast_calibration_ion_control_raw_data\\fast_calibration*"
#pattern = "Z:\Lab Data\Qudit_Ramsey_raw_data\Raw_data\qudit_ramsey_scan_*"

print(glob.glob(pattern))