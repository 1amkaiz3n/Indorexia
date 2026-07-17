import asyncio
import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
TIMEOUT = 60.0
MAX_RETRIES = 2


def _params(api_key: str, **kwargs) -> dict:
    return {"api_key": api_key, **kwargs}


async def _request(url: str, params: dict, desc: str) -> dict:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 429:
                    logger.warning("%s rate limited (attempt %d/%d)", desc, attempt, MAX_RETRIES)
                    await asyncio.sleep(3)
                    continue
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException as e:
            last_err = f"Timeout: {e}"
            logger.warning("%s timeout (attempt %d/%d)", desc, attempt, MAX_RETRIES)
            await asyncio.sleep(2)
        except httpx.HTTPStatusError as e:
            last_err = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            logger.warning("%s HTTP error (attempt %d/%d): %s", desc, attempt, MAX_RETRIES, last_err)
            if e.response.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(3)
                continue
            raise
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            logger.warning("%s error (attempt %d/%d): %s", desc, attempt, MAX_RETRIES, last_err)
            await asyncio.sleep(2)

    logger.error("%s failed after %d attempts: %s", desc, MAX_RETRIES, last_err)
    return {"error": last_err or "Unknown error"}


async def search_google(query: str, location: str | None = None) -> dict:
    settings = get_settings()
    params = _params(settings.serpapi_api_key, q=query, engine="google", num=20)
    if location:
        params["location"] = location
    return await _request("https://serpapi.com/search", params, f"Google search [{query}]")


async def google_trends(query: str) -> dict:
    settings = get_settings()
    params = _params(settings.serpapi_api_key, q=query, engine="google_trends", data_type="TIMESERIES")
    return await _request("https://serpapi.com/search", params, f"Google Trends [{query}]")


async def google_shopping(query: str, location: str | None = None) -> dict:
    settings = get_settings()
    params = _params(
        settings.serpapi_api_key,
        q=query,
        engine="google_shopping",
        gl="id",
        hl="id",
        currency="IDR",
    )
    if location:
        params["location"] = location
    return await _request("https://serpapi.com/search", params, f"Google Shopping [{query}]")
