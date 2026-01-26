from celery import Celery
from backend.database import update_scan_result
# We now import the new aggregator function for email
from backend.osint.email_osint import run_email_checks
from backend.osint.username_osint import check_github, check_whatsmyname
from backend.osint.domain_osint import check_crt_sh

# Configure Celery to use Redis
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

    # --- 1. Email Checks (Upgraded "Holehe" Logic) ---
    if email:
        # This returns a list of results (Gravatar, Spotify, Adobe, etc.)
        email_results = run_email_checks(email)
        
        for res in email_results:
            # Add the finding text
            findings.append(res['description'])
            
            # Apply Scoring based on the source
            if res['site'] == "Gravatar":
                risk_score += 10
            elif res['site'] in ["Spotify", "Adobe", "WordPress"]:
                # Active accounts on major platforms indicate a higher digital footprint
                risk_score += 20

    # --- 2. Username Checks ---
    if username:
        # GitHub Check
        gh = check_github(username)
        if gh['found']:
            risk_score += 10
            findings.append(gh['description'])
        
        # WhatsMyName (Social Media) Check
        wmn = check_whatsmyname(username)
        if wmn['found']:
            risk_score += 20
            findings.append(wmn['description'])

    # --- 3. Domain Checks ---
    if domain:
        crt = check_crt_sh(domain)
        if crt['found']:
            risk_score += 15
            findings.append(crt['description'])

    # Cap score at 100 (Normalization)
    risk_score = min(risk_score, 100)

    # Save final results to the SQLite database
    update_scan_result(scan_id, findings, risk_score)
    
    print(f"Scan {scan_id} complete. Score: {risk_score}")
    return {"status": "done", "score": risk_score}