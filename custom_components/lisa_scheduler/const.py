"""Constants for the LISA Scheduler integration."""

DOMAIN = "lisa_scheduler"

# Configuration keys
CONF_API_URL = "api_url"
CONF_API_TIMEZONE = "api_timezone"
CONF_INCLUDE_EXTERNAL_EVENTS = "include_external_events"
LEGACY_CONF_SCHEDULE_URL = "schedule_url"
CONF_LOGO_URL = "logo_url"
CONF_PRE_EVENT_TRIGGERS = "pre_event_triggers"
CONF_PRE_FIRST_EVENT_TRIGGERS = "pre_first_event_triggers"
CONF_PRE_LAST_EVENT_END_TRIGGERS = "pre_last_event_end_triggers"
CONF_POST_LAST_EVENT_TRIGGERS = "post_last_event_triggers"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENABLED = "enabled"
CONF_DRY_RUN = "dry_run"

# Default values
DEFAULT_PRE_EVENT_TRIGGERS = [120]  # 2 hours
DEFAULT_SCAN_INTERVAL = 600  # 10 minutes in seconds
DEFAULT_INCLUDE_EXTERNAL_EVENTS = False
DEFAULT_ENABLED = True
DEFAULT_DRY_RUN = False

# HA event names fired on state transitions
EVENT_WINDOW_STARTED = "lisa_scheduler_window_started"
EVENT_WINDOW_ENDED = "lisa_scheduler_window_ended"
EVENT_EVENT_STARTED = "lisa_scheduler_event_started"
EVENT_EVENT_ENDED = "lisa_scheduler_event_ended"
EVENT_PRE_EVENT_TRIGGER = "lisa_scheduler_pre_event_trigger"
EVENT_FIRST_EVENT_STARTED = "lisa_scheduler_first_event_started"
EVENT_LAST_EVENT_ENDED = "lisa_scheduler_last_event_ended"
EVENT_PRE_FIRST_EVENT_TRIGGER = "lisa_scheduler_pre_first_event_trigger"
EVENT_PRE_LAST_EVENT_END_TRIGGER = "lisa_scheduler_pre_last_event_end_trigger"
EVENT_POST_LAST_EVENT_TRIGGER = "lisa_scheduler_post_last_event_trigger"

# Service names
SERVICE_REFRESH_SCHEDULE = "refresh_schedule"
SERVICE_ENABLE = "enable"
SERVICE_DISABLE = "disable"
SERVICE_SET_OVERRIDE = "set_override"
SERVICE_CLEAR_OVERRIDE = "clear_override"

# Sensor attributes
ATTR_NEXT_EVENT = "next_event"
ATTR_EVENTS_TODAY = "events_today"
ATTR_EVENT_WINDOWS = "event_windows"
ATTR_LAST_UPDATE = "last_update"
ATTR_LAST_ERROR = "last_error"
ATTR_SCHEDULE_SOURCE = "schedule_source"

# Event types
EVENT_TYPE_TRAINING = "training"
EVENT_TYPE_MATCH = "match"
EVENT_TYPE_CLUB_EVENT = "event"
EVENT_TYPE_UNKNOWN = "unknown"

# Update intervals
UPDATE_INTERVAL_SCHEDULE = DEFAULT_SCAN_INTERVAL
UPDATE_INTERVAL_STATE = 60  # 1 minute for state checks

# Logging
LOGGER_NAME = "custom_components.lisa_scheduler"

# Schedule timezone returned by the API
CONF_TIMEZONE = "timezone"
DEFAULT_TIMEZONE = "Europe/Amsterdam"
