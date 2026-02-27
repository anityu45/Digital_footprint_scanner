import json
from celery import Celery

from backend.database import update_scan_result
from backend.osint.breach_osint import check_data_breaches
from backend.osint.username_osint import check_username_list


celery_app = Celery(
    "osint_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


@celery_app.task(name="run_osint_scan")
def run_osint_scan(scan_id, email, username, domain):
    findings = []
    risk_score = 0
    graph_nodes = []

    if email:
        breaches = check_data_breaches(email)
        if breaches:
            findings.append(f"SECURITY ALERT: Email found in {len(breaches)} data breaches")
            risk_score += 40
            for breach in breaches:
                findings.append(f"Breach: {breach['name']} ({breach['severity']})")
                graph_nodes.append(("Email", f"Breach: {breach['name']}"))

    if username:
        sherlock_results = check_username_list(username)
        if sherlock_results:
            findings.append(f"Sherlock identified {len(sherlock_results)} profiles")
            for res in sherlock_results:
                findings.append(f"{res['site']}: {res['url']}")
                graph_nodes.append(("Username", res["site"]))
                if res["site"] in ["Instagram", "Twitter", "Facebook", "Tinder"]:
                    risk_score += 10
                else:
                    risk_score += 2

    risk_score = min(risk_score, 100)
    findings.append(f"GRAPH_DATA:{json.dumps(graph_nodes)}")

    update_scan_result(scan_id, findings, risk_score)
    return {"status": "done", "score": risk_score}
