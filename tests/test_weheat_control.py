"""Tests for the Weheat Intelligence plan from the weheat_control extension."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weheat_insights.discovery import (
    ControlKey,
    RegistryEntity,
    map_control_entities,
)
from custom_components.weheat_insights.websocket_api import ws_dashboard_config

from .conftest import PUMP_UUID, WEHEAT_SENSORS, add_weheat_pump

INSTALLATION = "51ec3549-66f2-4297-bf9f-8ec605a8352a"
DHW_SENSORS = {
    **WEHEAT_SENSORS,
    "dhw_top_temperature": ("weheat_dhw_top", "°C", "temperature"),
    "dhw_bottom_temperature": ("weheat_dhw_bottom", "°C", "temperature"),
}


def _control(installation: str, key: str, **kwargs) -> RegistryEntity:
    return RegistryEntity(
        f"sensor.{installation}_{key}",
        f"{installation}_{key}",
        "weheat_control",
        **kwargs,
    )


def test_map_control_entities_one_installation() -> None:
    entities = [
        _control("abc", "dhw_plan"),
        _control("abc", "dhw_plan_next"),
        _control("abc", "dhw_plan_today"),
        _control("abc", "dhw_target_readback"),
        _control("abc", "boost_end"),
        _control("abc", "dhw_plan_tomorrow", disabled=True),
        RegistryEntity("sensor.x", "abc_dhw_plan", "template"),
    ]
    assert map_control_entities(entities, pump_count=1) == {
        ControlKey.DHW_PLAN: "sensor.abc_dhw_plan",
        ControlKey.DHW_PLAN_NEXT: "sensor.abc_dhw_plan_next",
        ControlKey.DHW_PLAN_TODAY: "sensor.abc_dhw_plan_today",
        ControlKey.DHW_TARGET_READBACK: "sensor.abc_dhw_target_readback",
    }


def test_map_control_entities_ambiguous_links_nothing() -> None:
    two = [_control("abc", "dhw_target_readback"), _control("def", "dhw_plan")]
    assert map_control_entities(two, pump_count=1) == {}
    assert map_control_entities([_control("abc", "dhw_plan")], pump_count=2) == {}
    assert map_control_entities([], pump_count=1) == {}


def _add_control(hass: HomeAssistant) -> dict[str, str]:
    entry = MockConfigEntry(domain="weheat_control", title="Weheat control")
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    return {
        key: registry.async_get_or_create(
            "sensor", "weheat_control", f"{INSTALLATION}_{key}", config_entry=entry
        ).entity_id
        for key in (
            "dhw_plan",
            "dhw_plan_next",
            "dhw_plan_today",
            "dhw_target_readback",
        )
    }


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain="weheat_insights",
        title="Pump",
        unique_id=PUMP_UUID,
        data={"heat_pump_id": PUMP_UUID},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _ours(hass: HomeAssistant, key: str) -> str | None:
    return er.async_get(hass).async_get_entity_id(
        "sensor", "weheat_insights", f"{PUMP_UUID}_{key}"
    )


def _dashboard(hass: HomeAssistant) -> dict:
    connection = MagicMock()
    ws_dashboard_config(hass, connection, {"id": 1, "type": "x"})
    return connection.send_result.call_args.args[1]["heat_pumps"][0]


async def test_hot_water_activity_without_extension(hass: HomeAssistant) -> None:
    weheat = add_weheat_pump(hass, sensors=DHW_SENSORS)
    state = weheat.entity_ids["heat_pump_state"]
    hass.states.async_set(state, "heating")
    await _setup(hass)

    activity = _ours(hass, "dhw_activity")
    assert activity is not None
    assert hass.states.get(activity).state == "none"
    for source, expected in (
        ("dhw", "dhw"),
        ("legionella_prevention", "legionella"),
        ("defrosting", "none"),
    ):
        hass.states.async_set(state, source)
        await hass.async_block_till_done()
        assert hass.states.get(activity).state == expected

    assert _ours(hass, "dhw_plan_target") is None
    assert _ours(hass, "dhw_plan_activity") is None
    assert _dashboard(hass)["control"] == {}


async def test_plan_sensors_follow_the_plan(hass: HomeAssistant) -> None:
    add_weheat_pump(hass, sensors=DHW_SENSORS)
    control = _add_control(hass)
    plan = control["dhw_plan"]
    hass.states.async_set(plan, "standby", {"reported_target_temperature": 52.9})
    await _setup(hass)

    target, activity = _ours(hass, "dhw_plan_target"), _ours(hass, "dhw_plan_activity")
    assert float(hass.states.get(target).state) == 52.9
    # "standby" in the plan means no hot water, not that the pump is idle.
    assert hass.states.get(activity).state == "none"

    hass.states.async_set(plan, "heating", {"reported_target_temperature": 50})
    await hass.async_block_till_done()
    assert hass.states.get(activity).state == "dhw"
    assert float(hass.states.get(target).state) == 50

    # Outside Intelligence mode the plan is unavailable, and so are ours.
    hass.states.async_set(plan, "unavailable")
    await hass.async_block_till_done()
    assert hass.states.get(target).state == "unavailable"
    assert hass.states.get(activity).state == "unavailable"

    config = _dashboard(hass)
    assert config["control"]["dhw_plan"] == plan
    assert config["control"]["dhw_target_readback"] == control["dhw_target_readback"]
    assert config["insights"]["dhw_plan_activity"] == activity


async def test_plan_sensors_removed_with_extension(hass: HomeAssistant) -> None:
    add_weheat_pump(hass, sensors=DHW_SENSORS)
    control = _add_control(hass)
    entry = await _setup(hass)
    assert _ours(hass, "dhw_plan_target") is not None

    registry = er.async_get(hass)
    for entity_id in control.values():
        registry.async_remove(entity_id)
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert _ours(hass, "dhw_plan_target") is None
    assert _ours(hass, "dhw_plan_activity") is None
    assert _dashboard(hass)["control"] == {}
