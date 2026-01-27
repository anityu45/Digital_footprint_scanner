import hashlib
import requests
import time

def check_gravatar(email):
    """Passive check: Is their face/name public?"""
    email_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            entry = data.get('entry', [{}])[0]
            return {
                "found": True, 
                "site": "Gravatar",
                "description": f"Gravatar Profile found (Name: {entry.get('displayName', 'Unknown')})"
            }
    except:
        pass
    return None

def check_spotify(email):
    """Active Check: Does a Spotify account exist?"""
    url = "https://spclient.wg.spotify.com/signup/public/v1/account"
    params = {"validate": "1", "email": email}
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200 and resp.json().get("status") == 1:
            return {"found": True, "site": "Spotify", "description": "Spotify Account exists (Target for Phishing)"}
    except:
        pass
    return None

def check_adobe(email):
    """Active Check: Does an Adobe account exist?"""
    url = "https://auth.services.adobe.com/signin/v2/users/accounts"
    headers = {"X-IMS-ClientId": "RestyleWeb1", "Content-Type": "application/json"}
    payload = {"username": email}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        if resp.status_code == 200 and isinstance(resp.json(), list):
             return {"found": True, "site": "Adobe", "description": "Adobe Account exists (High Value Target)"}
    except:
        pass
    return None

def run_email_checks(email):
    results = []
    checks = [check_gravatar, check_spotify, check_adobe]
    for check in checks:
        res = check(email)
        if res:
            results.append(res)
        time.sleep(0.5)
    return results