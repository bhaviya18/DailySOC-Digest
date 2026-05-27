import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from google import genai
import win32evtlog

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------------------------------
# Discover usable Gemini model
# -------------------------------------------------
def get_text_model():
    models = client.models.list()

    for model in models:
        if model.name.startswith("models/gemini"):
            return model.name

    raise RuntimeError("No Gemini model found")

MODEL_NAME = get_text_model()

print(f"Using Gemini model: {MODEL_NAME}")

# -------------------------------------------------
# Read Windows logs with fallback support
# -------------------------------------------------
def read_windows_events(limit=50):
    server = "localhost"

    try:
        log_type = "Security"

        handle = win32evtlog.OpenEventLog(
            server,
            log_type
        )

        print("Using Windows Security logs")

    except Exception:
        log_type = "Application"

        handle = win32evtlog.OpenEventLog(
            server,
            log_type
        )

        print(
            "Security logs unavailable — using Application logs"
        )

    flags = (
        win32evtlog.EVENTLOG_BACKWARDS_READ
        | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    )

    events = win32evtlog.ReadEventLog(
        handle,
        flags,
        0
    )

    return events[:limit]

# -------------------------------------------------
# Convert Windows events into SOC alerts
# -------------------------------------------------
def windows_events_to_alerts(events):
    alerts = []

    for event in events:
        event_id = event.EventID & 0xFFFF

        # -----------------------------------------
        # Security Events
        # -----------------------------------------
        if event_id == 4625:
            alerts.append({
                "severity": "high",
                "source": "Windows Security Log",
                "description": "Failed login attempt detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        elif event_id == 4624:
            alerts.append({
                "severity": "low",
                "source": "Windows Security Log",
                "description": "Successful login detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        elif event_id == 4672:
            alerts.append({
                "severity": "medium",
                "source": "Windows Security Log",
                "description": "Privileged logon activity detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        # -----------------------------------------
        # Application Events
        # -----------------------------------------
        elif event_id in [1000, 1001]:
            alerts.append({
                "severity": "medium",
                "source": "Windows Application Log",
                "description": "Application error detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

        elif event_id in [11707, 11724]:
            alerts.append({
                "severity": "low",
                "source": "Windows Application Log",
                "description": "Software installation activity detected",
                "timestamp": event.TimeGenerated.isoformat()
            })

    return alerts

# -------------------------------------------------
# Deduplicate alerts
# -------------------------------------------------
def deduplicate_alerts(alerts):
    seen = set()
    deduplicated = []

    for alert in alerts:
        key = (
            alert["source"],
            alert["description"]
        )

        if key not in seen:
            seen.add(key)
            deduplicated.append(alert)

    return deduplicated

# -------------------------------------------------
# Prioritize alerts
# -------------------------------------------------
def prioritize_alerts(alerts):
    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3
    }

    return sorted(
        alerts,
        key=lambda x: priority_order[x["severity"]]
    )

# -------------------------------------------------
# Gemini AI explanation
# -------------------------------------------------
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

Respond in three sections:

What happened:
Describe the event factually.

Why it matters:
Explain the security impact.

What to do next:
Provide practical remediation steps.

Do not use markdown.
Do not use bullet points.
Do not use symbols.
"""

    print(
        f"Running Gemini AI for: {alert['description']}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()

# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
def run_pipeline():
    os.makedirs("reports", exist_ok=True)

    raw_events = read_windows_events(limit=100)

    alerts = windows_events_to_alerts(raw_events)

    if not alerts:
        print("No security-relevant events found")
        return

    alerts = deduplicate_alerts(alerts)

    alerts = prioritize_alerts(alerts)

    now_utc = datetime.now(timezone.utc)

    digest = {
        "summary": {
            "date": now_utc.isoformat(),
            "total_alerts": len(alerts)
        },
        "alerts": []
    }

    for alert in alerts:
        explanation = ai_explain(alert)

        digest["alerts"].append({
            "severity": alert["severity"],
            "source": alert["source"],
            "description": alert["description"],
            "ai_explanation": explanation
        })

    timestamp = now_utc.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"reports/daily_digest_{timestamp}.json"
    )

    with open(filename, "w") as out:
        json.dump(digest, out, indent=2)

    print("\nAI-powered SOC digest generated")
    print(f"Report written to: {filename}")

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    run_pipeline()