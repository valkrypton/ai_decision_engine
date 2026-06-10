import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from ai_decision_engine.api.app import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "carddeals" in data["domains"]


def _mock_pipeline_response():
    return {
        "input": "sushi downtown",
        "domain": "carddeals",
        "intent": "find_deal",
        "entities": {"location": "downtown", "cuisine": "sushi"},
        "candidates": [{"name": "Sakura"}],
        "enriched": [{"name": "Sakura", "discount_value": 0.25}],
        "ranked": [{"name": "Sakura", "score": 0.9}],
        "final_response": "Sakura Sushi offers the best deal.",
        "error": "",
    }


def test_query_carddeals(client):
    with patch("ai_decision_engine.api.app.app.state") as mock_state:
        mock_state.pipeline = MagicMock()
        mock_state.pipeline.invoke.return_value = _mock_pipeline_response()
        resp = client.post("/query", json={"domain": "carddeals", "input": "sushi downtown"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["domain"] == "carddeals"
    assert data["intent"] == "find_deal"
    assert "final_response" in data
    assert data["latency_seconds"] >= 0


def test_query_invalid_domain(client):
    resp = client.post("/query", json={"domain": "fakething", "input": "hello"})
    assert resp.status_code == 400


def test_query_audio_without_path(client):
    resp = client.post("/query", json={"domain": "carddeals", "input": "test", "modality": "audio"})
    assert resp.status_code == 400


def test_query_auto_domain_detection(client):
    with patch("ai_decision_engine.api.app.detect_domain", return_value="carddeals"):
        with patch("ai_decision_engine.api.app.app.state") as mock_state:
            mock_state.pipeline = MagicMock()
            mock_state.pipeline.invoke.return_value = _mock_pipeline_response()
            resp = client.post("/query", json={"domain": "auto", "input": "find me sushi deals"})
    assert resp.status_code == 200
    assert resp.json()["domain"] == "carddeals"
