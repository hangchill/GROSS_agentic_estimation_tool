from __future__ import annotations

from src.schemas.state import GrossState


def verification_failed(state: GrossState) -> bool:
    """
    Determine whether verification failed.

    Verification is considered failed when:
    - state["verification"]["overall_status"] == "FAIL"

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if verification failed.
    """
    verification = state.get("verification", {})
    return verification.get("overall_status") == "FAIL"


def max_verification_attempts_reached(state: GrossState) -> bool:
    """
    Prevent infinite correction loops in generation.

    The generation workflow may loop between correction and verification,
    but it should not do so forever. This helper uses:
    - state["verification_attempts"]
    - state["max_verification_attempts"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        bool: True if verification attempts have reached the configured maximum.
    """
    attempts = state.get("verification_attempts", 0)
    max_attempts = state.get("max_verification_attempts", 2)
    return attempts >= max_attempts


def route_after_verification(state: GrossState) -> str:
    """
    Decide what generation should do after CoVE verification.

    Routing:
    - "correct_setb" if verification failed and retries remain
    - "finalize_setc" otherwise

    This matches the intended generation control flow:
    failed verification should trigger correction/regeneration, while
    passing verification proceeds to final output. 【1-ef413e】【1-916c23】

    Args:
        state (GrossState): Current workflow state.

    Returns:
        str: Next node label.
    """
    if verification_failed(state) and not max_verification_attempts_reached(state):
        return "correct_setb"

    return "finalize_setc"
