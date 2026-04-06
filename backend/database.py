import pymysql
import json
import logging
from contextlib import contextmanager
from typing import Optional
from passlib.context import CryptContext
from backend.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger("osint_api")

DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "cursorclass": pymysql.cursors.DictCursor,
}

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Helper Utilities ---

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)

@contextmanager
def get_db_cursor():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise e
    finally:
        conn.close()

def init_db():
    with get_db_cursor() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                scan_id VARCHAR(255) PRIMARY KEY,
                owner VARCHAR(255) NOT NULL,
                email VARCHAR(255) NULL,
                username VARCHAR(255) NULL,
                domain VARCHAR(255) NULL,
                status VARCHAR(50),
                findings JSON,
                risk_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner) REFERENCES users(username) ON DELETE CASCADE
            )
        """)

# --- Authentication Logic ---

def get_user(username: str) -> dict:
    with get_db_cursor() as c:
        c.execute("SELECT * FROM users WHERE username = %s", (username,))
        return c.fetchone()

def create_user(username: str, password: str) -> None:
    hashed = hash_password(password)
    with get_db_cursor() as c:
        c.execute(
            "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
            (username, hashed),
        )

# --- Scan Logic ---

def create_scan_entry(scan_id: str, owner: str, email: Optional[str] = None, username: Optional[str] = None, domain: Optional[str] = None) -> None:
    with get_db_cursor() as c:
        c.execute(
            """
            INSERT INTO scans 
                (scan_id, owner, email, username, domain, status, findings, risk_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (scan_id, owner, email, username, domain, "Running", json.dumps([]), 0),
        )

def update_scan_result(scan_id: str, findings: list, risk_score: int, status: str = "Completed") -> None:
    with get_db_cursor() as c:
        c.execute(
            """
            UPDATE scans
            SET status = %s, findings = %s, risk_score = %s
            WHERE scan_id = %s
            """,
            (status, json.dumps(findings), risk_score, scan_id),
        )

def get_scan_result(scan_id: str) -> dict:
    with get_db_cursor() as c:
        c.execute("SELECT * FROM scans WHERE scan_id = %s", (scan_id,))
        row = c.fetchone()
        if row and isinstance(row.get("findings"), str):
            row["findings"] = json.loads(row["findings"])
        return row

def get_scans_by_owner(owner: str, limit: int = 20, offset: int = 0) -> list:
    with get_db_cursor() as c:
        c.execute(
            """
            SELECT scan_id, email, username, domain, status, risk_score, created_at
            FROM scans WHERE owner = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (owner, limit, offset),
        )
        return c.fetchall()

def delete_scan(scan_id: str, owner: str) -> bool:
    """Deletes a single scan if the requesting user is the owner."""
    with get_db_cursor() as c:
        c.execute(
            "DELETE FROM scans WHERE scan_id = %s AND owner = %s",
            (scan_id, owner),
        )
        return c.rowcount > 0

def delete_all_scans_by_owner(owner: str) -> int:
    """
    Deletes ALL scans belonging to a user.
    Called automatically on logout — no scan data remains in the
    database after the user ends their session.
    Returns the number of rows deleted.
    """
    with get_db_cursor() as c:
        c.execute(
            "DELETE FROM scans WHERE owner = %s",
            (owner,),
        )
        return c.rowcount

def mark_stale_scans_failed(minutes: int = 15) -> int:
    with get_db_cursor() as c:
        c.execute(
            """
            UPDATE scans
            SET status = 'Failed', findings = %s, risk_score = 0
            WHERE status = 'Running' AND created_at < DATE_SUB(NOW(), INTERVAL %s MINUTE)
            """,
            (json.dumps([{"type": "error", "source": "System", "value": "Scan timed out or worker crashed.", "severity": "HIGH"}]), minutes)
        )
        return c.rowcount