from ai_decision_engine.state import DecisionState


def candidate_fetch_node(state: DecisionState) -> dict:
    domain = state.domain
    if domain == "carddeals":
        from ai_decision_engine.domains.carddeals.fetcher import fetch_carddeals
        candidates = fetch_carddeals(state.entities)
    elif domain == "hirestream":
        from ai_decision_engine.domains.hirestream.fetcher import fetch_hirestream
        candidates = fetch_hirestream(state.intent, state.entities)
    elif domain == "leadfinder":
        from ai_decision_engine.domains.leadfinder.fetcher import fetch_leadfinder
        candidates = fetch_leadfinder(state.entities)
    elif domain == "travelplanner":
        from ai_decision_engine.domains.travelplanner.fetcher import fetch_travelplanner
        candidates = fetch_travelplanner(state.entities)
    else:
        raise NotImplementedError(f"No fetcher for domain: {domain}")
    return {"candidates": candidates}
