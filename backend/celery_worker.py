import asyncio
import socket
import sys
import logging
from celery import Celery
from backend.config import REDIS_URL
from backend.database import update_scan_result
from backend.osint.breach_osint import check_data_breaches
from backend.osint.username_osint import check_username_with_sherlock

logger = logging.getLogger("celery_worker")

celery_app = Celery("osint_worker", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# FIXED: Changed from Selector to Proactor to prevent httpx from dropping SSL connections on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def calculate_risk(findings: list) -> int:
    """Calculates a dynamic risk score 0-100 based on findings."""
    if not findings:
        return 0
    score = 0
    for f in findings:
        if f.get("type") == "breach":
            score += 25 if f.get("severity") == "CRITICAL" else 15
        elif f.get("type") == "username":
            score += 5
        # Add a small base score for domain info
        elif f.get("type") == "domain":
            score += 10
    return min(score, 100)

@celery_app.task(name="run_osint_scan", bind=True, max_retries=2)
def run_osint_scan(self, scan_id: str, email: str, username: str, domain: str):
    """
    The main worker task. It uses asyncio.run to execute the 
    asynchronous OSINT modules.
    """
    logger.info(f"Worker STARTING scan: {scan_id} for {email or username or domain}")
    
    try:
        # Define an internal async function to run the tools
        async def execute_scans():
            findings = []
            
            # 1. Check Email Breaches
            if email:
                breaches = await check_data_breaches(email)
                for b in breaches:
                    findings.append({
                        "type": "breach", 
                        "source": "XposedOrNot",
                        "value": b.get("name"), 
                        "severity": b.get("severity"),
                    })
            
            # 2. Check Usernames (Sherlock)
            if username:
                sites = await check_username_with_sherlock(username)
                for s in sites:
                    findings.append({
                        "type": "username", 
                        "source": "Sherlock",
                        "value": s.get("site"), 
                        "url": s.get("url"),
                        "severity": "INFO"  # FIXED: Added severity so the UI doesn't crash!
                    })

            # 3. Check Domains (DNS Lookup)
            if domain:
                try:
                    ip_address = socket.gethostbyname(domain)
                    findings.append({
                        "type": "domain",
                        "source": "DNS",
                        "value": f"Resolved IP: {ip_address}",
                        "severity": "INFO"
                    })
                except socket.gaierror:
                    findings.append({
                        "type": "domain",
                        "source": "DNS",
                        "value": f"Domain could not be resolved.",
                        "severity": "LOW"
                    })

            
            return findings

        # Run the async loop and get results
        findings = asyncio.run(execute_scans())
        logger.info(f"Scan {scan_id} finished. Findings: {len(findings)}")
        
        # 3. Update the Database with findings and risk score
        update_scan_result(scan_id, findings, calculate_risk(findings))
        
    except Exception as exc:
        logger.error(f"Scan {scan_id} failed: {exc}")
        if self.request.retries < self.max_retries:
            # If API or network fails, retry after 30 seconds
            self.retry(exc=exc, countdown=30)
        else:
            # If retries exhausted, update DB so frontend doesn't hang
            error_finding = [{
                "type": "error",
                "source": "System",
                "value": f"Scan failed due to internal error: {str(exc)}",
                "severity": "HIGH"
            }]
            try:
                update_scan_result(scan_id, error_finding, 0, status="Failed")
            except Exception as db_error:
                logger.critical(f"CRITICAL: Could not update DB for failed scan {scan_id}: {db_error}")