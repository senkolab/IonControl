#Toggle_PMT-Camera_Test-Ion-Position.py created 2021-03-23 12:27:50.169682
import os
import sys
import glob
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *


base_folder = r"Z:\Lab Data\Sessions"
filename0 = ""
filename0, base_folder = GetDataFilePath(base_folder, filename0, NewFile=False)

stamp_it = time.strftime('%H%M%S', time.localtime())
setScan("Set_Camera")
startScan(globalOverrides=list(), wait=False)
time.sleep(5)
images_filename = f"Ion Image {stamp_it}.bmp"
filepath_image = base_folder + "\\" + images_filename
acquireBlackflyFrame(filepath_image)
time.sleep(5)
stopScan()

