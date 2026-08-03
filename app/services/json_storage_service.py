import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "research.json"
_lock = asyncio.Lock()


def _ensure_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"research": []}, indent=2))


def _read() -> list[dict]:
    _ensure_file()
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
        return data.get("research", [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _write(items: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({"research": items}, f, indent=2, default=str)


def _sort_items(items: list[dict], sort: str) -> list[dict]:
    pinned = [i for i in items if i.get("pinned")]
    unpinned = [i for i in items if not i.get("pinned")]
    if sort == "newest":
        pinned.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        unpinned.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort == "oldest":
        pinned.sort(key=lambda x: x.get("created_at", ""))
        unpinned.sort(key=lambda x: x.get("created_at", ""))
    else:
        pinned.sort(key=lambda x: x.get("score", 0), reverse=True)
        unpinned.sort(key=lambda x: x.get("score", 0), reverse=True)
    return pinned + unpinned


async def save_research(
    visitor_id: str,
    query: str,
    location: str,
    verdict: str,
    score: int,
    raw_data: dict,
    report: dict,
) -> dict | None:
    record = {
        "id": str(uuid.uuid4()),
        "visitor_id": visitor_id,
        "title": query,
        "query": query,
        "location": location,
        "verdict": verdict,
        "score": score,
        "pinned": False,
        "raw_data": raw_data,
        "report": report,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    async with _lock:
        items = _read()
        items.append(record)
        _write(items)
    return record


async def get_history(
    visitor_id: str,
    search: str = "",
    verdict: str = "",
    sort: str = "newest",
    limit: int = 50,
    offset: int = 0,
) -> list:
    async with _lock:
        items = _read()

    filtered = [i for i in items if i.get("visitor_id") == visitor_id]

    if search:
        search_lower = search.lower()
        filtered = [i for i in filtered if search_lower in i.get("query", "").lower()]

    if verdict:
        verdict_lower = verdict.lower()
        filtered = [i for i in filtered if verdict_lower in i.get("verdict", "").lower()]

    filtered = _sort_items(filtered, sort)

    return filtered[offset:offset + limit]


async def get_report(report_id: str, visitor_id: str) -> dict | None:
    async with _lock:
        items = _read()
    for item in items:
        if item.get("id") == report_id and item.get("visitor_id") == visitor_id:
            return item
    return None


async def delete_report(report_id: str, visitor_id: str) -> bool:
    async with _lock:
        items = _read()
        before = len(items)
        items = [i for i in items if not (i.get("id") == report_id and i.get("visitor_id") == visitor_id)]
        if len(items) < before:
            _write(items)
            return True
        return False


async def delete_all_reports(visitor_id: str) -> bool:
    async with _lock:
        items = _read()
        before = len(items)
        items = [i for i in items if i.get("visitor_id") != visitor_id]
        if len(items) < before:
            _write(items)
            return True
        return False


async def update_report(
    report_id: str,
    visitor_id: str,
    title: str | None = None,
    pinned: bool | None = None,
) -> dict | None:
    async with _lock:
        items = _read()
        for item in items:
            if item.get("id") == report_id and item.get("visitor_id") == visitor_id:
                if title is not None:
                    item["title"] = title
                if pinned is not None:
                    item["pinned"] = pinned
                _write(items)
                return item
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
