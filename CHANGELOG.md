# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-07-23

### Added
- Switch platform support for DALI device control (#11)
- Enhanced sensor on/off handling capabilities (#11)
- Additional gateway information display (#10)
- MQTTS (secure MQTT) protocol support (#9)

### Fixed
- Improved error handling and logging throughout the integration (#13)
- Enhanced debug logging capabilities for better troubleshooting
- Resolved mypy and pylint code quality issues

### Technical
- Updated PySrDaliGateway dependency to v0.3.0 (54a9e24)
- Enhanced bug report template with detailed logging instructions (a81c45c)

## [0.1.2] - 2025-07-15

### Added

- Automated release workflow for streamlined version management (8300c73)
- Enhanced bug report forms with improved log instructions (234a2d7, c7b5394)

### Changed

- Updated PySrDaliGateway dependency to version 0.1.4 for improved compatibility (6448845)
- Simplified event handling logic for better performance (6448845)
- Simplified bug report form by removing description field (a2f403b)

### Fixed

- Code scanning security alert regarding workflow permissions (#5)

### Infrastructure

- Added comprehensive CI/CD pipeline with automated release management
- Enhanced issue templates for better bug reporting experience

## [0.1.1] - 2025-07-10

### Added

- HACS integration support for one-click installation
- CodeQL code quality analysis workflow
- Comprehensive entity handling improvements

### Changed

- **BREAKING**: Migrated panel sensors to event entities for improved handling
- Updated to PySrDaliGateway library v0.1.3 (replacing internal DALI Gateway)
- Refactored import structure for better maintainability
- Updated installation guide with HACS one-click integration instructions
- Improved DALI Center logo using Home Assistant brand assets

### Fixed

- Panel sensor handling now uses proper event entities
- Default brightness and RGBW color values for light entities
- Type checking issues (mypy/pylint) resolved
- Hassfest validation issues fixed

### Removed

- Removed unused dependencies and cleaned up requirements structure
- Replaced internal DALI Gateway implementation with external library

## [0.1.0] - 2025-07-07

### Added

- Initial release of DALI Center integration for Home Assistant
- Automatic gateway discovery via network scanning
- Support for DALI lighting devices with brightness and on/off control
- DALI group control for managing multiple devices simultaneously
- Scene activation with dedicated button entities
- Energy monitoring sensors for power consumption tracking
- Motion sensor support for DALI motion detection devices
- Illuminance sensor support for DALI light sensors
- Panel button support for multi-key DALI control panels
- Real-time device status updates via MQTT
- Configuration flow with gateway selection and device discovery
- Entity selection with diff display for easy setup
- Multi-platform support (Light, Sensor, Button entities)
- Comprehensive device registry management
- Gateway offline/online status monitoring

### Technical Features

- MQTT communication with DALI Center gateways
- Device discovery and entity management
- Type-safe TypedDict definitions for all data structures
- Async/await support throughout the codebase
- Proper Home Assistant integration patterns
- Comprehensive test coverage

### Supported Device Types

- DALI Dimmer devices (Type 01xx)
- DALI CCT, RGB, XY, RGBW, RGBWA devices
- DALI Motion sensors (Type 02xx)
- DALI Illuminance sensors
- DALI Control panels (2-Key, 4-Key, 6-Key, 8-Key)
- DALI Groups and Scenes

[Unreleased]: https://github.com/maginawin/ha-dali-center/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/maginawin/ha-dali-center/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/maginawin/ha-dali-center/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/maginawin/ha-dali-center/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/maginawin/ha-dali-center/releases/tag/v0.1.0
