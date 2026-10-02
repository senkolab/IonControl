#test.py created 2024-02-28 18:27:05.925131
import numpy as np
import os
import sys
import glob
import time
import gc

from datetime import date
import serial
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import * 

# 138
#Set8GHzSideband(5.92,0,"ON")
# 137
Set8GHzSideband(8.1,0,"ON")