---
title: LISA Scheduler Documentation
tags: [home, index]
---

# LISA Scheduler

Welcome to the **LISA Scheduler** documentation! This Home Assistant integration scrapes a sports club's event schedule from a website and fires HA bus events on transitions, so your automations can trigger any action — heating, lighting, notifications, screens, and more. It does not control devices directly.

## Quick Navigation

### Getting Started

**New users start here:**
- [[quick-start/installation-ui|Installation via UI]] - No terminal needed!
- [[quick-start/installation-yaml|Installation via YAML]] - For advanced users
- [[quick-start/first-time-setup|First Time Setup]] - Configure after installation
- [[quick-start/testing-dry-run|Testing with Dry Run]] - Test safely before going live

### Configuration

- [[configuration/basic-settings|Basic Settings]] - Pre-event triggers, lead times, scan interval
- [[configuration/advanced-settings|Advanced Settings]] - Timezone, logo URL, dry run mode
- [[configuration/scraper-configuration|Scraper Configuration]] - Configure without writing code
- [[configuration/timing-optimization|Timing Optimization]] - Fine-tune trigger times
- [[configuration/examples|Configuration Examples]] - Real-world examples

### Scraper Setup

- [[scraper/overview|Scraper Overview]] - How schedule scraping works
- [[scraper/configuring-scraper|Configuring Scraper]] - No-code setup with CSS selectors
- [[scraper/troubleshooting|Scraper Troubleshooting]] - Fix scraping issues
- [[scraper/testing|Testing Your Scraper]] - Verify it works before deploying

### Usage

- [[usage/sensors|Available Sensors]] - What data is exposed
- [[usage/services|Available Services]] - How to control the scheduler
- [[usage/automations|Example Automations]] - Heating, lighting, notifications, and more
- [[usage/dashboard-cards|Dashboard Cards]] - Display schedule info
- [[usage/notifications|Notifications]] - Get alerts for upcoming events

### Troubleshooting

- [[troubleshooting/common-issues|Common Issues]] - FAQ
- [[troubleshooting/no-events-found|No Events Found]] - Fix scraper issues
- [[troubleshooting/actions-not-triggering|Actions Not Triggering]] - Automation problems
- [[troubleshooting/debugging|Debug Logging]] - Enable detailed logs

### Development

- [[development/setup|Development Setup]] - For contributors
- [[development/testing|Running Tests]] - Test the code
- [[development/contributing|Contributing Guide]] - How to contribute
- [[development/architecture|Technical Architecture]] - How it works internally

### Reference

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

## How It Works

LISA Scheduler follows a four-step flow:

1. **Scrape** — On each scan interval (default: every 6 hours), the integration fetches your club's event schedule from the configured URL.
2. **Calculate windows** — Each event is expanded into an event window: the window opens `pre_event_triggers` minutes before the event starts and closes when the event ends. Overlapping windows are merged.
3. **Detect transitions** — Every 60 seconds the coordinator checks whether the window or event state has changed since the last poll.
4. **Fire events — your automations act** — When a transition is detected, the integration fires a Home Assistant bus event. Your automations listen for these events and perform any action you choose.

## Features

### Schedule Scraping
- Fetches event schedules automatically on a configurable interval
- Supports HTML, API, and iCal sources
- Configurable scraper with CSS selectors — no Python required
- Multiple source URLs (e.g. separate training and match pages)

### HA Bus Events
- Fires 5 distinct events covering the full event lifecycle
- Multiple configurable pre-event trigger times (e.g. 120 and 30 minutes before)
- Event payloads carry the full window dict and `minutes_before` for pre-event triggers
- Device triggers available in the HA UI for use in automation editors

### Flexible Automation
- Works with any HA action: climate, lights, media players, notifications, scripts
- No assumptions about what you automate — the integration only fires events

### Safe Testing
- Dry run mode logs what would fire without actually firing HA events
- Manual overrides for emergency or ad-hoc windows
- Detailed debug logging

### Display
- Optional `logo_url` field shows your club logo as an entity picture on all entities
- Multiple sensors expose schedule data for dashboards

## Quick Example

Listen to `lisa_scheduler_window_started` in an automation to act when the pre-event window opens:

```yaml
automation:
  - alias: "Turn on lights when event window opens"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      - service: light.turn_on
        target:
          entity_id: light.clubhouse
```

Listen to `lisa_scheduler_pre_event_trigger` to act at specific lead times:

```yaml
automation:
  - alias: "Send notification 30 minutes before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
        event_data:
          minutes_before: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Event starts in 30 minutes!"
```

## HA Events Reference

| Event | When it fires | Key payload fields |
|-------|---------------|--------------------|
| `lisa_scheduler_window_started` | Pre-event window opens | Full window dict |
| `lisa_scheduler_window_ended` | Window closes (after event ends) | — |
| `lisa_scheduler_event_started` | Actual event begins | — |
| `lisa_scheduler_event_ended` | Event ends | — |
| `lisa_scheduler_pre_event_trigger` | Each configured lead time | `minutes_before: N` |

## Services

| Service | Description |
|---------|-------------|
| `lisa_scheduler.refresh_schedule` | Force an immediate schedule fetch |
| `lisa_scheduler.enable` | Re-enable the scheduler |
| `lisa_scheduler.disable` | Pause all event firing |
| `lisa_scheduler.set_override` | Activate a manual window override |
| `lisa_scheduler.clear_override` | Remove the active manual override |

## Support

- **Issues:** [GitHub Issues](https://github.com/stefan/home-assistant-lisa-scheduler/issues)
- **Forum:** [Home Assistant Community](https://community.home-assistant.io/)
- **Discussions:** [GitHub Discussions](https://github.com/stefan/home-assistant-lisa-scheduler/discussions)

## License

MIT License - See LICENSE file for details.

---

**Ready to get started?** -> [[quick-start/installation-ui|Install Now]]

**Need help?** -> [[troubleshooting/common-issues|Common Issues]]

**Want to customize?** -> [[scraper/configuring-scraper|Configure Scraper]]
