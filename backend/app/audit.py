import logging
import json
from datetime import datetime, timezone

# Configure a dedicated audit logger
audit_logger = logging.getLogger("securevault.audit")
audit_logger.setLevel(logging.INFO)

# Console handler — in production this would write to a file or SIEM
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(handler)


def log_event(event_type: str, username: str = None, ip: str = None, details: dict = None):
    """
    Log a security-relevant event in structured JSON format.
    JSON logs are easy to ingest into a SIEM like Splunk or Elastic.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "username": username,
        "ip": ip,
        "details": details or {}
    }
    audit_logger.info(json.dumps(entry))