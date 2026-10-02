#DSI_12000PRO_connet.py created 2026-08-13 11:05:33.573825

import socket
import numpy as np

DSI_IP = "192.168.168.40"   # Change to your SG12000PRO IP
DSI_PORT = 10001


def set_DSI12000PRO(freq_MHz, power_dBm, output=True):
    """
    Set frequency, power, and RF output state of the SG12000PRO.

    Example:
        set_DSI12000PRO(8037.75032, -10, True)
        set_DSI12000PRO(8037.75032, -10, False)
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)

    try:
        sock.connect((DSI_IP, DSI_PORT))

        sock.sendall(f"FREQ:CW {np.round(freq_MHz,6)}MHZ\r\n".encode("ascii"))
        sock.sendall(f"POWER {power_dBm}\r\n".encode("ascii"))

        if isinstance(output, str):
            output = output.upper() == "ON"

        if output:
            sock.sendall(b"OUTP:STAT ON\r\n")
        else:
            sock.sendall(b"OUTP:STAT OFF\r\n")

    finally:
        sock.close()
