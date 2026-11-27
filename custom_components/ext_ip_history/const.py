"""Constants for External IP History."""

DOMAIN = "ext_ip_history"

CONF_URL = "url"
CONF_INTERVAL = "interval"

DEFAULT_URL = "https://myexternalip.com/raw"
DEFAULT_INTERVAL = 60  # minutes

MAX_CHANGES = 50
HISTORY_HOURS = 24

LOG_FILE = "ext_ip_history.log"  # created in the HA config directory
MAX_LOG_BYTES = 1_000_000  # rotates to .log.1 above this size

STORAGE_VERSION = 1
