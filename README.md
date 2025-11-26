# ZHC Heating Scheduler

Automatic heating control for field hockey clubs based on training and match schedules.

## Quick Start

**→ [Complete Documentation](docs/index.md)** ←

### Installation

1. Install via HACS or manually
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "ZHC Heating Scheduler"
5. Follow the setup wizard

**Detailed guide:** [Installation via UI](docs/quick-start/installation-ui.md)

### Features

- ✅ **Automatic heating** before events
- ✅ **Configurable scraper** - no coding needed!
- ✅ **Multiple sources** - training + matches
- ✅ **Smart timing** - pre-heat and cool-down
- ✅ **Safe testing** - dry run mode
- ✅ **Rich sensors** - schedule visibility
- ✅ **Manual override** - emergency heating

## Configuration

### Basic YAML Example

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  scraper_sources:
    - url: "https://www.club.com/schedule"
      type: training
      selectors:
        container: "div.event"
        date: "span.date"
        time: "span.time"
```

**More examples:** [Configuration Guide](docs/configuration/examples.md)

## New in v0.2.0

🎉 **Configurable Scraper System**
- Configure scraper via YAML/UI without code
- Support multiple URLs (training + matches)
- CSS selectors, API endpoints, iCal feeds
- Easy to adapt for any website

📚 **Reorganized Documentation**
- Obsidian-style docs folder
- Clear navigation and structure
- New UI installation guide
- Comprehensive scraper guide

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](docs/quick-start/installation-ui.md) | Installation and setup |
| [Configuration](docs/configuration/basic-settings.md) | Settings and options |
| [Scraper Setup](docs/scraper/configuring-scraper.md) | Configure without code |
| [Usage](docs/usage/sensors.md) | Sensors, services, automations |
| [Troubleshooting](docs/troubleshooting/common-issues.md) | Fix common problems |
| [Development](docs/development/setup.md) | Contributing |

**→ [Full Documentation Index](docs/index.md)**

## Support

- **Issues:** [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)
- **Forum:** [Home Assistant Community](https://community.home-assistant.io/)
- **Guide:** [Troubleshooting](docs/troubleshooting/common-issues.md)

## Requirements

- Home Assistant 2024.1.0+
- Climate entity (Plugwise SA recommended)
- Python 3.11+

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

Created for the Zandvoortsche Hockey Club to automate heating and reduce energy costs.
