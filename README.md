# ZHC Heating Scheduler

A Home Assistant custom integration that automatically controls heating based on a field hockey club's schedule. The integration scrapes event schedules from a website and intelligently heats the club building before training sessions and matches.

**🏑 Specifically configured for Zandvoortsche Hockey Club (ZHC)** - Includes custom scraper for the LISA-powered schedule system used at https://www.zandvoortschehockeyclub.nl

> **Quick Start for ZHC**: See [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md) for step-by-step instructions specific to ZHC's website.

## Features

- **Automatic Schedule Scraping**: Fetches events from your club's website
- **Smart Pre-heating**: Starts heating before events to ensure the building is warm when people arrive
- **Cool-down Period**: Stops heating before events end to save energy
- **Flexible Configuration**: Both YAML and UI configuration support
- **Manual Overrides**: Temporarily override the schedule when needed
- **Rich Sensors**: Expose schedule information for use in automations and dashboards
- **Dry Run Mode**: Test the integration without actually controlling your heating
- **Plugwise Integration**: Designed to work with Plugwise SA thermostats

## Installation

> **For ZHC members**: Follow the [ZHC Setup Guide](ZHC_SETUP_GUIDE.md) for detailed instructions with the ZHC-specific scraper.

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/stefan/zhc-heating-scheduler`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "ZHC Heating Scheduler"
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/zhc_heating_scheduler` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### UI Configuration (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "ZHC Heating Scheduler"
4. Fill in the configuration form:
   - **Schedule URL**: URL of the website containing your club's schedule
   - **Climate Entity**: The entity ID of your Plugwise thermostat (e.g., `climate.plugwise_sa`)
   - **Pre-heat time**: How many hours before events to start heating (default: 2)
   - **Cool-down time**: How many minutes before event end to stop heating (default: 30)
   - **Target temperature**: Desired temperature in °C (default: 20)
   - **Scan interval**: How often to refresh the schedule in seconds (default: 21600 = 6 hours)
   - **Dry run mode**: Enable to test without controlling heating (default: off)

### YAML Configuration

Add to your `configuration.yaml`:

```yaml
zhc_heating_scheduler:
  schedule_url: "https://your-club-website.com/schedule"
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20.0
  scan_interval: 21600  # 6 hours
  enabled: true
  dry_run: false
```

## Sensors

The integration provides several sensors:

### Regular Sensors

- **sensor.zhc_next_heating_start**: Timestamp of when heating will next start
- **sensor.zhc_next_heating_stop**: Timestamp of when heating will next stop
- **sensor.zhc_current_event**: Name and details of the current or next event
- **sensor.zhc_events_today**: Number of heating windows today
- **sensor.zhc_heating_minutes_today**: Total heating minutes scheduled for today
- **sensor.zhc_total_heating_windows**: Total number of scheduled heating windows
- **sensor.zhc_last_schedule_update**: Timestamp of last schedule refresh

### Binary Sensors

- **binary_sensor.zhc_heating_active**: Whether heating should currently be active
- **binary_sensor.zhc_scheduler_enabled**: Whether the scheduler is enabled
- **binary_sensor.zhc_manual_override**: Whether a manual override is active

## Services

### `zhc_heating_scheduler.refresh_schedule`

Force an immediate refresh of the event schedule from the website.

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

### `zhc_heating_scheduler.enable`

Enable the heating scheduler.

```yaml
service: zhc_heating_scheduler.enable
```

### `zhc_heating_scheduler.disable`

Disable the heating scheduler (stops automatic heating control).

```yaml
service: zhc_heating_scheduler.disable
```

### `zhc_heating_scheduler.set_override`

Manually override the schedule to force heating for a specific period.

```yaml
service: zhc_heating_scheduler.set_override
data:
  start_time: "2024-11-24T14:00:00"
  end_time: "2024-11-24T18:00:00"
```

### `zhc_heating_scheduler.clear_override`

Clear any manual override and resume normal scheduling.

```yaml
service: zhc_heating_scheduler.clear_override
```

## Automation Examples

### Notify When Heating Starts

```yaml
automation:
  - alias: "Notify when club heating starts"
    trigger:
      - platform: state
        entity_id: binary_sensor.zhc_heating_active
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Club Heating Started"
          message: "Heating started for {{ state_attr('sensor.zhc_current_event', 'events')[0].title }}"
```

### Emergency Override Button

```yaml
script:
  emergency_heating:
    alias: "Emergency Heating (2 hours)"
    sequence:
      - service: zhc_heating_scheduler.set_override
        data:
          start_time: "{{ now().isoformat() }}"
          end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

### Dashboard Card

```yaml
type: entities
entities:
  - entity: binary_sensor.zhc_heating_active
  - entity: sensor.zhc_current_event
  - entity: sensor.zhc_next_heating_start
  - entity: sensor.zhc_next_heating_stop
  - entity: sensor.zhc_heating_minutes_today
  - type: button
    name: Refresh Schedule
    tap_action:
      action: call-service
      service: zhc_heating_scheduler.refresh_schedule
```

## Customizing the Scraper

### For ZHC (Zandvoortsche Hockey Club)

A custom scraper is **already included** for ZHC's LISA-powered website:
- See [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md) for setup instructions
- The scraper handles both training and match schedules
- Includes a test script to verify it works

### For Other Clubs

The default scraper uses generic HTML parsing to find events. If your club's website has a specific format, you can customize the scraper:

1. See `SCRAPER_GUIDE.md` for detailed instructions
2. Create a custom scraper class that inherits from `ScheduleScraper`
3. Override the `_parse_html()` method with your site-specific logic

## Troubleshooting

### No Events Found

- Check that the schedule URL is correct and accessible
- Enable debug logging to see what HTML is being fetched
- You may need to customize the scraper for your specific website

### Heating Not Starting

- Check that `binary_sensor.zhc_scheduler_enabled` is "on"
- Verify your climate entity is correct
- Check that there are upcoming events in the schedule
- Look at `sensor.zhc_next_heating_start` to see when heating is scheduled
- Try enabling dry run mode to see what the scheduler would do

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: debug
```

## Development

See `DEVELOPMENT.md` for information on:
- Setting up a development environment
- Running tests
- Contributing to the project

## Requirements

- Home Assistant 2024.1.0 or newer
- A climate entity (Plugwise SA recommended)
- Python 3.11 or newer

## License

MIT License - See LICENSE file for details

## Support

- **Issues**: https://github.com/stefan/zhc-heating-scheduler/issues
- **Discussions**: https://github.com/stefan/zhc-heating-scheduler/discussions

## Credits

Created for the field hockey club to automate heating management and reduce energy costs while ensuring comfort during events.
