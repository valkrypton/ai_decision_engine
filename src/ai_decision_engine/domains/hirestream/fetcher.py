import json
from pathlib import Path

_CANDIDATES_PATH = Path(__file__).parent / "fixtures_candidates.json"
_JOBS_PATH = Path(__file__).parent / "fixtures_jobs.json"


def fetch_hirestream(intent: str, entities: dict) -> list[dict]:
    if intent in ("find_jobs",):
        return _fetch_jobs(entities)
    return _fetch_candidates(entities)


def _fetch_candidates(entities: dict) -> list[dict]:
    with _CANDIDATES_PATH.open() as f:
        candidates = json.load(f)

    role = entities.get("role", "").lower()
    location = entities.get("location", "").lower()
    skills_raw = entities.get("skills", "")
    query_skills = {s.strip().lower() for s in skills_raw.split(",") if s.strip()} if skills_raw else set()

    results = []
    for c in candidates:
        if role and role not in c["role"].lower() and not any(role in s for s in c["skills"]):
            continue
        if location and location != "remote" and location not in c["location"].lower() and c["location"] != "remote":
            continue
        results.append(c)

    return results


def _fetch_jobs(entities: dict) -> list[dict]:
    with _JOBS_PATH.open() as f:
        jobs = json.load(f)

    location = entities.get("location", "").lower()
    role = entities.get("role", "").lower()

    results = []
    for j in jobs:
        if role and role not in j["title"].lower():
            continue
        if location and location != "remote" and location not in j["location"].lower() and j["location"] != "remote":
            continue
        results.append(j)

    return results
