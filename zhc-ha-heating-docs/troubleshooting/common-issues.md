---
title: Common Issues
tags: [troubleshooting, faq, help]
---

# Common Issues

Frequently asked questions and solutions to common problems.

## Installation Issues

### Integration Not Found After Installation

**Symptoms**: Can't find "ZHC Heating Scheduler" in integrations list

**Solutions**:
1. Restart Home Assistant
2. Check files are in `config/custom_components/zhc_heating_scheduler/`
3. Check logs for loading errors
4. Verify HACS installation completed

### Configuration Error on Startup

**Symptoms**: Integration fails to load, errors in log

**Solutions**:
1. Check YAML syntax (indentation, quotes)
2. Verify all required fields present
3. Check climate entity exists
4. Use Configuration Checker before restart

## Schedule Issues

### No Events Found

**Symptoms**: `sensor.zhc_current_event` shows "No events"

**See**: [[no-events-found|No Events Found Guide]] for complete troubleshooting

**Quick fixes**:
1. Check schedule URL is correct
2. Verify website is accessible
3. Configure custom scraper if needed
4. Check date/time formats

### Events Have Wrong Times

**Symptoms**: Times don't match website

**Solutions**:
1. Check timezone setting
2. Verify date format matches website
3. Check if website uses 24h vs 12h format
4. Test time parsing manually

### Events Missing Some Days

**Symptoms**: Some events don't appear

**Solutions**:
1. Check `scan_interval` - may need more frequent updates
2. Force refresh: `zhc_heating_scheduler.refresh_schedule`
3. Check website pagination
4. Verify date range in scraper

## Heating Control Issues

### Heating Never Starts

**Symptoms**: `binary_sensor.zhc_heating_active` never turns on

**See**: [[heating-not-starting|Heating Not Starting Guide]]

**Quick checks**:
1. Dry run mode disabled?
2. Scheduler enabled?
3. Upcoming events exist?
4. Climate entity working?

### Heating Starts at Wrong Time

**Symptoms**: Heating starts too early/late

**Solutions**:
1. Check `pre_heat_hours` setting
2. Verify timezone correct
3. Check event times are correct
4. See [[../configuration/timing-optimization|Timing Optimization]]

### Heating Doesn't Stop

**Symptoms**: Heating continues after event

**Solutions**:
1. Check `cool_down_minutes` setting
2. Verify scheduler is controlling entity
3. Check for manual overrides active
4. Review heating window calculations

## Sensor Issues

### Sensors Show "Unknown"

**Symptoms**: Sensor states are "unknown" or "unavailable"

**Solutions**:
1. Wait for first schedule refresh
2. Check integration loaded successfully
3. Restart Home Assistant
4. Check logs for errors

### Sensor Values Don't Update

**Symptoms**: Sensor values seem stuck

**Solutions**:
1. Force schedule refresh
2. Check `scan_interval` setting
3. Verify no errors in logs
4. Check coordinator is running

## Configuration Issues

### Can't Change Settings in UI

**Symptoms**: Configure button missing or doesn't work

**Solutions**:
1. Check integration supports options flow
2. Try YAML configuration instead
3. Restart after YAML changes
4. Check for configuration errors

### Changes Don't Take Effect

**Symptoms**: Updated settings but no change in behavior

**Solutions**:
1. Restart Home Assistant after YAML changes
2. Check configuration validated successfully
3. Force schedule refresh after changes
4. Check logs for errors

## Performance Issues

### Home Assistant Slow After Installation

**Symptoms**: HA response time degraded

**Solutions**:
1. Increase `scan_interval` (reduce frequency)
2. Check scraper isn't timing out
3. Optimize scraper selectors
4. Check website response time

### Schedule Refresh Takes Long Time

**Symptoms**: Refresh service call times out or takes minutes

**Solutions**:
1. Website may be slow - check manually
2. Optimize CSS selectors
3. Reduce number of sources
4. Consider API instead of HTML scraping

## Error Messages

### "Cannot connect to climate entity"

**Solution**:
1. Check entity ID is correct
2. Verify entity exists in Developer Tools → States
3. Test entity manually
4. Check entity domain is `climate.`

### "Schedule refresh failed"

**Solution**:
1. Check URL is accessible
2. Verify network connectivity
3. Check website isn't blocking requests
4. Review scraper configuration

### "Invalid heating window"

**Solution**:
1. Check event times are logical
2. Verify pre-heat/cool-down settings
3. Check for timezone issues
4. Review event data in logs

## Getting More Help

### Enable Debug Logging

See [[debugging|Debug Logging Guide]]

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler: debug
```

### Check Logs

Settings → System → Logs, search for "zhc"

### Community Support

- [Home Assistant Forum](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)

### Provide Information

When asking for help, include:
1. Home Assistant version
2. Integration version
3. Relevant log entries
4. Configuration (sanitized)
5. What you've already tried

## See Also

- [[no-events-found|No Events Found]]
- [[heating-not-starting|Heating Not Starting]]
- [[debugging|Debug Logging]]

---

**Updated**: 2024-11-26  
**Quick Help**: [[debugging|Enable Debug Logging]]

