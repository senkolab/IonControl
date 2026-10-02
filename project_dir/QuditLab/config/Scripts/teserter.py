#teserter.py created 2026-02-04 16:22:02.607517
import os
os.system(f'ssh pi@192.168.168.105 "cd /home/pi/pll-evalboard-synthesizer/src/Control-Programs/Pi5/ && ./PowersN770"')
os.system(f'ssh pi@192.168.168.105 "cd /home/pi/pll-evalboard-synthesizer/src/Control-Programs/Pi5/ && ./FreqsN770"')

'''
import os

remote_user = "pi"
remote_host = "192.168.168.105"
script_path = "./local_script.sh"

# Command to pipe the local script to bash on the remote host
ssh_command = f"ssh {remote_user}@{remote_host} 'bash -s' < {script_path}"

# Execute the command using os.system()
print(f"Executing remote script on {remote_host}...")
exit_status = os.system(ssh_command)

if exit_status == 0:
    print("Script executed successfully.")
else:
    print(f"Script execution failed with exit status {exit_status}.")
'''