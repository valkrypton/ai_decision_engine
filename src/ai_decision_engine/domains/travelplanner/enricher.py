def enrich_travelplanner(candidates: list[dict], entities: dict) -> list[dict]:
    budget_raw = entities.get("budget_usd", "")
    duration_raw = entities.get("duration_days", "")

    budget: float | None = None
    if budget_raw:
        digits = "".join(c for c in str(budget_raw) if c.isdigit() or c == ".")
        try:
            budget = float(digits)
        except ValueError:
            pass

    duration: int | None = None
    if duration_raw:
        digits = "".join(c for c in str(duration_raw) if c.isdigit())
        try:
            duration = int(digits)
        except ValueError:
            pass

    enriched = []
    for d in candidates:
        entry = dict(d)
        days = duration or d.get("recommended_days", 5)
        total_cost = d["flight_price_usd"] + (d["hotel_per_night_usd"] + d["avg_daily_spend_usd"]) * days
        entry["total_estimated_cost_usd"] = round(total_cost, 2)

        if budget is not None and budget > 0:
            entry["value_score"] = min(budget / total_cost, 1.0) if total_cost > 0 else 1.0
        else:
            max_cost = 5000.0
            entry["value_score"] = max(0.0, 1.0 - (total_cost / max_cost))

        entry["rating"] = float(d.get("rating", 0.0))
        entry["weather_score"] = float(d.get("weather_score", 0.5))

        enriched.append(entry)
    return enriched
