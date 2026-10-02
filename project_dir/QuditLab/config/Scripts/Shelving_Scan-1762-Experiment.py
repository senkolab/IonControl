#Scan_1762_Experiment.py created 2022-01-24 14:20:41.586830

import numpy as np
import gc

startfreq = 593 #593.66e6
endfreq = 597 #595e6
freqinterval = 0.01
freqstep = 0.01
Count_multiplier = int(freqinterval/freqstep)
AWG = True

FreqAWG = "AWG1_Frequency"

freq_array = np.arange(startfreq,endfreq,freqinterval)
freq_step_array = np.arange(startfreq,endfreq,freqstep)

#setScan("Shelving_PulseTime_Scan_Even")
setScan("Shelving_Pulse1ms_Even")
Count = Count_multiplier

createTrace('1762spectrum_data', 'Script Data', xLabel=f'Freq (MHz)')
for set_freq in freq_array:
    if AWG:
        setGlobal('AWGClockRef',int(1),'')
        setGlobal('AWGClockRef',int(0),'')
        #EOM_1762_freq = getGlobal("PDH_EOM_1762_Freq").magnitude
        #os.system('ssh pi@192.168.168.14 python setOffsetFrequency.py %s'%set_freq)
        #if not "%s"%EOM_1762_freq == "%s Hz"%set_freq:
        #    setGlobal("PDH_EOM_1762_Freq", set_freq, "Hz")
        EOM_1762_freq = getGlobal(FreqAWG).magnitude
        if not "%s"%EOM_1762_freq == "%s MHz"%set_freq:
            setGlobal(FreqAWG, np.round(set_freq,6), "MHz")
    else:
        EOM_1762_freq_glob = getGlobal("PDH_EOM_1762_Freq").magnitude
        if not "%s"%EOM_1762_freq_glob == "%s MHz"%set_freq:
            setGlobal("PDH_EOM_1762_Freq", np.round(set_freq, 6), "MHz")
        time.sleep(0.1)
    #if Count >= Count_multiplier:
    startScan(globalOverrides=list(), wait=True)
    gc.collect()
    #    Count = 0
    #Count = Count+1
    data = getAllData()['PMT Count'] #Returns all data associated with scan.
    ydata = data[1]
    ydataAvg = np.mean(np.array(ydata))
    ydataStD = np.std(np.array(ydata))
    plotPoint(set_freq, ydataAvg, '1762spectrum_data', plotStyle=0)
        
closeTrace('1762spectrum_data')
