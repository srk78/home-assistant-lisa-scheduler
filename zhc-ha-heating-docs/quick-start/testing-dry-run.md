---
title: Testing with Dry Run Mode
tags: [quickstart, testing, dry-run, safety]
---

# Testing with Dry Run Mode

Dry run mode allows you to safely test the ZHC Heating Scheduler without actually controlling your heating system. This guide shows you how to use it effectively.

## What is Dry Run Mode?

Dry run mode is a safety feature that:

✅ **Logs what would happen** - Shows all decisions  
✅ **Doesn't control heating** - No changes to climate entity  
✅ **Allows full testing** - Test schedule, timing, logic  
✅ **Safe for production** - Can run alongside live system  

## Enabling Dry Run Mode

### Via UI

1. Go to **Settings** → **Devices & Services**
2. Find "ZHC Heating Scheduler"
3. Click **Configure**
4. Check ☑️ **Dry run mode**
5. Click **Submit**

### Via YAML

```yaml
zhc_heating_scheduler:
  # ... other settings ...
  dry_run: true
```

Then restart Home Assistant.

## Testing Process

### Step 1: Enable Dry Run

Follow the steps above to enable dry run mode.

### Step 2: Force Schedule Refresh

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

### Step 3: Check Logs

Go to **Settings** → **System** → **Logs** and look for:

```
INFO: Fetching schedule from...
INFO: Found X events
INFO: Calculated Y heating windows
```

### Step 4: Monitor Dry Run Messages

Look for messages like:

```
INFO: DRY RUN: Would set heating to True (currently False)
INFO: DRY RUN: Target temperature would be 20.0°C
INFO: DRY RUN: Would set heating to False (currently True)
```

These show what the scheduler would do.

## What to Test

### 1. Schedule Parsing

**Verify:**
- [ ] Events are found
- [ ] Dates are correct
- [ ] Times are correct
- [ ] Event types are correct (training/match)

**Check:**
```
sensor.zhc_current_event
sensor.zhc_events_today
sensor.zhc_total_heating_windows
```

### 2. Heating Windows

**Verify:**
- [ ] Pre-heat time is correct
- [ ] Cool-down time is correct
- [ ] Windows don't overlap incorrectly
- [ ] Multiple events merge correctly

**Check:**
```
sensor.zhc_next_heating_start
sensor.zhc_next_heating_stop
```

### 3. Timing Logic

**Verify:**
- [ ] Heating starts at right time
- [ ] Heating stops at right time
- [ ] Transitions are smooth
- [ ] No unexpected behavior

**Watch logs** for dry run messages around event times.

### 4. State Transitions

**Verify:**
- [ ] `binary_sensor.zhc_heating_active` changes correctly
- [ ] State changes match log messages
- [ ] No rapid on/off cycling

## Example Test Scenario

### Scenario

Event: Training at 18:00-20:00  
Pre-heat: 2 hours  
Cool-down: 30 minutes  

**Expected behavior:**
- Heating starts: 16:00 (2 hours before)
- Heating stops: 19:30 (30 min before end)

### Test at 15:45 (Before start)

**Expected logs:**
```
INFO: Next heating start: 16:00
INFO: Current state: OFF
INFO: DRY RUN: Would set heating to True at 16:00
```

### Test at 16:05 (After start)

**Expected logs:**
```
INFO: Current heating window active
INFO: DRY RUN: Would set heating to True (currently False)
INFO: DRY RUN: Target temperature: 20.0°C
```

### Test at 19:35 (After stop)

**Expected logs:**
```
INFO: Heating window ended at 19:30
INFO: DRY RUN: Would set heating to False (currently True)
```

## Common Test Cases

### Test 1: Overlapping Events

**Setup:**
- Event 1: 14:00-16:00
- Event 2: 15:00-17:00

**Expected:**
- Windows merge
- Single continuous heating period
- One start, one stop

### Test 2: Multiple Events Same Day

**Setup:**
- Morning: 09:00-11:00
- Evening: 18:00-20:00

**Expected:**
- Two separate heating windows
- Heating off between events
- Correct start/stop for each

### Test 3: Last-Minute Event

**Setup:**
- Event in 30 minutes
- Pre-heat: 2 hours

**Expected:**
- Heating starts immediately
- Logs show "Late start" adjustment
- Still stops at correct time

## Interpreting Dry Run Logs

### Good Signs ✅

```
INFO: Found 15 events
INFO: Calculated 8 heating windows
INFO: Next heating in 2 hours 15 minutes
INFO: DRY RUN: Would set heating to True (currently False)
```

### Warning Signs ⚠️

```
WARNING: No events found
WARNING: Schedule refresh failed
WARNING: Invalid heating window (end before start)
```

### Error Signs ❌

```
ERROR: Failed to fetch schedule
ERROR: Cannot connect to climate entity
ERROR: Invalid configuration
```

## Debugging Issues

### No Dry Run Messages

**Possible causes:**
- Dry run mode not enabled
- No events in schedule
- Outside heating windows

**Solution:**
1. Verify dry run is enabled
2. Check event schedule
3. Wait for heating window time

### Wrong Timing

**Possible causes:**
- Incorrect pre-heat/cool-down settings
- Timezone issues
- Date format problems

**Solution:**
1. Check [[../configuration/timing-optimization|Timing Settings]]
2. Verify timezone: [[../configuration/advanced-settings|Advanced Settings]]
3. Check scraper date format

### Events Not Found

**Solution:** See [[../troubleshooting/no-events-found|No Events Found Guide]]

## When to Disable Dry Run

Disable dry run mode only after:

✅ **Schedule parsing works** - Events found correctly  
✅ **Timing is correct** - Start/stop times make sense  
✅ **Multiple cycles tested** - Several dry run cycles observed  
✅ **No errors in logs** - Clean operation for 24+ hours  
✅ **Confident in setup** - Understand how it works  

## Disabling Dry Run Mode

### Via UI

1. Settings → Devices & Services
2. Find "ZHC Heating Scheduler"
3. Click **Configure**
4. Uncheck ☐ **Dry run mode**
5. Click **Submit**

> [!WARNING]
> After disabling, the integration will control your heating!

### Via YAML

```yaml
zhc_heating_scheduler:
  # ... other settings ...
  dry_run: false
```

Then restart Home Assistant.

## After Disabling Dry Run

### Monitor First Cycle

- Watch logs closely
- Verify heating actually starts
- Check temperature reaches target
- Confirm heating stops correctly

### Be Ready to Intervene

Keep manual override ready:

```yaml
service: zhc_heating_scheduler.disable
```

Or use manual climate control as backup.

### Gradual Rollout

Consider:
1. Disable dry run for one event
2. Monitor closely
3. If successful, continue
4. If issues, re-enable dry run

## Re-enabling Dry Run

You can always re-enable dry run:
- After making configuration changes
- When troubleshooting issues
- Before seasonal changes
- When testing new features

It's safe to switch back and forth!

## Best Practices

### During Initial Setup

- ✅ Keep dry run enabled for at least 48 hours
- ✅ Test multiple event types
- ✅ Monitor logs regularly
- ✅ Verify all scenarios

### When Making Changes

- ✅ Re-enable dry run
- ✅ Test changes thoroughly
- ✅ Disable when confident

### Ongoing Operation

- ✅ Check logs periodically
- ✅ Monitor sensor values
- ✅ Review heating patterns
- ✅ Adjust settings as needed

## Testing Checklist

- [ ] Dry run mode enabled
- [ ] Schedule refresh successful
- [ ] Events found and parsed
- [ ] Heating windows calculated
- [ ] Dry run messages in logs
- [ ] Timing looks correct
- [ ] Multiple cycles tested
- [ ] No errors or warnings
- [ ] Ready to go live

## Next Steps

After successful dry run testing:

1. [[../configuration/timing-optimization|Optimize Timing]]
2. [[../usage/dashboard-cards|Create Dashboard]]
3. [[../usage/automations|Set Up Automations]]
4. [[../usage/notifications|Configure Notifications]]
5. Disable dry run mode
6. Monitor first real cycles

## See Also

- [[first-time-setup|First Time Setup]]
- [[../troubleshooting/debugging|Debug Logging]]
- [[../troubleshooting/common-issues|Common Issues]]

---

**Time needed**: 1-2 days (monitoring)  
**Difficulty**: Easy  
**Prerequisites**: Integration installed  
**Next**: [[../configuration/basic-settings|Configure Settings]]

