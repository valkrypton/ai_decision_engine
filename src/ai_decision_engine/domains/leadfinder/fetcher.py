import json
from pathlib import Path

_FIXTURES_PATH = Path(__file__).parent / "fixtures.json"


def fetch_leadfinder(entities: dict) -> list[dict]:
    with _FIXTURES_PATH.open() as f:
        companies = json.load(f)

    industry = entities.get("industry", "").lower()
    location = entities.get("location", "").lower()
    size = entities.get("company_size", "").lower()
    technology = entities.get("technology", "").lower()
    funding_stage = entities.get("funding_stage", "").lower()

    results = []
    for c in companies:
        if industry and industry not in c["industry"].lower():
            continue
        if location and location not in c["location"].lower():
            continue
        if size and size not in c["company_size"].lower():
            continue
        if technology and not any(technology in t.lower() for t in c.get("technology_stack", [])):
            continue
        if funding_stage and funding_stage not in c.get("funding_stage", "").lower():
            continue
        results.append(c)

    return results
