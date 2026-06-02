from __future__ import annotations

from src.graphs.node_utils import add_error, add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger
from graphs.extraction.nodes.ingestionDocumentsNodes.ingestPPTX import parse_text_from_pptx, render_full_slide_images, extract_visual_elements_with_docling

logger = get_logger(__name__)

# Number 0 : Before Structure and scope

def ingest_inputs(state: GrossState) -> GrossState:
    """
    Validate and initialise runtime inputs for extraction.

    This is the first node in the extraction workflow. It:
    - marks the workflow phase as EXTRACTION
    - ensures required input fields exist
    - Inputs: CR slides ingested by ingestPPTX.py into memory. 
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

    required = ["target_dm", "functionality_description", "slides_path"]
    missing = [field for field in required if field not in inputs]

    if missing:
        add_error(state, "ingest_inputs", f"Missing required input fields: {missing}")

    add_event(state, "ingest_inputs", "Inputs validated and extraction phase started.")
    return state


### Run Ingest_PPTX pipeline nodes 
# 1. parse_text_from_pptx
# 2. render_full_slide_images
# 3. extract_visual_elements_with_docling
# 4. analyze_slide_visuals_with_local_vlm  : dont need this since nodes are doing this
