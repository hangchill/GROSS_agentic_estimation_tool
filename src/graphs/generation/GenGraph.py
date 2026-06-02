from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.graphs.generation.nodes.correct_setb import correct_setb
from src.graphs.generation.nodes.finalize_setc import finalize_setc
from src.graphs.generation.nodes.groupings_seta import groupings_seta
from src.graphs.generation.nodes.impacts_backend import impacts_backend
from src.graphs.generation.nodes.impacts_interfaces import impacts_interfaces
from src.graphs.generation.nodes.impacts_ui import impacts_ui
from src.graphs.generation.nodes.scope_filter import scope_filter
from src.graphs.generation.nodes.verify_cove import verify_cove
from src.graphs.generation.routing import route_after_verification
from src.schemas.state import GrossState


def build_generation_subgraph():
    """
    Build the generation subgraph.

    Generation flow:
        scope_filter
        -> impacts_ui
        -> impacts_interfaces
        -> impacts_backend
        -> groupings_seta
        -> correct_setb
        -> verify_cove
        -> (conditional) correct_setb OR finalize_setc
        -> END

    Notes:
    - Set A is the initial draft of effort groupings.
    - correct_setb applies correction logic to produce Set B.
    - verify_cove performs PASS/FAIL verification.
    - FAIL routes back to correct_setb until retry limit is reached.
    - PASS routes to finalize_setc.
    """
    g = StateGraph(GrossState)

    # ---- generation nodes ----
    g.add_node("scope_filter", scope_filter)
    g.add_node("impacts_ui", impacts_ui)
    g.add_node("impacts_interfaces", impacts_interfaces)
    g.add_node("impacts_backend", impacts_backend)
    g.add_node("groupings_seta", groupings_seta)
    g.add_node("correct_setb", correct_setb)
    g.add_node("verify_cove", verify_cove)
    g.add_node("finalize_setc", finalize_setc)

    # ---- entry point ----
    g.set_entry_point("scope_filter")

    # ---- deterministic front half ----
    g.add_edge("scope_filter", "impacts_ui")
    g.add_edge("impacts_ui", "impacts_interfaces")
    g.add_edge("impacts_interfaces", "impacts_backend")
    g.add_edge("impacts_backend", "groupings_seta")
    g.add_edge("groupings_seta", "correct_setb")
    g.add_edge("correct_setb", "verify_cove")

    # ---- after verification: either correct again or finalize ----
    g.add_conditional_edges(
        "verify_cove",
        route_after_verification,
        {
            "correct_setb": "correct_setb",
            "finalize_setc": "finalize_setc",
        },
    )

    # ---- final output ----
    g.add_edge("finalize_setc", END)

    return g.compile()
