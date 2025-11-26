---
title: Installation via YAML Configuration
tags: [quickstart, installation, yaml, advanced]
---

# Installation via YAML Configuration

This guide shows you how to install and configure the ZHC Heating Scheduler using YAML configuration files. This method is for users comfortable with editing configuration files.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- Access to Home Assistant configuration files
- A climate entity (Plugwise SA recommended)
- Access to your club's schedule webpage

## Step 1: Install the Integration

### Option A: Via HACS

1. Open **HACS** in your Home Assistant instance
2. Go to **Integrations**
3. Click the three dots (⋮) → **Custom repositories**
4. Add repository:
   - **URL**: `https://github.com/stefan/zhc-heating-scheduler`
   - **Category**: Integration
5. Search for "ZHC Heating Scheduler" and install
6. Restart Home Assistant

### Option B: Manual Installation

1. Download the latest release from GitHub
2. Extract the `zhc_heating_scheduler` folder to:
   ```
   config/custom_components/zhc_heating_scheduler/
   ```
3. Restart Home Assistant

## Step 2: Configure via YAML

Add this to your `configuration.yaml`:

### Basic Configuration

```yaml
zhc_heating_scheduler:
  # Required settings
  schedule_url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
  climate_entity: "climate.plugwise_sa"
  
  # Timing settings
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20.0
  
  # Scan settings
  scan_interval: 21600  # 6 hours
  
  # Safety
  enabled: true
  dry_run: true  # Start with dry run enabled
```

### Advanced Configuration with Scraper

```yaml
zhc_heating_scheduler:
  # Basic settings
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20.0
  
  # Configurable scraper
  scraper_sources:
    - url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
      type: training
      method: html
      selectors:
        container: "div.event-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"
    
    - url: "https://www.zandvoortschehockeyclub.nl/wedstrijdschema"
      type: match
      method: html
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"
  
  # Date/time settings
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  timezone: "Europe/Amsterdam"
  
  # Control
  scan_interval: 21600
  enabled: true
  dry_run: true
```

## Step 3: Validate Configuration

Before restarting, check your configuration:

1. Go to **Developer Tools** → **YAML**
2. Click **Check Configuration**
3. Look for any errors related to `zhc_heating_scheduler`

## Step 4: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**
2. Click **Restart**
3. Wait for Home Assistant to come back online

## Step 5: Verify Installation

### Check Logs

1. Go to **Settings** → **System** → **Logs**
2. Search for "zhc"
3. Look for initialization messages

### Check Entities

1. Go to **Developer Tools** → **States**
2. Search for `sensor.zhc` and `binary_sensor.zhc`
3. You should see all entities

### Test Schedule Refresh

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

Check logs for "Found X events" messages.

## Configuration Options Reference

See [[../configuration/basic-settings|Basic Settings]] for detailed explanation of each option.

## Common YAML Configurations

### Minimal Configuration

```yaml
zhc_heating_scheduler:
  schedule_url: "https://club.com/schedule"
  climate_entity: "climate.heating"
```

### Production Configuration

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20.0
  scan_interval: 21600
  enabled: true
  dry_run: false  # Live mode
  
  scraper_sources:
    - url: "https://club.com/training"
      type: training
    - url: "https://club.com/matches"
      type: match
```

### Testing Configuration

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.test"
  pre_heat_hours: 0.5  # 30 minutes for quick testing
  cool_down_minutes: 5
  scan_interval: 600  # 10 minutes
  dry_run: true
```

## Troubleshooting

### Configuration Errors

**Error: "Invalid config"**
- Check YAML indentation (use spaces, not tabs)
- Verify all required fields are present
- Check quote marks around strings

**Error: "Entity not found"**
- Make sure climate entity exists
- Check entity ID in **Developer Tools** → **States**

### Integration Not Loading

1. Check logs for error messages
2. Verify files are in correct location
3. Ensure all required dependencies are met
4. Try restarting Home Assistant again

## Next Steps

- [[first-time-setup|Complete First Time Setup]]
- [[../configuration/basic-settings|Configure Basic Settings]]
- [[../configuration/scraper-configuration|Configure Scraper]]
- [[testing-dry-run|Test with Dry Run Mode]]

## Advantages of YAML Configuration

✅ **Version Control**: Track changes in Git  
✅ **Backup**: Easy to backup and restore  
✅ **Sharing**: Share configurations with others  
✅ **Automation**: Script configuration changes  
✅ **Documentation**: Comments in configuration

## See Also

- [[installation-ui|Installation via UI]] - Easier for beginners
- [[../configuration/examples|Configuration Examples]]
- [[../troubleshooting/common-issues|Common Issues]]

---

**Difficulty**: Intermediate  
**Time**: 15-20 minutes  
**Next**: [[first-time-setup|First Time Setup]]

