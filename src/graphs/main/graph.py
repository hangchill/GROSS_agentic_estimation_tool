from langgraph.graph import END, START, StateGraph

from src.graphs.checkpoints import make_checkpointer
from src.graphs.extraction.graph import build_extraction_subgraph
from src.graphs.generation.graph import build_generation_subgraph
from src.graphs.main.routing import needs_feedback
from src.schemas.state import GrossState

_extraction = build_extraction_subgraph()
_generation = build_generation_subgraph()


def run_extraction(state: GrossState) -> GrossState:
    state["phase"] = "EXTRACTION"
    return _extraction.invoke(state)


def run_generation(state: GrossState) -> GrossState:
    state["phase"] = "GENERATION"
    return _generation.invoke(state)


def mark_awaiting_user_input(state: GrossState) -> GrossState:
    state["phase"] = "AWAITING_USER_INPUT"
    return state


def build_main_graph(checkpoint_db: str = ".checkpoints/langgraph.sqlite3"):
    graph = StateGraph(GrossState)

    graph.add_node("extraction", run_extraction)
    graph.add_node("await_user_input", mark_awaiting_user_input)
    graph.add_node("generation", run_generation)

    graph.add_edge(START, "extraction")
    graph.add_conditional_edges(
        "extraction",
        lambda s: "await_user_input" if needs_feedback(s) else "generation",
        {"await_user_input": "await_user_input", "generation": "generation"},
    )
    graph.add_edge("await_user_input", END)
    graph.add_edge("generation", END)

    checkpointer = make_checkpointer(checkpoint_db)
    return graph.compile(checkpointer=checkpointer)
