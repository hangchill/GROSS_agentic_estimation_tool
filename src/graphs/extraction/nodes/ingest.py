from __future__ import annotations

from src.graphs.node_utils import add_error, add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def ingest_inputs(state: GrossState) -> GrossState:
    """
    Validate and initialise runtime inputs for extraction.

    This is the first node in the extraction workflow. It:
    - marks the workflow phase as EXTRACTION
    - ensures required input fields exist
    - initialises loop counters if absent

    Required inputs for this PoC:
    - target_dm
    - functionality_description
    - slides

    Reads:
        - state["inputs"]

    Writes:
        - state["phase"]
        - state["iteration"] if absent
        - state["max_iterations"] if absent
        - state["events"]
        - state["errors"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    logger.info("[INGEST INPUTS] Validating required fields and starting extraction...")
    state["phase"] = "EXTRACTION"
    state.setdefault("iteration", 1)
    state.setdefault("max_iterations", 3)

    inputs = state.setdefault("inputs", {})

    required = ["target_dm", "functionality_description", "slides"]
    missing = [field for field in required if field not in inputs]

    if missing:
        add_error(state, "ingest_inputs", f"Missing required input fields: {missing}")

    add_event(state, "ingest_inputs", "Inputs validated and extraction phase started.")
    return state
