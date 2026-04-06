# Nexus OSINT — Digital Footprint Scanner 🌍

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

> An end-to-end Open Source Intelligence (OSINT) platform that scans an email address, username, or domain across global databases and returns a structured, risk-scored intelligence report — all behind a secure JWT-authenticated API and a clean Streamlit dashboard.

---

## 📖 Table of Contents

1. [What This Project Does](#-what-this-project-does)
2. [System Architecture](#-system-architecture)
3. [How Data Flows — Step by Step](#-how-data-flows--step-by-step)
4. [OSINT Scan Modules](#-osint-scan-modules)
   - [Email Breach Scan](#1-email-breach-scan)
   - [Username Scan](#2-username-scan)
   - [Domain DNS Scan](#3-domain-dns-scan)
   - [Image Metadata (EXIF) Scan](#4-image-metadata-exif-scan)
5. [Risk Scoring Engine](#-risk-scoring-engine)
6. [Security Elements](#-security-elements)
7. [Frontend Pages](#-frontend-pages)
8. [API Reference](#-api-reference)
9. [Installation Guide](#-installation-guide)
10. [Running with Docker](#-running-with-docker)
11. [Project File Structure](#-project-file-structure)
12. [Environment Variables](#-environment-variables)
13. [Known Limitations](#-known-limitations)
14. [Future Improvements](#-future-improvements)

---

## 🎯 What This Project Does

Nexus OSINT lets a registered user pick a target — an **email address**, a **username**, or a **domain name** — and then automatically:

1. Checks if the email appeared in any **known data breaches**
2. Discovers which **social media and public platforms** the username is registered on
3. Resolves the domain to an **IP address via DNS**
4. Extracts hidden **EXIF metadata and GPS coordinates** from uploaded images

Every scan runs in the **background** (so the UI never freezes), stores results in a **MySQL database**, and returns a **0–100 risk score** based on what was found. All endpoints are protected by short-lived **JWT access tokens** with a Redis-backed **refresh + logout blacklist** system.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER / CLIENT                        │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐    │
│   │   app.py    │  │ new_scan.py │  │   dashbord.py      │    │
│   │  (Login /   │  │  (Launch    │  │  (History, Risk,   │    │
│   │  Register)  │  │   a Scan)   │  │   Findings Table)  │    │
│   └─────────────┘  └─────────────┘  └────────────────────┘    │
│          │                │                   │                 │
│          └────────────────┴───────────────────┘                 │
│                           │  api.py (HTTP requests)             │
└───────────────────────────│─────────────────────────────────────┘
                            │  REST API calls (JSON)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND  (port 8000)                  │
│                                                                 │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│   │  /auth/*     │   │  /scans/*    │   │ /osint/image-    │  │
│   │  Register    │   │  Start,Get,  │   │  metadata        │  │
│   │  Login       │   │  List,Delete │   │  (synchronous)   │  │
│   │  Logout      │   │              │   │                  │  │
│   │  Refresh     │   │              │   │                  │  │
│   └──────────────┘   └──────────────┘   └──────────────────┘  │
│          │                  │                                   │
│     JWT + Redis        Celery .delay()                         │
└───────────────────────────────────────────────────────────────-─┘
         │                    │
         ▼                    ▼
┌──────────────┐   ┌──────────────────────────────────────────────┐
│  REDIS       │   │         CELERY WORKER (background)           │
│  • JWT       │   │                                              │
│    blacklist │   │  ┌─────────────┐   ┌─────────────────────┐  │
│  • Sherlock  │   │  │  breach_    │   │  username_osint.py  │  │
│    site list │   │  │  osint.py   │   │  (Sherlock engine)  │  │
│    cache     │   │  │  (XON API)  │   └─────────────────────┘  │
│  • Celery    │   │  └─────────────┘                            │
│    task      │   │  ┌──────────────────────────────────────┐   │
│    broker +  │   │  │  DNS lookup (socket.gethostbyname)   │   │
│    result    │   │  └──────────────────────────────────────┘   │
│    backend   │   │                                              │
└──────────────┘   │  Risk Score = calculate_risk(findings)       │
                   └──────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │   MYSQL DATABASE        │
                        │                         │
                        │   users table           │
                        │   scans table           │
                        │   (findings stored      │
                        │    as JSON column)      │
                        └─────────────────────────┘
```

---

## 🔄 How Data Flows — Step by Step

### Starting a Scan

```
User fills form in new_scan.py
        │
        │  POST /scans  { "email": "target@example.com" }
        │  Authorization: Bearer <access_token>
        ▼
FastAPI validates JWT → checks Redis blacklist → if clean, continues
        │
        ├── Creates a row in MySQL: status="Running", findings=[]
        │
        └── Sends task to Celery via Redis broker:
            run_osint_scan.delay(scan_id, email, username, domain)
        │
        │  Returns immediately:  { "scan_id": "uuid", "status": "queued" }
        ▼
Frontend starts polling GET /scans/{scan_id} every 2 seconds

Meanwhile, in the Celery Worker:
        │
        ├── If email  → calls XposedOrNot API → gets breach list
        ├── If username → fetches Sherlock site list → probes each site
        └── If domain  → DNS resolve → get IP address
        │
        └── calculate_risk(findings) → 0-100 score
        │
        └── UPDATE MySQL: status="Completed", findings=[...], risk_score=N

Frontend poll hits "Completed" → renders findings table + risk score
```

### Image Metadata (Synchronous — No Queue)

```
User uploads image in image_tools.py
        │
        │  POST /osint/image-metadata  (multipart/form-data)
        ▼
FastAPI saves file to a temp path → calls collect_image_metadata(path)
        │
        ├── Pillow reads EXIF tags
        ├── Extracts GPS IFD if present
        └── Converts DMS → Decimal Degrees
        │
        │  Returns immediately: { metadata: {...}, location: {lat, lon} }
        ▼
Frontend shows map pin + Google Maps link + raw metadata JSON
Temp file deleted from disk immediately after
```

---

## 🔍 OSINT Scan Modules

### 1. Email Breach Scan

**File:** `breach_osint.py`

**What it does:** Queries the free [XposedOrNot](https://xposedornot.com/) API to check if an email address appears in any publicly known data breach.

**Input:**
```
email: str  →  e.g. "someone@gmail.com"
```

**What happens inside:**
- The email is URL-encoded (handles `+` aliases and special characters safely)
- An HTTP GET is sent to `https://api.xposedornot.com/v1/check-email/{email}`
- Response is parsed for a list of breach names

**Output (list of finding dicts):**
```json
[
  { "name": "LinkedIn",  "severity": "HIGH", "source": "XposedOrNot" },
  { "name": "Adobe",     "severity": "HIGH", "source": "XposedOrNot" }
]
```

**Response code handling:**

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Breaches found | Parse and return list |
| 404 | No breaches found (clean email) | Return empty list |
| 429 | Rate limited by XON | Log warning, return empty list |
| 5xx | API error | Log error, return empty list |

**Timeout:** 15 seconds. If the API hangs, the module gives up and logs a timeout error — it does not block the whole scan.

---

### 2. Username Scan

**File:** `username_osint.py`

**What it does:** Uses the [Sherlock](https://github.com/sherlock-project/sherlock) site database (500+ platforms) to check if a username is registered on each platform.

**Input:**
```
username: str  →  e.g. "johndoe"
```

**What happens inside:**

```
Step 1 — Fetch site list
    Check Redis cache (key: "sherlock_sites", TTL 24 hours)
        → If cached: use it immediately
        → If not: fetch from Sherlock GitHub JSON, then cache it

Step 2 — Build probe tasks
    For each site in the list (up to SHERLOCK_SITE_LIMIT, default 500):
        Build the profile URL: e.g. https://github.com/johndoe
        Create an async probe task

Step 3 — Run all probes concurrently
    asyncio.gather(*tasks) fires all HTTP probes at once

Step 4 — Per probe decision:
    errorType == "status_code"  → 200 means "found"
    errorType == "message"      → site returns a specific string if user NOT found
                                  absence of that string = user found
    Redirect to login page      → false positive, skip
```

**Output (list of finding dicts):**
```json
[
  { "site": "GitHub",    "url": "https://github.com/johndoe" },
  { "site": "Reddit",    "url": "https://www.reddit.com/user/johndoe/" },
  { "site": "TikTok",    "url": "https://www.tiktok.com/@johndoe" }
]
```

**Fallback:** If the Sherlock GitHub JSON cannot be fetched, a hardcoded list of 10 popular platforms (GitHub, Twitter, Instagram, Reddit, etc.) is used so the scan never completely fails.

**Timeout per probe:** 15 seconds. Slow sites are skipped silently.

---

### 3. Domain DNS Scan

**File:** `celery_worker.py` (inline, no separate module)

**What it does:** Resolves a domain name to its IP address using a standard DNS lookup.

**Input:**
```
domain: str  →  e.g. "example.com"
```

**What happens inside:**
- Calls Python's built-in `socket.gethostbyname(domain)`
- No external API call, no rate limiting

**Output:**
```json
{ "type": "domain", "source": "DNS", "value": "Resolved IP: 93.184.216.34", "severity": "INFO" }
```
or if the domain cannot be resolved:
```json
{ "type": "domain", "source": "DNS", "value": "Domain could not be resolved.", "severity": "LOW" }
```

---

### 4. Image Metadata (EXIF) Scan

**File:** `image_metadata_osint.py`

**What it does:** Reads the hidden EXIF data embedded in a JPEG or PNG image — including camera model, software, timestamps, and GPS coordinates if the photo was taken on a phone.

**Input:**
```
file_path: str  →  path to a temporary file saved by FastAPI
```

**What happens inside:**
- Pillow opens the image and reads all EXIF tags
- Binary blobs (e.g. MakerNote) are replaced with `"<binary data omitted>"` to keep the JSON clean
- GPS IFD (Image File Directory) is read separately using the modern `exif.get_ifd()` method
- GPS coordinates in Degrees/Minutes/Seconds are converted to standard Decimal Degrees:
  ```
  Decimal = Degrees + (Minutes / 60) + (Seconds / 3600)
  Negative for South latitude or West longitude
  ```

**Output:**
```json
{
  "success": true,
  "metadata": {
    "Make": "Apple",
    "Model": "iPhone 14 Pro",
    "DateTime": "2024:03:15 14:22:10",
    "Software": "17.3.1"
  },
  "location": {
    "latitude": 10.015,
    "longitude": 76.329,
    "google_maps": "https://www.google.com/maps?q=10.015,76.329"
  }
}
```

If no GPS data exists, `"location"` will be `null`. If no EXIF data exists at all, `"metadata"` will be `{}`.

**Supported formats:** JPEG, PNG only. File is deleted from disk immediately after the scan completes.

---

## 📊 Risk Scoring Engine

**File:** `celery_worker.py` → `calculate_risk(findings)`

After all modules finish, a single integer score from **0 to 100** is calculated:

| Finding Type | Severity | Points Added |
|---|---|---|
| `breach` | CRITICAL | +25 |
| `breach` | HIGH / any other | +15 |
| `username` | (any) | +5 per platform found |
| `domain` | (any) | +10 |

The score is capped at 100. A clean target with no findings returns 0.

**Example:** An email found in 3 breaches = 3 × 15 = **45 / 100 risk score**.

---

## 🔐 Security Elements

### Authentication Flow

```
Register  →  password hashed with bcrypt (passlib)  →  stored in MySQL

Login     →  bcrypt verify  →  issue:
               Access Token  (JWT, 30 min expiry)
               Refresh Token (JWT, 7 day expiry)

Every protected API call:
    Client sends:  Authorization: Bearer <access_token>
    Server checks:
        1. Header present and formatted correctly?
        2. Token in Redis blacklist?  (if yes → 401)
        3. JWT signature valid?
        4. Token type == "access"?
        5. Username ("sub") present in payload?
    All pass → extract username → proceed

Logout    →  access token added to Redis blacklist with 1-hour TTL
             (token expires naturally anyway, but blacklist prevents
              reuse within that window)

Refresh   →  client sends refresh_token → server verifies type == "refresh"
             → issues a new access token
```

### JWT Token Structure

```json
{
  "sub": "username",
  "type": "access",
  "exp": 1712345678
}
```

### Rate Limiting

The image metadata endpoint is rate-limited to **15 requests per minute per IP address** using SlowAPI. Exceeding this returns HTTP 429.

### Scan Ownership

Every scan row in MySQL stores the `owner` field (the logged-in username). The API always filters by `owner` when listing or deleting scans — a user cannot read or delete another user's scans.

### Stale Scan Cleanup

On startup and every 5 minutes, a background task runs `mark_stale_scans_failed()`. Any scan stuck in `"Running"` status for more than 15 minutes is automatically marked as `"Failed"` with an explanatory error finding. This prevents the frontend from polling forever if the Celery worker crashed.

### Input Validation

The `ScanRequest` Pydantic model enforces that **exactly one** of `email`, `username`, or `domain` is provided and non-empty. Providing two fields, zero fields, or empty strings all return HTTP 422 with a clear error message.

---

## 🖥️ Frontend Pages

All frontend pages are built with **Streamlit** and communicate with the FastAPI backend via the `api.py` helper module.

### `app.py` — Login & Registration

- Entry point of the entire platform
- Two tabs: **Authentication** and **New Operative Registration**
- On successful login, the JWT access token is saved in `st.session_state.access_token`
- All other pages check for this token at the top; if missing, they show an "UNAUTHORIZED" message and stop

### `new_scan.py` — Launch a Scan

- Radio button to choose target type: Email / Username / Domain
- Text input for the target value
- On submit: calls `POST /scans`, gets back a `scan_id`
- Polls `GET /scans/{scan_id}` every 2 seconds (up to 300 polls = ~10 minutes)
- A visual progress bar updates as polling continues
- When scan completes: shows a Risk Score metric, total findings count, and a full findings table with clickable URLs

### `dashbord.py` — Operations History

- Fetches all scans owned by the logged-in user
- Shows three summary metrics: total scans, completed scans, average risk score
- An interactive table of all scans with timestamps
- A dropdown to select any scan ID and decrypt (fetch) its full findings payload

### `image_tools.py` — EXIF Forensics

- File uploader (JPEG/PNG only)
- Shows a preview of the uploaded image
- On "Run Forensic Analysis": calls `POST /osint/image-metadata`
- If GPS coordinates are found: renders an interactive map pin and a Google Maps link
- Shows all extracted EXIF metadata in a collapsible JSON viewer

---

## 📡 API Reference

All endpoints live at `http://localhost:8000` by default.

### Authentication

| Method | Endpoint | Body | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/auth/register` | `{username, password}` | No | Create a new account |
| POST | `/auth/login` | `{username, password}` | No | Get access + refresh tokens |
| POST | `/auth/refresh` | `{refresh_token}` | No | Get a new access token |
| POST | `/auth/logout` | — | Yes (Bearer) | Blacklist the current access token |

### Scans

| Method | Endpoint | Body / Query | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/scans` | `{email OR username OR domain}` | Yes | Start a new background scan |
| GET | `/scans` | `?limit=10&offset=0` | Yes | List all your past scans |
| GET | `/scans/{scan_id}` | — | Yes | Get full results of a specific scan |
| DELETE | `/scans/{scan_id}` | — | Yes | Delete a scan you own |

### OSINT

| Method | Endpoint | Body | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/osint/image-metadata` | `multipart/form-data: file` | Yes | Extract EXIF from image |
| GET | `/health` | — | No | Check if the API is running |

### Response: Start Scan
```json
HTTP 202 Accepted
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

### Response: Get Scan Result
```json
HTTP 200 OK
{
  "scan_id": "550e8400-...",
  "owner": "admin",
  "email": "target@example.com",
  "username": null,
  "domain": null,
  "status": "Completed",
  "risk_score": 45,
  "findings": [
    {
      "type": "breach",
      "source": "XposedOrNot",
      "value": "LinkedIn",
      "severity": "HIGH"
    }
  ],
  "created_at": "2024-04-03T10:22:00"
}
```

---

## 🔧 Installation Guide

### Prerequisites

- Python 3.10 or higher
- MySQL 8 running locally
- Redis running locally
- pip

### Step-by-Step Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/nexus-osint.git
cd nexus-osint
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-strong-random-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=osint_db
REDIS_URL=redis://localhost:6379/0
```

**5. Initialize the database**
```bash
python setup_db.py
```
This creates the `users` and `scans` tables and adds a default `admin` user.

**6. Start the FastAPI backend**
```bash
uvicorn backend.main:app --reload --port 8000
```

**7. Start the Celery worker** (new terminal)
```bash
celery -A backend.celery_worker.celery_app worker --loglevel=info
```

**8. Start the Streamlit frontend** (new terminal)
```bash
streamlit run frontend/app.py
```

The dashboard opens at `http://localhost:8501`.

---

## 🐳 Running with Docker

Docker Compose starts all four services (Redis, MySQL, API, Celery worker) with a single command. The Streamlit frontend still runs locally since it is a development UI.

```bash
docker-compose up --build
```

Services started:

| Service | Port | Description |
|---------|------|-------------|
| `mysql` | 3306 | Database |
| `redis` | 6379 | Task queue + cache + blacklist |
| `api` | 8000 | FastAPI backend |
| `worker` | — | Celery background worker |

To stop everything:
```bash
docker-compose down
```

> **Note:** When running the frontend locally against Docker, make sure `BASE_URL` in `frontend/api.py` is set to `http://localhost:8000`.

---

## 📁 Project File Structure

```
nexus-osint/
│
├── backend/
│   ├── main.py                  # FastAPI app, all route definitions, startup logic
│   ├── config.py                # All settings loaded from .env
│   ├── database.py              # MySQL connection, all DB queries
│   ├── celery_worker.py         # Background task: orchestrates all OSINT modules
│   ├── limiter.py               # SlowAPI rate limiter instance
│   ├── setup_db.py              # One-time DB init + admin user creation
│   │
│   ├── auth/
│   │   ├── routes.py            # /auth/register, login, logout, refresh endpoints
│   │   ├── jwt_handler.py       # Token creation and verification helpers
│   │   └── dependencies.py      # get_current_user() FastAPI dependency
│   │
│   └── osint/
│       ├── breach_osint.py      # Email → XposedOrNot breach check
│       ├── username_osint.py    # Username → Sherlock platform probe
│       └── image_metadata_osint.py  # Image → EXIF + GPS extraction
│
├── frontend/
│   ├── app.py                   # Login / Register page (entry point)
│   ├── new_scan.py              # Launch a scan + live polling + results
│   ├── dashbord.py              # History table + payload decryption
│   ├── image_tools.py           # EXIF forensics + map visualization
│   └── api.py                   # All HTTP calls to the backend (centralized)
│
├── docker-compose.yml           # Starts MySQL, Redis, API, Worker
├── Dockerfile                   # Container build instructions
├── requirements.txt             # All Python dependencies
├── .env                         # Your secrets (never commit this)
└── .env.example                 # Template for .env
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (unsafe default) | JWT signing key — change this in production |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | `root@123` | MySQL password |
| `DB_NAME` | `osint_db` | MySQL database name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `SHERLOCK_DATA_URL` | GitHub raw JSON | Sherlock platform list source |
| `SHERLOCK_SITE_LIMIT` | `500` | Max number of sites to probe per username scan |
| `ALLOWED_ORIGINS` | `localhost:3000,localhost:8501` | CORS allowed origins |
| `ENV` | `development` | Environment mode |

---

## ⚠️ Known Limitations

- **Sherlock false positives:** Some platforms return HTTP 200 for any username (even non-existent ones). The false-positive check (redirect-to-login detection) catches the most common cases but is not perfect.
- **XON rate limits:** The XposedOrNot free API has undocumented rate limits. Running many email scans back-to-back may trigger 429 responses. Add a delay between scans if automating.
- **Image metadata only (no AI analysis):** The image module reads raw EXIF tags. It does not perform facial recognition or object detection.
- **DNS only (no WHOIS):** The domain module only does a simple DNS lookup. Full WHOIS or SSL certificate inspection is not yet implemented.
- **Blacklist TTL mismatch:** The logout blacklist TTL in Redis is hardcoded at 1 hour, but access tokens expire in 30 minutes. The blacklist window is intentionally larger but the unused 30 minutes is technically wasted Redis storage.

---

## 🚀 Future Improvements

- **WHOIS & SSL Scan:** Enrich domain scans with registrar info and certificate details
- **Shodan Integration:** Look up open ports and exposed services for an IP address
- **Email Header Analyzer:** Paste raw email headers to trace the sending mail server
- **Export to PDF:** Download any scan result as a formatted intelligence report
- **Admin Panel:** View all scans across all users (admin-only role)
- **Webhook Notifications:** POST to a URL when a long-running scan completes
- **Password Strength Audit:** Cross-check breached passwords against a hashed dictionary
- **Streamlit → React frontend:** Replace the Streamlit UI with a proper React dashboard for production deployments

---

## 📄 License

This project is licensed under the MIT License.

> **Ethical Use Notice:** This tool is designed for personal digital footprint awareness, security research, and authorized OSINT investigations only. Do not use it to scan individuals without their knowledge and consent. The authors are not responsible for misuse.
