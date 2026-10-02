import os
import sys
import time

os.system('ssh pi@192.168.168.122 cd Documents; python press_stop_button.py')
time.sleep(4)
os.system('ssh pi@192.168.168.122 cd Documents; python press_start_button.py')