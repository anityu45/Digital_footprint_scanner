import hashlib
import requests
import time

# --- 1. The Passive Check (Safe, Fast) ---
def check_gravatar(email):
    """Checks if a Gravatar profile exists."""
    email_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            # Try to grab a username or real name if available
            entry = data.get('entry', [{}])[0]
            name = entry.get('displayName', 'Unknown')
            return {
                "found": True, 
                "site": "Gravatar",
                "description": f"Gravatar Profile found (Name: {name})"
            }
    except:
        pass
    return None

# --- 2. The Active Checks (The "Holehe" Logic) ---
# These functions send a "fake" login or registration request to see 
# if the server responds with "Email already taken".

def check_spotify(email):
    """Checks if email is registered on Spotify."""
    url = "https://spclient.wg.spotify.com/signup/public/v1/account"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {"validate": "1", "email": email}
    try:
        # Spotify returns JSON with status: 1 if taken, 20 if valid/available
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == 1:  # 1 means 'That email is already on Spotify'
                return {"found": True, "site": "Spotify", "description": "Spotify Account exists"}
    except:
        pass
    return None

def check_wordpress(email):
    """Checks if email is registered on WordPress.com."""
    url = "https://public-api.wordpress.com/rest/v1.1/users/validate-email"
    data = {"email": email}
    try:
        resp = requests.post(url, data=data, timeout=5)
        if resp.status_code == 200:
            json_resp = resp.json()
            # If known, success is False because 'email is not available'
            if not json_resp.get("success"): 
                return {"found": True, "site": "WordPress", "description": "WordPress Account exists"}
    except:
        pass
    return None

def check_adobe(email):
    """Checks Adobe's API (often reliable for creatives)."""
    url = "https://auth.services.adobe.com/signin/v2/users/accounts"
    headers = {
        "X-IMS-ClientId": "RestyleWeb1",  # Public client ID
        "Content-Type": "application/json"
    }
    payload = {"username": email}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        if resp.status_code == 200:
            # If they return a list of accounts, it exists
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                 return {"found": True, "site": "Adobe", "description": "Adobe Account exists"}
    except:
        pass
    return None

# --- Main Aggregator ---
def run_email_checks(email):
    results = []
    
    # 1. Gravatar
    g = check_gravatar(email)
    if g: results.append(g)
    
    # 2. Active Checks (Simulated Holehe)
    # Add slight delay to be polite
    time.sleep(0.5)
    s = check_spotify(email)
    if s: results.append(s)
    
    time.sleep(0.5)
    w = check_wordpress(email)
    if w: results.append(w)
    
    time.sleep(0.5)
    a = check_adobe(email)
    if a: results.append(a)
    
    return results