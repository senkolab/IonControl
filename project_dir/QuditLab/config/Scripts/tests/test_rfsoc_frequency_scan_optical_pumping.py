"""Run RFSoC_FrequencyScan_OpticalPumping.py end to end against fake IonControl functions, a faked RFSoC HTTP server, and a synthetic ion.

The two Z:\\Lab Data\\D52_Calibration_Ba137 folders are redirected to a temp directory. The file formats checked here are the
ones the script wrote before the 2026-11-12 reliability fix, which other people's analysis may parse:
  summary file:         "freq,PD" per point, then the fit uncertainty as the last line
  each-experiment file: "freq,<numpy str() of the dark booleans>" per point, then the uncertainty
Since 2026-11-13 DC_check only warns (Collin: the resonant points it rejected were valid), so both files hold every point.
"""
import os
import re
import urllib.request

import numpy as np
import pytest
import scipy.optimize

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(SCRIPTS, "RFSoC_FrequencyScan_OpticalPumping.py")
SUMMARY_DIR = "Z:\\Lab Data\\D52_Calibration_Ba137\\Complete_Calibration_Raw_data\\"
EACH_DIR = "Z:\\Lab Data\\D52_Calibration_Ba137\\Calibration_experiments_raw_data_of_each_experiment\\"

# Synthetic ion (test inputs, not apparatus values)
CENTRE_MHZ = 610.0      # what the fake Get_1762_EOM_Freqs_an1an2 returns, and the true line centre
HWHM_MHZ = 0.006
P_DARK_PEAK = 0.45      # low enough that the script's DC_check (15 dark in a row) rarely fires by chance
SHOTS = 60
DARK_MEAN, BRIGHT_MEAN = 2.0, 30.0   # Poisson means; the script's threshold is 10


class FakeResponse:
    def read(self):
        return b'{"ok": true}'

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeLab:
    def __init__(self, seed=1, all_dark_points=(), stop_during_point=None, stop_before_point=None):
        self.rng = np.random.default_rng(seed)
        self.all_dark_points = set(all_dark_points)   # point indices that return only dark shots (DC_check rejects them)
        self.stop_during_point = stop_during_point    # Stop pressed while this point's scan runs
        self.stop_before_point = stop_before_point    # Stop pressed between points, after this many points
        self.globals = {"f_offset": 0.0, "f_upper": 0.0, "pitime_n2": 10.0, "pitime_n1": 10.0, "pitime_0": 10.0,
                        "pitime_p1": 10.0, "pitime_p2": 10.0, "Shelving_Pulse_Time": "40 us",
                        "OpticalPumpTimeGlobal": "1000 us", "RFSoC_Frequency": 0.0}
        self.stopped = False
        self.points = []   # (RFSoC_Frequency at scan time, counts) for every completed scan
        self.uploads = []
        self.n_started = 0

    def getGlobal(self, name):
        return self.globals[name]

    def setGlobal(self, name, value, unit):
        if not self.stopped:
            self.globals[name] = float(value) if unit == "MHz" else "%s %s" % (value, unit)

    def scriptIsStopped(self):
        return self.stopped

    def startScan(self, **k):
        if self.stopped:
            return None
        if self.n_started == self.stop_during_point:
            self.stopped = True       # the scan is cut short and every later IonControl call is a no-op
            self.n_started += 1
            return None
        f = self.globals["RFSoC_Frequency"]
        if self.n_started in self.all_dark_points:
            counts = self.rng.poisson(DARK_MEAN, SHOTS)
            counts[counts >= 10] = 0
        else:
            p = P_DARK_PEAK / (1 + ((f - CENTRE_MHZ) / HWHM_MHZ) ** 2)
            dark = self.rng.random(SHOTS) < p
            counts = np.where(dark, self.rng.poisson(DARK_MEAN, SHOTS), self.rng.poisson(BRIGHT_MEAN, SHOTS))
        self.last = (f, counts)
        self.n_started += 1

    def getAllData(self):
        if self.stopped:
            return None               # Script.py: a script function does nothing after Stop
        self.points.append(self.last)
        if len(self.points) == self.stop_before_point:
            self.stopped = True       # Stop pressed after this point's data was read, before the next point
        return {"PMT Count": (list(range(SHOTS)), list(self.last[1]))}


def dc_rejected(dark):
    run = 0
    for d in dark:
        run = run + 1 if d else 0
        if run >= 15:
            return True
    return False


def run_script(tmp_path, monkeypatch, lab, curve_fit_error=None):
    summary_dir = tmp_path / "summary"
    each_dir = tmp_path / "each"
    summary_dir.mkdir()
    each_dir.mkdir()
    src = open(SCRIPT).read()
    for a, b in ((SUMMARY_DIR, str(summary_dir) + os.sep), (EACH_DIR, str(each_dir) + os.sep)):
        assert src.count(a) == 1
        src = src.replace(a, b)

    fake_fd = type(os)("Functions_Data")
    fake_fd.Get_1762_EOM_Freqs_an1an2 = lambda want, f_offset, f_upper: [CENTRE_MHZ]
    monkeypatch.setitem(__import__("sys").modules, "Functions_Data", fake_fd)

    def urlopen(req, timeout=None):
        lab.uploads.append(req.data)
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    if curve_fit_error is not None:
        def failing_fit(*a, **k):
            raise curve_fit_error
        monkeypatch.setattr(scipy.optimize, "curve_fit", failing_fit)

    ns = dict(getGlobal=lab.getGlobal, setGlobal=lab.setGlobal, setScan=lambda name: None, startScan=lab.startScan,
              stopScan=lambda: None, getAllData=lab.getAllData, createTrace=lambda *a, **k: None,
              closeTrace=lambda *a, **k: None, plotPoint=lambda *a, **k: None, scriptIsStopped=lab.scriptIsStopped,
              setEvaluation=lambda name: None, __name__="__main__")
    error = None
    try:
        exec(compile(src, SCRIPT, "exec"), ns)
    except Exception as err:   # returned so each test states what it expects
        error = err
    summary = list(summary_dir.iterdir())
    each = list(each_dir.iterdir())
    return ns, error, summary, each


def read_summary(path):
    lines = path.read_text().split("\n")
    rows = [tuple(float(v) for v in line.split(",")) for line in lines[:-1]]
    return rows, float(lines[-1])


def read_each(path):
    text = path.read_text()
    rows = [(float(f), [t == "True" for t in body.split()])
            for f, body in re.findall(r"([0-9.eE+-]+),\[([^\]]*)\]", text)]
    return rows, float(text.rsplit("\n", 1)[-1])


def check_files_match(lab, summary_path, each_path):
    s_rows, s_unc = read_summary(summary_path)
    e_rows, e_unc = read_each(each_path)
    assert len(s_rows) == len(e_rows) == len(lab.points)   # every point, including long dark runs
    for (f, counts), (sf, pd), (ef, ebools) in zip(lab.points, s_rows, e_rows):
        dark = list(np.array(counts) < 10)
        assert sf == pytest.approx(f, abs=1e-9)
        assert ef == pytest.approx(f, abs=1e-9)   # each line's frequency is the one the RFSoC was set to for those shots
        assert ebools == dark
        assert pd == pytest.approx(np.mean(dark))
    return s_unc, e_unc


def test_normal_run_keeps_names_and_formats(tmp_path, monkeypatch):
    lab = FakeLab()
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab)
    assert error is None
    assert len(summary) == len(each) == 1
    freq_string = str(round(ns["freq_peak"], 4)).replace(".", "p")
    assert summary[0].name == "D52_calibration_raw_data_%s_%s.txt" % (freq_string, ns["dt_string"])
    assert each[0].name == "D52_calibration_each_exp_raw_data_%s_%s.txt" % (freq_string, ns["dt_string"])
    s_unc, e_unc = check_files_match(lab, summary[0], each[0])
    assert np.isfinite(s_unc) and s_unc == e_unc
    f, scanned = ns["freq_start"], []
    while f <= ns["freq_stop"]:   # the script's own stepping
        scanned.append(f)
        f = np.round(f + ns["freq_step"], 6)
    assert [p[0] for p in lab.points] == pytest.approx(scanned)
    assert ns["freq_peak"] == pytest.approx(CENTRE_MHZ, abs=0.003)


def test_long_dark_run_is_kept_and_warned(tmp_path, monkeypatch, capsys):
    lab = FakeLab(all_dark_points={3, 10})
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab)
    assert error is None
    check_files_match(lab, summary[0], each[0])   # points 3 and 10 are in both files, and later lines stay aligned
    out = capsys.readouterr().out
    warned = [line for line in out.splitlines() if line.startswith("DC_check:")]
    long_runs = [f for f, counts in lab.points if dc_rejected(np.array(counts) < 10)]
    assert len(warned) == len(long_runs) >= 2                  # one warning per point with 15+ dark shots in a row
    for i in (3, 10):
        assert any(str(lab.points[i][0]) in line for line in warned)


def test_stop_during_a_point_saves_points_already_taken(tmp_path, monkeypatch):
    lab = FakeLab(stop_during_point=20)
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab)
    assert error is None                      # before the fix: TypeError on getAllData() returning None, nothing saved
    assert len(lab.points) == 20
    check_files_match(lab, summary[0], each[0])


def test_stop_between_points_still_saves(tmp_path, monkeypatch):
    lab = FakeLab(stop_before_point=18)
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab)
    assert error is None
    assert len(lab.points) == 18
    check_files_match(lab, summary[0], each[0])


def test_failed_fit_saves_scan_as_nofit_then_raises(tmp_path, monkeypatch):
    lab = FakeLab()
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab, curve_fit_error=RuntimeError("Optimal parameters not found"))
    assert isinstance(error, RuntimeError)    # the script still stops on a failed fit, as before
    assert summary[0].name == "D52_calibration_raw_data_nofit_%s.txt" % ns["dt_string"]
    assert each[0].name == "D52_calibration_each_exp_raw_data_nofit_%s.txt" % ns["dt_string"]
    s_unc, e_unc = check_files_match(lab, summary[0], each[0])
    assert np.isnan(s_unc) and np.isnan(e_unc)
    assert lab.globals["RFSoC_Frequency"] == lab.points[-1][0]   # no fitted frequency was written back
    assert len(lab.uploads) == len(lab.points)                    # and no final upload


def test_stop_during_first_point_saves_empty_nofit_files_then_raises(tmp_path, monkeypatch):
    lab = FakeLab(stop_during_point=0)
    ns, error, summary, each = run_script(tmp_path, monkeypatch, lab)
    assert isinstance(error, ValueError)      # np.argmax of an empty list, as before
    assert summary[0].read_text() == "nan" and each[0].read_text() == "nan"
