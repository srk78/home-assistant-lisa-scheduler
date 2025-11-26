---
title: Basic Settings
tags: [configuration, settings, basics]
---

# Basic Settings

Configure the essential settings for the ZHC Heating Scheduler.

## Overview

Basic settings control:
- **Pre-heat timing** - When to start heating before events
- **Cool-down timing** - When to stop heating before events end
- **Target temperature** - Desired temperature when heating
- **Climate entity** - Which device to control

## Configuration Methods

Settings can be configured via:
1. **UI** - Settings → Devices & Services → Configure
2. **YAML** - `configuration.yaml` file

## Essential Settings

### Schedule URL

**Description**: The webpage containing your club's schedule

**UI Field**: Schedule URL  
**YAML Key**: `schedule_url`  
**Type**: String (URL)  
**Required**: Yes  

**Example**:
```yaml
schedule_url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
```

### Climate Entity

**Description**: The thermostat or heating control device

**UI Field**: Climate Entity  
**YAML Key**: `climate_entity`  
**Type**: Entity ID  
**Required**: Yes  

**Example**:
```yaml
climate_entity: "climate.plugwise_sa"
```

**Finding your climate entity**:
1. Developer Tools → States
2. Search for `climate.`
3. Copy the entity ID

### Pre-heat Time

**Description**: Hours before an event to start heating

**UI Field**: Pre-heat time (hours)  
**YAML Key**: `pre_heat_hours`  
**Type**: Integer (0-24)  
**Default**: 2  

**Example**:
```yaml
pre_heat_hours: 2
```

**Recommendations**:
- Small building (<200m²): 1-2 hours
- Medium building (200-500m²): 2-3 hours
- Large building (>500m²): 3-4 hours
- Poor insulation: Add 1-2 hours

See [[timing-optimization|Timing Optimization]] for details.

### Cool-down Time

**Description**: Minutes before event ends to stop heating

**UI Field**: Cool-down time (minutes)  
**YAML Key**: `cool_down_minutes`  
**Type**: Integer (0-120)  
**Default**: 30  

**Example**:
```yaml
cool_down_minutes: 30
```

**Recommendations**:
- Short events (<2h): 15-20 minutes
- Medium events (2-3h): 30 minutes
- Long events (>3h): 30-45 minutes

### Target Temperature

**Description**: Temperature to reach when heating

**UI Field**: Target temperature (°C)  
**YAML Key**: `target_temperature`  
**Type**: Float (5.0-35.0)  
**Default**: 20.0  

**Example**:
```yaml
target_temperature: 20.0
```

**Recommendations**:
- Sports facility: 18-20°C
- Changing rooms: 20-22°C
- Spectator areas: 18-20°C

## Complete Example

### UI Configuration

1. Settings → Devices & Services
2. ZHC Heating Scheduler → Configure
3. Fill in all fields
4. Click Submit

### YAML Configuration

```yaml
zhc_heating_scheduler:
  # Required
  schedule_url: "https://www.club.com/schedule"
  climate_entity: "climate.plugwise_sa"
  
  # Timing
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  # Temperature
  target_temperature: 20.0
```

## See Also

- [[advanced-settings|Advanced Settings]]
- [[timing-optimization|Timing Optimization]]
- [[examples|Configuration Examples]]
- [[../quick-start/first-time-setup|First Time Setup]]

---

**Difficulty**: Easy  
**Next**: [[advanced-settings|Advanced Settings]]

