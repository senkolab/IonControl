#turn_off_awg.py created 2026-02-27 15:34:48.652439

import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG_Upload import initialize_awg

initialize_awg(amplitude=1)
