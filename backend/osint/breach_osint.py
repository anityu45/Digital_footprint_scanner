import httpx
import logging
import urllib.parse
import asyncio
from typing import List, Dict

# Set up a basic logger for the OSINT API
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osint_api")

# Standard browser headers to prevent WAF blocking
XON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

async def check_data_breaches(email: str) -> List[Dict]:
    """
    Queries the XposedOrNot database to see if an email has been exposed in a data breach.
    """
    if not email:
        return []

    # 1. URL-encode the email to safely handle '+' aliases and special characters
    safe_email = urllib.parse.quote(email)
    url = f"https://api.xposedornot.com/v1/check-email/{safe_email}"

    # 2. Shorten timeout to 15s. If the API takes longer, it's likely hanging.
    async with httpx.AsyncClient(headers=XON_HEADERS, timeout=15.0) as client:
        try:
            resp = await client.get(url)

            # 404 = Clean result (No breaches found)
            if resp.status_code == 404:
                logger.info(f"No breaches found for {email}.")
                return []
                
            # 429 = Rate Limited
            if resp.status_code == 429:
                logger.warning(f"Rate limited by XON API for {email}. Consider adding a delay.")
                return []

            if resp.status_code == 200:
                data = resp.json()
                raw_breaches = data.get("breaches", [])

                # 3. Safely flatten the array in case XON returns a nested list
                flat_breaches = []
                for item in raw_breaches:
                    if isinstance(item, list):
                        flat_breaches.extend(item)  # Add all items from the sub-list
                    else:
                        flat_breaches.append(item)

                findings = []
                for name in flat_breaches:
                    findings.append({
                        "name": str(name),
                        "severity": "HIGH",
                        "source": "XposedOrNot"
                    })

                logger.info(f"Found {len(findings)} breaches for {email}.")
                return findings

            # Catch anything else (500, 503, etc.)
            logger.warning(f"Unexpected response {resp.status_code} from XON for {email}")

        except httpx.TimeoutException:
            logger.error(f"XposedOrNot API Timeout for {email}")
        except Exception as e:
            logger.error(f"XposedOrNot API Error: {e}")

    return []

# --- Testing Block ---
if __name__ == "__main__":
    async def test_run():
        # Testing a known compromised email format and a clean one
        test_emails = ["test@example.com", "clean_email_nobody_uses_12345@gmail.com"]
        
        for email in test_emails:
            print(f"\nScanning: {email}")
            results = await check_data_breaches(email)
            for r in results:
                print(f" - [BREACH] {r['name']}")
            
            # Sleep slightly to respect the free API rate limits
            await asyncio.sleep(1.5)

    # Run the async loop
    asyncio.run(test_run())