from ai_decision_engine.state import DecisionState
from ai_decision_engine.config import load_domain_config


def ranking_node(state: DecisionState) -> dict:
    config = load_domain_config(state.domain)
    weights: dict = config["ranking"]["weights"]
    higher_is_better: dict = config["ranking"].get("higher_is_better", {})
    max_results: int = config.get("response", {}).get("max_results", 5)

    candidates = state.enriched
    if not candidates:
        return {"ranked": []}

    # Normalize each field to [0, 1] across candidates
    field_values: dict[str, list[float]] = {}
    for field in weights:
        vals = [float(c.get(field, 0)) for c in candidates]
        mn, mx = min(vals), max(vals)
        if mx == mn:
            field_values[field] = [1.0] * len(vals)
        else:
            field_values[field] = [(v - mn) / (mx - mn) for v in vals]

    scored = []
    for i, candidate in enumerate(candidates):
        score = 0.0
        for field, weight in weights.items():
            norm = field_values[field][i]
            # Invert if lower is better (e.g. distance)
            if not higher_is_better.get(field, True):
                norm = 1.0 - norm
            score += weight * norm
        scored.append({**candidate, "score": round(score, 4)})

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)[:max_results]
    return {"ranked": ranked}
