---
title: First Time Setup
tags: [quickstart, setup, configuration]
---

# First Time Setup

Complete these steps after installing the ZHC Heating Scheduler to ensure everything is configured correctly.

## Prerequisites

- Integration installed (via [[installation-ui|UI]] or [[installation-yaml|YAML]])
- Climate entity available
- Schedule URL accessible

## Step 1: Verify Integration Status

### Check Integration

1. Go to **Settings** → **Devices & Services**
2. Find "ZHC Heating Scheduler" in the list
3. Status should show as "Configured"

### Check Entities

Go to **Developer Tools** → **States** and verify these entities exist:

**Sensors:**
- `sensor.zhc_next_heating_start`
- `sensor.zhc_next_heating_stop`
- `sensor.zhc_current_event`
- `sensor.zhc_events_today`
- `sensor.zhc_heating_minutes_today`
- `sensor.zhc_total_heating_windows`
- `sensor.zhc_last_schedule_update`

**Binary Sensors:**
- `binary_sensor.zhc_heating_active`
- `binary_sensor.zhc_scheduler_enabled`
- `binary_sensor.zhc_manual_override`

## Step 2: Test Schedule Fetching

### Manual Refresh

1. Go to **Developer Tools** → **Services**
2. Select `zhc_heating_scheduler.refresh_schedule`
3. Click **Call Service**

### Check Results

1. Go to **Settings** → **System** → **Logs**
2. Search for "zhc"
3. Look for messages like:
   - "Fetching schedule from..."
   - "Found X events"
   - "Calculated Y heating windows"

### If No Events Found

See [[../troubleshooting/no-events-found|No Events Found Guide]] for troubleshooting.

## Step 3: Review Schedule Data

### Check Current Event Sensor

1. Go to **Developer Tools** → **States**
2. Find `sensor.zhc_current_event`
3. Check the state shows upcoming events
4. Review attributes for event details

### Check Heating Times

1. Find `sensor.zhc_next_heating_start`
2. Verify the time makes sense
3. Find `sensor.zhc_next_heating_stop`
4. Verify it's after the start time

## Step 4: Test in Dry Run Mode

> [!IMPORTANT]
> Always test with dry run mode enabled first!

### Verify Dry Run is Enabled

1. Check logs for "DRY RUN" messages
2. Or check your configuration:
   - **UI**: Settings → Devices & Services → Configure
   - **YAML**: Check `dry_run: true` in config

### Monitor Dry Run Behavior

Watch the logs for messages like:
```
DRY RUN: Would set heating to True (currently False)
DRY RUN: Would set heating to False (currently True)
```

This shows what the scheduler would do without actually controlling heating.

## Step 5: Configure Basic Settings

### Review Pre-heat Time

Default: 2 hours before events

**Consider:**
- Building size (larger = more time)
- Insulation quality
- Outside temperature
- Type of heating system

**Adjust if needed:** See [[../configuration/timing-optimization|Timing Optimization]]

### Review Cool-down Time

Default: 30 minutes before event ends

**Consider:**
- How long building stays warm
- Event duration
- Energy cost vs comfort

**Adjust if needed:** See [[../configuration/basic-settings|Basic Settings]]

### Review Target Temperature

Default: 20°C

**Consider:**
- Sport facility: 18-20°C
- Changing rooms: 20-22°C
- Spectator areas: 18-20°C

## Step 6: Create Basic Automation

### Notification on Heating Start

```yaml
automation:
  - alias: "Notify when club heating starts"
    trigger:
      - platform: state
        entity_id: binary_sensor.zhc_heating_active
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Club Heating Started"
          message: "Heating for {{ state_attr('sensor.zhc_current_event', 'title') }}"
```

See [[../usage/automations|Automations Guide]] for more examples.

## Step 7: Create Dashboard Card

### Basic Card

```yaml
type: entities
title: Club Heating
entities:
  - entity: binary_sensor.zhc_heating_active
    name: Heating Status
  - entity: sensor.zhc_current_event
    name: Next Event
  - entity: sensor.zhc_next_heating_start
    name: Heating Starts
  - entity: sensor.zhc_heating_minutes_today
    name: Minutes Today
```

See [[../usage/dashboard-cards|Dashboard Cards]] for advanced examples.

## Step 8: Test Emergency Override

### Set Manual Override

```yaml
service: zhc_heating_scheduler.set_override
data:
  start_time: "{{ now().isoformat() }}"
  end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

### Verify Override Active

1. Check `binary_sensor.zhc_manual_override` is ON
2. Check logs for "Manual override set" message

### Clear Override

```yaml
service: zhc_heating_scheduler.clear_override
```

## Step 9: Disable Dry Run (When Ready)

> [!WARNING]
> Only disable dry run after thorough testing!

**Via UI:**
1. Settings → Devices & Services
2. Find ZHC Heating Scheduler
3. Click **Configure**
4. Uncheck "Dry run mode"
5. Click **Submit**

**Via YAML:**
1. Change `dry_run: true` to `dry_run: false`
2. Restart Home Assistant

## Step 10: Monitor First Real Heating Cycle

### Before First Event

- Check heating starts at expected time
- Verify temperature reaches target
- Monitor for any issues

### During Event

- Confirm heating maintains temperature
- Check building is comfortable

### After Event

- Verify heating stops at expected time
- Monitor cool-down behavior

## Setup Checklist

- [ ] Integration installed and loaded
- [ ] All entities present
- [ ] Schedule refresh successful
- [ ] Events found and parsed correctly
- [ ] Heating times calculated correctly
- [ ] Dry run tested and working
- [ ] Basic settings optimized
- [ ] Dashboard card created
- [ ] Notification automation created
- [ ] Emergency override tested
- [ ] Dry run disabled (after testing)
- [ ] First real cycle monitored

## Common Issues

### No Entities Showing

**Solution**: Restart Home Assistant

### Events Not Found

**Solution**: See [[../troubleshooting/no-events-found|No Events Found Guide]]

### Wrong Heating Times

**Solution**: Check [[../configuration/timing-optimization|Timing Optimization]]

### Heating Not Starting

**Solution**: See [[../troubleshooting/heating-not-starting|Heating Not Starting]]

## Next Steps

After completing setup:

1. **Fine-tune timing** - [[../configuration/timing-optimization|Timing Optimization]]
2. **Add automations** - [[../usage/automations|Automation Examples]]
3. **Customize dashboard** - [[../usage/dashboard-cards|Dashboard Cards]]
4. **Set up notifications** - [[../usage/notifications|Notifications]]

## Getting Help

If you encounter issues during setup:

1. Check [[../troubleshooting/common-issues|Common Issues]]
2. Enable [[../troubleshooting/debugging|Debug Logging]]
3. Ask on [Home Assistant Forum](https://community.home-assistant.io/)
4. Create [GitHub Issue](https://github.com/stefan/zhc-heating-scheduler/issues)

---

**Time needed**: 20-30 minutes  
**Difficulty**: Easy  
**Prerequisites**: Integration installed  
**Next**: [[testing-dry-run|Testing with Dry Run]]

