from __future__ import annotations

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def readiness_big3(state: GrossState) -> GrossState:
    """
    Assess readiness based on fields that are unknowns.

    Writes:
        - state["readiness"]
    """
    logger.info(
        "[READINESS BIG3] Deciding if extracted requirement data is READY or OPEN..."
    )
    truth_pack = state.get("truth_pack", {})
    unknowns = truth_pack.get("unknowns", [])
    blocking_unknowns = [u for u in unknowns if u.get("blocks_generation", False)]

    any_open = bool(blocking_unknowns)

    state["readiness"] = {
        "any_open": any_open,
        "status": "OPEN" if any_open else "READY",
        "open_count": len(blocking_unknowns),
        "blocking_unknowns": blocking_unknowns,
    }

    add_event(
        state,
        "readiness_big3",
        f"Readiness assessed as {state['readiness']['status']}.",
    )
    return state
