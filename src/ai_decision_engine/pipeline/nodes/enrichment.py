from ai_decision_engine.state import DecisionState


def enrichment_node(state: DecisionState) -> dict:
    if state.domain == "carddeals":
        from ai_decision_engine.domains.carddeals.enricher import enrich_carddeals
        enriched = enrich_carddeals(state.candidates, state.entities)
    else:
        raise NotImplementedError(f"No enricher for domain: {state.domain}")

    return {"enriched": enriched}
