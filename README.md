# 🔍 IOC Investigation Platform

> A lightweight, open-source SOC tool for threat intelligence enrichment.  
> Enter an IP, domain, URL, or file hash — get instant VirusTotal analysis with risk scoring.

---

## 📌 Description

**IOC Investigation Platform** is a web-based security tool built for SOC analysts and threat intelligence workflows. It automates IOC (Indicator of Compromise) enrichment by querying the VirusTotal API and presenting structured results with risk assessment.

Built with simplicity in mind — no complex infrastructure, just a FastAPI backend and a plain HTML/CSS/JS frontend with a dark terminal aesthetic.

---

## ✨ Features

- 🔎 **Auto-detection** of IOC type: IP, Domain, URL, Hash (MD5/SHA1/SHA256)
- 📡 **VirusTotal API v3** integration — real-time threat intelligence
- 📊 **Detection stats**: malicious, suspicious, harmless, undetected counts
- 🚦 **Risk scoring**: Low / Medium / High / Critical
- 💬 **Analyst recommendations** based on detection counts
- 🌑 **Dark terminal UI** — clean and focused
- 🐳 **Docker support** for easy local deployment
- 🔐 **Secure by default** — API keys via `.env`, never hardcoded

---

## 🏗️ Architecture

```
Browser (Frontend)
        │
        │ POST /api/lookup { "ioc": "..." }
        ▼
FastAPI Backend
  ├── detector.py    → Identifies IOC type
  ├── virustotal.py  → Queries VirusTotal API
  └── scoring.py     → Calculates risk + recommendation
        │
        │ JSON response
        ▼
Browser renders result
```

See [docs/architecture.md](docs/architecture.md) for full documentation.

---

## 🛠️ Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Backend  | Python 3.11, FastAPI        |
| HTTP     | httpx (async)               |
| Config   | python-dotenv               |
| Frontend | HTML5, CSS3, Vanilla JS     |
| Server   | Uvicorn                     |
| Deploy   | Docker, Docker Compose      |
| API      | VirusTotal API v3           |

---

## 📁 Project Structure

```
ioc-investigation-platform/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, endpoint /api/lookup
│   │   ├── detector.py      # IOC type detection (regex)
│   │   ├── virustotal.py    # VirusTotal API integration
│   │   └── scoring.py       # Risk scoring logic
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example         # Environment variable template
│
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Dark theme styles
│   └── app.js               # fetch() logic, DOM updates
│
├── docs/
│   └── architecture.md      # Technical documentation
│
├── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.11+
- [VirusTotal API key](https://www.virustotal.com/gui/sign-in) (free tier available)
- Docker & Docker Compose (optional)

---

### Option A: Run Without Docker (Recommended for Development)

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ioc-investigation-platform.git
cd ioc-investigation-platform
```

**2. Set up Python virtual environment**
```bash
cd backend
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure your API key**
```bash
cp .env.example .env
# Open .env and replace: VT_API_KEY=your_virustotal_api_key_here
```

**5. Start the backend**
```bash
uvicorn app.main:app --reload
# Server runs at http://localhost:8000
```

**6. Open the frontend**

Simply open `frontend/index.html` in your browser.  
No build step needed — it's plain HTML.

---

### Option B: Run With Docker

**1. Configure environment**
```bash
cd backend
cp .env.example .env
# Edit .env and add your VirusTotal API key
```

**2. Start all services**
```bash
# From the project root:
docker-compose up --build
```

**3. Access the platform**
- Frontend: http://localhost:80
- Backend API: http://localhost:8000

---

## 🔑 Environment Variables

| Variable    | Description                    | Required |
|-------------|--------------------------------|----------|
| `VT_API_KEY` | VirusTotal API key            | ✅ Yes   |

Get your free API key at: https://www.virustotal.com/gui/sign-in

> ⚠️ **Security**: Never commit `.env` to Git. The `.gitignore` already excludes it.

---

## 🚀 Usage

1. Open the platform in your browser
2. Enter any of the following:
   - **IP address**: `8.8.8.8`, `185.220.101.1`
   - **Domain**: `malware.example.com`, `phishing-site.ru`
   - **URL**: `http://evil.com/payload.exe`
   - **File hash**: `44d88612fea8a8f36de82e1238abc123` (MD5/SHA1/SHA256)
3. Click **INVESTIGATE** or press **Enter**
4. Review the results: detection stats, risk level, and analyst recommendation

---

## 📡 API Reference

### `POST /api/lookup`

**Request:**
```json
{
  "ioc": "8.8.8.8"
}
```

**Response:**
```json
{
  "ioc": "8.8.8.8",
  "ioc_type": "ip",
  "stats": {
    "malicious": 0,
    "suspicious": 0,
    "harmless": 79,
    "undetected": 14
  },
  "risk_level": "Low",
  "recommendation": "No threats detected. IOC appears clean...",
  "error": null
}
```

**Health Check:**
```
GET /
→ { "status": "ok", "message": "IOC Investigation Platform is running" }
```

---

## 📸 Screenshots

> _Screenshots coming soon — run locally and see for yourself!_

---

## 🗺️ Roadmap

- [ ] AbuseIPDB integration (IP reputation)
- [ ] WHOIS lookup for domains
- [ ] DNS resolution (A, MX, NS records)
- [ ] Shodan integration (open ports)
- [ ] PDF investigation report export
- [ ] SQLite history log
- [ ] Bulk IOC lookup (CSV upload)
- [ ] API authentication (API key middleware)
- [ ] OpenCTI / MISP integration
- [ ] MITRE ATT&CK mapping

---

## ⚠️ Disclaimer

This tool is intended for **authorized security research and investigation only**.

- Do not use this tool to investigate IOCs on systems you don't have permission to analyze
- Do not actively connect to, probe, or interact with malicious URLs or IPs
- VirusTotal free API has limits: 4 requests/minute, 500 requests/day
- This tool provides threat intelligence data — it does not constitute legal or forensic advice

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

---

*Built for the SOC community. Stay safe, investigate smart.*

## Acknowledgements
Built by [@abbas-babayev](https://github.com/abbas-babayev) and [@nugetts](https://github.com/nugetts)
