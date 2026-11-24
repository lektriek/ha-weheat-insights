"""Discover the entities the core Weheat integration created for a heat pump.

The core integration names its entities through translations, so entity_ids
depend on the language and on user renames. The unique_id is stable: it is
``f"{heat_pump_uuid}_{key}"``. We match on that, never on entity_id strings.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import CONTROL_DOMAIN, WEHEAT_DOMAIN


class WeheatKey(StrEnum):
    """Entity description keys used by the core Weheat integration."""

    WATER_OUTLET_TEMPERATURE = "water_outlet_temperature"
    RETURN_TEMPERATURE = "water_inlet_temperature"
    CH_INLET_TEMPERATURE = "ch_inlet_temperature"
    OUTSIDE_TEMPERATURE = "outside_temperature"
    ROOM_TEMPERATURE = "thermostat_room_temperature"
    ROOM_SETPOINT = "thermostat_room_temperature_setpoint"
    WATER_SETPOINT = "thermostat_water_setpoint"
    POWER_INPUT = "power_input"
    POWER_OUTPUT = "power_output"
    COP = "cop"
    STATE = "heat_pump_state"
    COMPRESSOR_PERCENTAGE = "compressor_percentage"
    CH_FLOW = "central_heating_flow_volume"
    DHW_TOP_TEMPERATURE = "dhw_top_temperature"
    DHW_BOTTOM_TEMPERATURE = "dhw_bottom_temperature"
    ELECTRICITY_USED = "electricity_used"
    ELECTRICITY_USED_INDOOR_UNIT = "electricity_used_indoor_unit"
    ELECTRICITY_USED_HEATING = "electricity_used_heating"
    ELECTRICITY_USED_DHW = "electricity_used_dhw"
    ELECTRICITY_USED_DEFROST = "electricity_used_defrost"
    ELECTRICITY_USED_STANDBY = "electricity_used_standby"
    ENERGY_OUTPUT = "energy_output"
    ENERGY_OUTPUT_HEATING = "energy_output_heating"
    ENERGY_OUTPUT_DHW = "energy_output_dhw"
    ENERGY_OUTPUT_DEFROST = "energy_output_defrost"
    GAS_BOILER = "indoor_unit_gas_boiler_state"
    ELECTRIC_HEATER = "indoor_unit_electric_heater_state"


_KEYS = {key.value: key for key in WeheatKey}

# "Supply" is the water going into the heating system: the CH inlet ("house
# in") sensor the installer clips onto the heating side, after the pump or
# 3-way valve. It sees what the radiators get, also with a buffer or mixing in
# between. Pumps without that sensor fall back to the heat pump's own outlet.
SUPPLY_KEYS = (WeheatKey.CH_INLET_TEMPERATURE, WeheatKey.WATER_OUTLET_TEMPERATURE)


def supply_candidates(entities: dict[WeheatKey, str]) -> list[str]:
    """Supply entities in order of preference: CH inlet, then pump outlet."""
    return [entities[key] for key in SUPPLY_KEYS if key in entities]


@dataclass(frozen=True, slots=True)
class RegistryEntity:
    """The registry fields discovery needs; decoupled from HA for testing."""

    entity_id: str
    unique_id: str
    platform: str
    disabled: bool = False


@dataclass(frozen=True, slots=True)
class WeheatHeatPump:
    """A heat pump device created by the core Weheat integration."""

    uuid: str
    device_id: str
    name: str
    model: str | None


def map_entities(uuid: str, entities: Iterable[RegistryEntity]) -> dict[WeheatKey, str]:
    """Map known Weheat keys to entity_ids for one heat pump.

    Disabled entities are skipped, as are entities from other platforms
    and keys we do not know (new core sensors are ignored, not an error).
    """
    prefix = f"{uuid}_"
    found: dict[WeheatKey, str] = {}
    for entity in entities:
        if entity.platform != WEHEAT_DOMAIN or entity.disabled:
            continue
        if not entity.unique_id.startswith(prefix):
            continue
        key = _KEYS.get(entity.unique_id.removeprefix(prefix))
        if key is not None:
            found[key] = entity.entity_id
    return found


def heat_pump_uuid(device: dr.DeviceEntry) -> str | None:
    """Return the Weheat heat pump uuid of a device, if it is a Weheat pump.

    Every device in the registry passes through here, not only Weheat ones.
    Home Assistant does not enforce that identifiers are (domain, id) pairs,
    and some integrations register longer tuples, so never unpack them.
    """
    for identifier in device.identifiers:
        if len(identifier) >= 2 and identifier[0] == WEHEAT_DOMAIN:
            return identifier[1]
    return None


def async_get_heat_pumps(hass: HomeAssistant) -> list[WeheatHeatPump]:
    """Return all heat pumps known to the core Weheat integration."""
    pumps: list[WeheatHeatPump] = []
    for device in dr.async_get(hass).devices.values():
        uuid = heat_pump_uuid(device)
        if uuid is None:
            continue
        pumps.append(
            WeheatHeatPump(
                uuid=uuid,
                device_id=device.id,
                name=device.name_by_user or device.name or uuid,
                model=device.model,
            )
        )
    return sorted(pumps, key=lambda pump: pump.name.casefold())


def async_get_heat_pump(hass: HomeAssistant, uuid: str) -> WeheatHeatPump | None:
    """Return one heat pump by uuid."""
    return next(
        (pump for pump in async_get_heat_pumps(hass) if pump.uuid == uuid), None
    )


def async_map_heat_pump_entities(
    hass: HomeAssistant, pump: WeheatHeatPump
) -> dict[WeheatKey, str]:
    """Map Weheat keys to entity_ids using the live entity registry."""
    registry = er.async_get(hass)
    return map_entities(
        pump.uuid,
        (
            RegistryEntity(
                entity_id=entry.entity_id,
                unique_id=entry.unique_id,
                platform=entry.platform,
                disabled=entry.disabled,
            )
            for entry in er.async_entries_for_device(
                registry, pump.device_id, include_disabled_entities=True
            )
        ),
    )


class ControlKey(StrEnum):
    """Entity keys of the weheat_control extension (Weheat Intelligence plan)."""

    DHW_PLAN = "dhw_plan"
    DHW_PLAN_YESTERDAY = "dhw_plan_yesterday"
    DHW_PLAN_TODAY = "dhw_plan_today"
    DHW_PLAN_TOMORROW = "dhw_plan_tomorrow"
    DHW_PLAN_NEXT = "dhw_plan_next"
    DHW_TARGET_READBACK = "dhw_target_readback"


def map_control_entities(
    entities: Iterable[RegistryEntity], pump_count: int
) -> dict[ControlKey, str]:
    """Map weheat_control keys to entity_ids, if that maps to one heat pump.

    weheat_control keys its entities by Weheat installation id, which Home
    Assistant cannot relate to the core integration's heat pump uuid. An
    installation has one heat pump, so we only link when there is exactly
    one installation and one heat pump; otherwise nothing.
    """
    if pump_count != 1:
        return {}
    by_installation: dict[str, dict[ControlKey, str]] = {}
    for entity in entities:
        if entity.platform != CONTROL_DOMAIN:
            continue
        # The readback sensor exists for every installation, so every
        # installation shows up here even outside Intelligence mode.
        key = next(
            (k for k in ControlKey if entity.unique_id.endswith(f"_{k.value}")), None
        )
        if key is None:
            continue
        installation = entity.unique_id.removesuffix(f"_{key.value}")
        found = by_installation.setdefault(installation, {})
        if not entity.disabled:
            found[key] = entity.entity_id
    if len(by_installation) != 1:
        return {}
    return next(iter(by_installation.values()))


def async_map_control_entities(hass: HomeAssistant) -> dict[ControlKey, str]:
    """Map the weheat_control entities, if installed and unambiguous."""
    registry = er.async_get(hass)
    return map_control_entities(
        (
            RegistryEntity(
                entity_id=entry.entity_id,
                unique_id=entry.unique_id,
                platform=entry.platform,
                disabled=entry.disabled,
            )
            for entry in registry.entities.values()
            if entry.platform == CONTROL_DOMAIN
        ),
        len(async_get_heat_pumps(hass)),
    )
