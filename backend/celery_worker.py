from celery import Celery
from backend.database import update_scan_result
from backend.osint.email_osint import run_email_checks
from backend.osint.username_osint import check_username_list
from backend.osint.domain_osint import check_crt_sh

celery_app = Celery(
    "osint_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="run_osint_scan")
def run_osint_scan(scan_id, email, username, domain):
    findings = []
    risk_score = 0

    print(f"Starting scan for: {email}, {username}...")

    # --- 1. Email Analysis ---
    if email:
        email_results = run_email_checks(email)
        for res in email_results:
            findings.append(f"📧 {res['description']}")
            
            # SCORING: Accounts that involve money (Spotify/Adobe) are high risk
            if res['site'] in ["Spotify", "Adobe"]:
                risk_score += 25
            elif res['site'] == "Gravatar":
                risk_score += 10

    # --- 2. Username Analysis (Web Search) ---
    if username:
        search_results = check_username_list(username)
        if search_results:
            count = len(search_results)
            findings.append(f"🔎 Username '{username}' found on {count} public pages.")
            
            for res in search_results:
                findings.append(f"🔗 Found on {res['site']}: {res['url']}")
                
                # SCORING: Social Media is risky (Identity Linkage)
                site_lower = res['site'].lower()
                if any(x in site_lower for x in ["twitter", "instagram", "facebook", "linkedin", "github"]):
                    risk_score += 15
                else:
                    risk_score += 5

    # --- 3. Domain Analysis ---
    if domain:
        crt = check_crt_sh(domain)
        if crt['found']:
            risk_score += 15
            findings.append(f"🌐 {crt['description']}")

    # Cap Score at 100
    risk_score = min(risk_score, 100)

    update_scan_result(scan_id, findings, risk_score)
    return {"status": "done", "score": risk_score}