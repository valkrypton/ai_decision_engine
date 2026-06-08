import json
from pathlib import Path

_FIXTURES_PATH = Path(__file__).parent / "fixtures.json"


def fetch_carddeals(entities: dict) -> list[dict]:
    with _FIXTURES_PATH.open() as f:
        restaurants = json.load(f)

    location = entities.get("location", "").lower()
    cuisine = entities.get("cuisine", "").lower()
    card_type = entities.get("card_type", "").lower()

    results = []
    for r in restaurants:
        if location and location not in r["location"].lower():
            continue
        if cuisine and cuisine not in r["cuisine"].lower():
            continue

        matching_deals = r["deals"]
        if card_type:
            matching_deals = [d for d in r["deals"] if card_type in d["card_type"].lower()]
        if not matching_deals:
            continue

        best_deal = max(matching_deals, key=lambda d: d["discount_pct"])
        results.append({**r, "best_deal": best_deal})

    return results
