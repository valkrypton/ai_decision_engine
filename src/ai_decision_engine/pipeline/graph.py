from langgraph.graph import StateGraph, END
from langgraph.pregel import RetryPolicy
from ai_decision_engine.state import DecisionState, PipelineInput, PipelineOutput
from ai_decision_engine.pipeline.nodes.input_understanding import input_understanding_node
from ai_decision_engine.pipeline.nodes.response_generation import response_generation_node
from ai_decision_engine.pipeline.domain_graph import build_domain_subgraph

_LLM_RETRY = RetryPolicy(max_attempts=3, backoff_factor=2.0)


def _route_after_understanding(state: DecisionState) -> str:
    if not state.intent:
        return "response_generation"
    return "domain_processing"


def build_graph():
    graph = StateGraph(DecisionState, input=PipelineInput, output=PipelineOutput)

    graph.add_node("input_understanding", input_understanding_node, retry=_LLM_RETRY)
    graph.add_node("domain_processing", build_domain_subgraph())
    graph.add_node("response_generation", response_generation_node, retry=_LLM_RETRY)

    graph.set_entry_point("input_understanding")
    graph.add_conditional_edges(
        "input_understanding",
        _route_after_understanding,
        {"domain_processing": "domain_processing", "response_generation": "response_generation"},
    )
    graph.add_edge("domain_processing", "response_generation")
    graph.add_edge("response_generation", END)

    return graph.compile()


pipeline = build_graph()
