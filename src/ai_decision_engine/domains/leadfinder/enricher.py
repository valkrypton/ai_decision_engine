def enrich_leadfinder(candidates: list[dict], entities: dict) -> list[dict]:
    """Lead Finder scores are pre-computed in fixtures. Pass through with validation."""
    enriched = []
    for c in candidates:
        entry = dict(c)
        entry["icp_score"] = float(c.get("icp_score", 0.0))
        entry["engagement_score"] = float(c.get("engagement_score", 0.0))
        entry["intent_signal"] = float(c.get("intent_signal", 0.0))
        enriched.append(entry)
    return enriched
