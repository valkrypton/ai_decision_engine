import json
from pathlib import Path

_FIXTURES_PATH = Path(__file__).parent / "fixtures.json"


def fetch_travelplanner(entities: dict) -> list[dict]:
    with _FIXTURES_PATH.open() as f:
        destinations = json.load(f)

    destination = entities.get("destination", "").lower()
    travel_style = entities.get("travel_style", "").lower()

    results = []
    for d in destinations:
        if destination and destination not in d["name"].lower() and destination not in d["country"].lower():
            continue
        if travel_style and not any(travel_style in tag for tag in d.get("tags", [])):
            continue
        results.append(d)

    return results if results else destinations
