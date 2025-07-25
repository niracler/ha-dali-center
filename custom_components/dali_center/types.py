"""Type definitions for the Dali Center integration."""

from dataclasses import dataclass
from typing import TypedDict
from homeassistant.config_entries import ConfigEntry

from PySrDaliGateway import DeviceType, SceneType, GroupType, DaliGatewayType, DaliGateway


class ConfigData(TypedDict, total=False):
    """Contains configuration data for the integration."""
    sn: str                   # Gateway serial number
    gateway: DaliGatewayType  # Gateway object
    devices: list[DeviceType]     # Device list
    groups: list[GroupType]       # Group list
    scenes: list[SceneType]       # Scene list


@dataclass
class DaliCenterData:
    """Runtime data for the Dali Center integration."""
    gateway: DaliGateway


type DaliCenterConfigEntry = ConfigEntry[DaliCenterData]
