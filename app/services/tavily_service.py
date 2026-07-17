import asyncio
import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
TIMEOUT = 60.0
MAX_RETRIES = 2


async def search_general(query: str) -> dict:
    settings = get_settings()
    last_err = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.tavily_api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 5,
                    },
                )
                if resp.status_code == 429:
                    logger.warning("Tavily rate limited (attempt %d/%d)", attempt, MAX_RETRIES)
                    await asyncio.sleep(3)
                    continue
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException as e:
            last_err = f"Timeout: {e}"
            logger.warning("Tavily timeout (attempt %d/%d)", attempt, MAX_RETRIES)
            await asyncio.sleep(2)
        except httpx.HTTPStatusError as e:
            last_err = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            logger.warning("Tavily HTTP error (attempt %d/%d): %s", attempt, MAX_RETRIES, last_err)
            if e.response.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(3)
                continue
            raise
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            logger.warning("Tavily error (attempt %d/%d): %s", attempt, MAX_RETRIES, last_err)
            await asyncio.sleep(2)

    logger.error("Tavily failed after %d attempts: %s", MAX_RETRIES, last_err)
    return {"error": last_err or "Unknown error"}
