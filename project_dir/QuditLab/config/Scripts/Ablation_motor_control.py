#Ablation_motor_control.py created 2026-09-22 12:47:18.493320
import sys
sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from Functions_AblationMotorControl import move_to_location

actual_x, actual_y = move_to_location(
    7.1298, 6.082,
    x_serial="27255859",
    y_serial="27255860",
)