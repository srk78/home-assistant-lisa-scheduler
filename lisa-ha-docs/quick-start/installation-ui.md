---
title: Installation via Home Assistant UI
tags: [quickstart, installation, ui]
---

# Installation via Home Assistant UI

This guide shows you how to install and configure the LISA Scheduler using only the Home Assistant user interface — no terminal or command line required.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- Access to your club's schedule webpage

## Step 1: Install the Integration

### Option A: Via HACS (Recommended)

1. Open **HACS** in your Home Assistant instance
   - Click on the sidebar menu
   - Select **HACS**

2. Go to **Integrations**
   - Click the three dots (⋮) in the top right corner
   - Select **Custom repositories**

3. Add the repository
   - **Repository URL**: `https://github.com/stefan/lisa-scheduler`
   - **Category**: Integration
   - Click **Add**

4. Install the integration
   - Search for "LISA Scheduler"
   - Click on it
   - Click **Download**
   - Wait for the download to complete

5. Restart Home Assistant
   - Go to **Settings** → **System** → **Restart**
   - Click **Restart**
   - Wait for Home Assistant to come back online

### Option B: Manual Installation (Advanced)

If you don't use HACS, you'll need to manually copy files. See [[installation-yaml|YAML Installation Guide]] for details.

## Step 2: Add the Integration

1. Navigate to **Settings** → **Devices & Services**

2. Click the **+ Add Integration** button (bottom right)

3. Search for "LISA Scheduler"
   - Type "lisa" in the search box
   - Click on **LISA Scheduler** when it appears

4. Fill in the configuration form:

### Configuration Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **Schedule URL** | Yes | The webpage containing your club's event schedule | `https://www.myclub.nl/schedule` |
| **Logo URL** | No | URL of your club's logo, shown as the entity picture | `https://www.myclub.nl/logo.png` |
| **Pre-event triggers** | No | Comma-separated minutes before each event to fire trigger events | `120, 30` |
| **Scan interval (seconds)** | No | How often to re-fetch the schedule (default: 21600) | `21600` |
| **Dry run mode** | No | Log what would happen without firing actual events — recommended for first setup | checked |

**Pre-event triggers explained**: entering `120, 30` causes the integration to fire a `lisa_scheduler_pre_event_trigger` event 120 minutes before each event and again 30 minutes before each event. Automations can listen for these to prepare in stages. Leave the field empty if you only need the standard window and event events.

5. Click **Submit**

## Step 3: Verify Installation

### Check the Integration

1. Go to **Settings** → **Devices & Services**
2. You should see "LISA Scheduler" in the list
3. Click on it to see entities

### Check the Entities

Go to **Developer Tools** → **States** and search for `lisa_scheduler`. You should see sensors and binary sensors such as:

- `sensor.lisa_scheduler_current_event`
- `sensor.lisa_scheduler_next_window_start`
- `binary_sensor.lisa_scheduler_window_active`
- `binary_sensor.lisa_scheduler_event_active`
- `binary_sensor.lisa_scheduler_enabled`

### Force a Schedule Refresh

1. Go to **Developer Tools** → **Services**
2. Select service: `lisa_scheduler.refresh_schedule`
3. Click **Call Service**
4. Check the logs (**Settings** → **System** → **Logs**, search for "lisa") for a message like "Found X events"

### Verify Events Fire

The integration fires Home Assistant bus events on schedule transitions. To confirm events are reaching the bus:

1. Go to **Developer Tools** → **Events**
2. In the **Listen to events** field, type `lisa_scheduler_*` (or a specific event such as `lisa_scheduler_window_started`)
3. Click **Start Listening**
4. Wait for an event to fire naturally, or use the `set_override` service to simulate a window immediately (see [[first-time-setup|First Time Setup]])
5. Received events will appear in the panel with their full payload

## Step 4: Test with Dry Run Mode

With dry run mode enabled (the default for a first setup), the integration logs what transitions it detects but does not fire HA bus events. Check the logs for messages like:

```
DRY RUN: Would fire event lisa_scheduler_window_started
```

This lets you confirm the scraper finds events and calculates windows correctly before going live.

## Step 5: Disable Dry Run Mode

Once you have verified the schedule is being parsed correctly:

1. Go to **Settings** → **Devices & Services**
2. Find "LISA Scheduler"
3. Click **Configure**
4. Uncheck **Dry run mode**
5. Click **Submit**

The integration will now fire HA events on every schedule transition. Create automations that listen for these events to trigger any action you need — heating, lighting, notifications, and so on.

## Step 6: Create a Dashboard Card (Optional)

1. Go to your dashboard
2. Click the three dots (⋮) → **Edit Dashboard**
3. Click **+ Add Card**
4. Choose **Entities Card**
5. Add these entities:
   - `binary_sensor.lisa_scheduler_window_active`
   - `binary_sensor.lisa_scheduler_event_active`
   - `sensor.lisa_scheduler_current_event`
   - `sensor.lisa_scheduler_next_window_start`
   - `sensor.lisa_scheduler_events_today`
6. Set a card title such as "Club Schedule"
7. Click **Save**

## Troubleshooting

### Integration Not Found

- Make sure you have restarted Home Assistant after installation
- Check that the files are in `config/custom_components/lisa_scheduler/`

### No Events Found

- Confirm the schedule URL is correct and loads in a browser
- The website may use JavaScript to render events; see [[../scraper/configuring-scraper|Scraper Configuration Guide]]

### Events Not Appearing on the Bus

- Confirm dry run mode is disabled
- Check `binary_sensor.lisa_scheduler_enabled` is ON
- Verify there are upcoming events in the sensor states

## Next Steps

- [[first-time-setup|Complete the First Time Setup]]
- [[../configuration/basic-settings|Configure Basic Settings]]
- [[../usage/automations|Create Automations]]
- [[../usage/dashboard-cards|Build Dashboard Cards]]

## Getting Help

1. Check the logs in **Settings** → **System** → **Logs**
2. Review the [[../troubleshooting/common-issues|Common Issues]] guide
3. Ask on the [Home Assistant Community Forum](https://community.home-assistant.io/)
4. Create an issue on [GitHub](https://github.com/stefan/lisa-scheduler/issues)

---

**Estimated time**: 10–15 minutes
**Difficulty**: Easy
**Next**: [[first-time-setup|First Time Setup]]
