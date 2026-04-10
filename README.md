# Nexus OSINT — Digital Footprint Scanner 🌍

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

> An end-to-end Open Source Intelligence (OSINT) platform that scans an email address, username, or domain across global databases and returns a structured, risk-scored intelligence report — all behind a secure JWT-authenticated API and a clean Streamlit dashboard. Scan data is held only for the duration of the session and permanently deleted the moment the user logs out.

---

## 📖 Table of Contents

1. [What This Project Does](#-what-this-project-does)
2. [System Architecture](#-system-architecture)
3. [How Data Flows — Step by Step](#-how-data-flows--step-by-step)
4. [OSINT Scan Modules](#-osint-scan-modules)
   - [Email Breach Scan](#1-email-breach-scan)
   - [Username Scan](#2-username-scan)
   - [Domain DNS Scan](#3-domain-dns-scan)
   - [Image Metadata EXIF Scan](#4-image-metadata-exif-scan)
5. [Risk Scoring Engine](#-risk-scoring-engine)
6. [Security Elements](#-security-elements)
7. [Privacy by Design](#-privacy-by-design)
8. [Frontend Pages](#-frontend-pages)
9. [API Reference](#-api-reference)
10. [Installation Guide](#-installation-guide)
11. [Running with Docker](#-running-with-docker)
12. [Project File Structure](#-project-file-structure)
13. [Environment Variables](#-environment-variables)
14. [Known Limitations](#-known-limitations)
15. [Future Improvements](#-future-improvements)

---

## 🎯 What This Project Does

Nexus OSINT lets a registered user pick a target — an **email address**, a **username**, or a **domain name** — and then automatically:

1. Checks if the email appeared in any **known data breaches**
2. Discovers which **social media and public platforms** the username is registered on
3. Resolves the domain to an **IP address via DNS**
4. Extracts hidden **EXIF metadata and GPS coordinates** from uploaded images

Every scan runs in the **background** so the UI never freezes. Results are stored temporarily in MySQL during the session and returned with a **0–100 risk score**. All endpoints are protected by short-lived **JWT access tokens** with a Redis-backed blacklist system. When the user logs out, **all scan data is permanently deleted from the database automatically**.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER / CLIENT                        │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐    │
│   │   app.py    │  │ new_scan.py │  │   dashbord.py      │    │
│   │  (Login /   │  │  (Launch    │  │  (History, Risk,   │    │
│   │  Register)  │  │   a Scan)   │  │  Clear History)    │    │
│   └─────────────┘  └─────────────┘  └────────────────────┘    │
│          │                │                   │                 │
│          └────────────────┴───────────────────┘                 │
│                           │  api.py (all HTTP calls)            │
└───────────────────────────│─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND  (port 8000)                  │
│                                                                 │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│   │  /auth/*     │   │  /scans/*    │   │ /osint/image-    │  │
│   │  Register    │   │  Start,Get,  │   │  metadata        │  │
│   │  Login       │   │  List,Delete │   │  (synchronous)   │  │
│   │  Logout ─────│───► deletes ALL  │   │                  │  │
│   │  (auto-wipe) │   │  scans on    │   │                  │  │
│   │  Refresh     │   │  logout      │   │                  │  │
│   └──────────────┘   └──────────────┘   └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌──────────────┐   ┌──────────────────────────────────────────────┐
│  REDIS       │   │         CELERY WORKER (background)           │
│              │   │                                              │
│  JWT         │   │  breach_osint.py   → XposedOrNot API         │
│  blacklist   │   │  username_osint.py → Sherlock 500+ sites     │
│              │   │  DNS lookup        → socket.gethostbyname    │
│  Sherlock    │   │                                              │
│  site cache  │   │  calculate_risk(findings) → 0-100 score      │
│              │   │  update_scan_result() → writes to MySQL      │
│  Celery      │   │                                              │
│  broker      │   └──────────────────────────────────────────────┘
└──────────────┘                    │
                                    ▼
                     ┌──────────────────────────┐
                     │      MYSQL DATABASE      │
                     │                          │
                     │  users  (permanent)      │
                     │  scans  (session-only,   │
                     │          wiped on logout)│
                     └──────────────────────────┘
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
        │  Returns immediately: { "scan_id": "uuid", "status": "queued" }
        ▼
Frontend polls GET /scans/{scan_id} every 2 seconds

Meanwhile, in the Celery Worker:
        ├── email    → XposedOrNot API → breach list
        ├── username → Sherlock site list → 500 concurrent probes
        └── domain   → socket.gethostbyname → IP address
        │
        └── calculate_risk(findings) → 0-100 score
        └── UPDATE MySQL: status="Completed", findings=[...], risk_score=N

Frontend poll hits "Completed" → renders findings table + risk score
```

### Logout — Automatic Data Wipe

```
User logs out
        │
        │  POST /auth/logout
        │  Authorization: Bearer <access_token>
        ▼
FastAPI verifies token is valid and extracts username
        │
        ├── Step 1: delete_all_scans_by_owner(username)
        │       DELETE FROM scans WHERE owner = username
        │       Every scan this user ran is permanently deleted
        │
        └── Step 2: redis_client.setex("blacklist:<token>", 3600, "true")
                Token blacklisted — cannot be reused
        │
        Returns:
        {
          "message": "Logged out successfully. All session data has been erased.",
          "scans_deleted": 3
        }
        ▼
Frontend clears session_state.access_token → user returned to login page
Nothing remains in the database
```

### Manual History Clear — From Dashboard

```
User opens Dashboard
        │
        ▼
Clicks "Clear All History" button
        │
        ▼
Two-step confirmation shown
(prevents accidental deletion)
        │
        ▼
User confirms → api.py loops through all scan IDs
        │
        │  DELETE /scans/{scan_id}  for each scan
        │  (uses existing endpoint — no new backend route needed)
        ▼
All scan records deleted from MySQL
Dashboard refreshes → shows empty state
```

### Image Metadata — No Queue, Synchronous

```
User uploads image in image_tools.py
        │
        │  POST /osint/image-metadata  (multipart/form-data)
        ▼
FastAPI writes bytes to a temp file on disk
        │
        ▼
collect_image_metadata(temp_path) called
        ├── Pillow reads all EXIF tags
        ├── Extracts GPS IFD separately
        └── Converts DMS coords to Decimal Degrees
            builds Google Maps URL (no API key needed)
        │
        ▼
Temp file deleted from disk immediately
        │
        ▼
Returns: { metadata: {...}, location: { lat, lon, google_maps } }
Frontend shows map pin + Maps link + raw metadata JSON
```

---

## 🔍 OSINT Scan Modules

### 1. Email Breach Scan

**File:** `breach_osint.py`

**What it does:** Queries the XposedOrNot API to check if an email appeared in any publicly known data breach. Security researchers monitor dark web forums and hacker communities where stolen credential dumps are posted. They collect those dumps, strip the passwords, and record only the email address and the breach name. Your tool queries this database — it never accesses raw breach data or passwords.

**Input:**
```
email: str  →  e.g. "someone@gmail.com"
```

**Output:**
```json
[
  { "name": "LinkedIn",  "severity": "HIGH", "source": "XposedOrNot" },
  { "name": "Adobe",     "severity": "HIGH", "source": "XposedOrNot" }
]
```

**Response handling:**

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Breaches found | Parse and return list |
| 404 | Clean email — no breaches | Return empty list |
| 429 | Rate limited | Log warning, return empty list |
| 5xx | API error | Log error, return empty list |

Timeout: 15 seconds.

---

### 2. Username Scan

**File:** `username_osint.py`

**What it does:** Uses the Sherlock project's database of 500+ platforms. For each platform it builds the profile URL with the username inserted, fires all requests simultaneously using async Python, and checks whether the profile exists.

**Input:**
```
username: str  →  e.g. "johndoe"
```

**Detection methods:**

| Type | Logic |
|------|-------|
| `status_code` | HTTP 200 = profile exists, 404 = does not |
| `message` | Site always returns 200 — checks if error text is absent from the page |
| Redirect guard | Redirected to login page = false positive, skip |

**Sherlock site list cached in Redis for 24 hours** — downloaded from GitHub once per day, loaded instantly for every scan after.

**Fallback:** If GitHub fetch fails, 10 hardcoded popular platforms are used so the scan never completely fails.

**Output:**
```json
[
  { "site": "GitHub",  "url": "https://github.com/johndoe" },
  { "site": "Reddit",  "url": "https://www.reddit.com/user/johndoe/" },
  { "site": "TikTok",  "url": "https://www.tiktok.com/@johndoe" }
]
```

---

### 3. Domain DNS Scan

**File:** `celery_worker.py` (inline)

**What it does:** Resolves a domain name to its IP address using Python's built in `socket` library. No external API, no API key, no rate limiting.

**Input:**
```
domain: str  →  e.g. "example.com"
```

**Output — resolved:**
```json
{ "type": "domain", "source": "DNS", "value": "Resolved IP: 93.184.216.34", "severity": "INFO" }
```

**Output — unresolvable:**
```json
{ "type": "domain", "source": "DNS", "value": "Domain could not be resolved.", "severity": "LOW" }
```

---

### 4. Image Metadata EXIF Scan

**File:** `image_metadata_osint.py`

**What it does:** Every photo taken on a phone or camera contains a hidden layer of data embedded inside the image file called EXIF. It includes device info, software, timestamps, and often GPS coordinates — invisible to the eye but fully readable by Pillow.

**Input:**
```
file_path: str  →  path to temp file saved by FastAPI
```

**GPS conversion formula:**
```
Raw in image:  (10°, 0', 54.0")  ref: N
Formula:       10 + (0 / 60) + (54.0 / 3600) = 10.015000
South or West: multiply result by -1
```

**Google Maps URL — no API key needed:**
```python
f"https://www.google.com/maps?q={lat},{lon}"
# Google Maps accepts coordinates directly in URL as a public feature
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

The image file is deleted from disk immediately after Pillow reads it. It is never written to MySQL or Redis.

---

## 📊 Risk Scoring Engine

**File:** `celery_worker.py` → `calculate_risk(findings)`

| Finding Type | Severity | Points Added |
|---|---|---|
| `breach` | CRITICAL | +25 |
| `breach` | HIGH / other | +15 |
| `username` | any | +5 per platform found |
| `domain` | any | +10 |

Capped at 100. Clean target with no findings returns 0.

---

## 🔐 Security Elements

### Full Authentication Flow

```
Register  →  password hashed with bcrypt  →  stored in MySQL

Login     →  bcrypt verify  →  issue:
               Access Token  (JWT, expires in 30 minutes)
               Refresh Token (JWT, expires in 7 days)

Every protected API call — 5 checks in order:
    1. Authorization header present and starts with "Bearer "?
    2. Token in Redis blacklist?           → if yes: 401 immediately
    3. JWT signature valid?                → if no:  401
    4. Token type == "access"?             → if no:  401
    5. Username ("sub") present in payload?→ if no:  401
    All pass → extract username → proceed

Logout    →  Step 1: permanently delete ALL scans owned by this user
             Step 2: add token to Redis blacklist with 1 hour TTL
             Token is dead immediately — not after 30 minutes

Refresh   →  client sends refresh_token
          →  server verifies type == "refresh"
          →  issues a brand new access token
```

### JWT Token Contents

```json
{
  "sub": "username",
  "type": "access",
  "exp": 1712345678
}
```

### Rate Limiting

Image metadata endpoint is limited to **15 requests per minute per IP**. Exceeding this returns HTTP 429. Enforced by SlowAPI.

### Scan Ownership Enforcement

Every scan row stores the `owner` field. Every query filters by owner — a user can never access another user's data:

```sql
SELECT * FROM scans WHERE owner = %s
DELETE FROM scans WHERE scan_id = %s AND owner = %s
```

### Stale Scan Cleanup

On startup and every 5 minutes a background task runs. Any scan stuck in `"Running"` for more than 15 minutes is marked `"Failed"` automatically. The `created_at` timestamp (set by MySQL automatically on insert) is used for this check:

```sql
WHERE status = 'Running'
AND created_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE)
```

### Input Validation

`ScanRequest` Pydantic model enforces exactly **one** of `email`, `username`, or `domain` is provided and non-empty. Two fields, zero fields, or empty strings all return HTTP 422 before any scan logic runs.

---

## 🛡️ Privacy by Design

The core privacy principle — **scan data exists only as long as it is needed.**

### Why Scans Are Stored At All

Celery runs in a separate process from FastAPI. The only way for the background worker to communicate results back to the frontend is through the shared MySQL database. The frontend polls `GET /scans/{scan_id}` every 2 seconds — that query reads from MySQL. Without this, there is no way to return results from a background process to the user.

The database is a temporary working space, not a permanent data store.

### When Scans Are Deleted

| Trigger | What Happens | How |
|---|---|---|
| User logs out | All scans deleted automatically | `DELETE FROM scans WHERE owner = username` in logout endpoint |
| User clicks Clear All History | All scans deleted manually | `clear_all_scans()` loops through each scan ID and calls DELETE |
| User deletes one scan | Single scan deleted | `DELETE FROM scans WHERE scan_id = ? AND owner = ?` |

### Logout Response Confirms Deletion

```json
{
  "message": "Logged out successfully. All session data has been erased.",
  "scans_deleted": 3
}
```

The response tells the frontend exactly how many records were wiped — no ambiguity.

### Images Are Never Stored

Uploaded images never touch MySQL or Redis. FastAPI writes to a temp file, Pillow reads it, temp file is deleted — all within a single request. Nothing persists after the response is returned.

---

## 🖥️ Frontend Pages

### `app.py` — Login and Registration

Entry point of the platform. Two tabs — Authentication and New Operative Registration. On login the JWT access token is saved in `st.session_state.access_token`. Every other page checks for this at the top and stops with an unauthorized warning if missing.

### `new_scan.py` — Launch a Scan

Radio button to choose target type (Email / Username / Domain). Text input for the value. On submit calls `POST /scans`, receives a `scan_id`, then polls `GET /scans/{scan_id}` every 2 seconds with a live progress bar. When complete shows risk score, total findings count, and a full findings table with clickable URLs.

### `dashbord.py` — Operations History

Shows all scans belonging to the logged in user. Three summary metrics at the top — total operations, successful traces, average risk score.

**Clear All History** — sits next to the Trace History heading. First click shows a two-step confirmation warning. Confirming permanently deletes every scan record from MySQL and refreshes the page immediately.

**Decrypt Specific Payload** — select any scan ID from a dropdown to fetch and display its full findings.

### `image_tools.py` — EXIF Forensics

File uploader for JPEG and PNG. Shows image preview. On analysis renders an interactive OpenStreetMap pin if GPS coordinates are found, a clickable Google Maps link, and all raw EXIF metadata in a collapsible JSON viewer.

### `api.py` — Centralized API Layer

Every HTTP call from every frontend page goes through this one file. No page makes direct HTTP calls itself.

| Function | Endpoint Called | Purpose |
|---|---|---|
| `login()` | POST /auth/login | Get access and refresh tokens |
| `register()` | POST /auth/register | Create a new account |
| `get_scans()` | GET /scans | List all scans for current user |
| `start_scan()` | POST /scans | Queue a new background scan |
| `get_scan_result()` | GET /scans/{id} | Fetch result of one scan |
| `delete_scan()` | DELETE /scans/{id} | Delete a single scan |
| `clear_all_scans()` | DELETE /scans/{id} × N | Loop and delete all scans |
| `analyze_image()` | POST /osint/image-metadata | Extract EXIF from image |

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### Authentication

| Method | Endpoint | Body | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/auth/register` | `{username, password}` | No | Create account |
| POST | `/auth/login` | `{username, password}` | No | Get tokens |
| POST | `/auth/refresh` | `{refresh_token}` | No | New access token |
| POST | `/auth/logout` | — | Yes | Blacklist token + delete all scans |

### Scans

| Method | Endpoint | Body / Query | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/scans` | `{email OR username OR domain}` | Yes | Start background scan |
| GET | `/scans` | `?limit=10&offset=0` | Yes | List your scans |
| GET | `/scans/{scan_id}` | — | Yes | Get full scan result |
| DELETE | `/scans/{scan_id}` | — | Yes | Delete one scan |

### OSINT

| Method | Endpoint | Body | Auth Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/osint/image-metadata` | `multipart: file` | Yes | Extract EXIF metadata |
| GET | `/health` | — | No | API health check |

### Logout Response
```json
HTTP 200 OK
{
  "message": "Logged out successfully. All session data has been erased.",
  "scans_deleted": 3
}
```

### Scan Result Response
```json
HTTP 200 OK
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
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

### Step-by-Step

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/nexus-osint.git
cd nexus-osint
```

**2. Create virtual environment**
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
```bash
cp .env.example .env
```

Minimum required values in `.env`:
```
SECRET_KEY=your-strong-random-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=osint_db
REDIS_URL=redis://localhost:6379/0
```

**5. Initialize the database**
```bash
python setup_db.py
```

Creates the `users` and `scans` tables and adds a default admin user.

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

Opens at `http://localhost:8501`

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

| Service | Port | Description |
|---------|------|-------------|
| `mysql` | 3306 | Database |
| `redis` | 6379 | Task queue + cache + blacklist |
| `api` | 8000 | FastAPI backend |
| `worker` | — | Celery background worker |

```bash
docker-compose down
```

> When running the Streamlit frontend locally against a Docker backend, ensure `BASE_URL` in `frontend/api.py` is set to `http://localhost:8000`.

---

## 📁 Project File Structure

```
nexus-osint/
│
├── backend/
│   ├── main.py                      # FastAPI app, all route definitions, startup logic
│   ├── config.py                    # All settings loaded from .env
│   ├── database.py                  # MySQL connection, all DB queries
│   │                                  + delete_all_scans_by_owner() for logout wipe
│   ├── celery_worker.py             # Background task, runs all OSINT modules
│   ├── limiter.py                   # SlowAPI rate limiter instance
│   ├── setup_db.py                  # One-time DB init + default admin user
│   │
│   ├── auth/
│   │   ├── routes.py                # /auth/* endpoints
│   │   │                              logout auto-deletes all user scans
│   │   ├── jwt_handler.py           # Token creation and verification helpers
│   │   └── dependencies.py          # get_current_user() FastAPI dependency
│   │
│   └── osint/
│       ├── breach_osint.py          # Email → XposedOrNot API
│       ├── username_osint.py        # Username → Sherlock 500+ platform probe
│       └── image_metadata_osint.py  # Image → Pillow EXIF + GPS extraction
│
├── frontend/
│   ├── app.py                       # Login / Register entry point
│   ├── new_scan.py                  # Launch scan + live polling + results display
│   ├── dashbord.py                  # History table + Clear All History button
│   ├── image_tools.py               # EXIF forensics + map + metadata viewer
│   └── api.py                       # All HTTP calls centralized
│                                      + delete_scan() and clear_all_scans()
│
├── docker-compose.yml               # Starts all 4 services
├── Dockerfile                       # Container build
├── requirements.txt                 # All Python dependencies
├── .env                             # Your secrets (never commit this)
└── .env.example                     # Template for .env
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (unsafe default) | JWT signing key — always change in production |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `osint_db` | MySQL database name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `SHERLOCK_DATA_URL` | GitHub raw JSON | Sherlock platform list source |
| `SHERLOCK_SITE_LIMIT` | `500` | Max platforms to probe per username scan |
| `ALLOWED_ORIGINS` | `localhost:3000,localhost:8501` | CORS allowed origins |
| `ENV` | `development` | Environment mode |

---

## ⚠️ Known Limitations

- **Plain text during session** — scan findings are stored as readable JSON in MySQL while the session is active. Encryption at rest is the logical next hardening step.
- **Sherlock false positives** — some platforms return HTTP 200 for any username. The login-redirect detection handles most cases but is not perfect.
- **XON rate limits** — the XposedOrNot free API has undocumented rate limits. Many rapid email scans may trigger 429 responses.
- **DNS only for domains** — the domain module only resolves IP addresses. WHOIS, port scanning, and Shodan integration are planned next.
- **No HTTPS enforcement** — all security layers are undermined without TLS in production. The API runs plain HTTP by default.
- **SECRET_KEY unsafe default** — always set a strong key in `.env` before any real use.
- **Blacklist TTL mismatch** — logout blacklist TTL is 1 hour but tokens expire in 30 minutes. The extra 30 minutes is harmless but wasted Redis storage.
- **Clear All History uses N requests** — the manual clear loops through each scan ID individually rather than a single bulk delete call. For users with many scans this could be slow. A dedicated `DELETE /scans` bulk endpoint would fix this.

---

## 🚀 Future Improvements

- **Encryption at rest** — encrypt the findings column in MySQL so scan data is unreadable even during an active session
- **Bulk delete endpoint** — single `DELETE /scans` API call to replace the current loop in `clear_all_scans()`
- **Auto-expiry** — automatically delete scans after a configurable time window even without logout
- **WHOIS lookup** — registrar info, owner details, registration and expiry dates for domain scans
- **Shodan integration** — open ports, running services, known CVE vulnerabilities for any resolved IP address
- **PDF export** — download any completed scan as a formatted intelligence report
- **Email header analyzer** — paste raw email headers to trace the originating mail server
- **Admin panel** — platform-wide scan count statistics for administrators
- **Webhook notifications** — POST to a configured URL when a long-running scan completes
- **React frontend** — replace Streamlit with a full React dashboard for production deployments

---

## 📄 License

This project is licensed under the MIT License.

> **Ethical Use Notice:** This tool is designed for personal digital footprint awareness, security research, and authorized OSINT investigations only. Do not use it to scan individuals without their knowledge and consent. All sources used are publicly available — breach notification APIs and public platform profile pages. The authors are not responsible for misuse.
