import httpx
from app.config import get_settings


def _headers() -> dict:
    s = get_settings()
    return {
        "apikey": s.supabase_key,
        "Authorization": f"Bearer {s.supabase_key}",
        "Content-Type": "application/json",
    }


def _ok():
    s = get_settings()
    return bool(s.supabase_url and s.supabase_key)


async def save_research(
    visitor_id: str,
    query: str,
    location: str,
    verdict: str,
    score: int,
    raw_data: dict,
    report: dict,
) -> dict | None:
    if not _ok():
        return None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{get_settings().supabase_url}/research",
            headers={**_headers(), "Prefer": "return=representation"},
            json={
                "visitor_id": visitor_id,
                "title": query,
                "query": query,
                "location": location,
                "verdict": verdict,
                "score": score,
                "raw_data": raw_data,
                "report": report,
            },
        )
        if resp.is_success:
            data = resp.json()
            return data[0] if isinstance(data, list) else data
        return None


async def get_history(
    visitor_id: str,
    search: str = "",
    verdict: str = "",
    sort: str = "newest",
    limit: int = 50,
    offset: int = 0,
) -> list:
    if not _ok():
        return []
    params = {
        "visitor_id": f"eq.{visitor_id}",
        "order": "pinned.desc,created_at.desc" if sort == "newest" else "pinned.desc,created_at.asc" if sort == "oldest" else "pinned.desc,score.desc",
        "limit": limit,
        "offset": offset,
    }
    if search:
        params["query"] = f"ilike.%{search}%"
    if verdict:
        params["verdict"] = f"ilike.%{verdict}%"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{get_settings().supabase_url}/research",
            headers=_headers(),
            params=params,
        )
        if resp.is_success:
            return resp.json()
        return []


async def get_report(report_id: str, visitor_id: str) -> dict | None:
    if not _ok():
        return None
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{get_settings().supabase_url}/research",
            headers=_headers(),
            params={
                "id": f"eq.{report_id}",
                "visitor_id": f"eq.{visitor_id}",
                "limit": 1,
            },
        )
        if resp.is_success:
            data = resp.json()
            return data[0] if data else None
        return None


async def delete_report(report_id: str, visitor_id: str) -> bool:
    if not _ok():
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{get_settings().supabase_url}/research",
            headers=_headers(),
            params={
                "id": f"eq.{report_id}",
                "visitor_id": f"eq.{visitor_id}",
            },
        )
        return resp.is_success


async def delete_all_reports(visitor_id: str) -> bool:
    if not _ok():
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{get_settings().supabase_url}/research",
            headers=_headers(),
            params={"visitor_id": f"eq.{visitor_id}"},
        )
        return resp.is_success


async def update_report(
    report_id: str,
    visitor_id: str,
    title: str | None = None,
    pinned: bool | None = None,
) -> dict | None:
    if not _ok():
        return None
    body = {}
    if title is not None:
        body["title"] = title
    if pinned is not None:
        body["pinned"] = pinned
    if not body:
        return None
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{get_settings().supabase_url}/research",
            headers={**_headers(), "Prefer": "return=representation"},
            params={
                "id": f"eq.{report_id}",
                "visitor_id": f"eq.{visitor_id}",
            },
            json=body,
        )
        if resp.is_success:
            data = resp.json()
            return data[0] if isinstance(data, list) else data
        return None


async def duplicate_report(report_id: str, visitor_id: str) -> dict | None:
    original = await get_report(report_id, visitor_id)
    if not original:
        return None
    return await save_research(
        visitor_id=visitor_id,
        query=original.get("query", ""),
        location=original.get("location", ""),
        verdict=original.get("verdict", ""),
        score=original.get("score", 0),
        raw_data=original.get("raw_data", {}),
        report=original.get("report", {}),
    )



