from celery import Celery
from backend.database import update_scan_result
from backend.osint.email_osint import check_gravatar, check_hibp
from backend.osint.username_osint import check_github, check_whatsmyname
from backend.osint.domain_osint import check_crt_sh

# Configure Celery
celery_app = Celery(
    "osint_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="run_osint_scan")
def run_osint_scan(scan_id, email, username, domain):
    findings = []
    risk_score = 0

    print(f"Starting scan for: {email}, {username}, {domain}")

    # 1. Email Checks
    if email:
        grav = check_gravatar(email)
        if grav['found']:
            risk_score += 10
            findings.append(grav['description'])
        
        hibp = check_hibp(email)
        if hibp['found']:
            risk_score += 30
            findings.append(hibp['description'])

    # 2. Username Checks
    if username:
        gh = check_github(username)
        if gh['found']:
            risk_score += 10
            findings.append(gh['description'])
        
        wmn = check_whatsmyname(username)
        if wmn['found']:
            risk_score += 20
            findings.append(wmn['description'])

    # 3. Domain Checks
    if domain:
        crt = check_crt_sh(domain)
        if crt['found']:
            risk_score += 15
            findings.append(crt['description'])

    # Cap score at 100
    risk_score = min(risk_score, 100)

    # Save to DB
    update_scan_result(scan_id, findings, risk_score)
    print(f"Scan {scan_id} complete. Score: {risk_score}")
    
    return {"status": "done", "score": risk_score}