from langgraph.graph import END, START, StateGraph

from src.graphs.generation.nodes.finalize_setc import finalize_setc
from src.graphs.generation.nodes.groupings_seta import groupings_seta
from src.graphs.generation.nodes.scope_filter import scope_filter
from src.schemas.state import GrossState


def build_generation_subgraph() -> StateGraph:
    generation_graph = StateGraph(GrossState)

    generation_graph.add_node("scope_filter", scope_filter)
    generation_graph.add_node("groupings_seta", groupings_seta)
    generation_graph.add_node("finalize_setc", finalize_setc)

    generation_graph.add_edge(START, "scope_filter")
    generation_graph.add_edge("scope_filter", "groupings_seta")
    generation_graph.add_edge("groupings_seta", "finalize_setc")
    generation_graph.add_edge("finalize_setc", END)

    return generation_graph.compile()
