from ai_decision_engine.state import DecisionState


def enrichment_node(state: DecisionState) -> dict:
    domain = state.domain
    if domain == "carddeals":
        from ai_decision_engine.domains.carddeals.enricher import enrich_carddeals
        enriched = enrich_carddeals(state.candidates, state.entities)
    elif domain == "hirestream":
        from ai_decision_engine.domains.hirestream.enricher import enrich_hirestream
        enriched = enrich_hirestream(state.candidates, state.entities, state.intent)
    elif domain == "leadfinder":
        from ai_decision_engine.domains.leadfinder.enricher import enrich_leadfinder
        enriched = enrich_leadfinder(state.candidates, state.entities)
    elif domain == "travelplanner":
        from ai_decision_engine.domains.travelplanner.enricher import enrich_travelplanner
        enriched = enrich_travelplanner(state.candidates, state.entities)
    else:
        raise NotImplementedError(f"No enricher for domain: {domain}")
    return {"enriched": enriched}
