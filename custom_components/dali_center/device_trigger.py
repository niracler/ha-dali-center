"""Device trigger support for Dali Center integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN
from PySrDaliGateway.const import BUTTON_EVENTS


def get_panel_button_count(dev_type: str) -> int:
    """Get button count for panel device type."""
    button_count_map = {
        "0302": 2,
        "0304": 4,
        "0306": 6,
        "0308": 8,
    }
    return button_count_map.get(dev_type, 4)


def get_trigger_types_for_button_count(button_count: int) -> list[str]:
    """Generate trigger types for the given button count."""
    trigger_types = []
    for button_num in range(1, button_count + 1):
        trigger_types.extend([
            f"button_{button_num}_double_press"
        ])

    for button_num in range(1, button_count + 1):
        trigger_types.extend([
            f"button_{button_num}_long_press"
        ])

    for button_num in range(1, button_count + 1):
        trigger_types.extend([
            f"button_{button_num}_long_press_stop"
        ])
    return trigger_types


# Default trigger types for validation (all possible triggers)
ALL_TRIGGER_TYPES = get_trigger_types_for_button_count(8)

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(ALL_TRIGGER_TYPES)}
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return triggers for Dali Center panel devices."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    if (
        not device
        or not device.model
        or not device.model.startswith("Panel Type")
    ):
        return []

    # Extract dev_type from device model (e.g., "Panel Type 0304" -> "0304")
    dev_type = device.model.replace("Panel Type ", "")
    button_count = get_panel_button_count(dev_type)
    trigger_types = get_trigger_types_for_button_count(button_count)

    return [
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in trigger_types
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach trigger for Dali Center panel button events."""
    event_config = event_trigger.TRIGGER_SCHEMA({
        event_trigger.CONF_PLATFORM: "event",
        event_trigger.CONF_EVENT_TYPE: "dali_center_button_event",
        event_trigger.CONF_EVENT_DATA: {
            "device_id": config[CONF_DEVICE_ID],
            "trigger_type": config[CONF_TYPE],
        },
    })

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )


async def fire_device_triggers(
    hass: HomeAssistant, device_id: str, property_list: list
) -> None:
    """Fire device triggers for panel button events."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    device_name = device.name if device else "DALI Panel"

    for prop in property_list:
        dpid = prop.get("dpid")
        key_no = prop.get("keyNo")

        event_type = BUTTON_EVENTS.get(dpid)
        if event_type and key_no:
            if event_type == "press":
                # Handle press events by triggering Button entity
                await _trigger_button_press(hass, device_id, key_no)
                return

            # Handle advanced gestures via device triggers
            # Skip rotate events for now
            if event_type == "rotate":
                continue

            trigger_type = f"button_{key_no}_{event_type}"

            event_data = {
                "device_id": device_id,
                "trigger_type": trigger_type,
            }

            hass.bus.async_fire(
                "dali_center_button_event",
                event_data,
            )

            # Add logbook entry for visibility
            await hass.services.async_call(
                "logbook",
                "log",
                {
                    "name": f"{device_name} Button {key_no}",
                    "message": f"{event_type.replace('_', ' ').title()} event",
                    "domain": DOMAIN,
                },
                blocking=False
            )


async def _trigger_button_press(hass: HomeAssistant, device_id: str, button_id: int) -> None:
    """Trigger Button entity press event from hardware."""

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Get device from registry
    device = device_registry.async_get(device_id)
    if not device:
        return

    device_name = device.name if device else "DALI Panel"

    # Find the button entity for this device and button ID
    for entity_entry in er.async_entries_for_device(entity_registry, device_id):
        if entity_entry.domain == "button" and entity_entry.unique_id.endswith(f"_btn_{button_id}"):
            # Trigger the button press service
            await hass.services.async_call(
                "button",
                "press",
                {"entity_id": entity_entry.entity_id},
                blocking=True
            )

            # Add logbook entry for visibility
            await hass.services.async_call(
                "logbook",
                "log",
                {
                    "name": f"{device_name} Button {button_id}",
                    "message": "Press event",
                    "domain": DOMAIN,
                },
                blocking=False
            )
            break
