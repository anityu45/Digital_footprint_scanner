import httpx
import asyncio
import logging
from typing import List, Dict
import json
import redis

from backend.config import SHERLOCK_URL, REDIS_URL, SHERLOCK_SITE_LIMIT

logger = logging.getLogger("osint_api")

# Establish a Redis connection. In a larger app, this might be a shared utility.
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    SHERLOCK_SITES_KEY = "sherlock_sites"
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis for caching: {e}")
    redis_client = None


async def _get_sherlock_sites(client: httpx.AsyncClient) -> dict:
    """
    Fetches Sherlock sites, using Redis as a cache with a 24-hour TTL.
    """
    # 1. Try to get from cache
    if redis_client:
        cached_sites = redis_client.get(SHERLOCK_SITES_KEY)
        if cached_sites:
            logger.info("Sherlock sites found in cache.")
            return json.loads(cached_sites)

    # 2. If not in cache, fetch from source
    logger.info("Fetching Sherlock sites from source...")
    sites_resp = await client.get(SHERLOCK_URL)
    sites_resp.raise_for_status()  # Will raise an exception for 4xx/5xx responses
    all_sites = sites_resp.json()

    # 3. Store in cache for next time
    if redis_client:
        # Cache for 24 hours (86400 seconds)
        redis_client.setex(SHERLOCK_SITES_KEY, 86400, json.dumps(all_sites))
        logger.info("Sherlock sites cached in Redis.")

    return all_sites


async def check_username_with_sherlock(username: str) -> List[Dict]:
    if not username:
        return []

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            # Step 1: Get the site list (now with caching)
            all_sites = await _get_sherlock_sites(client)

            # Step 2: Use the configurable site limit
            top_sites = list(all_sites.items())[:SHERLOCK_SITE_LIMIT]
            
            tasks = []
            for site_name, info in top_sites:
                if "{}" in info.get("url", ""):
                    url = info["url"].format(username)
                    tasks.append(_probe(client, site_name, url, info))

            results = await asyncio.gather(*tasks)
            return [r for r in results if r]

        except httpx.HTTPStatusError as e:
            logger.error(f"Could not fetch Sherlock site list: {e.request.url} - {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Username Scan Error: {e}")
            return []

async def _probe(client, name, url, info):
    try:
        resp = await client.get(url)
        
        # Sherlock's logic: if errorType is not specified, it defaults to 'status_code'.
        error_type = info.get("errorType", "status_code")

        if error_type == "status_code":
            if resp.status_code == 200:
                return {"site": name, "url": url}
        elif error_type == "message":
            if info.get("errorMsg") not in resp.text:
                return {"site": name, "url": url}
    except Exception as e:
        # Silently failing is risky. At least log the error for debugging.
        logger.debug(f"Probe failed for {name} at {url}: {e}")
    return None