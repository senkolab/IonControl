#D52_25_level_SPAM.py created 2024-03-01 16:24:43.974455

import time
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools',nargout = 0)
eng.SendAWGCommand("RES", nargout=0)
time.sleep(2)

import sys
import os
import datetime
import glob
import numpy as np

from scipy.optimize import curve_fit
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Data import *
from Functions_AWG import *
from Functions_Calibration import *
from Functions_Measurement import *
script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation)

use_an1_an2 = True
run_calibrations = True
# wait time for calibration
ramsey_real_wait_time = 200
reverse_readout_order = False

D = 25
init_kets = list(range(0,25))

#init_kets = [17,18]
#init_kets = [8,9,10,11,12,15,16,17,20,22,8,9,10,11,12,15,16,17,20,22]
#init_kets = [0,13,15,16,21,24]
#init_kets = np.flip(init_kets)
init_kets = list(init_kets)
#init_kets = range(16,25)

SetPulseTime = 500
threshold = 7
# need to flip heralding pulse number when doing readout backwards
init_ket0_heralding_pulse = 2 #18 is 545 MHz, 2 is 620 MHz (fast and lower B sensitivity than 623)
F1PumpTime = 1.5 #us
F1PumpReps = 60
InitReps = 0
fs = 4e9
pulse_program = "D52_25level_Heralded_SPAM_pulses"

PulseTime = getGlobal("Shelving_Pulse_Time")
if not "%s"%PulseTime == "%s us"%SetPulseTime:
    setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

F1_pumpTime = getGlobal('F1_PumpTime')
if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
    setGlobal("F1_PumpTime", F1PumpTime, "us")

OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
if not "%s"%OptPumpTime == "%s us"%0:
    setGlobal("OpticalPumpTimeGlobal", 0, "us")

Init_reps = getGlobal('InitialisationReps')
if not "%s"%Init_reps == InitReps:
    setGlobal("InitialisationReps", InitReps, "")

F1Pump_reps = getGlobal('F1_PumpReps')
if not "%s"%F1Pump_reps == F1PumpReps:
    setGlobal("F1_PumpReps", F1PumpReps, "")

os.system(f'ssh pi@192.168.168.102 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 0')

dt_string = datetime.datetime.now().strftime("%Y%m%d_%H%M")
year = datetime.datetime.now().strftime("%Y")
month = datetime.datetime.now().strftime("%m")
day = datetime.datetime.now().strftime("%d")

#f_offset = 545.382523
#f_upper = 623.184223

#pitime_n2 = 24.938 # [-2, 4, -4]
#pitime_n1 = 41.95 # [-2, 3, -3]
#pitime_0 = 53.154 # [2, 4, 2]
#pitime_p1 = 41.394 # [2, 4, 3]
#pitime_p2 = 51.819 # [2, 4, 4]

list_of_inits = [[[-1,3,-2],[0,4,-2],[1,4,0],[2,4,2]],
[[-2,3,-1],[0,3,0],[1,4,0],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

# inits from "New_Shelving_Calibration_ParamEstimated_Initialised.py" script
list_of_inits = [[[-1,3,-2],[0,3,0],[1,4,0],[2,4,3]],
[[-2,3,-1],[0,3,0],[1,4,2],[2,4,3]],
[[-2,2,-1],[-1,3,0],[1,3,2],[2,4,2]],
[[-2,3,-1],[-1,3,0],[0,3,2],[2,4,3]],
[[-2,3,-1],[-1,3,0],[0,3,2],[1,3,3]]
]

'''
# original list
SPAM_list_trans = [[-2, 4, -4], #ket 1
                    [-1, 4, -3], #ket 2
                    [0, 4, -2], #ket 3
                    [0, 4, -1], #ket 4
                    [0, 4, 0], #ket 5
                    [0, 4, 1], #ket 6
                    [2, 4, 2], #ket 7
                    [2, 4, 3], #ket 8
                    [2, 4, 4], #ket 9
                    [-2, 3, -3], #ket 10
                    [-2, 3, -2], #ket 11
                    [-2, 3, -1], #ket 12       
                    [0, 3, 0], #ket 13
                    [0, 3, 1], #ket 14
                    [0, 3, 2], #ket 15
                    [1, 3, 3], #ket 16
                    [-2, 2, -2], #ket 17
                    [-2, 2, -1],#ket 18
                    [0, 2, 0], #ket 19                 
                    [2, 2, 1], #ket 20
                    [0, 2, 2], #ket 21
                    [-1, 1, -1], #ket 22
                    [-2, 1, 0], #ket 23
                    [1, 1, 1]] #ket 24

SPAM_list_trans = [[-2, 4, -4],
                    [-1, 4, -3],
                    [0, 4, -2],
                    [2, 4, 3], 
                    [-2, 3, -3],                 
                    [0, 3, 1],
                    [2, 4, 4], 
                    [2, 4, 2], 
                    [-2, 3, -2],
                    [1, 3, 3],
                    [0, 4, -1],
                    [0, 3, 0], 
                    [0, 3, 2], 
                    [-2, 3, -1],      
                    [0, 4, 0], 
                    [-2, 2, -1],
                    [-2, 2, -2], 
                    [2, 2, 1], 
                    [0, 2, 0], 
                    [0, 2, 2],
                    [0, 4, 1], 
                    [-1, 1, -1], 
                    [-2, 1, 0], 
                    [1, 1, 1]] 
                    '''

# list with ket 15 (problematic for off-res pumping) moved to front                    
SPAM_list_trans = [[0, 4, 0], # this was ket 15
                    [-2, 4, -4],
                    [-1, 4, -3],
                    [0, 4, -2],
                    [2, 4, 3], 
                    [-2, 3, -3],                 
                    [0, 3, 1],
                    [2, 4, 4], 
                    [2, 4, 2], 
                    [-2, 3, -2],
                    [1, 3, 3],
                    [0, 4, -1],
                    [-1, 3, 0], 
                    [0, 3, 2], 
                    [-2, 3, -1],      
                    [-2, 2, -1],
                    [-2, 2, -2], 
                    [2, 2, 1], 
                    [0, 2, 0], 
                    [0, 2, 2],
                    [0, 4, 1], 
                    [-1, 1, -1], 
                    [-2, 1, 0], 
                    [1, 1, 1]] 

##################################################################
# beginning of main function
##################################################################
def Set_AWG_for_SPAM(init_ket, pulse_program, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData, createTrace, closeTrace, plotPoint, scriptIsStopped, setEvaluation = script_functions
    #set_freq = start_freq
    #createTrace('1762 nm freq scan', 'Script Data', xLabel=f'Freq (MHz)')
    rep = 0
    number_of_reps = 1
    while rep < number_of_reps:
        if scriptIsStopped():
            eng.quit()
            break
        

        eng.SendAWGCommand("RES", nargout=0)
        time.sleep(10)
        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("INIT:CONT 0", nargout=0)
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)
        eng.SendAWGCommand("SOUR:FUNC:MODE USER",nargout = 0)

        eng.SendAWGCommand("ROSC:SOUR EXT", nargout=0)
        time.sleep(0.1)
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)

        eng.SendAWGCommand("TRAC:DEL:ALL",nargout = 0)
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL",nargout = 0)
        zero_freq = [0]

        if scriptIsStopped():
            eng.quit()
            break

        init_state = SPAM_list[init_ket][2]
        set_prep_freq = np.round(SPAM_list[init_ket][0],6)
        set_prep_pulse_time = np.round(SPAM_list[init_ket][1],3)
        
        print('init freqs array',init_freqs_array[int(init_state+2)])
        matlab_init_freqs = matlab.double(init_freqs_array[int(init_state+2)])
        matlab_init_times = matlab.double(init_times_array[int(init_state+2)])
                
        matlab_set_prep_freq = matlab.double([set_prep_freq])
        matlab_set_prep_pulse_time = matlab.double([set_prep_pulse_time])
    
        power_factor = matlab.double([1])
        power_factor_dbm = matlab.double([1])
        seg_num = 1

        eng.Pulse_upload(matlab_init_freqs,matlab_init_times,fs,seg_num,power_factor,nargout = 0)
        print(seg_num, init_state,init_freqs_array[int(init_state+2)], init_times_array[int(init_state+2)])

        seg_num = seg_num + 1

        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)
        if scriptIsStopped():
            eng.quit()
            break
#shelving
        seg_num = seg_num+1
        eng.Pulse_upload(matlab_set_prep_freq,matlab_set_prep_pulse_time,fs,seg_num,power_factor_dbm,nargout = 0)
        print(seg_num, set_prep_freq, set_prep_pulse_time)
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)
#de-shelving for ket 0
        seg_num = seg_num+1
        eng.Pulse_upload(matlab_set_prep_freq,matlab_set_prep_pulse_time,fs,seg_num,power_factor_dbm,nargout = 0)
        print(seg_num, set_prep_freq, set_prep_pulse_time)
        seg_num = seg_num + 1
        eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)

        if scriptIsStopped():
            eng.quit()
            break

        for i,ket in enumerate(SPAM_list):
            print('i and ket', i, ket)
            # don't do this if flipping readout order or doing 3ms deshelving time
            
            if ket[3][0]==0 and ket[3][1]==2 and ket[3][2]==2:
                probe_freq = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[i-1],[1,2,2]],f_offset,f_upper))
                pulse_time = list(Get_1762_PiTimes([SPAM_list_trans[i-1],[1,2,2]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                newket=[probe_freq,pulse_time,SPAM_list_trans[0][0]]

                set_probe_freq = np.round(newket[0],6)
                set_probe_time = np.round(newket[1],3)
                print('set probe freq with 2 deshelvings', set_probe_freq)
                seg_num = seg_num + 1
                matlab_set_probe_freq = matlab.double(list(set_probe_freq))
                matlab_probe_pulse_time = matlab.double(list(set_probe_time))

            elif ket[3][0]==0 and ket[3][1]==4 and ket[3][2]==1:
                probe_freq = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[i-1],[1,4,1]],f_offset,f_upper))
                pulse_time = list(Get_1762_PiTimes([SPAM_list_trans[i-1],[1,4,1]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                newket=[probe_freq,pulse_time,SPAM_list_trans[0][0]]

                set_probe_freq = np.round(newket[0],6)
                set_probe_time = np.round(newket[1],3)
                print('set probe freq with 2 deshelvings', set_probe_freq)
                seg_num = seg_num + 1
                matlab_set_probe_freq = matlab.double(list(set_probe_freq))
                matlab_probe_pulse_time = matlab.double(list(set_probe_time))

            elif ket[3][0]==-1 and ket[3][1]==1 and ket[3][2]==-1:
                probe_freq = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[i-1],[-2,1,-1]],f_offset,f_upper))
                pulse_time = list(Get_1762_PiTimes([SPAM_list_trans[i-1],[-2,1,-1]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                newket=[probe_freq,pulse_time,SPAM_list_trans[0][0]]

                set_probe_freq = np.round(newket[0],6)
                set_probe_time = np.round(newket[1],3)
                print('set probe freq with 2 deshelvings', set_probe_freq)
                seg_num = seg_num + 1
                matlab_set_probe_freq = matlab.double(list(set_probe_freq))
                matlab_probe_pulse_time = matlab.double(list(set_probe_time))
                
            elif ket[3][0]==-2 and ket[3][1]==1 and ket[3][2]==0:
                probe_freq = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[i-1],[2,1,0]],f_offset,f_upper))
                pulse_time = list(Get_1762_PiTimes([SPAM_list_trans[i-1],[2,1,0]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                newket=[probe_freq,pulse_time,SPAM_list_trans[0][0]]

                set_probe_freq = np.round(newket[0],6)
                set_probe_time = np.round(newket[1],3)
                print('set probe freq with 2 deshelvings', set_probe_freq)
                seg_num = seg_num + 1
                matlab_set_probe_freq = matlab.double(list(set_probe_freq))
                matlab_probe_pulse_time = matlab.double(list(set_probe_time))

            elif ket[3][0]==1 and ket[3][1]==1 and ket[3][2]==1:
                probe_freq = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[i-1],[-1,1,1]],f_offset,f_upper))
                pulse_time = list(Get_1762_PiTimes([SPAM_list_trans[i-1],[-1,1,1]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
                newket=[probe_freq,pulse_time,SPAM_list_trans[0][0]]

                set_probe_freq = np.round(newket[0],6)
                set_probe_time = np.round(newket[1],3)
                print('set probe freq with 2 deshelvings, should be final ket?', set_probe_freq)
                seg_num = seg_num + 1
                matlab_set_probe_freq = matlab.double(list(set_probe_freq))
                matlab_probe_pulse_time = matlab.double(list(set_probe_time))

            else:
                set_probe_freq = np.round(ket[0],6)
                set_probe_time = np.round(ket[1],3)
                seg_num = seg_num + 1
                #print(seg_num)
                if set_probe_time == 0:
                    power_factor_dbm = matlab.double([0])
                matlab_set_probe_freq = matlab.double([set_probe_freq])
                matlab_probe_pulse_time = matlab.double([set_probe_time])
            # indent all the above to re-implement multiple deshelving pulses

            #print('index of SPAM list', i)
            #print(ket)
            if scriptIsStopped():
                eng.quit()
                break
            

            eng.Pulse_upload(matlab_set_probe_freq,matlab_probe_pulse_time,fs,seg_num,power_factor_dbm,nargout = 0)
            print(seg_num, set_probe_freq, set_probe_time)
            power_factor_dbm = matlab.double([1])
            seg_num = seg_num + 1
            eng.Pulse_upload_dummy(fs,seg_num,nargout = 0)


        eng.SendAWGCommand("SOUR:SEQ:DEF 1,1,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 2,2,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 3,3,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 4,4,1,1", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 5,5,1,0", nargout=0)
        eng.SendAWGCommand("SOUR:SEQ:DEF 6,6,1,1", nargout=0)
        seg_num = 6
        
        table_length = len(SPAM_list) 
        for i in range(table_length):
            if scriptIsStopped():
                eng.quit()
                break
            seg_num = seg_num + 1
            string = f"SOUR:SEQ:DEF {seg_num},{seg_num},1,0"
            print(f'{seg_num},{seg_num},1,0')
            eng.SendAWGCommand(string, nargout=0)
            seg_num = seg_num + 1
            string = f"SOUR:SEQ:DEF {seg_num},{seg_num},1,1"
            print(f'{seg_num},{seg_num},1,1')
            eng.SendAWGCommand(string, nargout=0)
        print(seg_num)

        Table_length_dummy =  getGlobal('Table_length')
        if not "%s"%Table_length_dummy == seg_num:
            setGlobal("Table_length", seg_num, "")


        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ",nargout = 0)

        eng.SendAWGCommand("OUTP:COUP DC",nargout = 0)

        eng.SendAWGCommand("SOUR:VOLT:LEV:AMPL 1.5",nargout = 0)
                
        if scriptIsStopped():
            eng.quit()
            break

        setScan(pulse_program)
        startScan(globalOverrides=list(), wait=True)
        stopScan()
        data = getAllData()['PMT Count']
        ydata = data[1]

        rep = rep + 1
##################################################################
# end of main function
##################################################################

for idx, init_ket in enumerate(init_kets):
    #os.system(f'ssh pi@192.168.168.24 python press_hard_switch.py')
    #time.sleep(20)
    #os.system(f'ssh pi@192.168.168.24 python press_button.py')
    #time.sleep(180)

    if run_calibrations:
        delta = 0
        freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)

        #ramsey_real_wait_time = 200
        #freq_offset = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[0,2,0],f_offset_input=None,f_upper_input=None,ref_pitimes=None)
        #freq_upper = run_fast_calibration(script_functions,delta,ramsey_real_wait_time,target_transition=[-1,4,-3],f_offset_input=None,f_upper_input=None,ref_pitimes=None)

        print('newly calibrated offset and upper freqs', freq_offset, freq_upper)
    

    PulseTime = getGlobal("Shelving_Pulse_Time")
    if not "%s"%PulseTime == "%s us"%SetPulseTime:
        setGlobal("Shelving_Pulse_Time", SetPulseTime, "us")

    F1_pumpTime = getGlobal('F1_PumpTime')
    if not "%s"%F1_pumpTime == "%s us"%F1PumpTime:
        setGlobal("F1_PumpTime", F1PumpTime, "us")

    OptPumpTime = getGlobal('OpticalPumpTimeGlobal')
    if not "%s"%OptPumpTime == "%s us"%0:
        setGlobal("OpticalPumpTimeGlobal", 0, "us")

    Init_reps = getGlobal('InitialisationReps')
    if not "%s"%Init_reps == InitReps:
        setGlobal("InitialisationReps", InitReps, "")

    F1Pump_reps = getGlobal('F1_PumpReps')
    if not "%s"%F1Pump_reps == F1PumpReps:
        setGlobal("F1_PumpReps", F1PumpReps, "")

    f_offset = float(getGlobal('f_offset'))
    f_upper = float(getGlobal('f_upper'))

    pitime_n2 = float(getGlobal('pitime_n2')) # [-2, 4, -4]
    pitime_n1 = float(getGlobal('pitime_n1')) # [-2, 3, -3]
    pitime_0 = float(getGlobal('pitime_0')) # [2, 4, 2]
    pitime_p1 = float(getGlobal('pitime_p1')) # [2, 4, 3]
    pitime_p2 = float(getGlobal('pitime_p2')) # [2, 4, 4]


    init_freqs = []
    pulse_times = []
    #init_trans = [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 4, 2], [2, 4, 3], [1, 3, 2], [2, 4, 0], [1, 4, 0], [0, 3, 0], [-1, 3, -2]]
    for i in list_of_inits:
        init_freqs.append(list(Get_1762_EOM_Freqs_an1an2(i,f_offset,f_upper)))
        pulse_times.append(list(Get_1762_PiTimes(i,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)))

    probe_freq = list(Get_1762_EOM_Freqs_an1an2(SPAM_list_trans,f_offset,f_upper))
    pulse_time = list(Get_1762_PiTimes(SPAM_list_trans,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))
    #SPAM_list_trans = [[2, 4, -4]] + SPAM_list_trans
    combined_data = zip(probe_freq,pulse_time,SPAM_list_trans)
    pi_time = pulse_time[0]
    SPAM_list = []

    for i,j,k in combined_data:
        SPAM_list.append([i,j,k[0],k])
    print(SPAM_list)

    init_freqs_array = [
    init_freqs[0],
    init_freqs[1],
    init_freqs[2],
    init_freqs[3],
    init_freqs[4]
    ]

    init_times_array = [
    pulse_times[0],
    pulse_times[1],
    pulse_times[2],
    pulse_times[3],
    pulse_times[4]
    ]
    print(init_freqs_array,init_times_array)

    freq_ket0 = list(Get_1762_EOM_Freqs_an1an2([SPAM_list_trans[init_ket0_heralding_pulse]],f_offset,f_upper))[0]
    piTime_ket0 = list(Get_1762_PiTimes([SPAM_list_trans[init_ket0_heralding_pulse]],pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2))[0]
    init_ket0 =SPAM_list_trans[init_ket0_heralding_pulse][0]
    init_ket_tot =SPAM_list_trans[init_ket0_heralding_pulse]


    # we no longer want to sort this purely by pi-times
    #SPAM_list.sort(key=lambda x: float(x[1]), reverse=reverse_readout_order)
    SPAM_list = [[freq_ket0,piTime_ket0,init_ket0,init_ket_tot]] + SPAM_list
    #SPAM_list = [SPAM_list[0]] + [SPAM_list[-1]] + [SPAM_list[-2]] + SPAM_list[1:-2] 
    print('SPAM LIST IS',SPAM_list)
    #for i in [1]:
    #    break




    SPAM_list = SPAM_list[:D]

    filename = f'Z:\Lab Data\\25lvl_SPAM\\SPAM_frequencies_raw_data\SPAM_measurement_Order_{dt_string}.txt'
    if idx == 0:
        for i,ket in enumerate(SPAM_list):
            with open(filename,'a') as file:
                file.write(f"{ket[0]}, {ket[1]}, {ket[2]}\n")
    else:
        pass

    init_freqs = []
    pulse_times = []
    #init_trans = [[-2, 2, -1], [-1, 3, 0], [0, 3, 2], [1, 4, 2], [2, 4, 3], [1, 3, 2], [2, 4, 0], [1, 4, 0], [0, 3, 0], [-1, 3, -2]]
    for i in list_of_inits:
        init_freqs.append(list(Get_1762_EOM_Freqs_an1an2(i,f_offset,f_upper)))
        pulse_times.append(list(Get_1762_PiTimes(i,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2)))

    init_freqs_array = [
    init_freqs[0],
    init_freqs[1],
    init_freqs[2],
    init_freqs[3],
    init_freqs[4]
    ]

    init_times_array = [
    pulse_times[0],
    pulse_times[1],
    pulse_times[2],
    pulse_times[3],
    pulse_times[4]
    ]

    for i,ket in enumerate(SPAM_list):
        pulse_time = ket[1]
        str_ket = f'ket_{i}'
        PulseTime = getGlobal(str_ket)
        if not "%s"%PulseTime == pulse_time:
            setGlobal(str_ket, pulse_time, "us")

    print('ran')

    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 16 %s'%0)
    #os.system('ssh pi@192.168.168.103 python ~/pll-evalboard-synthesizer/src/Control-Programs/att1.py 13 %s'%0)
    
    if init_ket == 0:
        print(pi_time)
        Heralding_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Heralding_pulse_time_dummy == "%s us"%pi_time:
            setGlobal("Hareld_pulse_time", pi_time, "us")
    else:
        print("Post-Herald pulse time is 0")
        Heralding_pulse_time_dummy = getGlobal('Hareld_pulse_time')
        if not "%s"%Heralding_pulse_time_dummy == "%s us"%0:
            setGlobal("Hareld_pulse_time", 0, "us")

    Set_AWG_for_SPAM(init_ket, pulse_program, script_functions)
eng.quit()