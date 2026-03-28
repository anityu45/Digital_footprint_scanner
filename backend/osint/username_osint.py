import httpx
import asyncio
import logging
from typing import List, Dict
import json
import redis

# Assuming these are defined in your backend.config
from backend.config import SHERLOCK_URL, REDIS_URL, SHERLOCK_SITE_LIMIT

logger = logging.getLogger("osint_api")

FALLBACK_SITES = {
    "GitHub": {"errorType": "status_code", "url": "https://github.com/{}"},
    "Twitter": {"errorType": "status_code", "url": "https://twitter.com/{}"},
    "Instagram": {"errorType": "status_code", "url": "https://www.instagram.com/{}"},
    "Reddit": {"errorType": "status_code", "url": "https://www.reddit.com/user/{}/"},
    "Medium": {"errorType": "status_code", "url": "https://medium.com/@{}"},
    "Patreon": {"errorType": "status_code", "url": "https://www.patreon.com/{}"},
    "TikTok": {"errorType": "status_code", "url": "https://www.tiktok.com/@{}"},
    "Twitch": {"errorType": "status_code", "url": "https://www.twitch.tv/{}"},
    "Snapchat": {"errorType": "status_code", "url": "https://www.snapchat.com/add/{}"},
    "Telegram": {
        "errorType": "message",
        "url": "https://t.me/{}",
        "errorMsg": "If you have <strong>Telegram</strong>, you can contact <a class=\"tgme_head_dl_button\""
    }
}

# Standard browser headers to prevent immediate blocking by WAFs (Cloudflare, etc.)
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Establish a Redis connection gracefully
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Ping to ensure connection is actually alive
    redis_client.ping()
    SHERLOCK_SITES_KEY = "sherlock_sites"
except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
    logger.error(f"Could not connect to Redis for caching: {e}")
    redis_client = None


async def _get_sherlock_sites(client: httpx.AsyncClient) -> dict:
    """
    Fetches Sherlock sites, using Redis as a cache with a 24-hour TTL.
    """
    if redis_client:
        try:
            cached_sites = redis_client.get(SHERLOCK_SITES_KEY)
            if cached_sites:
                logger.info("Sherlock sites found in cache.")
                return json.loads(cached_sites)
        except redis.RedisError as e:
            logger.warning(f"Redis get error: {e}")

    logger.info("Fetching Sherlock sites from source...")
    try:
        sites_resp = await client.get(SHERLOCK_URL)
        sites_resp.raise_for_status() 
        all_sites = sites_resp.json()

        if redis_client:
            try:
                # Cache for 24 hours (86400 seconds)
                redis_client.setex(SHERLOCK_SITES_KEY, 86400, json.dumps(all_sites))
                logger.info("Sherlock sites cached in Redis.")
            except redis.RedisError as e:
                logger.warning(f"Redis set error: {e}")
                
    except Exception as e:
        logger.warning(f"Could not fetch Sherlock sites, using fallback: {e}")
        all_sites = FALLBACK_SITES

    return all_sites


async def check_username_with_sherlock(username: str) -> List[Dict]:
    if not username:
        return []

    # Injecting the headers here to look like a real user
    async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=60.0, follow_redirects=True) as client:
        try:
            all_sites = await _get_sherlock_sites(client)
            top_sites = list(all_sites.items())[:SHERLOCK_SITE_LIMIT]
            
            tasks = []
            for site_name, info in top_sites:
                # FIX: Skip metadata keys like "$schema" that are strings instead of dicts
                if not isinstance(info, dict):
                    continue
                    
                if "{}" in info.get("url", ""):
                    url = info["url"].format(username)
                    tasks.append(_probe(client, site_name, url, info))

            results = await asyncio.gather(*tasks)
            # Filter out None values
            return [r for r in results if r]

        except httpx.HTTPStatusError as e:
            logger.error(f"Could not fetch Sherlock site list: {e.request.url} - {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Username Scan Error: {e}")
            return []

async def _probe(client: httpx.AsyncClient, name: str, url: str, info: dict) -> dict | None:
    try:
        # We use a slightly shorter timeout for individual probes so one slow site doesn't hang the batch
        resp = await client.get(url, timeout=15.0)
        
        error_type = info.get("errorType", "status_code")

        # False Positive Check: Did the site redirect us away from the profile page?
        if str(resp.url) != url and "login" in str(resp.url).lower():
             logger.debug(f"[{name}] False positive prevented: Redirected to login.")
             return None

        if error_type == "status_code":
            if resp.status_code == 200:
                return {"site": name, "url": url}
                
        elif error_type == "message":
            error_msg = info.get("errorMsg", "")
            # If the error message is NOT in the text, it means the profile likely exists
            if error_msg and error_msg not in resp.text:
                if resp.status_code == 200:
                    return {"site": name, "url": url}
                    
    except httpx.TimeoutException:
        logger.debug(f"[{name}] Probe timed out at {url}")
    except Exception as e:
        logger.debug(f"[{name}] Probe failed at {url}: {e}")
        
    return None