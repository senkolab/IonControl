#B_compensation_reset_DS345.py created 2023-06-06 14:32:35.003790
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *

# To change the function generator's values, enter amplitude in volts followed by phase in degrees.

#fun=0 for sine wave, func=1 for square wave
#trigmode=4 by default, corres to AFG triggering by internal AC power line trigger, not an external trigger, trig_mode=2 is pos-in from external trigger
#ds345 = DS345_BCompensation_setOutput(amp=1.0, phase=0, freq=60.1, func=0, offset=0, trig_mode=4, brst_count=3)
#ds345 = DS345_BCompensation_setOutput(amp=0.35, phase=8, freq=180.1, func=0, offset=0, trig_mode=4, brst_count=3)

ds345 = DS345_BCompensation_setOutput(amp=0.0, phase=0.0, freq=0.001, func=0, offset=0, trig_mode=4, brst_count=100)
