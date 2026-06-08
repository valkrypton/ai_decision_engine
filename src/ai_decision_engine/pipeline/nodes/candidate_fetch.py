from ai_decision_engine.state import DecisionState


def candidate_fetch_node(state: DecisionState) -> dict:
    if state.domain == "carddeals":
        from ai_decision_engine.domains.carddeals.fetcher import fetch_carddeals
        candidates = fetch_carddeals(state.entities)
    else:
        raise NotImplementedError(f"No fetcher for domain: {state.domain}")

    return {"candidates": candidates}
