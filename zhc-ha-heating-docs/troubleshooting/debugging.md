---
title: Debug Logging
tags: [troubleshooting, debugging, logging]
---

# Debug Logging

Enable detailed logging to troubleshoot issues with the ZHC Heating Scheduler.

## Enable Debug Logging

### Via configuration.yaml

Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: debug
```

### Specific Components

Enable debug logging for specific parts:

```yaml
logger:
  default: info
  logs:
    # All components
    custom_components.zhc_heating_scheduler: debug
    
    # Or specific components
    custom_components.zhc_heating_scheduler.coordinator: debug
    custom_components.zhc_heating_scheduler.scraper: debug
    custom_components.zhc_heating_scheduler.scheduler: debug
```

### Apply Changes

After editing `configuration.yaml`:

1. Go to **Developer Tools** → **YAML**
2. Click **Restart** (or just reload logger)
3. Or restart Home Assistant

## Viewing Logs

### Via UI

1. Go to **Settings** → **System** → **Logs**
2. Search for "zhc" or "heating"
3. Filter by level if needed

### Via Command Line

```bash
tail -f /config/home-assistant.log | grep zhc
```

## What to Look For

### Successful Operation

```
INFO: Setting up ZHC Heating Scheduler
INFO: Using configurable scraper with 2 sources
DEBUG: Fetching from source: https://...
INFO: Found 15 events
INFO: Calculated 8 heating windows
DEBUG: Next heating start: 2024-11-26 14:00:00
DEBUG: Current heating state: False
```

### Common Errors

**Schedule Fetch Errors**:
```
ERROR: Error fetching schedule: ...
ERROR: HTTP error fetching schedule: ...
WARNING: No events found in HTML
```

**Control Errors**:
```
ERROR: Cannot control climate entity
ERROR: Service call failed: ...
```

**Configuration Errors**:
```
ERROR: Invalid configuration: ...
WARNING: Climate entity not found
```

## Debug by Component

### Coordinator Debugging

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler.coordinator: debug
```

**Shows**:
- State updates
- Heating decisions
- Service calls
- Schedule refreshes

### Scraper Debugging

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler.scraper: debug
    custom_components.zhc_heating_scheduler.configurable_scraper: debug
```

**Shows**:
- HTTP requests
- HTML parsing
- Event extraction
- Date/time parsing

### Scheduler Debugging

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler.scheduler: debug
```

**Shows**:
- Heating window calculations
- Event merging
- Time calculations

## Collecting Debug Information

### For GitHub Issues

1. **Enable debug logging**
2. **Reproduce the problem**
3. **Collect logs** from the time of the problem
4. **Sanitize** (remove any personal info)
5. **Include** in GitHub issue

### Information to Include

- Home Assistant version
- Integration version
- Relevant log entries
- Configuration (sanitized)
- Steps to reproduce

### Log Format

```
2024-11-26 14:30:00 DEBUG (MainThread) [custom_components.zhc_heating_scheduler] Message here
```

Components:
- Timestamp
- Log level
- Thread
- Component name
- Message

## Temporary Debug Logging

For quick debugging without restart:

### Via Developer Tools

1. **Developer Tools** → **Services**
2. Service: `logger.set_level`
3. Data:
```yaml
custom_components.zhc_heating_scheduler: debug
```

This change lasts until restart.

## Performance Considerations

Debug logging generates a lot of output:
- **Disk space**: Can fill up quickly
- **Performance**: Slight impact
- **Log size**: May need rotation

### Disable When Done

Change back to `info` level:

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: info
```

## Advanced: Custom Log Handling

### Save to Separate File

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: debug
    
# Note: Requires custom setup
```

### Log Rotation

Home Assistant handles this automatically, but you can configure it in `configuration.yaml`.

## Common Debug Scenarios

### Scenario 1: Events Not Found

Enable scraper debug:
```yaml
custom_components.zhc_heating_scheduler.scraper: debug
```

Look for:
- HTML fetch success
- Parsing attempts
- Date/time format issues

### Scenario 2: Heating Not Starting

Enable coordinator debug:
```yaml
custom_components.zhc_heating_scheduler.coordinator: debug
```

Look for:
- State calculations
- Service call attempts
- Error messages

### Scenario 3: Wrong Timing

Enable scheduler debug:
```yaml
custom_components.zhc_heating_scheduler.scheduler: debug
```

Look for:
- Window calculations
- Pre-heat/cool-down application
- Event merging

## See Also

- [[common-issues|Common Issues]]
- [[no-events-found|No Events Found]]
- [[heating-not-starting|Heating Not Starting]]

---

**Difficulty**: Easy  
**Impact**: Helpful for all troubleshooting

