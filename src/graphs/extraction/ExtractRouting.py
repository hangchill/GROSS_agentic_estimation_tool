from __future__ import annotations

from src.schemas.state import GrossState


def has_user_answers(state: GrossState) -> bool:
    """
    Determine whether the user has provided clarification answers.

    This is used after synthesis. If user answers exist, the extraction
    graph should route through `pfr_merge` so those answers can be applied
    to unresolved unknowns before readiness is reassessed.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if user_answers_raw exists and is non-empty.
    """
    raw = state.get("user_answers_raw")
    return bool(raw and raw.strip())


def needs_feedback(state: GrossState) -> bool:
    """
    Determine whether extraction readiness is still OPEN.

    Readiness is considered OPEN when unresolved blocking unknowns remain.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if readiness.any_open is True.
    """
    readiness = state.get("readiness", {})
    return bool(readiness.get("any_open", False))


def max_iterations_reached(state: GrossState) -> bool:
    """
    Determine whether the extraction feedback loop has reached its maximum.

    The workflow allows extraction feedback to loop only up to a configured
    maximum iteration count (typically 3).

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if iteration >= max_iterations.
    """
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)
    return iteration >= max_iterations


def route_after_synthesis(state: GrossState) -> str:
    """
    Decide whether to apply PFR merge after synthesis.

    Routing:
    - "pfr_merge" if user clarification answers exist
    - "readiness_big3" otherwise

    Args:
        state (GrossState): Current workflow state.

    Returns:
        str: Next node label.
    """
    return "pfr_merge" if has_user_answers(state) else "readiness_big3"


def route_after_readiness(state: GrossState) -> str:
    """
    Decide what extraction should do after readiness assessment.

    Routing:
    - "feedback_template" if readiness is OPEN and max iterations not reached
    - "end" if readiness is READY
    - "end" if readiness is still OPEN but max iterations has been reached

    Note:
        The outer main graph will decide later whether READY extraction
        proceeds to generation or whether max-iteration OPEN extraction
        terminates.

    Args:
        state (GrossState): Current workflow state.

    Returns:
        str: "feedback_template" or "end"
    """
    if not needs_feedback(state):
        return "end"

    if max_iterations_reached(state):
        return "end"

    return "feedback_template"
