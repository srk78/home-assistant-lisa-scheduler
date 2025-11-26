---
title: Heating Not Starting
tags: [troubleshooting, heating, control]
---

# Heating Not Starting

Troubleshooting guide when heating doesn't start automatically.

## Symptoms

- Events are found correctly
- Heating windows calculated
- But heating never actually starts
- Climate entity doesn't turn on

## Quick Checks

### 1. Check Dry Run Mode

**Most common cause!**

**UI**: Settings → Devices & Services → ZHC Heating Scheduler → Configure  
**YAML**: Check `dry_run: false`

If dry run is enabled, logs will show:
```
DRY RUN: Would set heating to True
```

**Solution**: Disable dry run mode

### 2. Check Scheduler Enabled

Check `binary_sensor.zhc_scheduler_enabled` is **ON**

If OFF, enable with:
```yaml
service: zhc_heating_scheduler.enable
```

### 3. Check Climate Entity

Verify climate entity works manually:

1. Go to entity in UI
2. Try turning it on manually
3. Set temperature manually
4. Confirm it responds

### 4. Check Upcoming Events

Verify there are events:
- `sensor.zhc_current_event` should show next event
- `sensor.zhc_next_heating_start` should have a time

## Detailed Troubleshooting

### Step 1: Verify Integration Status

```yaml
# Check these sensors:
binary_sensor.zhc_scheduler_enabled  # Should be ON
binary_sensor.zhc_heating_active     # Should turn ON at heating time
sensor.zhc_next_heating_start        # Should show upcoming time
```

### Step 2: Check Logs

Settings → System → Logs, search for "zhc"

**Good signs**:
```
INFO: Next heating start: 2024-11-26 14:00:00
INFO: Current state: heating should be ON
INFO: Setting heating to True
```

**Bad signs**:
```
ERROR: Cannot control climate entity
ERROR: Climate entity not found
WARNING: Scheduler disabled
```

### Step 3: Test Manual Control

Try controlling climate entity directly:

```yaml
service: climate.turn_on
target:
  entity_id: climate.plugwise_sa
```

```yaml
service: climate.set_temperature
target:
  entity_id: climate.plugwise_sa
data:
  temperature: 20
```

If manual control doesn't work, the problem is with the climate entity, not the scheduler.

### Step 4: Check Timing

Is it actually time for heating to start?

Check:
```yaml
sensor.zhc_next_heating_start
```

If the time hasn't arrived yet, heating won't start!

### Step 5: Check Heating Window

The integration calculates heating windows based on:
- Event time
- Pre-heat time
- Cool-down time

**Example**:
- Event: 18:00-20:00
- Pre-heat: 2 hours
- Cool-down: 30 minutes
- **Heating window: 16:00-19:30**

If current time is outside this window, heating won't be active.

## Common Issues

### Issue 1: Permissions Problem

**Symptom**: Logs show permission denied

**Solution**:
1. Check Home Assistant has permission to control device
2. Verify climate entity isn't locked
3. Check device-specific access controls

### Issue 2: State Mismatch

**Symptom**: Scheduler thinks heating is on, but it's not

**Solution**:
1. Restart Home Assistant
2. Check climate entity state is accurate
3. Force state sync

### Issue 3: Configuration Error

**Symptom**: Integration loaded but not working

**Solution**:
1. Check configuration is valid
2. Verify all required fields present
3. Check entity IDs are correct
4. Review YAML syntax

### Issue 4: Network/Device Problem

**Symptom**: Climate entity not responding

**Solution**:
1. Check device is online
2. Verify network connectivity
3. Test device directly (not through HA)
4. Check device-specific issues

## Testing Procedure

### Test 1: Manual Override

Force heating on regardless of schedule:

```yaml
service: zhc_heating_scheduler.set_override
data:
  start_time: "{{ now().isoformat() }}"
  end_time: "{{ (now() + timedelta(hours=1)).isoformat() }}"
```

If this works, the issue is with schedule/timing.  
If this doesn't work, the issue is with device control.

### Test 2: Direct Service Call

Within a heating window, check logs for what the coordinator is trying to do.

If logs show service calls being made but heating doesn't start, issue is with climate entity or device.

### Test 3: Simple Schedule

Create a test event that should start heating soon:

1. Configure very short pre-heat time (15 minutes)
2. Add test event soon
3. Wait and monitor

## Advanced Diagnostics

### Check Coordinator State

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler.coordinator: debug
```

Look for:
- Heating state calculations
- Service call attempts
- Error messages

### Check Service Calls

Developer Tools → Events, listen to:
- `call_service`

Filter for:
- `climate.turn_on`
- `climate.set_temperature`

See if service calls are being made.

### Check Entity State

Developer Tools → States

Check `climate.plugwise_sa` (your entity):
- Current state (on/off)
- Current temperature
- Target temperature
- Available attributes

## Solutions by Cause

### If Dry Run Enabled

Disable in configuration or UI

### If Scheduler Disabled

```yaml
service: zhc_heating_scheduler.enable
```

### If Climate Entity Not Working

1. Fix climate entity first
2. Then test scheduler again

### If Timing Wrong

1. Check [[../configuration/timing-optimization|Timing Settings]]
2. Verify timezone correct
3. Check event times

### If No Events

See [[no-events-found|No Events Found Guide]]

## Prevention

### Monitor Key Sensors

Create alert if issues detected:

```yaml
automation:
  - alias: "Heating should be on but isn't"
    trigger:
      - platform: template
        value_template: >
          {{ is_state('binary_sensor.zhc_heating_active', 'on') and
             is_state('climate.plugwise_sa', 'off') }}
        for:
          minutes: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Heating control problem detected!"
```

### Regular Checks

- Review logs weekly
- Test heating before season starts
- Monitor first few cycles after any change

## Checklist

- [ ] Dry run mode disabled
- [ ] Scheduler enabled
- [ ] Climate entity works manually
- [ ] Upcoming events exist
- [ ] Current time within heating window
- [ ] No errors in logs
- [ ] Service calls being made
- [ ] Device responds to commands

## See Also

- [[../quick-start/testing-dry-run|Dry Run Mode]]
- [[../configuration/basic-settings|Basic Settings]]
- [[debugging|Debug Logging]]
- [[common-issues|Common Issues]]

---

**Difficulty**: Intermediate  
**Time needed**: 15-30 minutes  
**Most common cause**: Dry run mode still enabled

