from __future__ import annotations

from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def needs_feedback(state: GrossState) -> bool:
    """
    Determine whether extraction produced unresolved readiness gaps.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if readiness.any_open is True.
    """
    logger.info("[NEEDS FEEDBACK?] Determining if extraction needs feedback...")
    readiness = state.get("readiness", {})
    return bool(readiness.get("any_open", False))


def max_iterations_reached(state: GrossState) -> bool:
    """
    Determine whether the extraction feedback loop has reached its limit.

    The workflow allows feedback loops only up to the configured maximum,
    typically 3 iterations.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if iteration >= max_iterations.
    """
    logger.info(
        "[MAX ITERATIONS REACHED?] Checking if extraction has reached its limit..."
    )
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)
    return iteration >= max_iterations


def can_generate(state: GrossState) -> bool:
    """
    Determine whether generation is allowed to start.

    Generation is allowed only when:
    - extraction does not require feedback
    - a truth_pack exists

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if generation can proceed.
    """
    logger.info("[CAN GENERATE?] Determining if generation is allowed to start...")
    return (not needs_feedback(state)) and bool(state.get("truth_pack"))


def route_after_extraction(state: GrossState) -> str:
    """
    Decide what the main graph should do after extraction.

    Routing:
    - "generation" if extraction is READY
    - "await_user" if extraction is OPEN and iterations remain
    - "terminate" if extraction is OPEN and max iterations reached

    This matches the outer orchestration shown in the workflow:
    extraction either loops through feedback or passes to generation,
    and must terminate when insufficient data remains after max retries.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        str: Next node label.
    """
    logger.info("[DECIDING ACTION POST EXTRACTION]")
    if can_generate(state):
        return "generation"

    if needs_feedback(state) and max_iterations_reached(state):
        return "terminate"

    if needs_feedback(state):
        return "await_user"

    return "terminate"
