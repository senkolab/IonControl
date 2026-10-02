#8GHz_Sideband_DSInstruments.py created 2024-11-17 09:23:54.869777

import numpy as np
import os
import sys
import glob
import time
import gc

from datetime import date
import serial
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')
from Functions_Trap import * 

# 138
#
Set8GHzSideband(5.82, -10,"ON")
#135
#Set8GHzSideband(7.79,0,"ON")
# 137
#Set8GHzSideband(8.101,-20,"ON")
'''

ser = serial.Serial(
port='COM6',        
baudrate=115200,     
bytesize=serial.EIGHTBITS,
stopbits=serial.STOPBITS_ONE,
parity=serial.PARITY_NONE)

ser.close()

with serial.Serial(
    port="COM6",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
   stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=1,
) as ser:

    def send_command(command):
        command+= '\n'
        ser.write(command.encode())
        time.sleep(0.1)
        response = ser.readline().decode().strip()
        return response

    send_command(f"POWER {att_db}")
    send_command(f"FREQ:CW {freq}GHz")
    send_command("OUTP:STAT "+status)
#if send_command("SYST:ERR?") == "0,No error":
#    consolePrint("DS Instrument configured for:", error=False, color = "Cyan")
#    consolePrint(f"Frequency = {freq}GHz", error=False, color = "DarkCyan")
#    consolePrint(f"Power = {att_db}db", error=False, color = "DarkCyan")
#    consolePrint("RF"+status, error=False, color = "DarkGreen")
#else:
#    err_msg = send_command("SYST:ERR?")
#    consolePrint("DS Instrument config Failed", error = True)
#    consolePrint(f"Error: {err_msg}", error = True)

ser.close()
'''