#Digital Footprint Intelligence (OSINT Tool)

A full-stack Open Source Intelligence (OSINT) tool that helps you visualize your digital footprint. It scans emails, usernames, and domains to find public profiles, data breaches, and security risks, presenting everything in a professional Identity Graph.

## ✨ Features
* **🔍 Dual Scan Modes:**
    * **⚡ Quick Scan (15s):** Checks top 25 sites (Instagram, GitHub, Twitter, etc.).
    * **🕵️ Deep Scan (3-5m):** Uses the **Sherlock** engine to scan 400+ websites.
* **🔓 Breach Detection:** Checks if your email appeared in known data leaks (e.g., Collection #1).
* **🕸️ Identity Graph:** Visualizes connections between your email, username, and accounts using **Graphviz**.
* **📊 Risk Scoring:** Calculates a security risk score (0-100) based on your exposure.
* **📜 Detailed Reporting:** Provides direct links to found profiles and breach details.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **Backend:** FastAPI
* **Task Queue:** Celery + Redis
* **Engines:** Sherlock (Username search), NetworkX (Graphing)

---

## 🚀 Installation

### 1. Prerequisites
You need **Python 3.9+** and **Redis** installed.
* **Redis (Windows):** [Download here](https://github.com/microsoftarchive/redis/releases) or use Docker.
* **Graphviz (Required for Graphing):**
    * Download from [graphviz.org](https://graphviz.org/download/).
    * **Important:** During install, select **"Add Graphviz to the system PATH for all users"**.

### 2. Clone & Install Dependencies
```bash
git clone [https://github.com/yourusername/digital-footprint.git](https://github.com/yourusername/digital-footprint.git)
cd digital-footprint

# Install Python libraries
pip install fastapi uvicorn celery redis streamlit sherlock-project networkx graphviz requests
