# Smart Home Platform — Complete Unified Architecture

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)]()
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-Edge--First%20%7C%20Context--Aware-purple.svg)]()

A production-grade, enterprise-ready, edge-first, energy-aware, and context-aware Smart Home Platform spanning all 50+ domain areas in modern home automation, robotics, energy storage, and industrial gateway integration.

---

## Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Node.js v18+ & npm
- Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/Dhanunjay-narra/Smart-Home-Platform.git
cd Smart-Home-Platform

# 2. Create and activate Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Node.js frontend dependencies
npm install
```

---

## Build

To build the static frontend bundle and compile firmware artifacts:

```bash
# 1. Build Node / Frontend assets
npm run build || npm test

# 2. Build Docker container image
docker build -t smarthome/platform:v2.4.0 -f infrastructure/docker/Dockerfile .
```

---

## Run

### Starting the Platform Server

To start the unified server (serves both API Gateway and Web Application UI):

```bash
python run_server.py
```

Or on Windows, simply double click:
```cmd
run_app.bat
```

Open your browser to:
👉 **[http://localhost:8000](http://localhost:8000)**

API Documentation (Swagger UI):
👉 **[http://localhost:8000/api/docs](http://localhost:8000/api/docs)**

---

## Dependencies

### Backend Python Packages
- **FastAPI** (`0.110.0+`): Asynchronous ASGI Web Framework
- **Uvicorn** (`0.28.0+`): Lightning-fast ASGI web server
- **Pydantic** (`2.6.4+`): Data validation and settings management
- **WebSockets** (`12.0+`): Full-duplex real-time telemetry streaming
- **Python-Jose** (`3.3.0+`): Cryptographic JWT token encoding/decoding
- **Passlib** (`1.7.4+`): Secure password hashing (bcrypt/argon2)
- **Cryptography** (`42.0.5+`): Hardware signature validation & mTLS
- **Pytest** (`8.1.1+`): Comprehensive automated test framework

### Frontend Libraries
- **Tailwind CSS**: Modern utility-first stylesheet engine
- **Chart.js**: Real-time canvas telemetry visualization
- **FontAwesome / Lucide**: Modern UI iconography

---

## Usage

### 🔑 1-Click Login Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Platform Owner** | `admin@smarthome.local` | `HomeAdmin2026!` | Full Admin (All 50 Modules) |
| **Visiting Guest** | `guest@smarthome.local` | `GuestPass2026!` | Restricted Room Access |

*(You can also click the **1-Click Login** button on the top right of the web dashboard for instant one-tap evaluation).*

### Key Capabilities & Endpoints
- **Home Mode Switch**: Toggle between `HOME`, `AWAY`, `SLEEP`, and `VACATION`.
- **Solar & Storage**: Live solar MPPT tracking, battery SoC monitoring, and EV charging current throttle.
- **Natural Language Assistant**: Send text queries like *"Turn off living room lights"*, *"Set AC to 22C"*, or *"What is current solar power?"*.
- **Security & Cameras**: Live WebRTC camera stream simulation with AI person/vehicle bounding boxes and alarm arming.
- **Automated Test Suite**: Run `pytest tests/ -v` to execute all automated test scenarios.

---

## 🔒 Proprietary Ownership & Intellectual Property Notice

**Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.**

This software, source code, design specifications, firmware, and accompanying documentation are proprietary and confidential property of **Dhanunjay Narra**. Unauthorized copying, distribution, decompilation, modification, or commercial exploitation is strictly prohibited without express written authorization.
