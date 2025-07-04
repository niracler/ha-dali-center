"""Type definitions for the Dali Center integration."""

from typing import TypedDict
from homeassistant.config_entries import ConfigEntry

from .gateway.device import DeviceType
from .gateway.scene import SceneType
from .gateway.group import GroupType
from .gateway import DaliGatewayType


class ConfigData(TypedDict, total=False):
    """Contains configuration data for the integration."""
    sn: str                   # Gateway serial number
    gateway: DaliGatewayType  # Gateway object
    devices: list[DeviceType]     # Device list
    groups: list[GroupType]       # Group list
    scenes: list[SceneType]       # Scene list


type DaliCenterConfigEntry = ConfigEntry[ConfigData]
