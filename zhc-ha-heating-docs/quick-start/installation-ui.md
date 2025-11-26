---
title: Installation via Home Assistant UI
tags: [quickstart, installation, ui]
---

# Installation via Home Assistant UI

This guide shows you how to install and configure the ZHC Heating Scheduler using only the Home Assistant user interface - no terminal or command line required!

## Prerequisites

- Home Assistant 2024.1.0 or newer
- A climate entity (Plugwise SA recommended)
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
   - **Repository URL**: `https://github.com/stefan/zhc-heating-scheduler`
   - **Category**: Integration
   - Click **Add**

4. Install the integration
   - Search for "ZHC Heating Scheduler"
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

3. Search for "ZHC Heating Scheduler"
   - Type "zhc" or "heating" in the search box
   - Click on **ZHC Heating Scheduler** when it appears

4. Fill in the configuration form:

### Basic Configuration

| Field | Description | Example |
|-------|-------------|---------|
| **Schedule URL** | The webpage with your club's schedule | `https://www.zandvoortschehockeyclub.nl/trainingsschema` |
| **Climate Entity** | Your thermostat/heating control | `climate.plugwise_sa` |
| **Pre-heat time (hours)** | Hours before event to start heating | `2` |
| **Cool-down time (minutes)** | Minutes before event end to stop | `30` |
| **Target temperature (°C)** | Temperature when heating | `20.0` |
| **Scan interval (seconds)** | How often to refresh schedule | `21600` (6 hours) |
| **Dry run mode** | Test without controlling heating | ☑️ Enable for testing |

5. Click **Submit**

## Step 3: Verify Installation

### Check the Integration

1. Go to **Settings** → **Devices & Services**
2. You should see "ZHC Heating Scheduler" in your list
3. Click on it to see entities

### Check the Sensors

1. Go to **Developer Tools** → **States**
2. Search for `zhc`
3. You should see several entities:
   - `sensor.zhc_current_event`
   - `sensor.zhc_next_heating_start`
   - `binary_sensor.zhc_heating_active`
   - And more...

### Force a Schedule Refresh

1. Go to **Developer Tools** → **Services**
2. Select service: `zhc_heating_scheduler.refresh_schedule`
3. Click **Call Service**
4. Check logs for: "Found X events"

### View the Logs

1. Go to **Settings** → **System** → **Logs**
2. Search for "zhc" or "heating"
3. Look for messages like:
   - "Found X events"
   - "DRY RUN: Would set heating to..."

## Step 4: Test with Dry Run Mode

> [!TIP]
> Always test with dry run mode enabled first!

With dry run mode enabled (recommended for first setup):

1. The scheduler will log what it **would** do
2. But **won't actually** control your heating
3. You can verify everything works correctly

Check the logs to see messages like:
```
DRY RUN: Would set heating to True (currently False)
```

## Step 5: Configure Scraper (If Needed)

If no events are found, you may need to configure the scraper. See [[../scraper/configuring-scraper|Scraper Configuration Guide]].

For the ZHC website specifically, see [[../scraper/zhc-specific|ZHC-Specific Setup]].

## Step 6: Disable Dry Run Mode

Once you've verified everything works:

1. Go to **Settings** → **Devices & Services**
2. Find "ZHC Heating Scheduler"
3. Click **Configure**
4. Uncheck **Dry run mode**
5. Click **Submit**

🎉 **You're now live!** The integration will automatically control your heating.

## Step 7: Create a Dashboard Card (Optional)

1. Go to your dashboard
2. Click the three dots (⋮) → **Edit Dashboard**
3. Click **+ Add Card**
4. Choose **Entities Card**
5. Add these entities:
   - `binary_sensor.zhc_heating_active`
   - `sensor.zhc_current_event`
   - `sensor.zhc_next_heating_start`
   - `sensor.zhc_heating_minutes_today`
6. Set card title to "Club Heating"
7. Click **Save**

## Troubleshooting

### Integration Not Found

- Make sure you've restarted Home Assistant after installation
- Check that the files are in `config/custom_components/zhc_heating_scheduler/`

### No Events Found

- Check the schedule URL is correct
- The website might use JavaScript to load events
- See [[../troubleshooting/no-events-found|No Events Found Guide]]

### Climate Entity Not Found

- Make sure the entity ID is correct
- Check **Developer Tools** → **States** for your climate entity
- Entity must start with `climate.`

### Heating Not Starting

- Make sure dry run mode is disabled
- Check `binary_sensor.zhc_scheduler_enabled` is ON
- Verify there are upcoming events
- See [[../troubleshooting/heating-not-starting|Heating Not Starting Guide]]

## Next Steps

- [[first-time-setup|Complete the First Time Setup]]
- [[../configuration/basic-settings|Configure Basic Settings]]
- [[../usage/automations|Create Automations]]
- [[../usage/dashboard-cards|Build Dashboard Cards]]

## Getting Help

If you encounter issues:

1. Check the logs in **Settings** → **System** → **Logs**
2. Review the [[../troubleshooting/common-issues|Common Issues]] guide
3. Ask on the [Home Assistant Community Forum](https://community.home-assistant.io/)
4. Create an issue on [GitHub](https://github.com/stefan/zhc-heating-scheduler/issues)

---

**Estimated time**: 10-15 minutes  
**Difficulty**: Easy  
**Next**: [[first-time-setup|First Time Setup]]

