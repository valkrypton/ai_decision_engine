import pytest
from unittest.mock import patch, MagicMock
from ai_decision_engine.state import DecisionState
from ai_decision_engine.config import load_domain_config
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node
from ai_decision_engine.domains.carddeals.fetcher import fetch_carddeals
from ai_decision_engine.domains.carddeals.enricher import enrich_carddeals


# ── Config ──────────────────────────────────────────────────────────────────

def test_carddeals_config_loads():
    cfg = load_domain_config("carddeals")
    assert cfg["domain"] == "carddeals"
    assert "intents" in cfg
    assert "ranking" in cfg
    assert "weights" in cfg["ranking"]


def test_missing_domain_raises():
    with pytest.raises(FileNotFoundError):
        load_domain_config("nonexistent_domain")


# ── Fetcher ──────────────────────────────────────────────────────────────────

def test_fetch_no_filter_returns_all():
    results = fetch_carddeals({})
    assert len(results) > 0


def test_fetch_by_location():
    results = fetch_carddeals({"location": "downtown"})
    for r in results:
        assert "downtown" in r["location"].lower()


def test_fetch_by_cuisine():
    results = fetch_carddeals({"cuisine": "japanese"})
    for r in results:
        assert "japanese" in r["cuisine"].lower()


def test_fetch_by_card_type():
    results = fetch_carddeals({"card_type": "visa"})
    for r in results:
        assert any("visa" in d["card_type"].lower() for d in r["deals"])


def test_fetch_unknown_location_returns_empty():
    results = fetch_carddeals({"location": "mars"})
    assert results == []


# ── Enricher ─────────────────────────────────────────────────────────────────

def test_enrichment_adds_discount_value():
    candidates = fetch_carddeals({})
    enriched = enrich_carddeals(candidates, {})
    for e in enriched:
        assert "discount_value" in e
        assert 0 <= e["discount_value"] <= 1


def test_enrichment_budget_filter():
    candidates = fetch_carddeals({})
    enriched = enrich_carddeals(candidates, {"budget": "$10"})
    for e in enriched:
        assert "within_budget" in e


# ── Ranking ───────────────────────────────────────────────────────────────────

def test_ranking_returns_sorted_by_score():
    state = DecisionState(input="sushi downtown", domain="carddeals")
    state = DecisionState(**{**state.model_dump(), "candidates": fetch_carddeals({})})
    state = DecisionState(**{**state.model_dump(), "enriched": enrich_carddeals(state.candidates, {})})
    result = ranking_node(state)
    ranked = result["ranked"]
    assert len(ranked) > 0
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_ranking_respects_max_results():
    state = DecisionState(input="test", domain="carddeals")
    state = DecisionState(**{**state.model_dump(), "candidates": fetch_carddeals({})})
    state = DecisionState(**{**state.model_dump(), "enriched": enrich_carddeals(state.candidates, {})})
    result = ranking_node(state)
    cfg = load_domain_config("carddeals")
    max_results = cfg.get("response", {}).get("max_results", 5)
    assert len(result["ranked"]) <= max_results


def test_ranking_empty_enriched():
    state = DecisionState(input="test", domain="carddeals", enriched=[])
    result = ranking_node(state)
    assert result["ranked"] == []


# ── Node integration (non-LLM) ────────────────────────────────────────────────

def test_candidate_fetch_node_carddeals():
    state = DecisionState(
        input="sushi downtown",
        domain="carddeals",
        intent="find_deal",
        entities={"location": "downtown", "cuisine": "japanese"},
    )
    result = candidate_fetch_node(state)
    assert "candidates" in result
    assert len(result["candidates"]) > 0


def test_enrichment_node_carddeals():
    state = DecisionState(
        input="sushi downtown",
        domain="carddeals",
        intent="find_deal",
        entities={"location": "downtown"},
        candidates=fetch_carddeals({"location": "downtown"}),
    )
    result = enrichment_node(state)
    assert "enriched" in result
    for e in result["enriched"]:
        assert "discount_value" in e


# ── Input understanding (mocked) ───────────────────────────────────────────────

def test_input_understanding_node_mocked():
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = '{"intent": "find_deal", "entities": {"location": "downtown", "cuisine": "sushi"}}'

    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("ai_decision_engine.pipeline.nodes.input_understanding._client") as mock_client:
        mock_client.messages.create.return_value = mock_response
        from ai_decision_engine.pipeline.nodes.input_understanding import input_understanding_node
        state = DecisionState(input="sushi downtown under $30", domain="carddeals")
        result = input_understanding_node(state)

    assert result["intent"] == "find_deal"
    assert result["entities"]["location"] == "downtown"


# ── Response generation (mocked) ───────────────────────────────────────────────

def test_response_generation_node_empty_ranked():
    from ai_decision_engine.pipeline.nodes.response_generation import response_generation_node
    state = DecisionState(input="test", domain="carddeals", ranked=[])
    result = response_generation_node(state)
    assert "final_response" in result
    assert "No results" in result["final_response"]
