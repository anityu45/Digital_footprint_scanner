from duckduckgo_search import DDGS
from urllib.parse import urlparse

def get_domain_name(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return url

def check_username_list(username):
    """Searches the web for the username."""
    if not username: return []

    print(f"🕵️ Searching web for: {username}...")
    found_links = []
    query = f'inurl:"{username}"'
    
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=10)
            if results:
                for r in results:
                    found_links.append({
                        "site": get_domain_name(r.get('href')),
                        "url": r.get('href'),
                        "title": r.get('title')
                    })
    except Exception as e:
        print(f"Search error: {e}")

    return found_links