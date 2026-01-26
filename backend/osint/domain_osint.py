import requests

def check_crt_sh(domain):
    if not domain:
        return {"found": False, "description": "No domain provided"}
        
    url = f"https://crt.sh/?q={domain}&output=json"
    try:
        resp = requests.get(url, timeout=10)
        # crt.sh sometimes returns a list, sometimes empty
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                count = len(data)
                return {"found": True, "description": f"Found {count} SSL certificates (+15 Risk)"}
    except:
        pass
    return {"found": False, "description": "No certificates found"}