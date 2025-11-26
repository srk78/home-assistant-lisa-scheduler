---
title: Timing Optimization
tags: [configuration, timing, optimization]
---

# Timing Optimization

Optimize pre-heat and cool-down times for your specific building and needs.

## Understanding Timing

### Pre-heat Time

**Purpose**: Start heating early enough so the building is warm when people arrive

**Factors to consider**:
- Building size
- Insulation quality
- Outside temperature
- Heating system capacity
- Desired comfort level

### Cool-down Time

**Purpose**: Stop heating early to save energy while building stays warm

**Factors to consider**:
- Building thermal mass
- Event duration
- Number of people
- Energy costs

## Optimization Process

### Step 1: Start with Defaults

```yaml
pre_heat_hours: 2
cool_down_minutes: 30
```

### Step 2: Monitor First Events

Track:
- When heating starts
- Temperature at event start
- Temperature during event
- When heating stops
- Temperature at event end

### Step 3: Adjust Based on Results

**If too cold at start**:
- Increase `pre_heat_hours`
- Check insulation
- Verify target temperature

**If too warm at start**:
- Decrease `pre_heat_hours`
- Lower target temperature

**If too cold at end**:
- Decrease `cool_down_minutes`
- Check event duration

**If wasting energy**:
- Increase `cool_down_minutes`
- Fine-tune pre-heat

## Building Size Guidelines

### Small Building (<200m²)

```yaml
pre_heat_hours: 1-1.5
cool_down_minutes: 20-25
```

**Characteristics**:
- Heats quickly
- Cools quickly
- Less thermal mass

### Medium Building (200-500m²)

```yaml
pre_heat_hours: 2-2.5
cool_down_minutes: 25-35
```

**Characteristics**:
- Moderate heating time
- Good heat retention
- Standard setup

### Large Building (>500m²)

```yaml
pre_heat_hours: 3-4
cool_down_minutes: 35-45
```

**Characteristics**:
- Slow to heat
- Good heat retention
- High thermal mass

## Insulation Impact

### Good Insulation

- Faster heating
- Better heat retention
- Longer cool-down possible

**Adjustment**: -0.5 to -1 hour pre-heat

### Poor Insulation

- Slower heating
- Faster heat loss
- Shorter cool-down needed

**Adjustment**: +1 to +2 hours pre-heat

## Seasonal Adjustments

### Winter (Cold weather)

```yaml
pre_heat_hours: 3  # +1 hour
cool_down_minutes: 25  # -5 minutes
```

**Reasoning**:
- Colder start temperature
- More heat loss
- Longer to reach comfort

### Summer (Warm weather)

```yaml
pre_heat_hours: 1  # -1 hour
cool_down_minutes: 40  # +10 minutes
```

**Reasoning**:
- Warmer start temperature
- Less heat needed
- Building stays warm longer

## Event Type Optimization

### Short Events (<90 minutes)

```yaml
cool_down_minutes: 15-20
```

**Reasoning**: Less time to cool, people leaving sooner

### Long Events (>3 hours)

```yaml
cool_down_minutes: 40-45
```

**Reasoning**: More time to cool, energy savings significant

### Back-to-back Events

System automatically merges overlapping heating windows.

## Testing Methodology

### Week 1: Baseline

- Use defaults
- Monitor all events
- Record temperatures
- Note comfort levels

### Week 2: Adjust Pre-heat

- Modify pre-heat time
- Keep cool-down same
- Compare results

### Week 3: Adjust Cool-down

- Keep optimized pre-heat
- Modify cool-down time
- Compare results

### Week 4: Fine-tune

- Make small adjustments
- Test edge cases
- Document final settings

## Monitoring Tools

### Sensor to Watch

- `sensor.zhc_next_heating_start`
- `sensor.zhc_next_heating_stop`
- `binary_sensor.zhc_heating_active`

### Dashboard Card

```yaml
type: history-graph
title: Heating Pattern
entities:
  - binary_sensor.zhc_heating_active
  - climate.plugwise_sa
hours_to_show: 24
```

## Advanced: Dynamic Timing

### Temperature-based Adjustment

```yaml
automation:
  - alias: "Adjust pre-heat for cold weather"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        below: 5
    action:
      # Would need custom service to adjust timing
      # This is a future feature
```

## Common Scenarios

### Scenario 1: Cold Mornings

**Problem**: Building not warm enough for 9 AM events

**Solution**:
```yaml
pre_heat_hours: 3  # Start at 6 AM
```

### Scenario 2: Energy Waste

**Problem**: Building too warm at event end

**Solution**:
```yaml
cool_down_minutes: 45  # Stop heating 45 min before end
```

### Scenario 3: Weekend Events

**Problem**: Building very cold on Monday morning

**Solution**: Consider minimum temperature setback

## Optimization Checklist

- [ ] Baseline measurements taken
- [ ] Building characteristics documented
- [ ] Pre-heat time optimized
- [ ] Cool-down time optimized
- [ ] Seasonal adjustments planned
- [ ] Monitoring dashboard created
- [ ] Staff feedback collected
- [ ] Energy costs reviewed

## See Also

- [[basic-settings|Basic Settings]]
- [[advanced-settings|Advanced Settings]]
- [[../usage/sensors|Available Sensors]]
- [[../troubleshooting/heating-not-starting|Troubleshooting]]

---

**Time needed**: 2-4 weeks (testing period)  
**Difficulty**: Intermediate  
**Prerequisites**: Integration installed and running

