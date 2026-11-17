"""Offline tests for the DSI Signal Generator external parameter.

Importing externalParameter.StandardExternalParameter needs PyQt5, pint, pyqtgraph and a
loaded IonControl project, so these tests extract the ``if DSISignalGeneratorEnabled:``
block from that file with ast and run it against small stand-ins. The block's real
dependency, dsi_sg_controller, is used for PowerLimits and the error classes; the
connection itself is replaced by a fake ``open_generator`` so nothing touches a port.

Run with the driver package on the path:
    PYTHONPATH=<dsi_sg_controller>/src python -m pytest tests/test_dsi_sg_adapter.py
"""
import ast
import logging
import math
import os
from collections import OrderedDict

import pytest

pytest.importorskip("dsi_sg_controller")
import dsi_sg_controller as dsi  # noqa: E402

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                      "externalParameter", "StandardExternalParameter.py")


def _load_block():
    with open(SOURCE, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    for node in tree.body:
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Name)
                and node.test.id == "DSISignalGeneratorEnabled"):
            return node
    raise AssertionError("DSISignalGeneratorEnabled block not found")


class Settings(object):
    pass


class Q(object):
    def __init__(self, value, unit):
        self.value, self.unit = value, unit

    def m_as(self, unit):
        assert unit == self.unit, (unit, self.unit)
        return self.value


class FakeBase(object):
    """Stand-in for ExternalParameterBase (no Qt)."""
    _outputChannels = {None: None}
    _inputChannels = dict()

    def __init__(self, name, deviceSettings, globalDict):
        self.name = name
        self.settings = deviceSettings
        self.outputChannels = OrderedDict(
            (cname, type("Slow", (), {"settings": Settings()})()) for cname in self._outputChannels)

    def initializeChannelsToExternals(self):
        for cname in self._outputChannels:
            self.getValue(cname)

    def initOutput(self):
        raise AssertionError("the base initOutput must not be reached")


class FakeChannel(object):
    def __init__(self, gen):
        self.gen = gen

    def get_output(self):
        return self.gen.state["out"]

    def get_frequency_hz(self):
        return self.gen.state["freq"]

    def get_power_dbm(self):
        return self.gen.state["power"]

    def set_output(self, on):
        self.gen.writes.append(("out", on))
        self.gen.state["out"] = on
        return on

    def set_frequency_hz(self, hz):
        self.gen.writes.append(("freq", hz))
        self.gen.state["freq"] = hz
        return hz

    def set_power_dbm(self, dbm):
        lim = (self.gen.limits or {}).get(1)
        if lim is None:
            raise dsi.LimitError("no PowerLimits configured")
        lim.check_absolute(dbm, 1)
        lim.check_step(self.gen.state["power"], dbm, 1)
        self.gen.writes.append(("power", dbm))
        self.gen.state["power"] = dbm
        return dbm

    def ramp_power_dbm(self, target):
        lim = (self.gen.limits or {}).get(1)
        if lim is None:
            raise dsi.LimitError("no PowerLimits configured")
        lim.check_absolute(target, 1)
        while abs(target - self.gen.state["power"]) > 1e-9:
            delta = target - self.gen.state["power"]
            self.set_power_dbm(self.gen.state["power"] + math.copysign(min(abs(delta), lim.max_step_db), delta))
        return self.gen.state["power"]


class Recorder(object):
    """Fake open_generator: records each session's kwargs and every write."""

    def __init__(self):
        self.sessions = []
        self.writes = []
        self.state = {"out": False, "freq": 150e6, "power": -10.0}
        self.limits = None

    def __call__(self, **kwargs):
        self.sessions.append(kwargs)
        self.limits = kwargs.get("limits")
        recorder = self

        class Gen(object):
            idn = dsi.Idn("DS Instruments", kwargs["model"], kwargs["serial"], "12.43")

            def channel(self, n):
                assert n == 1
                return FakeChannel(recorder)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        return Gen()


class FakeProject(object):
    def __init__(self, entries):
        self.entries = entries

    def isEnabled(self, gui, obj):
        assert (gui, obj) == ("hardware", "DSI Signal Generator")
        return {k: v for k, v in self.entries.items() if v.get("enabled")}


RAMAN = {"enabled": True, "model": "SG6000L", "serial": "488", "port": "COM11", "host": "",
         "tcpPort": 10001, "channel": 1, "minPowerDbm": "-21", "maxPowerDbm": "-5",
         "maxStepDb": "1", "minFreqHz": "140e6", "maxFreqHz": "160e6", "powerResolutionDb": "0.5"}
TCP_UNIT = {"enabled": True, "model": "SG12000PRO", "serial": "77", "port": "",
             "host": "192.168.168.50", "tcpPort": 10001, "channel": 1, "minPowerDbm": "",
             "maxPowerDbm": "", "maxStepDb": "", "minFreqHz": "", "maxFreqHz": "", "powerResolutionDb": ""}


@pytest.fixture
def build():
    def make(entries):
        recorder = Recorder()
        project = FakeProject(entries)
        namespace = {
            "getProject": lambda: project,
            "ExternalParameterBase": FakeBase,
            "OrderedDict": OrderedDict,
            "logging": logging,
            "math": math,
            "Q": Q,
            "qtHelper": lambda: type("H", (), {"newData": None})(),
            "importErrorPopup": lambda name: (_ for _ in ()).throw(AssertionError(name)),
        }
        block = _load_block()
        extra = {"type_ignores": []} if "type_ignores" in ast.Module._fields else {}
        module = ast.Module(body=[block], **extra)
        namespace["DSISignalGeneratorEnabled"] = True
        exec(compile(module, SOURCE, "exec"), namespace)
        namespace["open_generator"] = recorder  # replace the real import after exec
        return namespace["DSISignalGenerator"], recorder
    return make


def test_raman_opens_over_serial_and_reads_without_writing(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    first = rec.sessions[0]
    assert first["port"] == "COM11" and "host" not in first
    assert first["model"] == "SG6000L" and first["serial"] == "488"
    assert first["limits"][1] == dsi.PowerLimits(-21.0, -5.0, 1.0)
    assert rec.writes == []
    param.initOutput()
    assert rec.writes == []


def test_tcp_entry_opens_over_tcp(build):
    cls, rec = build({"TcpUnit": dict(TCP_UNIT)})
    cls("tcp", Settings(), {}, "TcpUnit")
    assert rec.sessions[0]["host"] == "192.168.168.50"
    assert rec.sessions[0]["tcp_port"] == 10001
    assert "port" not in rec.sessions[0]
    assert rec.sessions[0]["limits"] is None


def test_power_write_refused_without_limits(build):
    cls, rec = build({"TcpUnit": dict(TCP_UNIT)})
    param = cls("tcp", Settings(), {}, "TcpUnit")
    with pytest.raises(dsi.LimitError):
        param.setValue("Power_dBm", Q(-6.0, ""))
    assert rec.writes == []


def test_power_write_within_limits_and_cap(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    value, done = param.setValue("Power_dBm", Q(-9.5, ""))
    assert done and value.value == -9.5
    with pytest.raises(dsi.LimitError):
        param.setValue("Power_dBm", Q(-4.0, ""))  # above maxPowerDbm
    assert rec.writes == [("power", -9.5)]


def test_frequency_outside_config_range_refused_before_sending(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    with pytest.raises(ValueError):
        param.setValue("Freq", Q(1.5e9, "Hz"))
    assert rec.writes == []
    value, _ = param.setValue("Freq", Q(151e6, "Hz"))
    assert value.value == 151e6


def test_output_toggle(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    assert param.setValue("OutEnable", Q(1, ""))[0].value == 1
    assert param.getValue("OutEnable").value == 1


@pytest.mark.parametrize("change", [{"serial": ""}, {"model": ""},
                                    {"host": "192.168.168.50"}, {"port": ""}])
def test_bad_config_is_refused_before_connecting(build, change):
    entry = dict(RAMAN)
    entry.update(change)
    cls, rec = build({"Raman": entry})
    with pytest.raises(ValueError):
        cls("raman", Settings(), {}, "Raman")
    assert rec.sessions == []


def test_disabled_entry_is_not_offered_or_opened(build):
    entry = dict(RAMAN, enabled=False)
    cls, rec = build({"Raman": entry, "TcpUnit": dict(TCP_UNIT)})
    assert cls.connectedInstruments() == ["TcpUnit"]
    with pytest.raises(KeyError):
        cls("raman", Settings(), {}, "Raman")


def test_unknown_channel(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    with pytest.raises(KeyError):
        param.getValue("Phase")


def test_power_and_frequency_jump_so_the_package_does_the_stepping(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    assert param.outputChannels["Power_dBm"].settings.jump is True
    assert param.outputChannels["Freq"].settings.jump is True
    assert not getattr(param.outputChannels["OutEnable"].settings, "jump", False)


def test_large_power_change_is_ramped_in_max_step_writes(build):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    value, done = param.setValue("Power_dBm", Q(-13.0, ""))
    assert done and value.value == -13.0
    assert rec.writes == [("power", -11.0), ("power", -12.0), ("power", -13.0)]


@pytest.mark.parametrize("requested, sent", [(-9.25, -9.0), (-9.3, -9.5), (-9.1, -9.0), (-5.2, -5.0),
                                             (-20.9, -21.0), (-9.0, -9.0)])
def test_power_request_rounded_to_resolution_inside_limits(build, requested, sent):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    rec.state["power"] = -9.0 if requested > -15 else -20.0
    assert param.setValue("Power_dBm", Q(requested, ""))[0].value == sent
    assert rec.state["power"] == sent


@pytest.mark.parametrize("requested", [-4.8, -21.2])
def test_out_of_limits_request_is_refused_not_rounded_in(build, requested):
    cls, rec = build({"Raman": dict(RAMAN)})
    param = cls("raman", Settings(), {}, "Raman")
    with pytest.raises(dsi.LimitError):
        param.setValue("Power_dBm", Q(requested, ""))
    assert rec.writes == []


def test_no_rounding_without_resolution(build):
    entry = dict(RAMAN, powerResolutionDb="")
    cls, rec = build({"Raman": entry})
    param = cls("raman", Settings(), {}, "Raman")
    assert param.setValue("Power_dBm", Q(-10.25, ""))[0].value == -10.25


def test_bad_resolution_refused(build):
    cls, rec = build({"Raman": dict(RAMAN, powerResolutionDb="0")})
    with pytest.raises(ValueError):
        cls("raman", Settings(), {}, "Raman")
