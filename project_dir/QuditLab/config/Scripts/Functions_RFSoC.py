#Functions_RFSoC.py created 2026-07-17 12:58:59.373064

#Raman_RFSoC_Quick_Upload.py created 2026-07-16 17:37:40.471307

import json
import urllib.request
import urllib.error




# RFSoC network address
RFSOC_IP = "192.168.168.43"
RFSOC_PORT = 9010

BASE_URL = f"http://{RFSOC_IP}:{RFSOC_PORT}"




def check_rfsoc_server(timeout=5):
    """Check whether the RFSoC server is reachable."""
    try:
        with urllib.request.urlopen(
            f"{BASE_URL}/health",
            timeout=timeout,
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        print("RFSoC server is reachable:")
        print(json.dumps(result, indent=2))

        return result

    except Exception as error:
        raise RuntimeError(
            f"Could not reach {BASE_URL}: {error}"
        ) from error


def upload_rows(
    rows,
    dac="DAC0",
    time_unit="us",
    timeout=30,
):
    """
    Upload a row table to DAC0 or DAC2.

    dac:
        "DAC0" or "DAC2"

    time_unit:
        "ns", "us", "ms", or "s"
    """
    dac = str(dac).upper()

    if dac not in {"DAC0", "DAC2"}:
        raise ValueError(
            "dac must be 'DAC0' or 'DAC2'."
        )

    if time_unit not in {"ns", "us", "ms", "s"}:
        raise ValueError(
            "time_unit must be 'ns', 'us', 'ms', or 's'."
        )

    payload = {
        "dac": dac,
        "rows": rows,
        "time_unit": time_unit,
    }

    request = urllib.request.Request(
        f"{BASE_URL}/upload_rows",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        response_text = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"RFSoC returned HTTP {error.code}: "
            f"{response_text}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to {BASE_URL}: "
            f"{error.reason}"
        ) from error

    return result


def upload_dac0(rows, time_unit="us"):
    return upload_rows(
        rows=rows,
        dac="DAC0",
        time_unit=time_unit,
    )


def upload_dac2(rows, time_unit="us"):
    return upload_rows(
        rows=rows,
        dac="DAC2",
        time_unit=time_unit,
    )

# Check the connection.
#check_rfsoc_server()

'''
tone_1 = 150
tone_2 = 150 

TABLE_DAC0 = [
    [0, False, [
        [0, [
            # f_MHz, phase_rad, amp, duration_us, phase_mode,
            # rep_rate_mode, enable, phase_latency_cycles, label
            [tone_1, 0.0, 1.0, 5e6,
             0, 0, True, 0, "DAC0 tone 0"],
        ]],
        #[1, [
        #    [tone_2, 0, 0.5, 5e6,
        #     0, 0, True, 0, "DAC0 tone 1, rep -1"],
        #]],
    ]],
]

TABLE_DAC0 = [    [0, False, []],]


response = upload_dac0(
    TABLE_DAC0,
    time_unit="us",
)

print(json.dumps(response, indent=2))
'''