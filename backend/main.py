import os
import tempfile
import uuid
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.celery_worker import run_osint_scan
from backend.database import create_scan_entry, get_scan_result, init_db
from backend.osint.image_metadata_osint import collect_image_metadata
from backend.auth.routes import router as auth_router
from backend.auth.dependencies import get_current_user
from fastapi import Depends

app = FastAPI()
app.include_router(auth_router)
# Initialize DB
init_db()


class ScanRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    domain: Optional[str] = None


@app.post("/scan")
async def start_scan(request: ScanRequest, user=Depends(get_current_user)):
    # Auto-detect username from email local-part if not provided.
    if request.email and not request.username:
        request.username = request.email.split("@")[0]

    scan_id = str(uuid.uuid4())

    create_scan_entry(scan_id, request.email, request.username, request.domain)
    run_osint_scan(scan_id, request.email, request.username, request.domain)

    return {
        "scan_id": scan_id,
        "status": "Scan started",
        "auto_detected_username": request.username,
    }


@app.get("/results/{scan_id}")
async def get_results(scan_id: str, user=Depends(get_current_user)):
    result = get_scan_result(scan_id)
    if result:
        return result
    return {"status": "Processing", "risk_score": 0, "findings": []}


try:
    import multipart  # type: ignore # noqa: F401

    MULTIPART_AVAILABLE = True
except ImportError:
    MULTIPART_AVAILABLE = False


if MULTIPART_AVAILABLE:

    @app.post("/osint/image-metadata")
    async def scan_image_metadata(file: UploadFile = File(...)):
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file name provided")

        suffix = os.path.splitext(file.filename)[1] or ".img"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        try:
            result = collect_image_metadata(temp_path)
            if not result.get("success"):
                raise HTTPException(status_code=400, detail=result.get("error", "Metadata scan failed"))
            return result
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

else:

    @app.post("/osint/image-metadata")
    async def image_metadata(file: UploadFile, user=Depends(get_current_user)):
        raise HTTPException(
            status_code=503,
            detail="Image uploads require python-multipart. Install with: pip install python-multipart",
        )
