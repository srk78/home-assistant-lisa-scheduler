---
title: Dashboard Cards
tags: [usage, dashboards, panels]
---

# Dashboard Cards

This library gives club operators copy-paste Home Assistant dashboard panels for LISA Scheduler. The panels are designed around four daily questions:

- What is happening now?
- What is next?
- Is the schedule healthy?
- Can I refresh, pause, or override quickly?

## Before You Copy

Entity IDs may differ in your Home Assistant instance. Check **Developer Tools -> States** and search for `lisa_scheduler` before pasting a card. The snippets below use the documented entity naming pattern:

- `sensor.lisa_scheduler_current_event`
- `sensor.lisa_scheduler_next_window_start`
- `sensor.lisa_scheduler_next_window_end`
- `sensor.lisa_scheduler_next_event_start`
- `sensor.lisa_scheduler_events_today`
- `sensor.lisa_scheduler_window_minutes_today`
- `sensor.lisa_scheduler_total_event_windows`
- `sensor.lisa_scheduler_last_schedule_update`
- `binary_sensor.lisa_scheduler_window_active`
- `binary_sensor.lisa_scheduler_event_active`
- `binary_sensor.lisa_scheduler_enabled`
- `binary_sensor.lisa_scheduler_manual_override_active`
- `button.lisa_scheduler_refresh_schedule`

If your entity IDs omit the `lisa_scheduler_` middle segment, replace them with the names from your own States page.

## Recommended Layout

Use a **Sections** dashboard view for new dashboards. Sections make it easier to resize cards and arrange operator panels for tablet, mobile, and desktop screens. Native snippets work without HACS. Enhanced snippets use popular custom cards and list their prerequisites before each YAML block.

## Enhanced Dashboard Prerequisites

Install only the custom cards used by the panel you want:

- **Mushroom**: primary status cards, chips, and operator-friendly controls.
- **Bubble Card**: mobile panels, pop-ups, footer actions, and compact navigation.
- **button-card**: dense custom status buttons and more expressive state styling.
- **apexcharts-card**: timeline/history panels and richer schedule graphs.
- **layout-card**: optional advanced layout control when HA Sections is not enough.

## Panel Library

| Panel | Best for | Native | Enhanced |
|-------|----------|--------|----------|
| [[dashboard-library/operator-overview|Operator Overview]] | Main club operations screen | Yes | Mushroom |
| [[dashboard-library/today-timeline|Today Timeline]] | Schedule timeline and daily load | Yes | apexcharts-card |
| [[dashboard-library/manual-override-control|Manual Override Control]] | Quick refresh, pause, and override workflows | Yes | Mushroom + Bubble Card |
| [[dashboard-library/diagnostics-panel|Diagnostics Panel]] | API and schedule health | Yes | button-card |
| [[dashboard-library/kiosk-public-display|Kiosk/Public Display]] | Clubhouse screen or wall tablet | Yes | Mushroom |
| [[dashboard-library/mobile-quick-panel|Mobile Quick Panel]] | Operator phone dashboard | Yes | Bubble Card |
| [[dashboard-library/automation-monitor|Automation Monitor]] | Watching transitions and automations | Yes | apexcharts-card |
| [[dashboard-library/enhanced-custom-dashboard|Enhanced Custom Dashboard]] | Full polished operator dashboard | No | Mushroom + Bubble + button-card + apexcharts |

## Quick Native Starter

Use this if you want one simple built-in card immediately:

```yaml
type: entities
title: Club Schedule
show_header_toggle: false
entities:
  - entity: sensor.lisa_scheduler_current_event
    name: Current or next event
  - entity: binary_sensor.lisa_scheduler_window_active
    name: Window active
  - entity: binary_sensor.lisa_scheduler_event_active
    name: Event active
  - entity: sensor.lisa_scheduler_next_window_start
    name: Next window opens
  - entity: sensor.lisa_scheduler_next_event_start
    name: Next event starts
  - entity: sensor.lisa_scheduler_events_today
    name: Events today
  - entity: sensor.lisa_scheduler_last_schedule_update
    name: Last schedule update
```

## Suggested Operator Dashboard Structure

For a full operator dashboard, create a Sections view and add these panels in this order:

1. [[dashboard-library/operator-overview|Operator Overview]]
2. [[dashboard-library/today-timeline|Today Timeline]]
3. [[dashboard-library/manual-override-control|Manual Override Control]]
4. [[dashboard-library/diagnostics-panel|Diagnostics Panel]]

For wall tablets or public screens, use [[dashboard-library/kiosk-public-display|Kiosk/Public Display]] as a separate dashboard with controls removed.

## See Also

- [[sensors|Available Sensors]]
- [[services|Available Services]]
- [[automations|Example Automations]]
