from flask import Flask, render_template_string
import json
import os
import re

app = Flask(__name__)

REPORTS_DIR = "reports"

# -------------------------------------------------
# STRICT AI TEXT PARSER (NO MARKDOWN RELIANCE)
# -------------------------------------------------
def parse_ai_explanation(text: str):
    sections = {
        "what_happened": "",
        "why_it_matters": "",
        "what_to_do": []
    }

    if not text:
        return sections

    # Remove markdown / symbols
    clean = re.sub(r"[*#]+", "", text)

    # Helper: split into proper sentences
    def split_sentences(block):
        sentences = re.split(r'(?<=[.!?])\s+', block.strip())
        return [s.strip().capitalize() for s in sentences if len(s.strip()) > 3]

    lines = [l.strip() for l in clean.splitlines() if l.strip()]
    current = None
    buffer = ""

    for line in lines:
        lower = line.lower()

        if "what happened" in lower:
            current = "what_happened"
            buffer = ""
            continue

        if "why it matters" in lower:
            sections["what_happened"] = " ".join(split_sentences(buffer))
            current = "why_it_matters"
            buffer = ""
            continue

        if "what to do" in lower or "what should be done" in lower:
            sections["why_it_matters"] = " ".join(split_sentences(buffer))
            current = "what_to_do"
            buffer = ""
            continue

        buffer += line + " "

    # Finalize last section
    if current == "what_to_do":
        sections["what_to_do"] = split_sentences(buffer)
    elif current == "why_it_matters":
        sections["why_it_matters"] = " ".join(split_sentences(buffer))

    return sections



# -------------------------------------------------
# HTML TEMPLATE (SOC-GRADE UI)
# -------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DailySOC Digest</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont;
            background: #0b1220;
            color: #e5e7eb;
            padding: 32px;
        }

        h1 {
            color: #38bdf8;
            margin-bottom: 24px;
        }

        .summary {
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }

        .alerts {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .alert {
            background: #020617;
            border-radius: 14px;
            border: 1px solid #1e293b;
            padding: 24px;
        }

        .alert.high { border-left: 6px solid #ef4444; }
        .alert.medium { border-left: 6px solid #f59e0b; }
        .alert.low { border-left: 6px solid #22c55e; }

        .badge {
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
            display: inline-block;
            margin-bottom: 10px;
        }

        .high .badge { background: #ef4444; color: #020617; }
        .medium .badge { background: #f59e0b; color: #020617; }
        .low .badge { background: #22c55e; color: #020617; }

        .meta {
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 8px;
        }

        .section {
            margin-top: 14px;
        }

        .section-title {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: #7dd3fc;
            margin-bottom: 4px;
        }

        .section-body {
            font-size: 14px;
            line-height: 1.6;
            color: #e5e7eb;
        }

        footer {
            margin-top: 40px;
            font-size: 12px;
            color: #64748b;
            text-align: center;
        }
    </style>
</head>

<body>

<h1>🛡️ DailySOC Digest</h1>

<div class="summary">
    <p><strong>Date:</strong> {{ summary.date }}</p>
    <p><strong>Total Alerts:</strong> {{ summary.total_alerts }}</p>
</div>

<div class="alerts">
{% for alert in alerts %}
    <div class="alert {{ alert.severity }}">
        <span class="badge">{{ alert.severity.upper() }}</span>

        <div class="meta"><strong>Source:</strong> {{ alert.source }}</div>
        <div class="meta"><strong>Description:</strong> {{ alert.description }}</div>

        {% if alert.ai.what_happened %}
        <div class="section">
            <div class="section-title">WHAT HAPPENED</div>
            <div class="section-body">{{ alert.ai.what_happened }}</div>
        </div>
        {% endif %}

        {% if alert.ai.why_it_matters %}
        <div class="section">
            <div class="section-title">WHY IT MATTERS</div>
            <div class="section-body">{{ alert.ai.why_it_matters }}</div>
        </div>
        {% endif %}

       {% if alert.ai.what_to_do %}
<div class="section">
    <div class="section-title">WHAT TO DO NEXT</div>
    <div class="section-body">
        <ol>
        {% for step in alert.ai.what_to_do %}
            <li>{{ step }}</li>
        {% endfor %}
        </ol>
    </div>
</div>
{% endif %}

    </div>
{% endfor %}
</div>

<footer>
    Internal SOC Dashboard · AI-assisted security triage
</footer>

</body>
</html>
"""

# -------------------------------------------------
# ROUTE
# -------------------------------------------------
@app.route("/")
def dashboard():
    files = sorted(os.listdir(REPORTS_DIR), reverse=True)
    if not files:
        return "No SOC reports found"

    with open(os.path.join(REPORTS_DIR, files[0])) as f:
        report = json.load(f)

    for alert in report["alerts"]:
        alert["ai"] = parse_ai_explanation(alert.get("ai_explanation", ""))

    return render_template_string(
        HTML_TEMPLATE,
        summary=report["summary"],
        alerts=report["alerts"]
    )

if __name__ == "__main__":
    app.run(debug=True)
