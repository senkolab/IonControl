#Toggle_PMT-Camera_Test-Ion-Position.py created 2021-03-23 12:27:50.169682
import os
import sys
import glob
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *

num_exp = 1
toggle_program = "Toggle_PMT-Camera"
base_folder = r"Z:\Lab Data\Sessions"
filename0 = ""
filename0, base_folder = GetDataFilePath(base_folder, filename0, NewFile=False)

images_dirname = "Images"
filepath_images = makeRelativeDirectory(base_folder, images_dirname)

#filepath_images = r'Z:\Lab Data\Sessions'

print(filepath_images)

for i in range(num_exp):
    images_filename = f"Ion-Image_{i+50}.jpg"
    filepath_image = filepath_images + "\\" + images_filename
    filepath_image = filepath_image.replace(" ", "%20")
    print(filepath_image)
    acquireBlackflyFrame(filepath_image)
    #setScan(toggle_program)
    #startScan(globalOverrides=list(), wait=True)
    #stopScan()

