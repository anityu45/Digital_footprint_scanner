from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
from backend.celery_worker import run_osint_scan
from backend.database import init_db, create_scan_entry, get_scan_result

app = FastAPI()

# Initialize DB
init_db()

class ScanRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    domain: Optional[str] = None

@app.post("/scan")
def start_scan(request: ScanRequest):
    # --- AUTO-GUESS LOGIC ---
    # If user gives email "john.doe@gmail.com" but NO username,
    # we automatically scan for username "john.doe"
    if request.email and not request.username:
        derived_username = request.email.split("@")[0]
        request.username = derived_username
        print(f"🔹 Auto-detected username from email: {derived_username}")

    scan_id = str(uuid.uuid4())
    
    # Save to DB
    create_scan_entry(scan_id, request.email, request.username, request.domain)
    
    # Start Background Task
    run_osint_scan.delay(scan_id, request.email, request.username, request.domain)
    
    return {"scan_id": scan_id, "status": "Scan started", "auto_detected_username": request.username}

@app.get("/results/{scan_id}")
def get_results(scan_id: str):
    result = get_scan_result(scan_id)
    if result:
        return result
    return {"status": "Processing", "risk_score": 0, "findings": []}