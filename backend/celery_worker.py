from celery import Celery
from backend.database import update_scan_result
from backend.osint.username_osint import check_username_list
from backend.osint.breach_osint import check_data_breaches
from backend.osint.domain_osint import check_crt_sh
from backend.osint.email_osint import run_email_checks # Keep your existing email checker

celery_app = Celery(
    "osint_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="run_osint_scan")
def run_osint_scan(scan_id, email, username, domain):
    findings = []
    risk_score = 0
    graph_nodes = [] # Data for the Visual Graph

    print(f"🚀 Starting Advanced Scan for: {email} / {username}")

    # --- 1. BREACH CHECK (The Scary Part) ---
    if email:
        breaches = check_data_breaches(email)
        if breaches:
            findings.append(f"⚠️ **SECURITY ALERT:** Email found in {len(breaches)} Data Breaches!")
            risk_score += 40 # Huge risk
            for b in breaches:
                findings.append(f"❌ Breach: {b['name']} ({b['severity']})")
                graph_nodes.append(("Email", f"Breach: {b['name']}"))

    # --- 2. USERNAME CHECK (Sherlock Engine) ---
    if username:
        # This now runs the REAL Sherlock tool
        sherlock_results = check_username_list(username)
        
        if sherlock_results:
            findings.append(f"🔎 Sherlock identified {len(sherlock_results)} profiles:")
            
            for res in sherlock_results:
                findings.append(f"🔗 {res['site']}: {res['url']}")
                graph_nodes.append(("Username", res['site'])) # Add to graph
                
                # Dynamic Scoring
                if res['site'] in ["Instagram", "Twitter", "Facebook", "Tinder"]:
                    risk_score += 10
                else:
                    risk_score += 2

    # --- 3. DOMAIN CHECK ---
    if domain:
        crt = check_crt_sh(domain)
        if crt['found']:
            risk_score += 15
            findings.append(f"🌐 {crt['description']}")
            graph_nodes.append(("Domain", "Subdomains Found"))

    # Cap Score
    risk_score = min(risk_score, 100)
    
    # Save everything (including graph data)
    # We append the graph data as a special finding at the end to parse it later, 
    # or you could add a new column in DB. For MVP, we stick to findings list.
    import json
    # Storing graph data as a JSON string in the last finding for the frontend to pick up
    findings.append(f"GRAPH_DATA:{json.dumps(graph_nodes)}")

    update_scan_result(scan_id, findings, risk_score)
    return {"status": "done", "score": risk_score}