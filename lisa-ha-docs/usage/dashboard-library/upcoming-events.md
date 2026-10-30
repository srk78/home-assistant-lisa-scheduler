---
title: Upcoming Events Panel
tags: [usage, dashboards, panels]
---

# Upcoming Events Panel

Shows every upcoming match and training session. LISA Scheduler ships this as a sidebar panel; a dashboard card version is available if you prefer a card on an existing view.

## Sidebar Panel (built in)

After installing or updating the integration and restarting Home Assistant, a **LISA Schedule** entry appears in the sidebar. It lists upcoming events grouped by day, with filter tabs for **All**, **Matches** and **Trainings**, and refreshes itself every minute.

- Events that have already ended are hidden; an event that is running now stays visible.
- A `~` before the end time means the API estimated the end time.
- The panel is visible to all users, not only admins.
- The list comes from the websocket command `lisa_scheduler/upcoming_events` (optional `event_types` list of `match` / `training`), which you can also call from your own frontend code.
- The panel shows whatever the API returns. Events outside the club venue only appear when `include_external_events` is enabled.

## Dashboard Card Version

The **Last Schedule Update** sensor exposes the loaded events in its `api_events` attribute. This Markdown card lists the upcoming ones, soonest first:

```yaml
type: markdown
title: Upcoming games and training
content: >-
  {% set now_iso = now().strftime('%Y-%m-%dT%H:%M:%S') %}
  {% set events = state_attr('sensor.lisa_scheduler_last_schedule_update', 'api_events') or [] %}
  {% for e in events | sort(attribute='start_time') if e.end_time > now_iso %}
  - **{{ e.start_time[:16] | replace('T', ' ') }}** · {{ 'Match' if e.event_type == 'match' else 'Training' }} · {{ e.title }}{% if e.location %} ({{ e.location }}){% endif %}
  {% else %}
  No upcoming events.
  {% endfor %}
```

To show only matches or only trainings, add `and e.event_type == 'match'` (or `'training'`) to the `if` in the `for` line.

The comparison uses the ISO text of the timestamps, so it assumes your Home Assistant time zone matches the schedule time zone (default `Europe/Amsterdam`).

The API is read for the next 14 days, so the list never reaches further ahead than that.
