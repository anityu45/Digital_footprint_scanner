import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from backend.database import init_db, save_scan, get_scan
from backend.celery_worker import run_osint_scan

app = FastAPI()

# Initialize DB on startup
init_db()

class ScanRequest(BaseModel):
    email: str
    username: str
    domain: str = ""

@app.post("/scan")
def start_scan(request: ScanRequest):
    scan_id = str(uuid.uuid4())
    
    # Save initial state to DB
    save_scan(scan_id, request.email, request.username, request.domain)
    
    # Trigger Celery Task
    # We use .delay() to send it to Redis
    run_osint_scan.delay(scan_id, request.email, request.username, request.domain)
    
    return {"scan_id": scan_id, "status": "PENDING"}

@app.get("/scan/{scan_id}")
def get_scan_status(scan_id: str):
    data = get_scan(scan_id)
    if not data:
        return {"error": "Scan not found"}
    return data