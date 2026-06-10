import pytest
from unittest.mock import MagicMock
from ai_decision_engine.observability import timed_node, _result_summary
from ai_decision_engine.state import DecisionState


def test_timed_node_returns_result():
    @timed_node("test_node")
    def my_node(state):
        return {"output": "hello"}

    state = DecisionState(input="test", domain="carddeals")
    result = my_node(state)
    assert result == {"output": "hello"}


def test_timed_node_propagates_exception():
    @timed_node("failing_node")
    def bad_node(state):
        raise ValueError("intentional failure")

    state = DecisionState(input="test", domain="carddeals")
    with pytest.raises(ValueError, match="intentional failure"):
        bad_node(state)


def test_result_summary_empty():
    assert _result_summary("node", {}) == "empty"


def test_result_summary_list():
    summary = _result_summary("node", {"ranked": [1, 2, 3]})
    assert "ranked=3 items" in summary


def test_result_summary_long_string():
    long = "x" * 100
    summary = _result_summary("node", {"final_response": long})
    assert "..." in summary


def test_result_summary_short_value():
    summary = _result_summary("node", {"intent": "find_deal"})
    assert "find_deal" in summary
