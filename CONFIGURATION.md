# Configuration Guide

This guide provides detailed information about all configuration options for the ZHC Heating Scheduler.

## Configuration Methods

The integration supports two configuration methods:
1. **UI Configuration Flow** (recommended) - Configure through Home Assistant UI
2. **YAML Configuration** - Configure in `configuration.yaml`

## Configuration Options

### Required Options

#### `schedule_url`
- **Type**: URL string
- **Required**: Yes
- **Description**: The URL of the website containing your club's schedule
- **Example**: `https://www.your-club.com/schedule`

#### `climate_entity`
- **Type**: Entity ID
- **Required**: Yes
- **Description**: The entity ID of the climate device to control (must start with `climate.`)
- **Example**: `climate.plugwise_sa`
- **Note**: The climate entity must already exist in Home Assistant

### Timing Options

#### `pre_heat_hours`
- **Type**: Integer (0-24)
- **Required**: No
- **Default**: 2
- **Description**: Number of hours before an event to start heating
- **Example**: `2` means heating starts 2 hours before an event
- **Considerations**:
  - Larger buildings may need more pre-heat time
  - Consider outdoor temperature (may need more time in winter)
  - Balance comfort with energy efficiency

#### `cool_down_minutes`
- **Type**: Integer (0-120)
- **Required**: No
- **Default**: 30
- **Description**: Number of minutes before an event ends to stop heating
- **Example**: `30` means heating stops 30 minutes before the event ends
- **Rationale**: 
  - Building retains heat for a while after heating stops
  - Saves energy at the end of events when people are leaving
  - Prevents overheating

### Temperature Options

#### `target_temperature`
- **Type**: Float (5.0-35.0)
- **Required**: No
- **Default**: 20.0
- **Unit**: Celsius
- **Description**: The temperature to set when heating is active
- **Example**: `20.5`
- **Recommendations**:
  - Sports facilities: 18-20°C
  - Changing rooms: 20-22°C
  - Balance comfort with energy efficiency

### Schedule Refresh Options

#### `scan_interval`
- **Type**: Integer (600-86400)
- **Required**: No
- **Default**: 21600 (6 hours)
- **Unit**: Seconds
- **Description**: How often to refresh the schedule from the website
- **Example**: `3600` (1 hour)
- **Considerations**:
  - More frequent updates = more accurate but more load on website
  - Less frequent = less accurate but more efficient
  - Default (6 hours) is a good balance for most use cases
  - Events are checked every minute, only schedule fetching is affected

### Control Options

#### `enabled`
- **Type**: Boolean
- **Required**: No
- **Default**: true
- **Description**: Whether the scheduler is enabled
- **Example**: `true` or `false`
- **Note**: Can be changed at runtime using services

#### `dry_run`
- **Type**: Boolean
- **Required**: No
- **Default**: false
- **Description**: When enabled, the scheduler logs what it would do but doesn't actually control the heating
- **Example**: `true` or `false`
- **Use Cases**:
  - Testing the integration before going live
  - Debugging schedule issues
  - Verifying pre-heat and cool-down times

## Complete YAML Example

```yaml
zhc_heating_scheduler:
  # Required
  schedule_url: "https://www.zhc.nl/schedule"
  climate_entity: "climate.plugwise_sa"
  
  # Timing (optional)
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  # Temperature (optional)
  target_temperature: 20.0
  
  # Refresh (optional)
  scan_interval: 21600  # 6 hours
  
  # Control (optional)
  enabled: true
  dry_run: false
```

## Updating Configuration

### UI Configuration

To update configuration after initial setup:

1. Go to **Settings** → **Devices & Services**
2. Find "ZHC Heating Scheduler"
3. Click **Configure**
4. Modify the values
5. Click **Submit**

### YAML Configuration

1. Edit `configuration.yaml`
2. Update the values under `zhc_heating_scheduler:`
3. Restart Home Assistant or reload the integration

## Configuration Validation

The integration validates configuration to prevent common errors:

- **Schedule URL**: Must be a valid URL format
- **Climate Entity**: Must exist and start with `climate.`
- **Pre-heat Hours**: Must be between 0 and 24
- **Cool-down Minutes**: Must be between 0 and 120
- **Target Temperature**: Must be between 5.0°C and 35.0°C
- **Scan Interval**: Must be between 600 (10 min) and 86400 (24 hours)

## Tips for Optimal Configuration

### Pre-heat Time Recommendations

| Building Size | Insulation | Recommended Pre-heat |
|---------------|------------|---------------------|
| Small (<200m²) | Good | 1-2 hours |
| Medium (200-500m²) | Good | 2-3 hours |
| Large (>500m²) | Good | 3-4 hours |
| Any size | Poor | Add 1-2 hours |

### Cool-down Time Recommendations

- **Short events (<2h)**: 15-20 minutes
- **Medium events (2-3h)**: 30 minutes (default)
- **Long events (>3h)**: 30-45 minutes

### Scan Interval Recommendations

- **Static schedules** (rarely change): 12-24 hours
- **Normal schedules**: 6 hours (default)
- **Frequently updated schedules**: 1-3 hours
- **Never less than**: 10 minutes (to avoid overloading the website)

## Advanced: Per-Event Configuration

Currently, the integration applies the same pre-heat and cool-down times to all events. If you need different settings for different event types, you can:

1. Create multiple instances of the integration (not recommended)
2. Use Home Assistant automations to adjust settings based on event type
3. Customize the scheduler code (see DEVELOPMENT.md)

Example automation to adjust for different event types:

```yaml
automation:
  - alias: "Adjust heating for matches"
    trigger:
      - platform: state
        entity_id: sensor.zhc_current_event
    condition:
      - condition: template
        value_template: "{{ 'match' in trigger.to_state.state | lower }}"
    action:
      # Matches might need more pre-heat time
      # You would need to implement this in the integration
```

## Environment-Specific Examples

### Small Club (1 field, simple schedule)

```yaml
zhc_heating_scheduler:
  schedule_url: "https://smallclub.com/schedule"
  climate_entity: "climate.clubhouse_heating"
  pre_heat_hours: 1
  cool_down_minutes: 20
  target_temperature: 19.0
  scan_interval: 43200  # 12 hours
```

### Large Club (multiple fields, frequent events)

```yaml
zhc_heating_scheduler:
  schedule_url: "https://bigclub.com/schedule"
  climate_entity: "climate.main_clubhouse"
  pre_heat_hours: 3
  cool_down_minutes: 45
  target_temperature: 20.5
  scan_interval: 3600  # 1 hour
```

### Testing Configuration

```yaml
zhc_heating_scheduler:
  schedule_url: "https://testclub.com/schedule"
  climate_entity: "climate.test_thermostat"
  pre_heat_hours: 0.5  # 30 minutes for quick testing
  cool_down_minutes: 5
  target_temperature: 20.0
  scan_interval: 600  # 10 minutes for testing
  dry_run: true  # Don't actually control heating during testing
```

