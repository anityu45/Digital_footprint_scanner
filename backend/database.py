import sqlite3
import json
from datetime import datetime

DB_NAME = "scans.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            status TEXT,
            email TEXT,
            username TEXT,
            domain TEXT,
            result JSON,
            risk_score INTEGER,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_scan(scan_id, email, username, domain):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scans (id, status, email, username, domain, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (scan_id, "PENDING", email, username, domain, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_scan_result(scan_id, result, risk_score):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE scans SET status=?, result=?, risk_score=? WHERE id=?",
              ("SUCCESS", json.dumps(result), risk_score, scan_id))
    conn.commit()
    conn.close()

def get_scan(scan_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE id=?", (scan_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None