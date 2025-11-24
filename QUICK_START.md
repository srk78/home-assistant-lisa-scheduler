# Quick Start Guide

Get your ZHC Heating Scheduler up and running in minutes!

## Installation (5 minutes)

### Option 1: HACS (Recommended)
1. Open HACS → Integrations
2. Add custom repository: `https://github.com/stefan/zhc-heating-scheduler`
3. Search for "ZHC Heating Scheduler"
4. Click Download
5. Restart Home Assistant

### Option 2: Manual
1. Copy `custom_components/zhc_heating_scheduler` to your HA config
2. Restart Home Assistant

## Initial Setup (2 minutes)

1. **Go to Settings → Devices & Services**
2. **Click "+ Add Integration"**
3. **Search for "ZHC Heating Scheduler"**
4. **Fill in the form:**
   - Schedule URL: Your club's schedule webpage
   - Climate Entity: Select your thermostat
   - Pre-heat: 2 hours (default)
   - Cool-down: 30 minutes (default)
   - Target temp: 20°C (default)

5. **Click Submit**

✅ Done! The integration will now:
- Check the schedule every 6 hours
- Start heating 2 hours before events
- Stop heating 30 minutes before events end

## Quick Test (3 minutes)

### 1. Enable Dry Run Mode

Go to Settings → Devices & Services → ZHC Heating Scheduler → Configure:
- Enable "Dry run mode"
- Click Submit

### 2. Check Logs

Settings → System → Logs

Look for messages like:
```
DRY RUN: Would set heating to True (currently False)
```

### 3. Force Schedule Refresh

Developer Tools → Services:
```yaml
service: zhc_heating_scheduler.refresh_schedule
```

Check logs to see events found.

### 4. Verify Sensors

Go to Developer Tools → States, search for:
- `sensor.zhc_next_heating_start`
- `sensor.zhc_current_event`
- `binary_sensor.zhc_heating_active`

### 5. Disable Dry Run

When everything looks good:
- Go back to Configure
- Disable "Dry run mode"
- ✅ Now live!

## Common First-Time Issues

### "No events found"

**Cause**: Website structure not recognized by generic parser

**Solution**: Create a custom scraper (see SCRAPER_GUIDE.md)

**Quick check**:
1. Visit your schedule URL in a browser
2. View page source
3. Look for date/time patterns
4. File an issue with the HTML structure for help

### Climate entity not found

**Cause**: Typo or entity doesn't exist

**Solution**:
1. Go to Developer Tools → States
2. Search for "climate."
3. Copy exact entity ID
4. Reconfigure integration with correct ID

### Heating not starting

**Check these:**
- [ ] Is `binary_sensor.zhc_scheduler_enabled` = ON?
- [ ] Are there upcoming events? (check `sensor.zhc_current_event`)
- [ ] Is `sensor.zhc_next_heating_start` in the future?
- [ ] Is dry run mode disabled?
- [ ] Does your climate entity respond to manual control?

## Dashboard Card (1 minute)

Add this to your dashboard:

```yaml
type: entities
title: Club Heating Schedule
entities:
  - entity: binary_sensor.zhc_heating_active
    name: Heating Status
  - entity: sensor.zhc_current_event
    name: Next Event
  - entity: sensor.zhc_next_heating_start
    name: Heating Starts
  - entity: sensor.zhc_heating_minutes_today
    name: Minutes Today
  - type: divider
  - type: button
    name: Refresh Schedule
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: zhc_heating_scheduler.refresh_schedule
```

## Emergency Heating (1 minute)

Create a script for emergency heating:

```yaml
script:
  emergency_heating:
    alias: Emergency Heating
    icon: mdi:fire
    sequence:
      - service: zhc_heating_scheduler.set_override
        data:
          start_time: "{{ now().isoformat() }}"
          end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

Add to dashboard as a button!

## Next Steps

### Customize Settings
- Adjust pre-heat time based on building size
- Fine-tune cool-down period
- Set optimal temperature

### Create Automations
- Notifications when heating starts
- Alerts if schedule refresh fails
- Weather-based adjustments

### Monitor Performance
- Track energy usage
- Analyze heating patterns
- Optimize settings

## Need Help?

1. **Documentation**: Check README.md and other guides
2. **Issues**: [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)
3. **Community**: Home Assistant forums
4. **Debug**: Enable debug logging (see README.md)

## Pro Tips

💡 **Start with dry run mode** - Test without affecting heating

💡 **Use generous pre-heat times initially** - You can always reduce them

💡 **Check logs regularly at first** - Catch issues early

💡 **Create dashboard card** - Easy monitoring of schedule

💡 **Set up failure notifications** - Know if schedule refresh fails

---

**⏱️ Total setup time: ~10 minutes**

**🎉 You're all set!** Your club building will now automatically heat before events.

