#LoadTargteNumIons.py created 2020-02-19 18:07:50.097868

import numpy as np
from PIL import Image
import glob
import os

def find_peaks(in_array):
    import numpy as np
    in_array = in_array.astype(float)
    a = in_array[1:-1] - in_array[0:-2]
    b = in_array[1:-1] - in_array[2:]
    index = (a>=0) & (b>=0)
    index = np.append(np.insert(index,False,0),False)
    local_peaks = in_array[index]
    c = np.asarray(range(0,len(in_array)))
    peak_positions = c[index]
    return [peak_positions,local_peaks]

setScan("LoadTargetNIons")
Filepath = "Z:/Lab Data/IonImageFolder/"
TargetNIons = getGlobal("TargetNIons")
CycleLimit = 100
Count = 0
xmin = 110; xmax = 170; ymin = 90; ymax = 120
multiplier = 3
number_of_ions = 0
GUINumberofIons = getGlobal("NumberofIons")
GUILoadAttempts = getGlobal("LoadAttempts")

while number_of_ions < TargetNIons and Count < CycleLimit:
    if scriptIsStopped():
        break
    files = glob.glob(Filepath + "IonImage*.Bmp")
    InitFileLen = len(files)
    startScan(globalOverrides=list(), wait=False)
    files = glob.glob(Filepath + "IonImage*.Bmp")
    while len(files) <= InitFileLen:
        if scriptIsStopped():
            break
        time.sleep(0.2)
        files = glob.glob(Filepath + "IonImage*.Bmp")
    stopScan()
    files = glob.glob(Filepath + "IonImage*.Bmp")
    im = Image.open(files[-1])
    A = np.array(im)
    threshold = np.percentile(A,50) + multiplier*(np.percentile(A,95)-np.percentile(A,50))
    [max_y_ind,max_x_ind]=np.where(A == np.amax(A[ymin:ymax,xmin:xmax]))
    [peak_positions,local_peaks] = find_peaks(A[int(max_y_ind[0]),xmin:xmax])
    peak_positions_th = peak_positions[local_peaks > threshold]
    peak_positions_th = peak_positions_th.astype(float)
    if len(peak_positions_th) > 1:
        peak_positions_th_diff = peak_positions_th[1:]-peak_positions_th[0:-1]
        peak_positions_th_diff_end0 = np.append(peak_positions_th_diff,0)
        peak_positions_th_diff_start0 = np.append(0,peak_positions_th_diff)
        peak_positions_th[peak_positions_th_diff_end0 == 1] = peak_positions_th[peak_positions_th_diff_end0 == 1] + 0.5
        index = np.asarray(range(0,len(peak_positions_th)))
        peak_positions_th = np.delete(peak_positions_th,index[peak_positions_th_diff_start0 == 1])
    number_of_ions = len(peak_positions_th)
    if number_of_ions != GUINumberofIons:
        setGlobal("NumberofIons",number_of_ions,"")
        GUINumberofIons = getGlobal("NumberofIons")
    im.close()
    for h in range(0,len(files)-1):
        os.remove(files[h])
    Count += 1
    if Count != GUILoadAttempts:
        setGlobal("LoadAttempts",Count,"")
        GUILoadAttempts = getGlobal("LoadAttempts")