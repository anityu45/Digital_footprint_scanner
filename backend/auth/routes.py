import redis
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from backend.database import get_user, verify_password, create_user, delete_all_scans_by_owner
from backend.config import REDIS_URL

# Connect to Redis for the logout blacklist
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic Models for Input Validation ---
class AuthRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# --- Endpoints ---
@router.post("/register")
def register(body: AuthRequest):
    existing_user = get_user(body.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(body.username, body.password)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(body: AuthRequest):
    user = get_user(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_access_token(body.username),
        "refresh_token": create_refresh_token(body.username),
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh(body: RefreshRequest):
    username = verify_token(body.refresh_token, expected_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {
        "access_token": create_access_token(username),
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    # Verify the token is valid before doing anything
    username = verify_token(token, expected_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 1. Wipe all scan records belonging to this user from the database
    deleted_count = delete_all_scans_by_owner(username)

    # 2. Blacklist the token in Redis so it cannot be reused
    redis_client.setex(f"blacklist:{token}", 3600, "true")

    return {
        "message": "Logged out successfully. All session data has been erased.",
        "scans_deleted": deleted_count
    }