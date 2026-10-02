#B_compensation_set_DS345.py created 2023-08-02 12:38:46.630902
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_AWG import *


tval = np.linspace(0,1.0/60,600)
amps=[0.1034, -0.163]
freqs=[60,180]
phis=[-10.694, -1.124]

ds345_waveform_generator(tval,
                        scale=1.0,
                        phase_offset=0,
                        amps=np.array([1,1]),
                        freqs=np.array([60,180]),
                        phis=np.array([0,0]))