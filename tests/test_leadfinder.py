import pytest
from ai_decision_engine.config import load_domain_config
from ai_decision_engine.domains.leadfinder.fetcher import fetch_leadfinder
from ai_decision_engine.domains.leadfinder.enricher import enrich_leadfinder
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node
from ai_decision_engine.state import DecisionState


def test_leadfinder_config_loads():
    cfg = load_domain_config("leadfinder")
    assert cfg["domain"] == "leadfinder"
    assert "icp_score" in cfg["ranking"]["weights"]


def test_fetch_all_companies():
    results = fetch_leadfinder({})
    assert len(results) >= 5


def test_fetch_by_industry():
    results = fetch_leadfinder({"industry": "software"})
    for r in results:
        assert "software" in r["industry"].lower()


def test_fetch_by_location():
    results = fetch_leadfinder({"location": "new york"})
    for r in results:
        assert "new york" in r["location"].lower()


def test_fetch_by_technology():
    results = fetch_leadfinder({"technology": "python"})
    for r in results:
        assert any("python" in t.lower() for t in r["technology_stack"])


def test_fetch_unknown_returns_empty():
    results = fetch_leadfinder({"industry": "underwater-basket-weaving"})
    assert results == []


def test_enricher_passes_through_scores():
    companies = fetch_leadfinder({})
    enriched = enrich_leadfinder(companies, {})
    for e in enriched:
        assert "icp_score" in e
        assert "engagement_score" in e
        assert "intent_signal" in e
        assert 0.0 <= e["icp_score"] <= 1.0


def test_ranking_leadfinder_sorted():
    state = DecisionState(input="saas companies sf", domain="leadfinder", intent="find_leads", entities={})
    fetch_result = candidate_fetch_node(state)
    state = DecisionState(**{**state.model_dump(), **fetch_result})
    enrich_result = enrichment_node(state)
    state = DecisionState(**{**state.model_dump(), **enrich_result})
    rank_result = ranking_node(state)
    ranked = rank_result["ranked"]
    assert len(ranked) > 0
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)
