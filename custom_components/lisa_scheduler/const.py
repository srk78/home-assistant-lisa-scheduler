"""Constants for the LISA Scheduler integration."""

DOMAIN = "lisa_scheduler"

# Configuration keys
CONF_SCHEDULE_URL = "schedule_url"
CONF_LOGO_URL = "logo_url"
CONF_PRE_EVENT_MINUTES = "pre_event_minutes"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENABLED = "enabled"
CONF_DRY_RUN = "dry_run"

# Default values
DEFAULT_PRE_EVENT_MINUTES = 120  # 2 hours
DEFAULT_SCAN_INTERVAL = 21600  # 6 hours in seconds
DEFAULT_ENABLED = True
DEFAULT_DRY_RUN = False

# HA event names fired on state transitions
EVENT_WINDOW_STARTED = "lisa_scheduler_window_started"
EVENT_WINDOW_ENDED = "lisa_scheduler_window_ended"
EVENT_EVENT_STARTED = "lisa_scheduler_event_started"
EVENT_EVENT_ENDED = "lisa_scheduler_event_ended"

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
EVENT_TYPE_UNKNOWN = "unknown"

# Update intervals
UPDATE_INTERVAL_SCHEDULE = 21600  # 6 hours
UPDATE_INTERVAL_STATE = 60  # 1 minute for state checks

# Logging
LOGGER_NAME = "custom_components.lisa_scheduler"

# Scraper configuration
CONF_SCRAPER_SOURCES = "scraper_sources"
CONF_DATE_FORMAT = "date_format"
CONF_TIME_FORMAT = "time_format"
CONF_TIMEZONE = "timezone"

# Scraper source configuration keys
CONF_SOURCE_URL = "url"
CONF_SOURCE_TYPE = "type"
CONF_SOURCE_METHOD = "method"
CONF_SOURCE_SELECTORS = "selectors"
CONF_SOURCE_API_ENDPOINT = "api_endpoint"
CONF_SOURCE_API_HEADERS = "api_headers"
CONF_SOURCE_API_PARAMS = "api_params"

# Scraper methods
SCRAPER_METHOD_HTML = "html"
SCRAPER_METHOD_API = "api"
SCRAPER_METHOD_ICAL = "ical"

# Default scraper settings
DEFAULT_DATE_FORMAT = "%d-%m-%Y"
DEFAULT_TIME_FORMAT = "%H:%M"
DEFAULT_TIMEZONE = "Europe/Amsterdam"
