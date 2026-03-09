---
title: Common Issues
tags: [troubleshooting, faq, help]
---

# Common Issues

Frequently asked questions and solutions to common problems.

## Installation Issues

### Integration Not Found After Installation

**Symptoms**: Can't find "LISA Scheduler" in the integrations list

**Solutions**:
1. Restart Home Assistant
2. Check files are in `config/custom_components/lisa_scheduler/`
3. Check logs for loading errors
4. Verify HACS installation completed

### Configuration Error on Startup

**Symptoms**: Integration fails to load, errors in log

**Solutions**:
1. Check YAML syntax (indentation, quotes)
2. Verify all required fields are present
3. Use the Configuration Checker before restarting

## Schedule Issues

### No Events Found

**Symptoms**: `sensor.lisa_current_event` shows "No events" or "No upcoming events"

**See**: [[no-events-found|No Events Found Guide]] for complete troubleshooting

**Quick fixes**:
1. Check the schedule URL is correct
2. Verify the website is accessible from your HA host
3. Configure a custom scraper if needed
4. Check date/time formats

### Events Have Wrong Times

**Symptoms**: Times don't match the website

**Solutions**:
1. Check the timezone setting
2. Verify the date format matches the website
3. Check whether the website uses 24h or 12h format
4. Test time parsing with debug logging enabled

### Events Missing Some Days

**Symptoms**: Some events do not appear

**Solutions**:
1. Check `scan_interval` — may need more frequent updates
2. Force a refresh: call `lisa_scheduler.refresh_schedule`
3. Check website pagination
4. Verify the date range the scraper covers

## Actions Not Triggering

### Automations Don't Run During an Event Window

**Symptoms**: `binary_sensor.lisa_window_active` is on, but automations don't fire

**See**: [[actions-not-triggering|Actions Not Triggering Guide]] for complete troubleshooting

**Quick checks**:
1. Is the scheduler enabled? Check `binary_sensor.lisa_scheduler_enabled`
2. Is dry run mode off? Check integration options
3. Does the automation trigger event_type match exactly? (e.g. `lisa_scheduler_window_started`)
4. Is the automation itself enabled?

### Pre-Event Trigger Not Firing at Expected Time

**Symptoms**: The `lisa_scheduler_pre_event_trigger` event does not appear, or fires at the wrong time

**Solutions**:
1. Verify `pre_event_triggers` is configured (e.g. `"120, 30"`)
2. Check the automation condition uses `minutes_before` to distinguish trigger values
3. Confirm the trigger time hasn't already passed when the scheduler first starts
4. Enable debug logging and look for `_fire_pre_event_triggers` log lines

## Sensor Issues

### Sensors Show "Unknown"

**Symptoms**: Sensor states are "unknown" or "unavailable"

**Solutions**:
1. Wait for the first schedule refresh to complete
2. Check the integration loaded successfully (Settings → System → Logs)
3. Restart Home Assistant
4. Check logs for errors

### Sensor Values Don't Update

**Symptoms**: Sensor values appear stuck

**Solutions**:
1. Call `lisa_scheduler.refresh_schedule` to force a refresh
2. Check the `scan_interval` setting
3. Verify there are no errors in the logs
4. Check the coordinator is running (look for periodic update log lines)

## Configuration Issues

### Can't Change Settings in UI

**Symptoms**: Configure button is missing or does not respond

**Solutions**:
1. Try YAML configuration instead
2. Restart after YAML changes
3. Check for configuration validation errors in the logs

### Changes Don't Take Effect

**Symptoms**: Updated settings but behavior hasn't changed

**Solutions**:
1. Restart Home Assistant after YAML changes
2. Confirm the configuration validated without errors
3. Force a schedule refresh after changes
4. Check logs for errors

## Performance Issues

### Home Assistant Slow After Installation

**Symptoms**: HA response time has degraded

**Solutions**:
1. Increase `scan_interval` to reduce fetch frequency
2. Check whether the scraper is timing out on each poll
3. Optimize CSS selectors
4. Check source website response time

### Schedule Refresh Takes a Long Time

**Symptoms**: The refresh service call times out or takes minutes

**Solutions**:
1. Test the website URL manually — it may be slow
2. Optimize CSS selectors
3. Reduce the number of scraper sources
4. Consider using an API or iCal source instead of HTML scraping

## Error Messages

### "Schedule refresh failed"

**Solution**:
1. Check the URL is accessible from your HA host
2. Verify network connectivity
3. Check the website isn't blocking automated requests
4. Review scraper configuration

### "Invalid event window"

**Solution**:
1. Check event times are logical (start before end)
2. Verify `pre_event_minutes` setting
3. Check for timezone issues
4. Review event data in debug logs

## Getting More Help

### Enable Debug Logging

See [[debugging|Debug Logging Guide]]

```yaml
logger:
  logs:
    custom_components.lisa_scheduler: debug
```

### Check Logs

Settings → System → Logs, search for `lisa_scheduler`.

### Community Support

- [Home Assistant Forum](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/stefan/lisa-scheduler/issues)

### Provide Information

When asking for help, include:
1. Home Assistant version
2. Integration version
3. Relevant log entries
4. Configuration (sanitized — remove URLs or tokens if needed)
5. What you have already tried

## See Also

- [[no-events-found|No Events Found]]
- [[actions-not-triggering|Actions Not Triggering]]
- [[debugging|Debug Logging]]

---

**Updated**: 2026-03-09
**Quick Help**: [[debugging|Enable Debug Logging]]
