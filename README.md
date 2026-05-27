# DailySOC Digest – AI-Powered SOC Automation

DailySOC Digest is an AI-assisted Security Operations Center (SOC) automation tool that ingests real Windows Security Event Logs, normalizes them into SOC alerts, and generates professional security analysis and remediation guidance using Google Gemini.

This project demonstrates how modern SOC workflows can be enhanced using AI to reduce alert fatigue and improve incident response quality.

---

## 🔍 Key Features

- Ingests real Windows Security Event Logs (administrator access required)
- Detects authentication and privilege-related security activity
- Normalizes raw logs into SOC-style alerts
- Deduplicates and prioritizes alerts by severity
- Uses Google Gemini to generate analyst-grade explanations
- Produces structured JSON security reports
- Displays alerts in a clean, professional SOC-style web dashboard

---

## 🧠 How It Works

Windows Security Logs
↓
SOC Event Normalization
↓
Severity Prioritization
↓
Gemini AI Analysis
↓
JSON Security Reports
↓
Web Dashboard


---

## 🛠 Technology Stack

- Python
- Flask
- Google Gemini (LLM)
- Windows Event Logs (pywin32)
- HTML / CSS (SOC-style dashboard)

---

## 🚨 Security Events Covered

- Failed login attempts (Event ID 4625)
- Successful login events (Event ID 4624)
- Privileged logon activity (Event ID 4672)

---

## ▶️ Setup & Usage

> **Note:** This project is designed for Windows systems.

1. Clone the repository
2. Install dependencies:
3. Create a `.env` file and add your Gemini API key:
4. Run the SOC pipeline:
5. Start the web dashboard:
6. Open in your browser:
   http://127.0.0.1:5000

---

## 🎯 Use Case

DailySOC Digest helps SOC analysts by:
- Converting raw security logs into actionable alerts
- Explaining alerts in clear, professional language
- Providing structured remediation guidance
- Improving response speed and decision-making

---

## ⚠️ Disclaimer

This project is for educational and portfolio purposes only.  
It is not intended for production use without proper security hardening and review.

---

## 👤 Author

**Bhaviya Talwar**  

---

## ⭐ Acknowledgements
- Windows Event Logging
- Google Gemini API
- Open-source Python ecosystem





