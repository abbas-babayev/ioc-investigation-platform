# Architecture Documentation

## IOC Investigation Platform — How It Works

---

## 1. Platform Overview

The IOC Investigation Platform is a lightweight web application designed for SOC analysts to quickly enrich Indicators of Compromise (IOCs) using the VirusTotal API.

A user enters a suspicious indicator (IP, domain, URL, or file hash), the system identifies its type, queries VirusTotal, and returns a structured threat assessment with risk level and analyst recommendation.

---

## 2. Request Flow

```
User (Browser)
    │
    │  Types IOC → clicks INVESTIGATE
    │
    ▼
Frontend (HTML/CSS/JS)
    │
    │  POST /api/lookup  { "ioc": "8.8.8.8" }
    │
    ▼
Backend (FastAPI)
    │
    ├── detector.py     → Identifies IOC type (ip/domain/url/hash)
    │
    ├── virustotal.py   → Sends request to VirusTotal API v3
    │                     Returns raw detection stats
    │
    └── scoring.py      → Calculates risk level + recommendation
    │
    │  JSON Response
    │
    ▼
Frontend
    │
    └── Renders: IOC, type, stats, risk badge, recommendation
```

---

## 3. Backend Modules

### `main.py` — Entry Point
- Creates FastAPI app
- Configures CORS middleware (allows browser to call the API)
- Defines POST `/api/lookup` endpoint
- Orchestrates: detect → lookup → score → return

### `detector.py` — IOC Type Detection
Uses regex patterns to identify:
| Type    | Pattern Example         |
|---------|------------------------|
| URL     | `https://evil.com/x`  |
| IP      | `192.168.1.1`          |
| Hash    | 32/40/64 hex chars     |
| Domain  | `malware.example.com`  |
| Unknown | None of the above      |

Order matters: URL is checked before domain to avoid misclassification.

### `virustotal.py` — VirusTotal Integration
Maps IOC types to API endpoints:
| IOC Type | VT Endpoint                    |
|----------|-------------------------------|
| IP       | `/api/v3/ip_addresses/{ip}`  |
| Domain   | `/api/v3/domains/{domain}`   |
| Hash     | `/api/v3/files/{hash}`       |
| URL      | `/api/v3/urls/{base64_url}`  |

URL lookup uses base64url encoding (VirusTotal v3 requirement).
Uses `httpx` async client with 15s timeout.
Handles: 200 OK, 404 Not Found, 401 Unauthorized, 429 Rate Limit.

### `scoring.py` — Risk Scoring Engine
```
malicious = 0, suspicious = 0  →  Low
malicious = 0, suspicious > 0  →  Low (with advisory)
malicious 1–3                  →  Medium
malicious 4–10                 →  High
malicious > 10                 →  Critical
```
Returns a risk level string and a plain-English analyst recommendation.

---

## 4. Frontend Flow

1. User enters IOC in `index.html` input field
2. `app.js:investigate()` fires on button click or Enter key
3. `fetch()` sends POST request to `http://localhost:8000/api/lookup`
4. Response is parsed and passed to `showResult(data)`
5. DOM is updated: stats, risk badge (with CSS class), recommendation
6. If error → `showError(message)` displays error block

---

## 5. VirusTotal Integration Details

- API Version: v3
- Authentication: `x-apikey` header
- Free tier limits: **4 requests/minute, 500 requests/day**
- The API key is read from environment variable `VT_API_KEY` via `.env`
- Never hardcode API keys in source code

---

## 6. Risk Scoring Rationale

VirusTotal aggregates results from 70+ antivirus engines.
The `malicious` count reflects how many engines flagged the IOC as a threat.

- **Low (0 detections):** No evidence of threat. Standard monitoring applies.
- **Medium (1–3):** Low-confidence detection. Could be false positive. Investigate context.
- **High (4–10):** Multi-vendor confirmation. Block and investigate.
- **Critical (>10):** Confirmed threat. Incident response warranted.

---

## 7. Security Considerations

- `.env` is listed in `.gitignore` — never committed to git
- `.env.example` provides a safe template
- CORS is currently open (`*`) — restrict to specific origin in production
- No authentication on the API — add API key or OAuth for production use
- Do not actively probe malicious IOCs without proper network containment

---

## 8. Future Improvements (Roadmap)

| Feature               | Description                               |
|-----------------------|-------------------------------------------|
| AbuseIPDB integration | Reputation data for IP addresses          |
| WHOIS lookup          | Registration info for domains             |
| DNS resolution        | A/MX/NS records for domains               |
| Shodan integration    | Open ports and services for IPs           |
| PDF export            | Generate investigation report             |
| History log           | Store past lookups in SQLite              |
| Rate limiting         | Protect API from abuse                    |
| Authentication        | Multi-user support with API keys          |
| Bulk lookup           | Investigate multiple IOCs at once         |
