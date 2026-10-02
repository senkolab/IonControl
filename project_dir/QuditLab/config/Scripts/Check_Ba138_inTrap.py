#Check_Ba138_inTrap.py created 2025-10-02 09:45:00.002629

import numpy as np
import os
import sys
import glob
import time
import gc

from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import *
from Functions_Data import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

Ba138_Present = Check_Ba138_Present(5.82, 4, script_functions)

if Ba138_Present:
    print("\n\nOne or more Barium-138 ions are present.\n")
else:
    print("\n\nNo Barium-138 ions.\n")
