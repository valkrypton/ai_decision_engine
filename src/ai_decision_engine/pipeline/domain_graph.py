from langgraph.graph import StateGraph, END
from ai_decision_engine.state import DecisionState
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node


def build_domain_subgraph():
    subgraph = StateGraph(DecisionState)

    subgraph.add_node("fetch", candidate_fetch_node)
    subgraph.add_node("enrich", enrichment_node)
    subgraph.add_node("rank", ranking_node)

    subgraph.set_entry_point("fetch")
    subgraph.add_edge("fetch", "enrich")
    subgraph.add_edge("enrich", "rank")
    subgraph.add_edge("rank", END)

    return subgraph.compile()
