import httpx
import logging
from typing import List, Dict

logger = logging.getLogger("osint_api")

async def check_data_breaches(email: str) -> List[Dict]:
    """
    Queries XposedOrNot breach database.
    No API key required for email exposure endpoint.
    """
    if not email:
        return []

    url = f"https://api.xposedornot.com/v1/check-email/{email}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)

            # 404 = no breach found
            if resp.status_code == 404:
                return []

            if resp.status_code == 200:
                data = resp.json()
                raw_breaches = data.get("breaches", [])

                findings = []
                for b in raw_breaches:
                    name = b[0] if isinstance(b, list) and b else str(b)

                    findings.append({
                        "name": name,
                        "severity": "HIGH",
                        "source": "XposedOrNot"
                    })

                return findings

            logger.warning(f"Unexpected response {resp.status_code}")

        except Exception as e:
            logger.error(f"XposedOrNot API Error: {e}")

    return []