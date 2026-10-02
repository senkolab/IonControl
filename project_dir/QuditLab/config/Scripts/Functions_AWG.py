#AWG_Functions.py created 2022-06-14 12:16:08.973843

# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 15:13:08 2022

@author: brendan
"""

import numpy as np
#import matplotlib.pyplot as plt
import math
import time
import pyvisa as visa
from struct import pack
from struct import unpack

#                                       EXAMPLE
#               Setup for sending waveform
#segment = 10
#amplitude_dBm = 10
#amplitude_W = 10**(amplitude_dBm/10)
    
#clock = 4.6e9
#num_points = 384
#freq = 30e6
#phase = 0

#               Create normalized waveform
#Waveform1 = Waveform(clock, freq, timeQ=True)

#               Setup connection to AWG and send the waveform
#AWG1 = AWG(connect=connect, address=awg_visa_address)
#AWG1.send_single_awseg(Waveform1, segment, amp_dBm=amplitude_dBm)

#Class for a connection to the AWG 81160A
class AWG:
    def __init__(self, connect=True, address='TCPIP0::192.168.168.124::5025::SOCKET'):
        self.connect = connect
        self.address = address
        self.chunk_size = 1e6
        #To establish a fake connection
        if not self.connect:
            self.rm = None
            self.awg = None
        else:
            self.rm = visa.ResourceManager()
            self.awg = self.rm.open_resource(self.address)
        self.commands()
    #Define many of the most commonly used VISA commands
    def commands(self):
        self.cmd_abort = ':ABORT'
        self.cmd_usermode = ':FUNC:MODE user'
        self.cmd_clockset = ':FREQ:RAST '
        self.cmd_coupling = ':OUTP:COUP '
        self.cmd_segdel = ':TRAC:DEL '
        self.cmd_segset = ':TRAC:DEF '
        self.cmd_segsel = ':TRAC:SEL '
        self.cmd_traceheader = ':TRAC:DATA #'
    #Switch mode between connect to AWG and false connection
    def change_connect(self):
        if self.connect:
            self.connect = False
            print('Removing connection to awg')
            self.rm = None
            self.awg = None
        else:
            self.connect = True
            print('Initiating connection to awg')
            self.rm = visa.ResourceManager()
            self.awg = self.rm.open_resource(self.address)
    #Send single ARBITRARY WAVEFORM (aw) segment to awg
    def send_single_awseg(self, Waveform, segment, amp_dBm=10):
        if self.connect:
            #Stop current operation, switch to aw mode, set clock, ac mode
            self.awg.write(f'{self.cmd_abort}')
            self.awg.write(f'{self.cmd_usermode}')
            self.awg.write(f'{self.cmd_clockset}{Waveform.clock:.12g}')
            self.awg.write(f'{self.cmd_coupling}AC')
            #Clear segment, define length, select segment
            self.awg.write(f'{self.cmd_segdel}{segment}')
            self.awg.write(f'{self.cmd_segset}{segment},{len(Waveform.data)}')
            self.awg.write(f'{self.cmd_segsel}{segment}')
        #Calc amplitude percentage
        amp_perc = self.amp_perc_calc(amp_dBm)
        #Convert normalized sine wave into correct power, bit-resolved waveform
        data_bits = np.round(2047*Waveform.data*amp_perc + 2048)
        #Change to 2 byte data type
        data_bits = np.array(data_bits, dtype="uint16")
        #Swap byte order
        data_bits.byteswap(inplace=True)
        num_bytes = str(len(data_bits)/8)
        self.data_bits = data_bits
        self.num_bytes = num_bytes
        if self.connect:
            t1 = time.time()
            #Write the waveform
            print(f'Sending arbitrary waveform ... \n')
            result = self.write_block(data_bits)
            print(f'result: {result}, Total time elapsed: {time.time()-t1}')
            #Check success of delivery to awg
            self.awg.write('')
            print(self.awg.query('*OPC?'))
    #Write the entire block of data to the waveform, a chunk at a time
    def write_block(self, data_bits):
        length_block = len(data_bits)
        header = f'{self.cmd_traceheader}{len(str(length_block*2))}{length_block*2}'
        #Case where data block is already shorter than the chunk size
        if length_block < self.chunk_size:
            chunk_size_temp = length_block
        else:
            chunk_size_temp = self.chunk_size
        #Send header to awg, to prepare for data
        self.awg.write(header)
        #Write data, a chunk at a time
        for i in np.arange(1, length_block, chunk_size_temp):
            if i + (chunk_size_temp - 1) < length_block:
                n = i + (chunk_size_temp - 1)
            else:
                #Last bit of data, partial chunk
                n = length_block
            print(f'i:{i}, n:{n}')
            chunk = np.array(data_bits[int(i):int(n)], dtype='uint16')
            #Send chunk to awg
            self.awg.write(f'{chunk}')
        return 1
    #Calculate the amplitude in percentage from dBm
    def amp_perc_calc(self, amp_dBm):
        amp_max_dBm = 10
        amp_min_dBm = -20
        pow_max = 10**(amp_max_dBm/10)
        pow_min = 10**(amp_min_dBm/10)
        amp_perc = amp_dBm/(pow_max-pow_min)
        return amp_perc

#Class for a train of waveforms chained together
class WaveformTrain:
    def __init__(self, clock):
        self.clock = clock
        self.waveforms = np.array([])
        self.wf_parts = np.array([])
        self.num_points = 0
        self.waveforms
        self.data = np.array([])
    #Add a simple cosine wave to the wavetrain. Can pick position. Defined based on number of data points
    def add_sine_points(self, num_points, freq, phase, position):
        if position not in self.wf_parts:
            wf = Waveform(self.clock, freq, timeQ=False, num_points=num_points, phase=phase)
            self.num_points += wf.num_points
            self.waveforms = np.append(self.waveforms, wf)
            self.wf_parts = np.append(self.wf_parts, position)
        else:
            return 'Waveform not added, position matches already assigned position'
    #Add a simple cosine wave to the wavetrain. Can pick position. Defined based on pulse time
    def add_sine_time(self, time, freq, phase, position):
        if position not in self.wf_parts:
            wf = Waveform(self.clock, freq, timeQ=True, time=time, phase=phase)
            self.num_points += wf.num_points
            self.waveforms = np.append(self.waveforms, wf)
            self.wf_parts = np.append(self.wf_parts, position)
        else:
            return 'Waveform not added, position matches already assigned position'
    #Put together all waveforms into a single waveform as a train
    def _gen_wf_data(self):
        #Sort the waveforms based on positions assigned
        waveforms_ordered = [x for _, x in sorted(zip(self.wf_parts, self.waveforms))]
        data = np.array([])
        for waveform in waveforms_ordered:
            data = np.append(data, waveform.data)
        return data
    #Give the total waveform train data points
    def wf_data(self):
        if len(self.data) == 0:
            data = self._gen_wf_data()
            self.data = data
        return self.data
    
    def __repr__(self):
        return f'Waveform train with clock {self.clock}, {len(self.waveforms)} parts, ' + \
    f'freqs {[x.freq for x in self.waveforms]}, {self.num_points} total points'
    def __str__(self):
        return f'Waveform train with clock {self.clock}, {len(self.waveforms)} parts, ' + \
    f'freqs {[x.freq for x in self.waveforms]}, {self.num_points} total points.\n' + \
    f'Ordered like {[x for x in self.wf_parts]}'
        
#Class containing a single cosine waveform
class Waveform:
    def __init__(self, clock, freq, timeQ=True, num_points=384, time=1e-6, phase=0):
        self.clock = clock
        self.num_points = num_points
        self.freq = freq
        self.time = time
        self.phase = phase
        self.timeQ = timeQ
        self._generate_sine_2()
    #Change the waveform parameter and update raw waveform based on this change
    def change_waveform(self, num_points, freq, phase):
        self.num_points = num_points
        self.freq = freq
        self.phase = phase
        self.num_points, self.data = self._generate_sine_2(self.num_points, self.freq, self.clock, self.phase)
    #Generate simple discretized sine wave data points
    def _generate_sine_1(self):
        self.cycles = self.freq*self.num_points/self.clock
        self.phase_deg = self.phase*math.pi/180
        #Setup discretized frequency
        self.freq_disc = 1/self.num_points*math.pi*2*self.cycles
        self.data = np.zeros(self.num_points)
        for i in range(self.num_points):
            self.data[i] = math.cos(self.freq_disc*(i-1)+self.phase_deg)
    #Generate simple discretized sine wave data points
    def _generate_sine_2(self):
        if not self.timeQ:
            if self.num_points < 384:
                self.num_points = 384
                print(f'Given number of points not enough, automatically set to minimum of 384 points')
            elif self.num_points%32 != 0:
                self.num_points = round(self.num_points/32)*32
                print(f'Given number of points not factor of 32, automatically rounded to nearest factor: {self.num_points}')
            num_points_init = self.num_points
            #Calculate the new number of points/cycles to end wave near integer cycle
            cycles_init = self.freq*num_points_init/self.clock
            cycles_goal = math.ceil(cycles_init) - 0.1
            num_points_inter = cycles_goal*self.clock/self.freq
            self.num_points = round(num_points_inter/32)*32
        else:
            num_points_raw = round(self.clock*self.time)
            if num_points_raw < 384:
                raise Exception(f'Given time too short for the clock cycle of {self.clock}, results ' + \
                      f'in just {round(num_points_raw)}<384 data points')
            time_init = self.time
            num_points_raw = round(self.clock*time_init)
            self.num_points = round(num_points_raw/32)*32
            time_actual = self.num_points/self.clock
            self.time = time_actual
        
        self.cycles = self.freq*self.num_points/self.clock
        self.phase_deg = self.phase*math.pi/180
        #Setup discretized frequency
        self.freq_disc = 1/self.num_points*math.pi*2*self.cycles
        if not self.timeQ:
            print(f'Cycles_init: {cycles_init}, -> Cycles: {self.cycles}')
            print(f'num_points_init: {num_points_init}, -> num_points: {self.num_points}')
        else:
            print(f'time: {time_init}, -> {self.time}')
            print(f'num_points: {self.num_points}')
        self.data = np.zeros(self.num_points)
        for i in range(self.num_points):
            self.data[i] = math.cos(self.freq_disc*(i-1)+self.phase_deg)
            
    def __repr__(self):
        return f'Waveform frequency {self.freq}'
    def __str__(self):
        return f'Waveform with clock rate: {self.clock}, time: {self.time}, points: ' + \
        f'{self.num_points}, frequency: {self.freq}, phase: {self.phase}'
            

#def plot_fourier(data, num_rep, clock, amp_W, plot_max = 1.5e9, noise_level=10**(-60/10), plot_rep=False):
#    num_points = data.size
#    num_big = num_points*num_rep
#    data_rep = np.tile(data, num_rep)
#    
#    if plot_rep:
#        plt.figure(figsize=(25, 10))
#        plt.plot(data_rep)


#    Y = np.fft.fft(data_rep)
#    freqs = np.fft.fftfreq(num_big, d=1/clock)

#    P2 = abs(Y/num_big)
#    P1 = P2[0:int(num_big/2)]
#    P1[1:-2] = 2*P1[1:-2]
#    P1_scale = sum(P1)/amp_W
#    P1 /= P1_scale
#    P1 += noise_level

#    P1_nonoise = P1[P1 > noise_level]
#    P1_max_arg = np.argmax(P1_nonoise)
#    P1_red, P1_max, P1_blue = P1_nonoise[P1_max_arg-1:P1_max_arg+2]
#    print(f'Peak: {P1_max} mW, Nearest red peak: {P1_red} mW, Nearest blue peak: {P1_blue} mW')
#    mean_ratio = np.mean([P1_max/P1_red, P1_max/P1_blue])
#    print(f'The ratio of first sidebands to peak is {mean_ratio}')

#    freqs = freqs[freqs >= 0]
#    freqs_plot = freqs[freqs < plot_max]
#    P1_plot = 10*np.log10(P1[freqs < plot_max])

#    plt.figure(figsize=(25, 7))
#    plt.plot(freqs_plot*1e-6, P1_plot)

def DS345_BCompensation_setOutput(amp=10,phase=0,freq=60.1,func=0,brst_count=3, trig_mode=4, offset=0):

    ADDRESS = "ASRL4::INSTR"
    __AMP__ = amp
    __OFFSET__ = offset
    __BURST_COUNT__ = 1
    __FREQ__ =freq
    #__DATA__ =  data
    __PHASE__ = phase
    __WAVEFORM__ = func
    __COUNT__ = brst_count
    __TRIGMODE__ = trig_mode


    '''
    
    This First block of code 
    
    
    '''
    rm = visa.ResourceManager()#Shows all available instruments and their ports
    #rm.list_resources()
    ds345 = rm.open_resource(ADDRESS) #Use comport address as shown in 
    ds345.write("*CLS") # clears registers
    ds345.query("*IDN?") #Checks that the machine is connected
    #print(ds345.query("*IDN?"))
    ds345.write("*SRE 16") # enables "message available bit"
    #Basic settings never change
    ds345.write("FUNC " + str(__WAVEFORM__)) #Set function type
    #Oft changed settings
    ds345.write("FREQ " + str(__FREQ__)) # sets Frequency
    ds345.write("AMPL " + str(__AMP__) + "VP") # sets amplitude
    ds345.write("OFFS " +str(__OFFSET__))#Sets offset
    ds345.write("PHSE "+str(__PHASE__))#Sets Phase
    #Setup trigger stuff
    ds345.write("BCNT %i" % __BURST_COUNT__) # sets burst count
    ds345.write("TSRC " + str(__TRIGMODE__)) # sets trigger source to Negative input (triggers on negative crossing of trigger signal.)
    ds345.write("MTYP 5") # sets the type of modulation to burst modulation
    ds345.write("MENA 1") # enables modulation
    ds345.write("*TRG") # triggers burst'''
    ds345.write("BCNT " + str(__COUNT__))
    return ds345

def line_signal(t,phi_list,A_list,freq_list,flag=0):
    scale =1/(sum(A_list))
    y1=A_list[0]*scale*np.sin(2*np.pi*t*(freq_list[0])+phi_list[0])
    #plt.plot(tval,10*y1,label="Fundamental")
  
    ytot=y1
    for i in range(1,len(A_list)):
        y = A_list[i]*scale*np.sin(2*np.pi*t*freq_list[i]+phi_list[i])
        ytot+=y
    if flag ==1:
        plt.title('Recreated Line Signal')
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage V")
        #plt.plot(tval,y2,label ="third harmonic")
        #plt.plot(tcc2,acc2,label ="real signal")
        #plt.plot(tcc2real,acc2,label ="Line signal")
        #print(max(10*ytot))
        plt.plot(tval,10*ytot,label="Recreated")
        plt.xlim(0)
        plt.legend(loc="best")
        plt.show()
    #val = sum(abs(acc2-10*ytot))
    return ytot

def ds345_waveform_generator(tval,
                            scale=1.0,
                            phase_offset=0,
                            amps=np.array([1,1]),
                            freqs=np.array([60,180]),
                            phis=np.array([0,0])):

    ADDRESS = "ASRL4::INSTR"
#    __AMP__ = 2
#    __OFFSET__ = 0
    __BURST_COUNT__ = 3

    __PHASE__ = 0

    # Connect to DS345
    rm = visa.ResourceManager()#Shows all available instruments and their ports
    ds345 = rm.open_resource(ADDRESS) #Use comport address as shown in 
    ds345.write("*CLS") # clears registers
    ds345.query("*IDN?") #Checks that the machine is connected
    ds345.write("FUNC5\n") # sets to arbitrary waveform to produce output
    ds345.write("*SRE 16") # enables "message available bit"
#    ds345.write("AMPL " + str(__AMP__) + "VP") # sets amplitude
#    ds345.write("OFFS " +str(__OFFSET__))#Sets offset
#    ds345.write("PHSE "+str(__PHASE__))#Sets Phase
    ds345.write("BCNT %i" % __BURST_COUNT__) # sets burst count
#    ds345.write("FUNC 0") #Set function type
    ds345.write("TSRC 4") # sets trigger source line input
    ds345.write("MTYP 5") # sets the type of modulation to burst modulation
    ds345.write("MENA 1") # enables modulation
#    ds345.write("*TRG") # triggers burst'''

    # Create the waveform
    y1=amps[0]*scale*np.sin(2*np.pi*tval*freqs[0]+phis[0]+phase_offset)
    ytot=y1
    for i in range(1,len(amps)):
        y = amps[i]*scale*np.sin(2*np.pi*tval*freqs[i]+phis[i]+phase_offset)
        ytot+=y

    __DATA__ = ytot

    #  creates binary data to send to the generator, including the checksum
    chksum = 0
    input = pack('h', 0)
    for i in range (1, len(__DATA__)):
        input += pack('h', __DATA__[i])
        chksum += __DATA__[i]
    input += pack('h', chksum)
    chksum=pack('h',chksum)
    ok = ds345.query("LDWF? 0,%i" % (len(__DATA__))) # tells machine that 'len(__DATA__) ' vector vertices will be sent
    if str.rstrip(str(ok)) != "1": # quit if there's an error loading the waveform
        print (f"NOT Ready to send waveform: ok= {ok}")
        quit()
    else :
        print ("Ready to send waveform")


    # write_raw is needed rather than just write, since write will try
    # to treat input as python's unicode type, which may only take
    # 8 bit values

    ds345.write_raw(input)
    ds345.write_binary_values('',data,datatype='h')


    return ds345
