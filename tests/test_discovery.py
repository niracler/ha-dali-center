#!/usr/bin/env python3
"""Test script for multi-interface Dali Gateway Discovery"""

from custom_components.dali_center.gateway.discovery import DaliGatewayDiscovery
import asyncio
import logging
import pytest


# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_discovery():
    """Test the multi-interface gateway discovery"""
    logger.info("Starting multi-interface gateway discovery test")

    discovery = DaliGatewayDiscovery()

    # Test interface detection
    logger.info("Detecting network interfaces...")
    interfaces = discovery._get_valid_interfaces()  # pylint: disable=protected-access
    logger.info("Found %s network interfaces:", len(interfaces))
    for interface in interfaces:
        logger.info(
            "  %s: %s (%s)",
            interface["name"],
            interface["address"],
            interface["network"]
        )

    # Test gateway discovery
    logger.info("Starting gateway discovery...")
    gateways = await discovery.discover_gateways()

    logger.info("Discovery completed! Found %s gateways:", len(gateways))
    for gateway in gateways:
        interface_info = getattr(gateway, "_discovered_interface", "Unknown")
        logger.info("  Gateway: %s", gateway["gw_sn"])
        logger.info(
            "    IP: %s", gateway["gw_ip"]
        )
        logger.info(
            "    Port: %s", gateway["port"]
        )
        logger.info("    Name: %s", gateway["name"])
        logger.info("    Discovery interface: %s", interface_info)
        logger.info(
            "    Channel total: %s",
            gateway["channel_total"]
        )
        logger.info("    ---")

if __name__ == "__main__":
    try:
        asyncio.run(test_discovery())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Test error: %s", e)
        import traceback  # pylint: disable=import-outside-toplevel
        traceback.print_exc()
