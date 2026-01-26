import requests

def check_github(username):
    if not username:
        return {"found": False, "description": "No username provided"}
        
    url = f"https://api.github.com/users/{username}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return {"found": True, "description": "GitHub account exists (+10 Risk)"}
    except:
        pass
    return {"found": False, "description": "GitHub account not found"}

def check_whatsmyname(username):
    if not username:
        return {"found": False, "description": "No username provided"}

    # Simplified check on a few major sites
    sites = [
        {"name": "Twitter/X", "url": f"https://twitter.com/{username}"},
        {"name": "Instagram", "url": f"https://www.instagram.com/{username}/"},
        {"name": "Pastebin", "url": f"https://pastebin.com/u/{username}"}
    ]
    
    found_sites = []
    for site in sites:
        try:
            resp = requests.get(site["url"], timeout=3)
            if resp.status_code == 200:
                found_sites.append(site["name"])
        except:
            continue

    if found_sites:
        return {"found": True, "description": f"Username found on: {', '.join(found_sites)} (+20 Risk)"}
    
    return {"found": False, "description": "Username not found on checked lists"}