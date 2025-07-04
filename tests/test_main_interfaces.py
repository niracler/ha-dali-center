#!/usr/bin/env python3
"""Test script for main network interfaces (Ethernet and WiFi)"""

from custom_components.dali_center.gateway.discovery import DaliGatewayDiscovery  # pylint: disable=wrong-import-position
import asyncio
import logging
import pytest


# Set up logging
import os
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
level = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure discovery module logging is also properly displayed
discovery_logger = logging.getLogger(
    "custom_components.dali_center.gateway.discovery"
)
discovery_logger.setLevel(level)


@pytest.mark.asyncio
async def test_main_interfaces():
    """Test discovery on main network interfaces only"""
    logger.info("Starting gateway discovery on main network interfaces...")

    discovery = DaliGatewayDiscovery()

    # Get all interfaces
    all_interfaces = discovery._get_valid_interfaces()  # pylint: disable=protected-access

    # Filter to main interfaces (en0 and en1)
    main_interfaces = [
        iface for iface in all_interfaces
        if iface["name"] in ["en0", "en1"]
    ]

    logger.info("Found %s main network interfaces:", len(main_interfaces))
    for interface in main_interfaces:
        network_type = (
            "Ethernet" if interface["name"] == "en0" else "WiFi"
        )
        logger.info(
            "  %s: %s (%s)",
            interface["name"],
            interface["address"],
            network_type
        )

    if not main_interfaces:
        logger.warning("No main network interfaces found")
        return

    # Test gateway discovery
    logger.info("Starting gateway discovery...")
    gateways = await discovery.discover_gateways()

    logger.info("Discovery completed! Found %s gateways:", len(gateways))

    if gateways:
        for i, gateway in enumerate(gateways, 1):
            interface_info = getattr(
                gateway, "_discovered_interface", "Unknown")
            network_type = (
                "Ethernet network" if gateway["gw_ip"].startswith(
                    "192.168.1") else "WiFi network"
            )

            logger.info("  Gateway %s:", i)
            logger.info("    Serial: %s", gateway["gw_sn"])
            logger.info("    IP address: %s (%s)", gateway["gw_ip"],
                        network_type)
            logger.info("    Port: %s",
                        gateway["port"])
            logger.info("    Name: %s", gateway["name"])
            logger.info("    Discovery interface: %s", interface_info)
            logger.info("    Channel count: %s",
                        len(gateway["channel_total"]))
            logger.info("    %s", "-" * 40)
    else:
        logger.info("  No gateways found")
        logger.info("  Possible reasons:")
        logger.info("    - Gateway device not powered on")
        logger.info("    - Gateway not on the same network")
        logger.info("    - Firewall blocking multicast traffic")

if __name__ == "__main__":
    try:
        asyncio.run(test_main_interfaces())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Test error: %s", e)
        import traceback  # pylint: disable=import-outside-toplevel
        traceback.print_exc()
