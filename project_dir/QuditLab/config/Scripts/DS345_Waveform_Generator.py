#DS345_Waveform_Generator.py created 2023-07-26 16:03:12.611005

import pyvisa as visa
from struct import pack
from struct import unpack
import numpy as np

def line_signal(t,phi_list,A_list,freq_list,flag=0):
    scale =1/(sum(A_list))
    y1=A_list[0]*scale*np.sin(2*np.pi*t*(freq_list[0])+phi_list[0])
  
    ytot=y1
    for i in range(1,len(A_list)):
        y = A_list[i]*scale*np.sin(2*np.pi*t*freq_list[i]+phi_list[i])
        ytot+=y

    return ytot

def Waveform_Generate(data, trig_mode=4, brst_count=3):

    ADDRESS = "ASRL4::INSTR"
    __AMP__ = 2
    __OFFSET__ = 0
    __BURST_COUNT__ = brst_count
    __FREQ__ = 90
    __DATA__ =  data
    __PHASE__ = 0
    __TRIGMODE__ = trig_mode


    '''
    
    This First block of code 
    
    
    '''
    rm = visa.ResourceManager()#Shows all available instruments and their ports
    #rm.list_resources()
    ds345 = rm.open_resource(ADDRESS) #Use comport address as shown in 
    ds345.write("*CLS") # clears registers
    ds345.query("*IDN?") #Checks that the machine is connected
    print(ds345.query("*IDN?"))
    ds345.write("*SRE 16") # enables "message available bit"
    #ds345.write("FREQ " + str(__FREQ__)) # sets Frequency
    ds345.write("AMPL " + str(__AMP__) + "VP") # sets amplitude
    ds345.write("OFFS " +str(__OFFSET__))#Sets offset
    ds345.write("PHSE "+str(__PHASE__))#Sets Phase
    
    #     creates binary data to send to the generator, including the checksum
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
#

    # write_raw is needed rather than just write, since write will try
    # to treat input as python's unicode type, which may only take
    # 8 bit values

    ds345.write_raw(input)
    ds345.write_binary_values('',data,datatype='h')



    ds345.write("FUNC5\n") # sets to arbitrary waveform to produce output
    ds345.write("BCNT %i" % __BURST_COUNT__) # sets burst count
    ds345.write("FUNC 0") #Set function type
    ds345.write("TSRC " + str(__TRIGMODE__)) # sets trigger source to Negative input (triggers on negative crossing of trigger signal.)
    ds345.write("MTYP 5") # sets the type of modulation to burst modulation
    ds345.write("MENA 1") # enables modulation
    ds345.write("*TRG") # triggers burst'''
    return ds345
    
tval = np.linspace(0,1.0/60.1,600)
A_list = [0.05]
freq_list = [100]
phasevals = [np.pi/180*20]
data = line_signal(tval,phasevals,A_list,freq_list,flag=0)
data = (data*2046).astype(int)

Waveform_Generate(data)