"""IonControl externalParameter adapter for the DP832 controller."""

import re
from collections.abc import Mapping as MappingABC
from typing import Any, Dict, Mapping, Optional, Tuple

from .controller import DP832Controller, normalize_resource_string
from .errors import RigolValidationError

try:
    from externalParameter.ExternalParameterBase import ExternalParameterBase  # type: ignore
except Exception:  # pragma: no cover - optional at integration time

    class ExternalParameterBase:  # type: ignore[override]
        """Fallback base for offline development outside IonControl."""

        def __init__(self, name, config, globalDict):
            self.name = name
            self.config = config
            self.globalDict = globalDict

        def close(self) -> None:
            return None


try:
    from modules.quantity import Q as _IonQ  # type: ignore
except Exception:  # pragma: no cover - optional at integration time
    _IonQ = None


def _q(value: Any, unit: str) -> Any:
    """Return an IonControl quantity when available, else raw value."""
    if _IonQ is None:
        return value
    if unit:
        return _IonQ(value, unit)
    return _IonQ(value)


class RigolDP832Parameter(ExternalParameterBase):  # type: ignore[misc]
    """Thin translation layer from IonControl channels to DP832 controller API."""

    className = "Rigol DP832"

    _CANONICAL_OUTPUT_CHANNELS: Dict[str, str] = {
        "Volt1": "V",
        "Volt2": "V",
        "Volt3": "V",
        "Curr1": "A",
        "Curr2": "A",
        "Curr3": "A",
        "OnOff1": "",
        "OnOff2": "",
        "OnOff3": "",
    }

    _CANONICAL_INPUT_CHANNELS: Dict[str, str] = {
        "MeasVolt1": "V",
        "MeasVolt2": "V",
        "MeasVolt3": "V",
        "MeasCurr1": "A",
        "MeasCurr2": "A",
        "MeasCurr3": "A",
    }

    # Keep class-level defaults for discovery and backward compatibility.
    _outputChannels: Dict[str, str] = dict(_CANONICAL_OUTPUT_CHANNELS)
    _inputChannels: Dict[str, str] = dict(_CANONICAL_INPUT_CHANNELS)

    def __init__(self, name: str, config: Mapping[str, Any], globalDict: Mapping[str, Any], instrument: str = ""):
        output_alias_cfg = config.get("output_aliases")
        input_alias_cfg = config.get("input_aliases")

        self._output_alias_to_canonical, self._outputChannels = self._build_alias_maps(
            canonical_units=self._CANONICAL_OUTPUT_CHANNELS,
            alias_cfg=output_alias_cfg,
            map_name="output_aliases",
        )
        self._input_alias_to_canonical, self._inputChannels = self._build_alias_maps(
            canonical_units=self._CANONICAL_INPUT_CHANNELS,
            alias_cfg=input_alias_cfg,
            map_name="input_aliases",
        )

        super().__init__(name, config, globalDict)

        target = instrument or str(config.get("instrument", "")).strip()
        if not target:
            raise RigolValidationError("No instrument provided. Use VISA string, host, or host:port.")

        timeout_ms = int(config.get("timeout_ms", 3000))
        query_delay_ms = int(config.get("query_delay_ms", 50))
        verify_readback = bool(config.get("verify_readback", True))
        retries = int(config.get("retries", 2))
        backend = config.get("backend", "__controller_default__")

        self.instrument = normalize_resource_string(target)
        controller_kwargs = {
            "timeout_ms": timeout_ms,
            "query_delay_ms": query_delay_ms,
            "retries": retries,
            "verify_readback": verify_readback,
        }
        if backend != "__controller_default__":
            controller_kwargs["backend"] = str(backend) if backend is not None else None

        self.controller = DP832Controller(self.instrument, **controller_kwargs)
        self.controller.connect()

    def setValue(self, channel: str, value: Any) -> Any:  # noqa: N802 - IonControl API style
        canonical = self._resolve_output_alias(channel)
        op, idx = self._parse_output_channel(canonical)
        if op == "volt":
            self.controller.set_voltage(idx, self._as_unit(value, "V"))
            return self.getValue(channel)
        if op == "curr":
            self.controller.set_current(idx, self._as_unit(value, "A"))
            return self.getValue(channel)
        self.controller.set_output(idx, self._as_bool(value))
        return self.getValue(channel)

    def getValue(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
        canonical = self._resolve_output_alias(channel)
        op, idx = self._parse_output_channel(canonical)
        if op == "volt":
            return _q(self.controller.get_voltage_setpoint(idx), "V")
        if op == "curr":
            return _q(self.controller.get_current_setpoint(idx), "A")
        return _q(1 if self.controller.get_output(idx) else 0, "")

    def getExternalValue(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
        return self.getInputData(channel)

    def getInputData(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
        canonical = self._resolve_input_alias(channel)
        op, idx = self._parse_input_channel(canonical)
        if op == "meas_volt":
            return _q(self.controller.measure_voltage(idx), "V")
        return _q(self.controller.measure_current(idx), "A")

    @classmethod
    def connectedInstruments(cls):  # noqa: N802 - IonControl API style
        return []

    def close(self) -> None:
        self.controller.close()
        super_close = getattr(super(), "close", None)
        if callable(super_close):
            super_close()

    def _resolve_output_alias(self, channel: str) -> str:
        """Resolve configured output alias to canonical DP832 channel name."""
        try:
            return self._output_alias_to_canonical[channel]
        except KeyError as exc:
            raise RigolValidationError(f"Unsupported output channel: {channel!r}") from exc

    def _resolve_input_alias(self, channel: str) -> str:
        """Resolve configured input alias to canonical DP832 channel name."""
        try:
            return self._input_alias_to_canonical[channel]
        except KeyError as exc:
            raise RigolValidationError(f"Unsupported input channel: {channel!r}") from exc

    @staticmethod
    def _build_alias_maps(
        *,
        canonical_units: Dict[str, str],
        alias_cfg: Optional[Any],
        map_name: str,
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Build alias and exported channel maps from per-instance configuration."""
        if alias_cfg is None:
            alias_to_canonical = {name: name for name in canonical_units}
            return alias_to_canonical, dict(canonical_units)

        if not isinstance(alias_cfg, MappingABC):
            raise RigolValidationError(f"{map_name} must be a mapping of alias to canonical channel")

        alias_to_canonical: Dict[str, str] = {}
        exported_channels: Dict[str, str] = {}

        for alias, canonical in alias_cfg.items():
            if not isinstance(alias, str) or not alias.strip():
                raise RigolValidationError(f"{map_name} keys must be non-empty strings")

            alias_name = alias.strip()
            if not isinstance(canonical, str) or canonical not in canonical_units:
                allowed = ", ".join(sorted(canonical_units.keys()))
                raise RigolValidationError(f"{map_name}[{alias_name!r}] must map to one of: {allowed}")

            if alias_name in alias_to_canonical:
                raise RigolValidationError(f"Duplicate alias in {map_name}: {alias_name!r}")

            alias_to_canonical[alias_name] = canonical
            exported_channels[alias_name] = canonical_units[canonical]

        return alias_to_canonical, exported_channels

    @staticmethod
    def _parse_output_channel(channel: str) -> Tuple[str, int]:
        match = re.fullmatch(r"(Volt|Curr|OnOff)([123])", channel)
        if not match:
            raise RigolValidationError(f"Unsupported output channel: {channel!r}")
        prefix, idx_raw = match.groups()
        prefix_map = {"Volt": "volt", "Curr": "curr", "OnOff": "onoff"}
        return prefix_map[prefix], int(idx_raw)

    @staticmethod
    def _parse_input_channel(channel: str) -> Tuple[str, int]:
        match = re.fullmatch(r"(MeasVolt|MeasCurr)([123])", channel)
        if not match:
            raise RigolValidationError(f"Unsupported input channel: {channel!r}")
        prefix, idx_raw = match.groups()
        prefix_map = {"MeasVolt": "meas_volt", "MeasCurr": "meas_curr"}
        return prefix_map[prefix], int(idx_raw)

    @staticmethod
    def _as_unit(value: Any, unit: str) -> float:
        if hasattr(value, "m_as"):
            return float(value.m_as(unit))
        return float(value)

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if hasattr(value, "m_as"):
            return float(value.m_as("")) > 0
        return float(value) > 0
