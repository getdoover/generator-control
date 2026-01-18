# Generator Control

<!-- ![Doover Logo](https://doover.com/wp-content/uploads/Doover-Logo-Landscape-Navy-padded-small.png) -->
<img src="https://doover.com/wp-content/uploads/Doover-Logo-Landscape-Navy-padded-small.png" alt="App Icon" style="max-width: 300px;">

**Control generators with warmup/cooldown cycles, run sensing, and error notifications.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/getdoover/generator-control)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/getdoover/generator-control/blob/main/LICENSE)

[Configuration](#configuration) | [Developer](https://github.com/getdoover/generator-control/blob/main/DEVELOPMENT.md) | [Need Help?](#need-help)

<br/>

## Overview

Control generators with warmup/cooldown cycles, run sensing, and error notifications.

<br/>

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Display Name** | Display name for the generator | `Engine` |
| **Run Command Pin** | Output pin to control the generator | `0` |
| **Run Sense Pins** | Input pins to detect generator running | `Required` |
| **Warmup Time** | Seconds to warm up | `60` |
| **Cooldown Time** | Seconds to cool down | `30` |

<br/>
## Integrations

### Tags

This app exposes the following tags for integration with other apps:

| Tag | Description |
|-----|-------------|
| `state` | Current state of the generator (off, running_user, running_auto, etc.) |
| `run_request_reason` | Reason for the current run request from another app |

<br/>
This app works seamlessly with:

- **Platform Interface**: Core Doover platform component


<br/>

## Need Help?

- Email: support@doover.com
- [Community Forum](https://doover.com/community)
- [Full Documentation](https://docs.doover.com)
- [Developer Documentation](https://github.com/getdoover/generator-control/blob/main/DEVELOPMENT.md)

<br/>

## Version History

### v1.0.0 (Current)
- Initial release

<br/>

## License

This app is licensed under the [Apache License 2.0](https://github.com/getdoover/generator-control/blob/main/LICENSE).
