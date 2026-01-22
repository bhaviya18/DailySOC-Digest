import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai
import win32evtlog

# -------------------------------
# Setup
# -------------------------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# Discover usable Gemini model
# -------------------------------
def get_text_model():
    models = client.models.list()
    for model in models:
        if model.name.startswith("models/gemini"):
            return model.name
    raise RuntimeError("No Gemini text model found")

MODEL_NAME = get_text_model()
print(f"Using Gemini model: {MODEL_NAME}")

# -------------------------------
# Read Windows Security Logs
# -------------------------------
def read_security_events(limit=30):
    server = "localhost"
    log_type = "Security"

    handle = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(handle, flags, 0)

    return events[:limit]

# -------------------------------
# Convert Windows Events → SOC Alerts
# -------------------------------
def windows_events_to_alerts(events):
    alerts = []

    for event in events:
        event_id = event.EventID & 0xFFFF

        if event_id == 4625:
            alerts.append({
                "source": "Windows Security Log",
                "severity": "high",
                "description": "Failed login attempt detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        elif event_id == 4624:
            alerts.append({
                "source": "Windows Security Log",
                "severity": "low",
                "description": "Successful login detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        elif event_id == 4672:
            alerts.append({
                "source": "Windows Security Log",
                "severity": "medium",
                "description": "Special privileges assigned to logon",
                "timestamp": event.TimeGenerated.isoformat()
            })

    return alerts

# -------------------------------
# Ingest REAL alerts
# -------------------------------
raw_events = read_security_events()
alerts = windows_events_to_alerts(raw_events)

# -------------------------------
# Deduplicate & prioritize
# -------------------------------
seen = set()
deduplicated = []

for alert in alerts:
    key = (alert["source"], alert["description"])
    if key not in seen:
        seen.add(key)
        deduplicated.append(alert)

priority_order = {"high": 1, "medium": 2, "low": 3}
deduplicated.sort(key=lambda x: priority_order[x["severity"]])

# -------------------------------
# Gemini AI Explanation
# -------------------------------
def ai_explain(alert):
    prompt = f"""
You are a senior SOC analyst writing an internal security report.

Write in clear, professional English.
Use complete sentences.
Avoid casual language.
Avoid repetition.
Be concise and precise.

Alert details:
Source: {alert['source']}
Severity: {alert['severity']}
Description: {alert['description']}

Respond in three short sections:

What happened:
Describe the event factually in one or two sentences.

Why it matters:
Explain the security impact and potential risk clearly.

What to do next:
Provide practical, actionable remediation steps.

Do not use markdown.
Do not use bullet points.
Do not use symbols.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()

# -------------------------------
# Build Digest
# -------------------------------
now_utc = datetime.now(timezone.utc)

digest = {
    "summary": {
        "date": now_utc.isoformat(),
        "total_alerts": len(deduplicated)
    },
    "alerts": []
}

for alert in deduplicated:
    explanation = ai_explain(alert)
    digest["alerts"].append({
        "severity": alert["severity"],
        "source": alert["source"],
        "description": alert["description"],
        "ai_explanation": explanation
    })

# -------------------------------
# Save Report
# -------------------------------
os.makedirs("reports", exist_ok=True)
timestamp = now_utc.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"reports/daily_digest_{timestamp}.json"

with open(filename, "w") as out:
    json.dump(digest, out, indent=2)

print("AI-powered SOC digest generated using REAL Windows logs")
print(f"Report written to {filename}")
