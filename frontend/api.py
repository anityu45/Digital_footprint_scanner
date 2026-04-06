import requests
import streamlit as st

BASE_URL = "http://localhost:8000"

def get_headers():
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def login(username, password):
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    return resp

def register(username, password):
    resp = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    return resp

def get_scans():
    resp = requests.get(f"{BASE_URL}/scans", headers=get_headers())
    return resp.json().get("scans", []) if resp.status_code == 200 else []

def start_scan(payload):
    resp = requests.post(f"{BASE_URL}/scans", json=payload, headers=get_headers())
    return resp

def get_scan_result(scan_id):
    resp = requests.get(f"{BASE_URL}/scans/{scan_id}", headers=get_headers())
    return resp.json() if resp.status_code == 200 else None

def delete_scan(scan_id):
    resp = requests.delete(f"{BASE_URL}/scans/{scan_id}", headers=get_headers())
    return resp.status_code == 204

def clear_all_scans(scan_ids: list) -> int:
    """
    Deletes every scan in the provided list one by one.
    Uses the existing DELETE /scans/{scan_id} endpoint — no new backend route needed.
    Returns the count of successfully deleted scans.
    """
    deleted = 0
    for scan_id in scan_ids:
        if delete_scan(scan_id):
            deleted += 1
    return deleted

def analyze_image(file_bytes, filename, mime_type):
    files = {"file": (filename, file_bytes, mime_type)}
    resp = requests.post(f"{BASE_URL}/osint/image-metadata", files=files, headers=get_headers())
    return resp