import pytest
from unittest.mock import patch, MagicMock
from ai_decision_engine.pipeline.router import REGISTERED_DOMAINS, detect_domain


def test_registered_domains_contains_all():
    for domain in ["carddeals", "hirestream", "leadfinder", "travelplanner"]:
        assert domain in REGISTERED_DOMAINS


def _make_mock_response(domain: str, confidence: float = 0.9):
    block = MagicMock()
    block.type = "text"
    block.text = f'{{"domain": "{domain}", "confidence": {confidence}}}'
    resp = MagicMock()
    resp.content = [block]
    return resp


def test_detect_domain_carddeals():
    with patch("ai_decision_engine.pipeline.router._client") as mock_client:
        mock_client.messages.create.return_value = _make_mock_response("carddeals")
        result = detect_domain("find me sushi deals with visa card")
    assert result == "carddeals"


def test_detect_domain_hirestream():
    with patch("ai_decision_engine.pipeline.router._client") as mock_client:
        mock_client.messages.create.return_value = _make_mock_response("hirestream")
        result = detect_domain("find python engineers in san francisco")
    assert result == "hirestream"


def test_detect_domain_leadfinder():
    with patch("ai_decision_engine.pipeline.router._client") as mock_client:
        mock_client.messages.create.return_value = _make_mock_response("leadfinder")
        result = detect_domain("find saas companies for outreach")
    assert result == "leadfinder"


def test_detect_domain_travelplanner():
    with patch("ai_decision_engine.pipeline.router._client") as mock_client:
        mock_client.messages.create.return_value = _make_mock_response("travelplanner")
        result = detect_domain("plan a beach vacation under 2000 dollars")
    assert result == "travelplanner"


def test_detect_domain_unknown_falls_back_to_first():
    with patch("ai_decision_engine.pipeline.router._client") as mock_client:
        mock_client.messages.create.return_value = _make_mock_response("unknown_domain", 0.3)
        result = detect_domain("something random")
    assert result == REGISTERED_DOMAINS[0]
