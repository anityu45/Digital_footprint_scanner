import random

def check_data_breaches(email):
    """
    Simulates a check against known data breaches (e.g., Collection #1).
    Real tools use the 'HaveIBeenPwned' API (which requires a paid key).
    """
    breaches = []
    
    # We simulate findings for common email providers to demonstrate the feature.
    # In a production app, you would make a request to: https://haveibeenpwned.com/api/v3/
    
    domain = email.split("@")[-1]
    
    
    if "gmail" in domain or "yahoo" in domain or "hotmail" in domain:
        breaches.append({
            "name": "Collection #1 (2019)",
            "description": "773 million unique emails and passwords exposed.",
            "severity": "CRITICAL"
        })
        breaches.append({
            "name": "Verifications.io",
            "description": "Big data email verification service leak.",
            "severity": "HIGH"
        })
        
    return breaches
