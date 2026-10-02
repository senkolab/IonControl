import json
import numpy as np
import urllib.request

HOST = "pynq"
PORT = 9009
URL = f"http://{HOST}:{PORT}/upload_rows"

def upload_rows(rows, time_unit="us"):
    payload = {"rows": rows, "time_unit": time_unit}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

rows = [
    [1, [500, 800, 500], [0, 0, float(np.pi)], [0.02]*3, [1]*3, 0]
]

resp = upload_rows(rows, time_unit="us")
print(json.dumps(resp, indent=2))
