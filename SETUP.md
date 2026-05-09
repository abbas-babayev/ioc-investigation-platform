# SETUP.md — Step-by-Step Deployment Guide

> Complete installation and deployment guide for **IOC Investigation Platform**  
> Target OS: **Ubuntu 24.04 LTS** | Network: **LAN + Tailscale VPN**

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Update the System](#2-update-the-system)
3. [Install Base Utilities](#3-install-base-utilities)
4. [Install Docker](#4-install-docker)
5. [Install Tailscale](#5-install-tailscale)
6. [Download the Project](#6-download-the-project)
7. [Configure Environment Variables](#7-configure-environment-variables)
8. [Configure Network Access](#8-configure-network-access)
9. [Open Firewall Ports](#9-open-firewall-ports)
10. [Start the Project](#10-start-the-project)
11. [Verify Everything Works](#11-verify-everything-works)
12. [Push to GitHub](#12-push-to-github)
13. [Useful Docker Commands](#13-useful-docker-commands)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. System Requirements

| Component      | Requirement                          |
|----------------|--------------------------------------|
| OS             | Ubuntu 24.04 LTS                     |
| RAM            | 512 MB minimum (1 GB recommended)    |
| Disk           | 2 GB free space                      |
| Network        | LAN and/or Tailscale VPN             |
| VirusTotal Key | Free API key (500 requests/day)      |
| GitHub account | Required for pushing the project     |

Get your free VirusTotal API key at: https://www.virustotal.com/gui/sign-in

---

## 2. Update the System

Always start with a full system update on a fresh server:

```bash
# Update the package list and upgrade all installed packages
sudo apt update && sudo apt upgrade -y
```

> `sudo` — runs the command as administrator  
> `apt` — Ubuntu's package manager  
> `-y` — automatically answers "yes" to all prompts

---

## 3. Install Base Utilities

Install essential tools needed for the next steps:

```bash
# Install curl, git, unzip, nano and other required utilities
sudo apt install -y \
  curl \
  wget \
  git \
  unzip \
  nano \
  ca-certificates \
  gnupg \
  lsb-release \
  software-properties-common
```

| Tool     | Purpose                                      |
|----------|----------------------------------------------|
| `curl`   | Download files and test API endpoints        |
| `git`    | Version control — required for GitHub        |
| `unzip`  | Extract ZIP archives                         |
| `nano`   | Simple terminal text editor                  |
| `gnupg`  | Verify package signatures (security)         |

---

## 4. Install Docker

Docker allows us to run the backend and frontend as isolated containers without installing Python or Nginx manually.

### 4.1 — Add Docker's official GPG key

```bash
# Create the directory for storing GPG keys
sudo install -m 0755 -d /etc/apt/keyrings

# Download and save Docker's GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Make the key readable by all users
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

### 4.2 — Add Docker's official repository

```bash
# Add the Docker repository to apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 4.3 — Install Docker Engine

```bash
# Update package list (now includes Docker repo)
sudo apt update

# Install Docker and all required components
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

### 4.4 — Start Docker and enable autostart

```bash
# Start the Docker service now
sudo systemctl start docker

# Enable Docker to start automatically on server reboot
sudo systemctl enable docker
```

### 4.5 — Add your user to the docker group

```bash
# This allows running docker without sudo every time
sudo usermod -aG docker $USER

# Apply group changes without logging out
newgrp docker
```

### 4.6 — Verify Docker installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Run the test container — should print "Hello from Docker!"
docker run hello-world
```

Expected output:
```
Docker version 26.x.x
Docker Compose version v2.x.x
Hello from Docker!
```

✅ If you see `Hello from Docker!` — Docker is working correctly.

---

## 5. Install Tailscale

Tailscale creates a private VPN network between your devices. Each device gets a stable IP like `100.x.x.x`.

### 5.1 — Install Tailscale

```bash
# Official one-line installer from Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
```

### 5.2 — Connect to your Tailscale network

```bash
# Start Tailscale and authenticate
sudo tailscale up
```

A URL will appear in the terminal — open it in your browser and authorize the server in your Tailscale account.

### 5.3 — Get your Tailscale IP

```bash
# Display your Tailscale IPv4 address
tailscale ip -4
```

Example output: `100.66.5.102`

### 5.4 — Check Tailscale status

```bash
# Show connected devices and their status
tailscale status
```

---

## 6. Download the Project

### Option A — Upload via SCP (from your local machine)

```bash
# Run this on YOUR LOCAL computer, not the server
scp ioc-investigation-platform.zip your_user@YOUR_SERVER_IP:/home/your_user/
```

### Option B — Clone from GitHub (if already pushed)

```bash
# Clone the repository directly on the server
git clone https://github.com/YOUR_USERNAME/ioc-investigation-platform.git
cd ioc-investigation-platform
```

### Option C — Unzip if already uploaded via SFTP/panel

```bash
# Navigate to home directory
cd ~

# Extract the ZIP archive
unzip ioc-investigation-platform.zip

# Enter the project folder
cd ioc-investigation-platform
```

---

## 7. Configure Environment Variables

The `.env` file stores your secret API keys. It is never committed to Git.

```bash
# Navigate to the backend directory
cd ~/ioc-investigation-platform/backend

# Create .env from the template
cp .env.example .env

# Open the file for editing
nano .env
```

You will see:
```
VT_API_KEY=your_virustotal_api_key_here
```

Replace `your_virustotal_api_key_here` with your real VirusTotal API key.

Save and exit nano:
- `Ctrl + O` → then `Enter` (save)
- `Ctrl + X` (exit)

Verify the key was saved:
```bash
# Should print your API key (not the placeholder)
cat .env
```

> ⚠️ **Security rule**: `.env` is listed in `.gitignore` and will never be pushed to GitHub.

---

## 8. Configure Network Access

Two files need to be updated to allow access from both your LAN IP (`192.168.56.64`) and Tailscale IP (`100.66.5.102`).

### 8.1 — Update docker-compose.yml

```bash
nano ~/ioc-investigation-platform/docker-compose.yml
```

Make sure the ports section looks like this:

```yaml
version: "3.9"

services:

  backend:
    build:
      context: ./backend
    ports:
      # Listen on ALL network interfaces: localhost, LAN and Tailscale
      - "0.0.0.0:8000:8000"
    env_file:
      - ./backend/.env
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      # Listen on ALL network interfaces: localhost, LAN and Tailscale
      - "0.0.0.0:80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped
```

Save: `Ctrl+O` → Enter → `Ctrl+X`

### 8.2 — Update app.js (dynamic API URL)

```bash
nano ~/ioc-investigation-platform/frontend/app.js
```

Find this line:
```javascript
const API_URL = "http://localhost:8000";
```

Replace it with:
```javascript
// Automatically use the same hostname the browser is using.
// If accessed via 192.168.56.64 → API goes to 192.168.56.64:8000
// If accessed via 100.66.5.102  → API goes to 100.66.5.102:8000
const API_URL = `http://${window.location.hostname}:8000`;
```

Save: `Ctrl+O` → Enter → `Ctrl+X`

---

## 9. Open Firewall Ports

```bash
# Allow HTTP traffic on port 80 (frontend)
sudo ufw allow 80/tcp

# Allow API traffic on port 8000 (backend)
sudo ufw allow 8000/tcp

# Allow all traffic through the Tailscale network interface
sudo ufw allow in on tailscale0

# Apply the new rules
sudo ufw reload

# Verify all rules are active
sudo ufw status
```

Expected output should include:
```
80/tcp     ALLOW
8000/tcp   ALLOW
```

> If you use a cloud provider (Hetzner, DigitalOcean, AWS, etc.) — also open ports 80 and 8000 in your cloud firewall/security group panel.

---

## 10. Start the Project

```bash
# Navigate to the project root
cd ~/ioc-investigation-platform

# Build Docker images and start all containers in the background
docker compose up --build -d
```

> `--build` — rebuilds images (required after code changes)  
> `-d` — detached mode, runs in background

Check that both containers are running:
```bash
docker compose ps
```

Expected output:
```
NAME                STATUS
backend             running
frontend            running
```

---

## 11. Verify Everything Works

### Test backend API from the server itself

```bash
# Health check — all three should return {"status":"ok",...}
curl http://localhost:8000
curl http://192.168.56.64:8000
curl http://100.66.5.102:8000
```

### Test a full IOC lookup

```bash
# Send a test request to the API
curl -X POST http://localhost:8000/api/lookup \
  -H "Content-Type: application/json" \
  -d '{"ioc": "8.8.8.8"}'
```

Expected response:
```json
{
  "ioc": "8.8.8.8",
  "ioc_type": "ip",
  "stats": { "malicious": 0, "suspicious": 0, "harmless": 79, "undetected": 14 },
  "risk_level": "Low",
  "recommendation": "No threats detected...",
  "error": null
}
```

### Access from other devices

Open in your browser from any device on your network:

| Access point         | URL                          |
|----------------------|------------------------------|
| Server itself        | `http://localhost`           |
| LAN (local network)  | `http://192.168.56.64`       |
| Tailscale VPN        | `http://100.66.5.102`        |

---

## 12. Push to GitHub

### 12.1 — Configure Git identity

```bash
# Set your name and email (used in commit history)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 12.2 — Initialize the repository

```bash
cd ~/ioc-investigation-platform

# Initialize a new local git repository
git init
```

### 12.3 — Stage all files

```bash
# Add all files except those listed in .gitignore
# .env will NOT be included — it is protected by .gitignore
git add .

# Verify what will be committed (check .env is NOT listed)
git status
```

### 12.4 — Create the first commit with co-author

```bash
# Commit with a descriptive message and co-author tag
# Replace CO_AUTHOR_NAME and CO_AUTHOR_EMAIL with real values
git commit -m "feat: initial MVP - IOC Investigation Platform

- FastAPI backend with VirusTotal API v3 integration
- IOC type detection: IP, domain, URL, hash
- Risk scoring: Low / Medium / High / Critical
- Dark theme frontend with vanilla JS
- Docker Compose deployment
- LAN + Tailscale network support

Co-authored-by: CO_AUTHOR_NAME <CO_AUTHOR_GITHUB_EMAIL>"
```

> The `Co-authored-by:` line must use the **exact email linked to their GitHub account**.  
> GitHub will then show both avatars on the commit automatically.

### 12.5 — Create a repository on GitHub

1. Go to https://github.com/new
2. Set repository name: `ioc-investigation-platform`
3. Choose **Public** (for open source)
4. Do **NOT** initialize with README (you already have one)
5. Click **Create repository**

### 12.6 — Connect local repo to GitHub and push

```bash
# Add the GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ioc-investigation-platform.git

# Rename the default branch to main
git branch -M main

# Push all files to GitHub
git push -u origin main
```

GitHub will ask for your credentials:
- Username: your GitHub username
- Password: use a **Personal Access Token** (not your account password)

### 12.7 — Create a Personal Access Token (if needed)

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Set expiration and check scope: `repo`
4. Copy the token and use it as your password when pushing

### 12.8 — Add co-author as collaborator (optional)

If your co-author needs to push code too:

1. Go to your repo on GitHub
2. **Settings** → **Collaborators** → **Add people**
3. Enter their GitHub username
4. They will receive an email invitation to accept

---

## 13. Useful Docker Commands

```bash
# Show running containers and their status
docker compose ps

# View backend logs (useful when something breaks)
docker compose logs backend

# Follow logs in real time (Ctrl+C to stop)
docker compose logs -f backend

# Stop all containers
docker compose down

# Restart after making code changes
docker compose up --build -d

# Enter the backend container for debugging
docker compose exec backend bash

# Remove all stopped containers and unused images (free up space)
docker system prune -f
```

---

## 14. Troubleshooting

### ❌ "Cannot connect to backend" in the browser

```bash
# Check if containers are actually running
docker compose ps

# Check backend logs for errors
docker compose logs backend

# Verify ports are open
sudo ufw status
```

### ❌ "Invalid API key" error

```bash
# Check your .env file — the key must be real, not the placeholder
cat ~/ioc-investigation-platform/backend/.env

# Restart backend after fixing the key
docker compose up --build -d
```

### ❌ "Rate limit exceeded" error

The free VirusTotal API allows **4 requests per minute** and **500 per day**.  
Wait 60 seconds and try again. For higher limits, upgrade your VirusTotal plan.

### ❌ Frontend loads but API calls fail

This usually means `app.js` still has `localhost` hardcoded.  
Check that the dynamic URL fix from Step 8.2 was applied:

```bash
grep "API_URL" ~/ioc-investigation-platform/frontend/app.js
# Should show: const API_URL = `http://${window.location.hostname}:8000`;
```

Then rebuild:
```bash
docker compose up --build -d
```

### ❌ Tailscale IP not reachable

```bash
# Verify Tailscale is running and connected
tailscale status

# Verify the UFW rule for tailscale0 exists
sudo ufw status | grep tailscale

# If missing, add it:
sudo ufw allow in on tailscale0
sudo ufw reload
```

---

## ✅ Final Checklist

```
[ ] System updated (apt update && upgrade)
[ ] Base utilities installed
[ ] Docker installed and running
[ ] docker run hello-world succeeds
[ ] Tailscale installed and authenticated
[ ] Project files extracted on the server
[ ] .env created with real VT_API_KEY
[ ] docker-compose.yml uses 0.0.0.0 for all ports
[ ] app.js uses window.location.hostname (not localhost)
[ ] UFW ports 80 and 8000 are open
[ ] UFW allows tailscale0 interface
[ ] docker compose up --build -d succeeds
[ ] curl http://localhost:8000 returns {"status":"ok"}
[ ] curl http://192.168.56.64:8000 returns {"status":"ok"}
[ ] curl http://100.66.5.102:8000 returns {"status":"ok"}
[ ] Frontend opens in browser from all three addresses
[ ] Code pushed to GitHub with co-author tag
```

---

*IOC Investigation Platform — Open Source SOC Tool*  
*For authorized security investigation only.*
