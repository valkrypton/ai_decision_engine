def enrich_carddeals(candidates: list[dict], entities: dict) -> list[dict]:
    budget_str = entities.get("budget", "")
    budget = None
    if budget_str:
        digits = "".join(c for c in budget_str if c.isdigit() or c == ".")
        try:
            budget = float(digits)
        except ValueError:
            pass

    enriched = []
    for c in candidates:
        entry = dict(c)
        entry["discount_value"] = c["best_deal"]["discount_pct"] / 100.0
        entry["within_budget"] = True
        if budget is not None:
            estimated_meal = 25.0
            discounted = estimated_meal * (1 - entry["discount_value"])
            entry["within_budget"] = discounted <= budget
        enriched.append(entry)
    return enriched
