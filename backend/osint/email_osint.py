import hashlib
import requests

def check_gravatar(email):
    """Checks if a Gravatar profile exists for the email hash."""
    if not email:
        return {"found": False, "description": "No email provided"}
        
    email_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return {
                "found": True, 
                "description": "Gravatar profile found (+10 Risk)"
            }
    except Exception:
        pass
    return {"found": False, "description": "No Gravatar found"}

def check_hibp(email):
    """
    Simulated HIBP check since the real API requires a paid key.
    Returns a mock breach if specific keywords are used.
    """
    if not email:
        return {"found": False, "description": "No email provided"}
        
    # Simulation Logic for testing
    if "breach" in email or "test" in email:
        return {"found": True, "description": "Email found in simulated breach (+30 Risk)"}
    
    return {"found": False, "description": "No breaches found (Simulated)"}