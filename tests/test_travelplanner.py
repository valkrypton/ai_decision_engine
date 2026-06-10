import pytest
from ai_decision_engine.config import load_domain_config
from ai_decision_engine.domains.travelplanner.fetcher import fetch_travelplanner
from ai_decision_engine.domains.travelplanner.enricher import enrich_travelplanner
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node
from ai_decision_engine.state import DecisionState


def test_travelplanner_config_loads():
    cfg = load_domain_config("travelplanner")
    assert cfg["domain"] == "travelplanner"
    assert "value_score" in cfg["ranking"]["weights"]
    assert "rating" in cfg["ranking"]["weights"]


def test_fetch_no_filter_returns_all():
    results = fetch_travelplanner({})
    assert len(results) >= 5


def test_fetch_by_destination():
    results = fetch_travelplanner({"destination": "Barcelona"})
    assert len(results) == 1
    assert results[0]["name"] == "Barcelona"


def test_fetch_by_travel_style():
    results = fetch_travelplanner({"travel_style": "beach"})
    assert len(results) > 0
    for r in results:
        assert "beach" in r["tags"]


def test_fetch_unknown_destination_returns_all():
    results = fetch_travelplanner({"destination": "Mars"})
    assert len(results) >= 5


def test_enricher_adds_cost_and_scores():
    destinations = fetch_travelplanner({})
    enriched = enrich_travelplanner(destinations, {"budget_usd": "3000", "duration_days": "5"})
    for e in enriched:
        assert "total_estimated_cost_usd" in e
        assert "value_score" in e
        assert "rating" in e
        assert 0.0 <= e["value_score"] <= 1.0


def test_enricher_no_budget_uses_relative_scoring():
    destinations = fetch_travelplanner({})
    enriched = enrich_travelplanner(destinations, {})
    for e in enriched:
        assert "value_score" in e
        assert e["value_score"] >= 0.0


def test_ranking_travelplanner_sorted():
    state = DecisionState(
        input="beach trip budget 2000",
        domain="travelplanner",
        intent="plan_trip",
        entities={"travel_style": "beach", "budget_usd": "2000", "duration_days": "5"},
    )
    fetch_result = candidate_fetch_node(state)
    state = DecisionState(**{**state.model_dump(), **fetch_result})
    enrich_result = enrichment_node(state)
    state = DecisionState(**{**state.model_dump(), **enrich_result})
    rank_result = ranking_node(state)
    ranked = rank_result["ranked"]
    assert len(ranked) > 0
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_ranking_travelplanner_max_results():
    state = DecisionState(input="trip", domain="travelplanner", intent="find_destinations", entities={})
    fetch_result = candidate_fetch_node(state)
    state = DecisionState(**{**state.model_dump(), **fetch_result})
    enrich_result = enrichment_node(state)
    state = DecisionState(**{**state.model_dump(), **enrich_result})
    rank_result = ranking_node(state)
    cfg = load_domain_config("travelplanner")
    max_r = cfg.get("response", {}).get("max_results", 5)
    assert len(rank_result["ranked"]) <= max_r
