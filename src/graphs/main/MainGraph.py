from __future__ import annotations

from langgraph.graph import END, StateGraph

from graphs.extraction.ExtractGraph import build_extraction_subgraph
from graphs.generation.GenGraph import build_generation_subgraph
from graphs.main.MainRouting import route_after_extraction
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

_extraction_graph = build_extraction_subgraph()
_generation_graph = build_generation_subgraph()


def run_extraction(state: GrossState) -> GrossState:
    """
    Execute the extraction subgraph.

    Extraction is responsible for:
    - building structured requirement data
    - identifying unknowns
    - assessing readiness
    - generating feedback questions if needed

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated state returned by extraction.
    """
    logger.info("========== EXTRACTION START ==========")
    state["phase"] = "EXTRACTION"
    return _extraction_graph.invoke(state)


def run_generation(state: GrossState) -> GrossState:
    """
    Execute the generation subgraph.

    Generation is responsible for:
    - selecting the in-scope extracted slice
    - producing Set A / Set B / verification / final Set C

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated state returned by generation.
    """
    logger.info("========== GENERATION START ==========")
    state["phase"] = "GENERATION"
    state.setdefault("verification_attempts", 0)
    state.setdefault("max_verification_attempts", 2)

    return _generation_graph.invoke(state)


def await_user(state: GrossState) -> GrossState:
    """
    Mark the workflow as waiting for user clarification.

    This branch is reached when extraction readiness is OPEN but the
    maximum feedback iteration count has not yet been reached.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated state marked as awaiting user.
    """
    logger.info("========== AWAITING USER INPUT ==========")
    state["phase"] = "AWAITING_USER"
    state.setdefault("events", []).append(
        {
            "node": "await_user",
            "message": "Workflow paused for user clarification.",
        }
    )
    return state


def terminate_insufficient_data(state: GrossState) -> GrossState:
    """
    Terminate the workflow due to insufficient requirement data.

    This is reached when readiness remains OPEN after the maximum allowed
    extraction feedback iterations.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated state marked as terminated.
    """
    logger.info("========== TERMINATING THE WORKFLOW ==========")
    state["phase"] = "TERMINATED_INSUFFICIENT_DATA"
    state.setdefault("events", []).append(
        {
            "node": "terminate_insufficient_data",
            "message": "Maximum feedback iterations reached with unresolved readiness gaps.",
        }
    )
    return state


def build_main_graph(checkpointer=None):
    """
    Build the top-level GROSS workflow graph.

    Main graph responsibility:
    - Run extraction first
    - Route to user feedback if extraction is OPEN
    - Route to generation if extraction is READY
    - Terminate if extraction remains OPEN after max iterations

    Args:
        checkpointer: Optional LangGraph checkpointer.
            - Use None in tests.
            - Use a real saver in CLI / local runs.

    Returns:
        Compiled graph ready for invocation.
    """
    g = StateGraph(GrossState)

    g.add_node("extraction", run_extraction)
    g.add_node("await_user", await_user)
    g.add_node("generation", run_generation)
    g.add_node("terminate", terminate_insufficient_data)

    g.set_entry_point("extraction")

    g.add_conditional_edges(
        "extraction",
        route_after_extraction,
        {
            "await_user": "await_user",
            "generation": "generation",
            "terminate": "terminate",
        },
    )

    g.add_edge("await_user", END)
    g.add_edge("generation", END)
    g.add_edge("terminate", END)

    return g.compile(checkpointer=checkpointer)
