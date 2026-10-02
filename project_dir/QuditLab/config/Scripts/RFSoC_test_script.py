#RFSoC_test_script.py created 2025-09-26 12:29:55.395467

import json
import numpy as np
import urllib.request
HOST = "pynq"
# HOST = "129.97.41.202"
PORT = 9009
URL  = f"http://{HOST}:{PORT}/upload_rows"
 
def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
 
micro_freq = 610.3922 #+ 20.764

rows = [
    [1, [micro_freq], [0], [10], [0], 0],
    #[1, [610.396464 + 20.772], [0], [10e6], [0], 0],
    #[1, [613.99914], [0], [10e6], [0], 0],
    #[2, [800], [0], [1], [0], 0]
]
resp = upload_rows(rows, time_unit="us")
print(json.dumps(resp, indent=2))