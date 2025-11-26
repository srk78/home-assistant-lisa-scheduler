"""Constants for the ZHC Heating Scheduler integration."""

DOMAIN = "zhc_heating_scheduler"

# Configuration keys
CONF_SCHEDULE_URL = "schedule_url"
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_PRE_HEAT_HOURS = "pre_heat_hours"
CONF_COOL_DOWN_MINUTES = "cool_down_minutes"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TARGET_TEMPERATURE = "target_temperature"
CONF_ENABLED = "enabled"
CONF_DRY_RUN = "dry_run"

# Default values
DEFAULT_PRE_HEAT_HOURS = 2
DEFAULT_COOL_DOWN_MINUTES = 30
DEFAULT_SCAN_INTERVAL = 21600  # 6 hours in seconds
DEFAULT_TARGET_TEMPERATURE = 20.0  # Celsius
DEFAULT_ENABLED = True
DEFAULT_DRY_RUN = False

# Service names
SERVICE_REFRESH_SCHEDULE = "refresh_schedule"
SERVICE_ENABLE = "enable"
SERVICE_DISABLE = "disable"
SERVICE_SET_OVERRIDE = "set_override"
SERVICE_CLEAR_OVERRIDE = "clear_override"

# Sensor attributes
ATTR_NEXT_EVENT = "next_event"
ATTR_EVENTS_TODAY = "events_today"
ATTR_HEATING_WINDOWS = "heating_windows"
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
LOGGER_NAME = "custom_components.zhc_heating_scheduler"

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

