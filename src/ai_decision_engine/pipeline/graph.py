from langgraph.graph import StateGraph, END
from ai_decision_engine.state import DecisionState
from ai_decision_engine.pipeline.nodes.input_understanding import input_understanding_node
from ai_decision_engine.pipeline.nodes.candidate_fetch import candidate_fetch_node
from ai_decision_engine.pipeline.nodes.enrichment import enrichment_node
from ai_decision_engine.pipeline.nodes.ranking import ranking_node
from ai_decision_engine.pipeline.nodes.response_generation import response_generation_node


def build_graph():
    graph = StateGraph(DecisionState)

    graph.add_node("input_understanding", input_understanding_node)
    graph.add_node("candidate_fetch", candidate_fetch_node)
    graph.add_node("enrichment", enrichment_node)
    graph.add_node("ranking", ranking_node)
    graph.add_node("response_generation", response_generation_node)

    graph.set_entry_point("input_understanding")
    graph.add_edge("input_understanding", "candidate_fetch")
    graph.add_edge("candidate_fetch", "enrichment")
    graph.add_edge("enrichment", "ranking")
    graph.add_edge("ranking", "response_generation")
    graph.add_edge("response_generation", END)

    return graph.compile()


pipeline = build_graph()
