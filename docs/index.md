---
title: ZHC Heating Scheduler Documentation
tags: [home, index]
---

# ZHC Heating Scheduler

Welcome to the **ZHC Heating Scheduler** documentation! This Home Assistant integration automatically controls your field hockey club's heating based on training and match schedules.

## Quick Navigation

### 🚀 Getting Started

**New users start here:**
- [[quick-start/installation-ui|Installation via UI]] - No terminal needed!
- [[quick-start/installation-yaml|Installation via YAML]] - For advanced users
- [[quick-start/first-time-setup|First Time Setup]] - Configure after installation
- [[quick-start/testing-dry-run|Testing with Dry Run]] - Test safely

### ⚙️ Configuration

- [[configuration/basic-settings|Basic Settings]] - Pre-heat, cool-down, temperature
- [[configuration/advanced-settings|Advanced Settings]] - Scan interval, timezone
- [[configuration/scraper-configuration|Scraper Configuration]] - **NEW!** Configure without code
- [[configuration/timing-optimization|Timing Optimization]] - Fine-tune heating times
- [[configuration/examples|Configuration Examples]] - Real-world examples

### 🔍 Scraper Setup

- [[scraper/overview|Scraper Overview]] - How scraping works
- [[scraper/configuring-scraper|Configuring Scraper]] - **NEW!** No-code setup
- [[scraper/zhc-specific|ZHC-Specific Setup]] - For Zandvoortsche Hockey Club
- [[scraper/troubleshooting|Scraper Troubleshooting]] - Fix scraping issues
- [[scraper/testing|Testing Your Scraper]] - Verify it works

### 📊 Usage

- [[usage/sensors|Available Sensors]] - What data is exposed
- [[usage/services|Available Services]] - How to control the scheduler
- [[usage/automations|Example Automations]] - Notifications and more
- [[usage/dashboard-cards|Dashboard Cards]] - Display schedule info
- [[usage/notifications|Notifications]] - Get alerts

### 🔧 Troubleshooting

- [[troubleshooting/common-issues|Common Issues]] - FAQ
- [[troubleshooting/no-events-found|No Events Found]] - Fix scraper issues
- [[troubleshooting/heating-not-starting|Heating Not Starting]] - Control problems
- [[troubleshooting/debugging|Debug Logging]] - Enable detailed logs

### 💻 Development

- [[development/setup|Development Setup]] - For contributors
- [[development/testing|Running Tests]] - Test the code
- [[development/contributing|Contributing Guide]] - How to contribute
- [[development/architecture|Technical Architecture]] - How it works

### 📚 Reference

- [[reference/configuration-options|All Configuration Options]] - Complete reference
- [[reference/api-reference|API Reference]] - Code documentation
- [[reference/changelog|Changelog]] - Version history

## Start Here Guides

### I want to install via UI (Easiest)
1. [[quick-start/installation-ui|Install via UI]]
2. [[quick-start/first-time-setup|First Time Setup]]
3. [[quick-start/testing-dry-run|Test with Dry Run]]
4. [[usage/dashboard-cards|Create Dashboard]]

### I want to use YAML configuration
1. [[quick-start/installation-yaml|Install via YAML]]
2. [[configuration/basic-settings|Configure Settings]]
3. [[scraper/configuring-scraper|Configure Scraper]]
4. [[troubleshooting/debugging|Enable Debug Logs]]

### My website isn't working (No events found)
1. [[troubleshooting/no-events-found|No Events Found Guide]]
2. [[scraper/configuring-scraper|Configure Custom Scraper]]
3. [[scraper/testing|Test Your Configuration]]
4. [[scraper/troubleshooting|Scraper Troubleshooting]]

### I'm a developer
1. [[development/setup|Set Up Development Environment]]
2. [[development/architecture|Understand the Architecture]]
3. [[development/testing|Run Tests]]
4. [[development/contributing|Contribute]]

## Features

### ✅ Automatic Heating Control
- Heats building before events start
- Smart pre-heat timing
- Energy-saving cool-down period
- Works with Plugwise SA and other climate entities

### ✅ Flexible Scraping
- **NEW:** Configure scraper without code!
- Support for multiple schedule URLs
- HTML, API, and iCal sources
- Easy to adapt for different websites

### ✅ Rich Integration
- Multiple sensors for schedule data
- Services for manual control
- Automations for notifications
- Beautiful dashboard cards

### ✅ Safe Testing
- Dry run mode for testing
- Manual overrides for emergencies
- Detailed logging
- Configuration validation

## What's New

### Version 0.2.0 - Configurable Scraper
- ✨ **No-code scraper configuration** via YAML/UI
- ✨ **Multiple source support** (training + matches)
- ✨ **CSS selector configuration** - no Python needed
- ✨ **API and iCal support** built-in
- ✨ **Configuration validator** with helpful errors
- 📚 **Reorganized documentation** in Obsidian style
- 📚 **New UI installation guide** for beginners

See [[reference/changelog|full changelog]] for details.

## Key Concepts

### Pre-heat Time
Hours before an event to start heating. The building needs time to warm up!

**Example:** With 2 hours pre-heat, heating starts at 12:00 for a 14:00 event.

### Cool-down Time
Minutes before an event ends to stop heating. Saves energy while building stays warm.

**Example:** With 30 minutes cool-down, heating stops at 15:30 for a 16:00 event end.

### Heating Windows
Calculated time periods when heating should be active, including pre-heat and cool-down.

### Scraper
The component that fetches event schedules from your website. Now configurable without coding!

## Quick Examples

### Basic YAML Configuration

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20
  
  scraper_sources:
    - url: "https://www.club.com/schedule"
      type: training
      selectors:
        container: "div.event"
        date: "span.date"
        time: "span.time"
```

### Emergency Heating Script

```yaml
script:
  emergency_heating:
    sequence:
      - service: zhc_heating_scheduler.set_override
        data:
          start_time: "{{ now().isoformat() }}"
          end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

### Dashboard Card

```yaml
type: entities
title: Club Heating
entities:
  - binary_sensor.zhc_heating_active
  - sensor.zhc_current_event
  - sensor.zhc_next_heating_start
  - sensor.zhc_heating_minutes_today
```

## Support

- **Issues:** [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)
- **Forum:** [Home Assistant Community](https://community.home-assistant.io/)
- **Discussions:** [GitHub Discussions](https://github.com/stefan/zhc-heating-scheduler/discussions)

## License

MIT License - See LICENSE file for details.

---

**Ready to get started?** → [[quick-start/installation-ui|Install Now]]

**Need help?** → [[troubleshooting/common-issues|Common Issues]]

**Want to customize?** → [[scraper/configuring-scraper|Configure Scraper]]

