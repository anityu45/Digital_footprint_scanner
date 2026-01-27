import sqlite3
import json

DB_NAME = "footprint.db"

def init_db():
    """Initializes the SQLite database with the scans table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            email TEXT,
            username TEXT,
            domain TEXT,
            status TEXT,
            findings TEXT,
            risk_score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def create_scan_entry(scan_id, email, username, domain):
    """Creates a new scan entry in the database with status 'Running'."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO scans (scan_id, email, username, domain, status, findings, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (scan_id, email, username, domain, "Running", "[]", 0))
    conn.commit()
    conn.close()

def update_scan_result(scan_id, findings, risk_score):
    """Updates the scan result when the worker finishes."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Serialize the list of findings into a JSON string
    findings_json = json.dumps(findings)
    
    c.execute('''
        UPDATE scans 
        SET status = ?, findings = ?, risk_score = ?
        WHERE scan_id = ?
    ''', ("Completed", findings_json, risk_score, scan_id))
    conn.commit()
    conn.close()

def get_scan_result(scan_id):
    """Retrieves the scan result for the frontend."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT status, findings, risk_score FROM scans WHERE scan_id = ?', (scan_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        status, findings_str, risk_score = row
        # Deserialize JSON string back to list
        try:
            findings = json.loads(findings_str)
        except:
            findings = []
            
        return {
            "status": status,
            "findings": findings,
            "risk_score": risk_score
        }
    return None