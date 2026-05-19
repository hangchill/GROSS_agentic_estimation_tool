"""
Functions in this file define routing conditions, allowing the graph to decide:
- Do I need to stop the pipeline and ask the user for more info?
- Can I proceed to the next step aka Generation?
"""

from src.schemas.state import GrossState


def needs_feedback(state: GrossState) -> dict:
    """
    Determines whether the workflow needs user feedback before proceeding

    This function inspects the extraction readiness results (Big-3 readiness check) stored
    in the state and returns True if there are unresolved issues

    A workflow requires feedback when:
    - At least one FCU has missing membership ,implementation detail, or state (current vs to-be)
    - There are unknowns that block accurate downstream processing
    - readiness["any_open"] is True

    Args:
        state (GrossState): The current graph state

    Returns:
        bool:
            True -> extraction is incomplete, user input required
            False -> extraciton is sufficiently complete to proceed
    """
    readiness = state.get("readiness") or {}
    return bool(
        readiness.get("any_open", False)
    )  # since convention for readiness["any_open"] is boolean


def can_generate(state: GrossState) -> bool:
    """
    Determine whether the workflow can proceed to the generation phase

    This function ensures that:
    1. all extraciton readiness issues have been resolved
    2. a valid "truth_pack" (Requirements Data) has been produced

    Generation can only occur when:
    - no feedback is required (rediness is fully closed)
    - structured requirement data exists in the state

    Args:
        state (GrossState): The current graph state

    Returns:
        bool:
            True -> safe to proceed to generation
            False -> must resolve extraction issues first
    """
    return not needs_feedback(state) and bool(state.get("truth_pack"))
