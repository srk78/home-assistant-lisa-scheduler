---
title: Installation via YAML Configuration
tags: [quickstart, installation, yaml, advanced]
---

# Installation via YAML Configuration

This guide shows you how to install and configure the LISA Scheduler using YAML configuration files. This method is for users comfortable with editing Home Assistant configuration files.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- Access to Home Assistant configuration files
- Access to your club's schedule webpage

## Step 1: Install the Integration

### Option A: Via HACS

1. Open **HACS** in your Home Assistant instance
2. Go to **Integrations**
3. Click the three dots (⋮) → **Custom repositories**
4. Add repository:
   - **URL**: `https://github.com/stefan/lisa-scheduler`
   - **Category**: Integration
5. Search for "LISA Scheduler" and install
6. Restart Home Assistant

### Option B: Manual Installation

1. Download the latest release from GitHub
2. Extract the `lisa_scheduler` folder to:
   ```
   config/custom_components/lisa_scheduler/
   ```
3. Restart Home Assistant

## Step 2: Configure via YAML

Add the integration to your `configuration.yaml`. The LISA Scheduler fires Home Assistant bus events on schedule transitions; automations in `automations.yaml` (or defined inline) respond to those events.

### Basic Configuration

```yaml
lisa_scheduler:
  # Required
  schedule_url: "https://www.myclub.nl/schedule"

  # Optional — club logo shown as entity picture
  logo_url: "https://www.myclub.nl/logo.png"

  # Optional — minutes before each event to fire pre_event_trigger events
  # List one or more values; omit to disable pre-event triggers
  pre_event_triggers:
    - 120
    - 30

  # How often to re-fetch the schedule (seconds, default: 21600)
  scan_interval: 21600

  # Start with dry_run enabled; set to false once verified
  dry_run: true
```

### Advanced Configuration with Scraper Sources

```yaml
lisa_scheduler:
  # Optional club logo
  logo_url: "https://www.myclub.nl/logo.png"

  # Pre-event triggers at 120 and 30 minutes before each event
  pre_event_triggers:
    - 120
    - 30

  # Configurable scraper — multiple URLs/source types supported
  scraper_sources:
    - url: "https://www.myclub.nl/training-schedule"
      type: training
      method: html
      selectors:
        container: "div.event-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"

    - url: "https://www.myclub.nl/match-schedule"
      type: match
      method: html
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"

  # Date/time parsing
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  timezone: "Europe/Amsterdam"

  scan_interval: 21600
  dry_run: true
```

### Example Automations

The integration does not control devices directly. It fires these HA bus events, which your automations act on:

| Event | When |
|-------|------|
| `lisa_scheduler_window_started` | Pre-event window opens (lead time before event) |
| `lisa_scheduler_window_ended` | Window closes (after event ends) |
| `lisa_scheduler_event_started` | Actual event begins |
| `lisa_scheduler_event_ended` | Actual event ends |
| `lisa_scheduler_pre_event_trigger` | Each configured pre-event trigger time; payload includes `minutes_before` |

**Basic notification example:**

```yaml
automation:
  - alias: "Notify when pre-event window opens"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      - service: notify.notify
        data:
          message: "Pre-event window opened for an upcoming club event."
```

**Pre-event trigger example (different actions per lead time):**

```yaml
automation:
  - alias: "Act on pre-event trigger"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 120 }}"
            sequence:
              - service: notify.notify
                data:
                  message: "Event in 2 hours — time to prepare."
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 30 }}"
            sequence:
              - service: notify.notify
                data:
                  message: "Event in 30 minutes."
```

## Step 3: Validate Configuration

Before restarting, check your configuration:

1. Go to **Developer Tools** → **YAML**
2. Click **Check Configuration**
3. Look for any errors related to `lisa_scheduler`

## Step 4: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**
2. Click **Restart**
3. Wait for Home Assistant to come back online

## Step 5: Verify Installation

### Check Logs

1. Go to **Settings** → **System** → **Logs**
2. Search for "lisa"
3. Look for initialization messages and "Found X events"

### Check Entities

1. Go to **Developer Tools** → **States**
2. Search for `lisa_scheduler`
3. Confirm sensors and binary sensors are present

### Test Schedule Refresh

Call the service manually to trigger an immediate re-fetch:

```yaml
service: lisa_scheduler.refresh_schedule
```

Check the logs for "Found X events".

## Configuration Reference

### Common Configurations

**Minimal:**

```yaml
lisa_scheduler:
  schedule_url: "https://club.com/schedule"
```

**Production:**

```yaml
lisa_scheduler:
  schedule_url: "https://club.com/schedule"
  logo_url: "https://club.com/logo.png"
  pre_event_triggers:
    - 120
    - 30
  scan_interval: 21600
  dry_run: false
```

**Testing (short intervals for quick feedback):**

```yaml
lisa_scheduler:
  schedule_url: "https://club.com/schedule"
  pre_event_triggers:
    - 5
  scan_interval: 600
  dry_run: true
```

## Advantages of YAML Configuration

- **Version control**: track changes in Git
- **Backup**: easy to back up and restore
- **Sharing**: share configurations with others
- **Comments**: document your configuration inline

## Troubleshooting

### Configuration Errors

**Error: "Invalid config"**
- Check YAML indentation (use spaces, not tabs)
- Verify all required fields are present
- Check that string values are quoted

**Error: "Integration not found"**
- Confirm the files are in `config/custom_components/lisa_scheduler/`
- Restart Home Assistant after installation

### Integration Not Loading

1. Check logs for error messages
2. Verify files are in the correct location
3. Try restarting Home Assistant again

## Next Steps

- [[first-time-setup|Complete First Time Setup]]
- [[../configuration/basic-settings|Configure Basic Settings]]
- [[../configuration/scraper-configuration|Configure Scraper]]

## See Also

- [[installation-ui|Installation via UI]] — easier for beginners
- [[../configuration/examples|Configuration Examples]]
- [[../troubleshooting/common-issues|Common Issues]]

---

**Difficulty**: Intermediate
**Time**: 15–20 minutes
**Next**: [[first-time-setup|First Time Setup]]
