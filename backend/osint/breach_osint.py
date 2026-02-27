import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

XON_CHECK_EMAIL_URL = "https://api.xposedornot.com/v1/check-email"
XON_TIMEOUT_SECONDS = 12


def _severity_from_count(count: int) -> str:
    if count >= 10:
        return "CRITICAL"
    if count >= 5:
        return "HIGH"
    if count >= 2:
        return "MEDIUM"
    return "LOW"


def check_data_breaches(email: str) -> list[dict[str, Any]]:
    """
    Check an email against XposedOrNot breach data.

    Returns a normalized list of:
    { name, description, severity }
    """
    if not email or "@" not in email:
        return []

    url = f"{XON_CHECK_EMAIL_URL}/{email.strip().lower()}"

    try:
        response = requests.get(url, timeout=XON_TIMEOUT_SECONDS)

        if response.status_code == 404:
            # XON returns not found when no breaches are present.
            return []

        if response.status_code == 429:
            logger.warning("XposedOrNot rate limit hit for %s", email)
            return []

        response.raise_for_status()
        payload = response.json()

        # Docs show shape: {"breaches": [["BreachA", "BreachB", ...]]}
        raw = payload.get("breaches", [])
        breach_names: list[str] = []
        for item in raw:
            if isinstance(item, list):
                breach_names.extend([str(x).strip() for x in item if str(x).strip()])
            elif isinstance(item, str) and item.strip():
                breach_names.append(item.strip())

        breach_names = list(dict.fromkeys(breach_names))  # de-duplicate, keep order
        if not breach_names:
            return []

        severity = _severity_from_count(len(breach_names))
        return [
            {
                "name": name,
                "description": f"Found via XposedOrNot breach index for {email}",
                "severity": severity,
            }
            for name in breach_names
        ]

    except requests.RequestException as exc:
        logger.exception("XposedOrNot request failed for %s: %s", email, exc)
        return []
    except ValueError:
        logger.exception("Failed to parse XposedOrNot JSON for %s", email)
        return []
