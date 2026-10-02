#test.py created 2022-06-30 14:07:22.523655
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from TrapFunctions import *
from DataFunctions import *

BaseFolder = r"Z:\Lab Data\Sessions"
addname = "7o20x_6o11y"
filename0 = f"dadada.txt"
filename0, base_folder = GetDataFilePath(filename0, NewFile=False)

print(filename0)
print(base_folder)