import win32evtlog

server = 'localhost'
log_type = 'Security'  # Requires admin privileges

handle = win32evtlog.OpenEventLog(server, log_type)

flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

events = win32evtlog.ReadEventLog(handle, flags, 0)

print("Recent Windows SECURITY Events:\n")

for event in events[:10]:
    print(f"Event ID: {event.EventID & 0xFFFF}")
    print(f"Source: {event.SourceName}")
    print(f"Time Generated: {event.TimeGenerated}")
    print("-" * 40)
