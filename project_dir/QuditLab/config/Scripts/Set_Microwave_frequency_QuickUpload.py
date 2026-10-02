#Set_Microwave_frequency_QuickUpload.py created 2026-08-13 11:28:38.636320
import sys

sys.path.append(r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab\config\Scripts')

from DSI_12000PRO_connet import set_DSI12000PRO


set_DSI12000PRO(8037.750392123456, -10, False)