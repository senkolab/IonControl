"""Run Measure_Laser_Powers.py against a simulated lab: fake IonControl functions and real PM16 drivers on fake VISA resources.

Needs the sibling thorlabs_opm_controller checkout (src + tests/conftest.py for FakeResource); skipped without it.
"""
import importlib.util
import os
import sys
import types

import pytest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(SCRIPTS, "Measure_Laser_Powers.py")
OPM = os.path.abspath(os.path.join(SCRIPTS, *[".."] * 5, "..", "thorlabs_opm_controller"))
if not os.path.isdir(OPM):
    OPM = "/Users/collineps/Projects/thorlabs_opm_controller"
if not os.path.isdir(OPM):
    pytest.skip("thorlabs_opm_controller checkout not found", allow_module_level=True)
sys.path.insert(0, os.path.join(OPM, "src"))
_spec = importlib.util.spec_from_file_location("opm_conftest", os.path.join(OPM, "tests", "conftest.py"))
opm_conftest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(opm_conftest)

from thorlabs_opm_controller.controller import PM16
from thorlabs_opm_controller.errors import OpmError

POWER_UW = {"Keep_493_on_only": 55.0, "Keep_554_on_only": 10.0, "Keep_650_on_only": 255.0,
            "Keep_405_on_only": 1700.0, "Keep_614_on_only": 9.0}
METER_OF = {"Keep_493_on_only": "CRM", "Keep_554_on_only": "CRM", "Keep_650_on_only": "CRM",
            "Keep_405_on_only": "UV", "Keep_614_on_only": "UV"}
DARK_UW = 0.02
DEFAULT_ON = ("Keep_493_on_only", "Keep_650_on_only", "Keep_614_on_only")   # apparatus default after stopScan
READS_BEFORE_END_CHECK = 24   # wait_stable (4 reads) + the 20-sample average; the next read is the end-of-reading check


class ScriptException(Exception):
    """Stands in for an error raised by an IonControl script call (not a RuntimeError)."""


class UnsupportedQueryResource(opm_conftest.FakeResource):
    """Behaves like the real PM16-120 on a header it does not know (seen on the lab PC: SENS:AVER:COUN? gives -113 Undefined header): the query
    times out, and every attempt leaves an error in the meter's error queue, to be raised by whichever command checks errors next."""

    def query(self, command):
        if command == "SENS:AVER:COUN?":
            self.commands.append(("query", command))
            self.error_queue.append('-113,"Undefined header - command unknown"')
            raise TimeoutError("simulated VISA timeout: no response to %s" % command)
        return super().query(command)


class FakeLab:
    """Mirror position and active beam; the meter sees power only when its beam is selected and the mirrors are at the meters."""

    def __init__(self, mirrors_at_meters=False, stop_after=None, lag_reads=0):
        self.lag_reads = lag_reads   # reads a change takes to settle on the meter (0 = instant)
        self.settling = 0
        self.before = {"CRM": 0.0, "UV": 0.0}
        self.at_meters = mirrors_at_meters
        self.beam = "default"     # active preset; "default" = idle state after stopScan, None = all off
        self.log = []
        self.stop_after = stop_after
        self.stopped = False
        self.sink = []
        self.file_lines = []
        self.dirs_made = []
        self.resources = []
        self.noise_rel = 0.0   # alternating +/- fractional flicker on every reading
        self.noise_n = 0
        self.globals_set = []   # (number of presets run so far, name, value, unit)
        self.leak_uW = 0.0   # light on the CRM meter that no preset controls
        self.scan = None
        self.starts = {}   # preset -> number of times started
        self.reads_since_start = 0
        self.revert_presets = set()   # presets whose program "ends" (apparatus back to default) after revert_after reads
        self.revert_nth = {1}         # which starts of those presets revert (1 = the first attempt only)
        self.revert_after = READS_BEFORE_END_CHECK
        self.fail_on_start = None     # preset whose startScan raises ScriptException

    def _changed(self):
        self.before = {m: self.steady_W(m) for m in ("CRM", "UV")}
        self.settling = self.lag_reads

    def startScan(self, **k):
        if self.fail_on_start == self.scan:
            raise ScriptException("simulated IonControl error starting %s" % self.scan)
        self.starts[self.scan] = self.starts.get(self.scan, 0) + 1
        self.reads_since_start = 0

    def _reverted(self):
        return (self.scan in self.revert_presets and self.starts.get(self.scan) in self.revert_nth
                and self.reads_since_start > self.revert_after)

    def setScan(self, name):
        self._changed()
        self.scan = name
        self.log.append(name)
        if name == "Toggle_Beam_Samplers":
            self.at_meters = not self.at_meters
        elif name == "All_CW_beams_off":
            self.beam = None
        else:
            self.beam = name
        if self.stop_after is not None and len(self.log) >= self.stop_after:
            self.stopped = True

    def stopScan(self):
        self._changed()
        self.beam = "default"

    def power_W(self, meter):
        self.reads_since_start += 1
        steady = self.steady_W(meter)
        if self.settling > 0:
            frac = self.settling / self.lag_reads
            self.settling -= 1
            return self.before[meter] * frac + steady * (1 - frac)
        if self.noise_rel:
            self.noise_n += 1
            return steady * (1 + self.noise_rel * (-1) ** self.noise_n)
        return steady

    def steady_W(self, meter):
        if self.at_meters:
            on = DEFAULT_ON if (self.beam == "default" or self._reverted()) else (self.beam,)
            total = sum(POWER_UW[b] for b in on if b in POWER_UW and METER_OF[b] == meter)
            if total:
                return (total + DARK_UW) * 1e-6
        if self.at_meters and meter == "CRM":
            return (DARK_UW + self.leak_uW) * 1e-6
        return DARK_UW * 1e-6

    def meter(self, key, serial, model, fail=False):
        if fail:
            raise OpmError("simulated meter failure on %s" % key)
        lab = self
        res = UnsupportedQueryResource(idn="Thorlabs,PM16-120,%s,1.0.0" % serial)
        lab.resources.append(res)

        class Reader(list):
            def pop(self, i=0):
                return lab.power_W(key)

            def __bool__(self):
                return True

        res.reads = Reader()
        pm = PM16("FAKE", resource_factory=opm_conftest.resource_factory(res))
        pm.connect()
        return pm


def run_script(tmp_path, monkeypatch, lab, fail=(), pm_log=None, replacements=()):
    monkeypatch.chdir(tmp_path)
    fd = types.ModuleType("Functions_Data")
    fd.GetDataFilePath = lambda name, **k: (str(tmp_path / name.replace("*", "1")), str(tmp_path) + "/")
    fd.makeRelativeDirectory = lambda path, directory="new folder": lab.dirs_made.append((path, directory)) or path

    def save(path, text):
        lab.file_lines.append(text)

    fd.SaveDataToTextFile = save
    lab.paths = []
    fd.SaveDataToTextFile = lambda path, text: (lab.paths.append(path), save(path, text))
    monkeypatch.setitem(sys.modules, "Functions_Data", fd)
    import time
    monkeypatch.setattr(time, "sleep", lambda s: None)

    serial_to_key = {"190927111": "CRM", "200707115": "UV"}
    opened = []

    def open_meter(model=None, serial=None, **k):
        key = serial_to_key[serial]
        opened.append(key)
        return lab.meter(key, serial, model, fail=key in fail)

    out = []
    ns = dict(getGlobal=lambda k: None, setGlobal=lambda *a: lab.globals_set.append((len(lab.log),) + a), setScan=lab.setScan,
              startScan=lab.startScan, stopScan=lab.stopScan, getAllData=lambda: None,
              createTrace=lambda *a, **k: None, closeTrace=lambda *a, **k: None,
              plotPoint=lambda x, y, name, **k: lab.sink.append((x, round(y, 3))),
              consolePrint=lambda msg, error=False, **k: out.append((msg, error)),
              scriptIsStopped=lambda: lab.stopped)
    src = open(SCRIPT).read().replace("from thorlabs_opm_controller import open_meter, OpmError",
                                      "from thorlabs_opm_controller import OpmError")
    for a, b in replacements:
        assert a in src
        src = src.replace(a, b)
    ns["open_meter"] = open_meter
    try:
        exec(compile(src, SCRIPT, "exec"), ns)
    finally:
        lab.opened = opened
        lab.console = out
    return ns


def test_normal_run_order_rows_and_restore(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    assert lab.log == ["Toggle_Beam_Samplers",
                       "All_CW_beams_off", "Keep_493_on_only", "Keep_554_on_only", "Keep_650_on_only",
                       "All_CW_beams_off", "Keep_405_on_only", "Keep_614_on_only",
                       "Toggle_Beam_Samplers", "PMT_CheckCounts_For-Script_Even"]
    assert lab.log.count("Toggle_Beam_Samplers") % 2 == 0 and not lab.at_meters
    header, *rows = lab.file_lines
    assert header.startswith("timestamp, label,")
    assert len(rows) == 5
    by_label = {r.split(", ")[1]: r.split(", ") for r in rows}
    assert float(by_label["493"][5]) == pytest.approx(55.0, abs=0.01)
    assert float(by_label["554"][5]) == pytest.approx(10.0, abs=0.01)
    assert float(by_label["493"][11]) == pytest.approx(DARK_UW, abs=0.001)
    assert by_label["390"][2:5] == ["390.0", "400.0", "True"]
    assert by_label["493"][4] == "False"
    assert all(r.split(", ")[-1] == "True" for r in rows)
    assert len(rows[0].split(", ")) == 15
    text = "\n".join(m for m, e in lab.console)
    assert "| Laser (nm) | Power (µW) | Notes |" in text and "| 390 | 1700.0 | read at 400 nm |" in text


def test_out_of_tolerance_is_flagged_red(tmp_path, monkeypatch):
    lab = FakeLab()
    POWER_UW["Keep_650_on_only"] = 270.0
    try:
        run_script(tmp_path, monkeypatch, lab)
    finally:
        POWER_UW["Keep_650_on_only"] = 255.0
    assert [m for m, e in lab.console if e and m.startswith("650 nm")]
    assert any(l.split(", ")[1] == "650" and l.endswith("False") for l in lab.file_lines)
    assert not any(l.endswith("False") for l in lab.file_lines if l.split(", ")[1] != "650")


def test_meter_failure_skips_that_meter_and_restores(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab, fail=("CRM",))
    assert lab.opened == ["CRM", "UV"]
    labels = [l.split(", ")[1] for l in lab.file_lines[1:]]
    assert labels == ["390", "614"]
    assert lab.log.count("Toggle_Beam_Samplers") == 2 and not lab.at_meters
    assert lab.log[-1] == "PMT_CheckCounts_For-Script_Even"


def test_stop_mid_run_restores_mirrors(tmp_path, monkeypatch):
    lab = FakeLab(stop_after=4)   # stop after Keep_493_on_only
    run_script(tmp_path, monkeypatch, lab)
    assert lab.log.count("Toggle_Beam_Samplers") == 2 and not lab.at_meters
    assert lab.log[-1] == "PMT_CheckCounts_For-Script_Even"
    assert "Keep_614_on_only" not in lab.log and "Keep_405_on_only" not in lab.log


def test_mirrors_initially_wrong_way_round_still_end_at_trap(tmp_path, monkeypatch):
    lab = FakeLab(mirrors_at_meters=True)   # first toggle sends the beams to the trap instead
    run_script(tmp_path, monkeypatch, lab)
    assert not lab.at_meters
    assert len(lab.file_lines) == 6
    assert any(e and "wrong way round" in m for m, e in lab.console)
    assert any(e and "not where the script assumed" in m for m, e in lab.console)


def test_routing_failure_skips_both_meters_and_restores_start_state(tmp_path, monkeypatch):
    lab = FakeLab()
    saved = dict(POWER_UW)
    POWER_UW.update({k: 0.0 for k in POWER_UW})   # beams never reach the meter
    try:
        run_script(tmp_path, monkeypatch, lab)
    finally:
        POWER_UW.update(saved)
    assert len(lab.file_lines) == 1   # header only
    failed = [m for m, e in lab.console if m.startswith("Not measured:")]
    assert len(failed) == 1 and "CRM" in failed[0] and "UV" in failed[0] and "routing check failed" in failed[0]
    assert lab.log.count("Toggle_Beam_Samplers") % 2 == 0 and not lab.at_meters
    assert lab.log[-1] == "PMT_CheckCounts_For-Script_Even"


def test_open_ended_ranges_pass_high_and_fail_low(tmp_path, monkeypatch):
    lab = FakeLab()
    POWER_UW.update({"Keep_405_on_only": 1500.0, "Keep_614_on_only": 50.0})
    try:
        run_script(tmp_path, monkeypatch, lab)
    finally:
        POWER_UW.update({"Keep_405_on_only": 1700.0, "Keep_614_on_only": 9.0})
    flags = {l.split(", ")[1]: l.split(", ")[-1] for l in lab.file_lines[1:]}
    assert flags["390"] == "False" and flags["614"] == "True"
    assert any(l.split(", ")[1] == "614" and l.split(", ")[-2] == "none" for l in lab.file_lines)


def test_high_dark_reading_skips_that_meter_without_blaming_routing(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.leak_uW = 347.0   # what the real CRM meter showed with All_CW_beams_off
    run_script(tmp_path, monkeypatch, lab)
    assert [l.split(", ")[1] for l in lab.file_lines[1:]] == ["390", "614"]   # the UV meter still ran
    assert not {"Keep_493_on_only", "Keep_554_on_only", "Keep_650_on_only"} & set(lab.log)
    assert lab.log.count("Toggle_Beam_Samplers") == 2 and not lab.at_meters
    assert any(e and "still lighting this meter" in m for m, e in lab.console)
    assert any(m.startswith("Not measured:") and "CRM" in m and "dark reading too high" in m for m, e in lab.console)
    assert not any("wrong way round" in m for m, e in lab.console)


def test_reading_still_settling_after_preset_start_is_waited_out(tmp_path, monkeypatch):
    lab = FakeLab(lag_reads=12)   # a ~3 s transition, far slower than the real one; the real CRM dark read 103 +/- 161 uW because it started mid-transition
    run_script(tmp_path, monkeypatch, lab)
    rows = [l.split(", ") for l in lab.file_lines[1:]]
    assert len(rows) == 5
    assert all(float(r[11]) == pytest.approx(DARK_UW, abs=0.01) for r in rows)
    assert all(r[-1] == "True" for r in rows)
    assert not any(e and "still changing" in m for m, e in lab.console)


def test_reading_near_the_end_of_the_program_only_warns(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab, replacements=[("PRESET_HOLD_S = WAIT_S - 2.0", "PRESET_HOLD_S = -1.0")])
    rows = [l.split(", ") for l in lab.file_lines[1:]]
    assert len(rows) == 5 and all(r[-1] == "True" for r in rows)   # the timing margin no longer aborts or invalidates
    assert any(e and "raise WAIT_S" in m for m, e in lab.console)


def test_wait_global_is_written_before_any_preset_runs(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    assert lab.globals_set == [(0, "LaserPowerMeasurementWait", 10.0, "s")]


def test_one_dead_beam_is_flagged_without_aborting_or_toggling_mirrors(tmp_path, monkeypatch):
    lab = FakeLab()
    saved = POWER_UW["Keep_493_on_only"]
    POWER_UW["Keep_493_on_only"] = 0.0   # what the real CRM showed: 493 nm preset gives dark-level light
    try:
        run_script(tmp_path, monkeypatch, lab)
    finally:
        POWER_UW["Keep_493_on_only"] = saved
    rows = {l.split(", ")[1]: l.split(", ") for l in lab.file_lines[1:]}
    assert len(rows) == 5
    assert rows["493"][-1] == "False" and float(rows["493"][5]) == pytest.approx(0.0, abs=0.01)
    assert rows["554"][-1] == "True" and rows["650"][-1] == "True"
    assert lab.log.count("Toggle_Beam_Samplers") == 2 and not lab.at_meters
    assert any(e and "493 nm reads" in m and "off or blocked" in m for m, e in lab.console)
    assert not any("wrong way round" in m for m, e in lab.console)


def test_script_source_is_ascii_and_table_prints_micro_sign(tmp_path, monkeypatch):
    assert open(SCRIPT, "rb").read().isascii()   # IonControl reads scripts in the Windows codepage, which turns a UTF-8 micro sign into mojibake
    lab = FakeLab()
    POWER_UW["Keep_493_on_only"] = 47.7
    try:
        run_script(tmp_path, monkeypatch, lab)
    finally:
        POWER_UW["Keep_493_on_only"] = 55.0
    text = "\n".join(m for m, e in lab.console)
    assert "| Laser (nm) | Power (\u00b5W) | Notes |" in text and "outside 50-60 \u00b5W" in text


def test_results_table_is_a_single_console_message(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    tables = [m for m, e in lab.console if m.strip().startswith("| Laser (nm)")]
    assert len(tables) == 1
    assert tables[0].startswith("\n") and tables[0].endswith("\n")   # blank lines either side so it renders when pasted under a list item or above an image
    lines = tables[0].strip("\n").split("\n")
    assert len(lines) == 2 + 5 and all(l.startswith("|") for l in lines)
    assert {l.count("|") for l in lines} == {4}   # same number of columns in every row, none with an empty cell
    assert all(l.split("|")[3].strip() for l in lines)
    assert not any(m.strip().startswith("| ") for m, e in lab.console if m != tables[0])


def test_results_file_goes_in_a_subfolder_of_the_day_folder(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    assert lab.dirs_made == [(str(tmp_path) + "/", "Laser Powers")]
    assert set(lab.paths) and all("Laser Powers\\Laser_Powers_" in p and p.endswith("_1.txt") for p in lab.paths)
    assert any(m.startswith("Saved to ") and "Laser Powers" in m for m, e in lab.console)


def test_results_file_records_n_samples_and_integration_time(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    header, *rows = lab.file_lines
    cols = header.split(", ")
    assert cols[6:11] == ["stdev_uW", "n_samples", "integration_ms", "held_s", "valid"]
    for r in rows:
        f = r.split(", ")
        assert len(f) == len(cols)
        assert f[7] == "20" and float(f[8]) == pytest.approx(3.0)   # 20 host samples; nominal 3 ms per sample


def test_script_never_asks_the_meter_for_averaging_which_the_pm16_rejects(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    assert len(lab.file_lines) == 6 and not any(m.startswith("Not measured:") for m, e in lab.console)   # no -113 left to poison the next beam
    assert lab.resources and not any(c == ("query", "SENS:AVER:COUN?") for r in lab.resources for c in r.commands)
    assert not any("SENS:AVER" in c for r in lab.resources for k, c in r.commands)


def test_hold_time_is_printed_for_each_beam_and_saved(tmp_path, monkeypatch):
    lab = FakeLab()
    run_script(tmp_path, monkeypatch, lab)
    beam_lines = [m for m, e in lab.console if " nm: " in m and "uW (want" in m]
    assert len(beam_lines) == 5 and all("held " in m and "s of 10 s" in m for m in beam_lines)
    assert any(m.startswith("CRM: dark") and "held" in m for m, e in lab.console)
    assert all(r.split(", ")[9].replace(".", "").isdigit() for r in lab.file_lines[1:])


def test_state_lost_mid_reading_is_retried_and_then_valid(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.revert_presets = {"Keep_650_on_only"}   # the first attempt's program "ends" before the end-of-reading check; the retry is fine
    run_script(tmp_path, monkeypatch, lab)
    assert lab.starts["Keep_650_on_only"] == 2
    row = next(l.split(", ") for l in lab.file_lines[1:] if l.split(", ")[1] == "650")
    assert row[10] == "True" and float(row[5]) == pytest.approx(255.0, abs=0.01)
    assert any(e and "650 nm" in m and "retrying" in m for m, e in lab.console)
    assert not any(m.startswith("Not measured:") for m, e in lab.console)


def test_state_lost_on_every_attempt_marks_the_beam_invalid_and_carries_on(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.revert_presets = {"Keep_554_on_only"}
    lab.revert_nth = {1, 2}
    run_script(tmp_path, monkeypatch, lab)
    rows = {l.split(", ")[1]: l.split(", ") for l in lab.file_lines[1:]}
    assert len(rows) == 5
    assert rows["554"][10] == "False" and rows["554"][5] == "nan" and rows["554"][-1] == "False"
    assert all(rows[k][10] == "True" for k in ("493", "650", "390", "614"))
    assert 554.0 not in [x for x, y in lab.sink] and len(lab.sink) == 4   # no plotted point for the invalid beam
    text = "\n".join(m for m, e in lab.console)
    assert "| 554 | nan | invalid reading |" in text
    assert any(m.startswith("Not measured:") and "554 nm" in m for m, e in lab.console)


def test_dark_reading_that_loses_its_state_skips_that_meter_only(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.revert_presets = {"All_CW_beams_off"}
    lab.revert_nth = {1, 2}   # both CRM dark attempts; the UV dark (third start) is fine
    run_script(tmp_path, monkeypatch, lab)
    assert [l.split(", ")[1] for l in lab.file_lines[1:]] == ["390", "614"]
    assert any(m.startswith("Not measured:") and "CRM" in m and "dark reading unreliable" in m for m, e in lab.console)
    assert lab.log.count("Toggle_Beam_Samplers") == 2 and not lab.at_meters


def test_summary_is_printed_and_mirrors_restored_even_when_an_ioncontrol_call_fails(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.fail_on_start = "Keep_405_on_only"   # an IonControl-side error on the UV meter, after the CRM beams were measured
    with pytest.raises(ScriptException):
        run_script(tmp_path, monkeypatch, lab)
    tables = [m for m, e in lab.console if m.strip().startswith("| Laser (nm)")]
    assert len(tables) == 1 and "| 493 |" in tables[0] and "| 650 |" in tables[0]   # the CRM results were not lost
    assert lab.log.count("Toggle_Beam_Samplers") % 2 == 0 and not lab.at_meters
    assert lab.log[-1] == "PMT_CheckCounts_For-Script_Even"


def test_one_percent_flicker_on_a_bright_beam_does_not_hold_up_the_stability_wait(tmp_path, monkeypatch):
    lab = FakeLab()
    lab.noise_rel = 0.01   # the 1700 uW UV beam took 7.6 s to "settle" at a 1% tolerance
    run_script(tmp_path, monkeypatch, lab)
    assert not any(e and "still changing" in m for m, e in lab.console)
    rows = [l.split(", ") for l in lab.file_lines[1:]]
    assert len(rows) == 5 and all(r[10] == "True" for r in rows)
