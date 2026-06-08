import pytest
from ai_decision_engine.config import load_domain_config
from ai_decision_engine.domains.hirestream.fetcher import fetch_hirestream
from ai_decision_engine.domains.hirestream.enricher import enrich_hirestream
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node
from ai_decision_engine.state import DecisionState


def test_hirestream_config_loads():
    cfg = load_domain_config("hirestream")
    assert cfg["domain"] == "hirestream"
    assert "skill_match" in cfg["ranking"]["weights"]


def test_fetch_candidates_no_filter():
    results = fetch_hirestream("find_candidates", {})
    assert len(results) > 0
    assert all(r["type"] == "candidate" for r in results)


def test_fetch_jobs_intent():
    results = fetch_hirestream("find_jobs", {})
    assert len(results) > 0
    assert all(r["type"] == "job" for r in results)


def test_fetch_candidates_by_location():
    results = fetch_hirestream("find_candidates", {"location": "san francisco"})
    for r in results:
        assert "san francisco" in r["location"].lower() or r["location"] == "remote"


def test_fetch_candidates_by_role():
    results = fetch_hirestream("find_candidates", {"role": "machine learning"})
    assert len(results) > 0
    for r in results:
        assert "machine learning" in r["role"].lower() or any("python" in s for s in r["skills"])


def test_enricher_candidates_adds_skill_match():
    candidates = fetch_hirestream("find_candidates", {})
    enriched = enrich_hirestream(candidates, {"skills": "python, react"}, "find_candidates")
    for e in enriched:
        assert "skill_match" in e
        assert 0.0 <= e["skill_match"] <= 1.0
        assert "experience_fit" in e
        assert "location_match" in e


def test_enricher_jobs_adds_fit_scores():
    jobs = fetch_hirestream("find_jobs", {})
    enriched = enrich_hirestream(jobs, {"skills": "python, postgresql", "experience_years": "5"}, "find_jobs")
    for e in enriched:
        assert "skill_match" in e
        assert "experience_fit" in e


def test_ranking_hirestream_sorted():
    state = DecisionState(
        input="python engineer sf",
        domain="hirestream",
        intent="find_candidates",
        entities={"skills": "python", "location": "san francisco"},
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


def test_ranking_hirestream_max_results():
    state = DecisionState(input="any engineer", domain="hirestream", intent="find_candidates", entities={})
    fetch_result = candidate_fetch_node(state)
    state = DecisionState(**{**state.model_dump(), **fetch_result})
    enrich_result = enrichment_node(state)
    state = DecisionState(**{**state.model_dump(), **enrich_result})
    rank_result = ranking_node(state)
    cfg = load_domain_config("hirestream")
    max_r = cfg.get("response", {}).get("max_results", 5)
    assert len(rank_result["ranked"]) <= max_r
