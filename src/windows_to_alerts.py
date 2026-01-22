import win32evtlog
from datetime import datetime, timezone

def read_security_events(limit=20):
    server = 'localhost'
    log_type = 'Security'

    handle = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    events = win32evtlog.ReadEventLog(handle, flags, 0)
    return events[:limit]

def convert_to_alert(event):
    event_id = event.EventID & 0xFFFF

    if event_id == 4625:
        return {
            "source": "Windows Security Log",
            "severity": "high",
            "description": "Failed login attempt detected",
            "timestamp": event.TimeGenerated.replace(tzinfo=timezone.utc).isoformat()
        }

    if event_id == 4624:
        return {
            "source": "Windows Security Log",
            "severity": "low",
            "description": "Successful login detected",
            "timestamp": event.TimeGenerated.replace(tzinfo=timezone.utc).isoformat()
        }

    if event_id == 4672:
        return {
            "source": "Windows Security Log",
            "severity": "medium",
            "description": "Special privileges assigned to new logon",
            "timestamp": event.TimeGenerated.replace(tzinfo=timezone.utc).isoformat()
        }

    return None

print("Converted SOC Alerts:\n")

events = read_security_events()
alerts = []

for event in events:
    alert = convert_to_alert(event)
    if alert:
        alerts.append(alert)
        print(alert)
