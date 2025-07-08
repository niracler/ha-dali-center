"""Platform for Dali Center energy sensors."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfEnergy, LIGHT_LUX
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from PySrDaliGateway import DaliGateway, Device
from PySrDaliGateway.helper import is_light_device, is_motion_sensor, is_illuminance_sensor, is_panel_device
from PySrDaliGateway.const import BUTTON_EVENTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    # pylint: disable=unused-argument

    gateway: DaliGateway = hass.data[DOMAIN][entry.entry_id]
    devices: list[Device] = [
        Device(gateway, device)
        for device in entry.data.get("devices", [])
    ]

    _LOGGER.debug(
        "Processing initially known devices for energy sensors: %s",
        devices
    )

    added_devices = set()
    new_sensors: list[SensorEntity] = []
    for device in devices:
        if device.dev_id in added_devices:
            continue

        if is_light_device(device.dev_type):
            new_sensors.append(DaliCenterEnergySensor(device))
            added_devices.add(device.dev_id)
        elif is_motion_sensor(device.dev_type):
            new_sensors.append(DaliCenterMotionSensor(device))
            added_devices.add(device.dev_id)
        elif is_illuminance_sensor(device.dev_type):
            new_sensors.append(DaliCenterIlluminanceSensor(device))
            added_devices.add(device.dev_id)
        elif is_panel_device(device.dev_type):
            new_sensors.append(DaliCenterPanelSensor(device))
            added_devices.add(device.dev_id)

    if new_sensors:
        async_add_entities(new_sensors)


class DaliCenterEnergySensor(SensorEntity):
    """Representation of a Dali Center Energy Sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    def __init__(self, device: Device) -> None:
        self._device = device

        self._name = "Current Hour Energy"
        self._unique_id = f"{device.unique_id}_energy"
        self._device_id = device.unique_id

        self._available = device.status == "online"
        self._state: float = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
        }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> float | None:
        return self._state

    async def async_added_to_hass(self) -> None:
        signal = f"dali_center_energy_update_{self._device_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_energy_update
            )
        )

        signal = f"dali_center_update_available_{self._device_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update_available
            )
        )

    def _handle_device_update_available(self, available: bool) -> None:
        self._available = available
        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )

    def _handle_energy_update(self, energy_value: float) -> None:
        self._state = energy_value

        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )


class DaliCenterMotionSensor(SensorEntity):
    """Representation of a Dali Center Motion Sensor."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["no_motion", "motion", "vacant", "presence", "occupancy"]
    _attr_has_entity_name = True

    def __init__(self, device: Device) -> None:
        self._device = device
        self._name = "State"
        self._unique_id = f"{device.unique_id}"
        self._device_id = device.unique_id
        self._available = device.status == "online"
        self._state: str = "no_motion"

    @property
    def icon(self) -> str:
        return "mdi:motion-sensor"

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.name,
            "manufacturer": "Dali Center",
            "model": f"Motion Sensor Type {self._device.dev_type}",
            "via_device": (DOMAIN, self._device.gw_sn),
        }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> str | None:
        return self._state

    async def async_added_to_hass(self) -> None:
        signal = f"dali_center_update_{self._unique_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update
            )
        )

        signal = f"dali_center_update_available_{self._unique_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update_available
            )
        )

        # Read initial status
        self._device.read_status()

    def _handle_device_update_available(self, available: bool) -> None:
        self._available = available
        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )

    def _handle_device_update(self, property_list: list) -> None:

        for prop in property_list:
            dpid = prop.get("dpid")
            if dpid is not None:
                # For motion sensor, the dpid itself represents the motion state
                # Map dpid values to enum options
                motion_map = {
                    1: "no_motion",
                    2: "motion",
                    3: "vacant",
                    4: "occupancy",
                    5: "presence"
                }
                if dpid in motion_map:
                    self._state = motion_map[dpid]
                    _LOGGER.debug(
                        "%s %s state changed to: %s (dpid: %s) %s",
                        self._name, self._unique_id,
                        self._state, dpid, prop
                    )
                else:
                    # Default to no_motion for unknown dpid values
                    self._state = "no_motion"
                    _LOGGER.debug(
                        "%s %s unknown dpid: %s, setting to no_motion",
                        self._name, self._unique_id, dpid
                    )

        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )


class DaliCenterIlluminanceSensor(SensorEntity):
    """Representation of a Dali Center Illuminance Sensor."""

    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_has_entity_name = True

    def __init__(self, device: Device) -> None:
        self._device = device
        self._name = "State"
        self._unique_id = f"{device.unique_id}"
        self._device_id = device.unique_id
        self._available = device.status == "online"
        self._state: Optional[float] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.name,
            "manufacturer": "Dali Center",
            "model": f"Illuminance Sensor Type {self._device.dev_type}",
            "via_device": (DOMAIN, self._device.gw_sn),
        }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> float | None:
        return self._state

    async def async_added_to_hass(self) -> None:
        signal = f"dali_center_update_{self._unique_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update
            )
        )

        signal = f"dali_center_update_available_{self._unique_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update_available
            )
        )

        # Read initial status
        self._device.read_status()

    def _handle_device_update_available(self, available: bool) -> None:
        self._available = available
        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )

    def _handle_device_update(self, property_list: list) -> None:

        for prop in property_list:
            dpid = prop.get("dpid")
            value = prop.get("value")

            # Handle illuminance sensor status (dpid 4 for illuminance value)
            if dpid == 4 and value is not None:
                if value > 1000 or value <= 0:
                    _LOGGER.warning(
                        "%s %s value is not normal: %s lux (dpid: %s) %s",
                        self._name, self._unique_id,
                        value, dpid, prop
                    )
                    continue

                self._state = float(value)
                _LOGGER.debug(
                    "%s %s value updated to: %s lux (dpid: %s) %s",
                    self._name, self._unique_id,
                    self._state, dpid, prop
                )

        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )


class DaliCenterPanelSensor(SensorEntity):
    """Representation of a Dali Center Panel Event Sensor."""
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [
        "idle",
        "button_1_single_click", "button_1_double_click", "button_1_long_press",
        "button_2_single_click", "button_2_double_click", "button_2_long_press",
        "button_3_single_click", "button_3_double_click", "button_3_long_press",
        "button_4_single_click", "button_4_double_click", "button_4_long_press",
        "button_5_single_click", "button_5_double_click", "button_5_long_press",
        "button_6_single_click", "button_6_double_click", "button_6_long_press",
        "button_7_single_click", "button_7_double_click", "button_7_long_press",
        "button_8_single_click", "button_8_double_click", "button_8_long_press",
    ]
    _attr_has_entity_name = True

    def __init__(self, device: Device) -> None:
        self._device = device
        self._name = "Event"
        self._unique_id = f"{device.unique_id}_event"
        self._device_id = device.unique_id
        self._available = device.status == "online"
        self._state: str = "idle"
        self._reset_task: Optional[asyncio.Task] = None

    @property
    def icon(self) -> str:
        return "mdi:gesture-tap-button"

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.name,
            "manufacturer": "Dali Center",
            "model": f"Panel Type {self._device.dev_type}",
            "via_device": (DOMAIN, self._device.gw_sn),
        }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> str | None:
        return self._state

    async def async_added_to_hass(self) -> None:
        signal = f"dali_center_update_{self._device_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update
            )
        )

        signal = f"dali_center_update_available_{self._device_id}"
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal, self._handle_device_update_available
            )
        )

        self._device.read_status()

    def _handle_device_update_available(self, available: bool) -> None:
        self._available = available
        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )

    def _handle_device_update(self, property_list: list) -> None:
        for prop in property_list:
            event_type = prop.get("dpid")
            button_number = prop.get("keyNo")

            if button_number is not None and event_type is not None:
                event_name = f"button_{button_number}_{
                    BUTTON_EVENTS.get(event_type, "single_click")
                }"

                if event_name in self._attr_options:
                    self._state = event_name
                    _LOGGER.debug(
                        "%s %s event: %s (dpid: %s, value: %s)",
                        self._name, self._unique_id,
                        event_name, event_type, button_number
                    )
                    self._schedule_reset_to_idle()
                else:
                    _LOGGER.warning(
                        "%s %s unknown event value: %s (dpid: %s)",
                        self._name, self._unique_id, event_name, event_type
                    )

        self.hass.loop.call_soon_threadsafe(
            self.schedule_update_ha_state
        )

    def _schedule_reset_to_idle(self) -> None:
        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()

        self.hass.loop.call_soon_threadsafe(
            self._create_reset_task
        )

    def _create_reset_task(self) -> None:
        self._reset_task = self.hass.async_create_task(
            self._reset_to_idle_after_delay())

    async def _reset_to_idle_after_delay(self) -> None:
        try:
            await asyncio.sleep(2)
            self._state = "idle"
            self.hass.loop.call_soon_threadsafe(
                self.schedule_update_ha_state
            )
            _LOGGER.debug("%s %s reset to idle", self._name, self._unique_id)
        except asyncio.CancelledError:
            pass
