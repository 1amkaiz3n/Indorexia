"""Deduplication engine for competitor data.

Merges duplicate businesses found across multiple queries and sources.
One business = one entity regardless of how many times it was found.
"""

import logging
from app.schemas.research import Competitor

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    name = name.lower().strip()
    name = name.replace("  ", " ")
    prefixes = ["toko ", "warung ", "kedai ", "rumah makan ", "depot ", "studio ", "salon "]
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
            break
    suffixes = [" shop", " store", " online", " official"]
    for s in suffixes:
        if name.endswith(s):
            name = name[: -len(s)]
            break
    return name.strip()


def normalize_address(addr: str | None) -> str:
    if not addr:
        return ""
    a = addr.lower().strip()
    a = a.replace("jalan ", "jl ").replace("jl. ", "jl ")
    a = a.replace("kecamatan ", "kec ").replace("kabupaten ", "kab ")
    a = a.replace("provinsi ", "prov ")
    a = a.replace("  ", " ")
    return a.strip()


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""
    p = phone.strip()
    p = p.replace("-", "").replace(" ", "").replace("+62", "0")
    p = p.replace("(", "").replace(")", "").replace(".", "")
    if p.startswith("62"):
        p = "0" + p[2:]
    return p


def extract_city(address: str | None) -> str:
    if not address:
        return ""
    known_cities = [
        "bandung", "jakarta", "surabaya", "yogyakarta", "semarang", "medan",
        "makassar", "palembang", "tangerang", "bekasi", "depok", "bogor",
        "ciamis", "tasikmalaya", "garut", "sukabumi", "cirebon", "malang",
        "solo", "surakarta", "denpasar", "batam", "pekanbaru", "padang",
        "banjarmasin", "samarinda", "manado", "kendari", "ambon", "jayapura",
    ]
    addr_lower = address.lower()
    for city in known_cities:
        if city in addr_lower:
            return city
    return ""


def _compute_name_similarity(a: str, b: str) -> float:
    """Simple character-level similarity for name matching."""
    a = normalize_name(a)
    b = normalize_name(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) < 3 or len(b) < 3:
        return 0.0
    shorter = a if len(a) <= len(b) else b
    longer = b if len(a) <= len(b) else a
    matches = sum(1 for i, c in enumerate(shorter) if i < len(longer) and c == longer[i])
    return matches / len(longer)


def deduplicate(competitors: list[Competitor]) -> list[Competitor]:
    """Deduplicate a list of competitors, keeping the best entry for each unique business.
    
    Dedup priority (tried in order):
    1. Exact Google Maps URL match
    2. Exact phone number match
    3. Exact website match
    4. Normalized name + normalized address match (high similarity)
    5. Name similarity > 0.85 + same city
    """
    if not competitors:
        return []

    unique: list[Competitor] = []

    for comp in competitors:
        is_dup = False
        for existing in unique:
            if _is_duplicate(existing, comp):
                is_dup = True
                _merge_keep_better(existing, comp)
                break
        if not is_dup:
            unique.append(comp)

    logger.info("Dedup: %d -> %d competitors", len(competitors), len(unique))
    return unique


def _is_duplicate(a: Competitor, b: Competitor) -> bool:
    """Check if two competitors represent the same business."""
    # 1. Exact Maps URL
    if a.maps_link and b.maps_link and a.maps_link == b.maps_link and len(a.maps_link) > 20:
        return True

    # 2. Exact phone
    a_phone = normalize_phone(a.phone)
    b_phone = normalize_phone(b.phone)
    if a_phone and b_phone and a_phone == b_phone and len(a_phone) >= 8:
        return True

    # 3. Exact website
    if a.website and b.website and a.website == b.website:
        return True

    # 4. Normalized name + normalized address
    a_name = normalize_name(a.name)
    b_name = normalize_name(b.name)
    a_addr = normalize_address(a.address)
    b_addr = normalize_address(b.address)
    if a_name and b_name and a_addr and b_addr:
        if a_name == b_name and a_addr == b_addr:
            return True
        name_sim = _compute_name_similarity(a_name, b_name)
        addr_sim = _compute_name_similarity(a_addr, b_addr)
        if name_sim > 0.85 and addr_sim > 0.70:
            return True

    # 5. Name similarity + same city
    a_city = extract_city(a.address)
    b_city = extract_city(b.address)
    if a_name and b_name and a_city and b_city and a_city == b_city:
        name_sim = _compute_name_similarity(a_name, b_name)
        if name_sim > 0.85:
            return True

    return False


def _merge_keep_better(existing: Competitor, incoming: Competitor):
    """Merge incoming data into existing, keeping the richer entry per field."""
    if not existing.rating and incoming.rating:
        existing.rating = incoming.rating
    if not existing.reviews and incoming.reviews:
        existing.reviews = incoming.reviews
    if not existing.phone and incoming.phone:
        existing.phone = incoming.phone
    if not existing.website and incoming.website:
        existing.website = incoming.website
    if not existing.address and incoming.address:
        existing.address = incoming.address
    if not existing.hours and incoming.hours:
        existing.hours = incoming.hours
    if not existing.maps_link and incoming.maps_link:
        existing.maps_link = incoming.maps_link
    if not existing.type and incoming.type:
        existing.type = incoming.type
