from __future__ import annotations

from src.graphs.node_utils import add_error, add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger
from graphs.extraction.nodes.ingestionDocumentsNodes.ingestPPTX import parse_text_from_pptx, render_pptx_slides_to_images, extract_and_attach_full_images, extract_and_append_flowchart_elements_with_docling
import os

logger = get_logger(__name__)

# Number 0 : Before Structure and scope 
 # Get the inputs 

def ingest_inputs(state: GrossState) -> GrossState:
    """
    Validate and initialise runtime inputs for extraction.
    Input processing (ready for LLM access later) 

    This is the first node in the extraction workflow. It:
    - marks the workflow phase as EXTRACTION
    - ensures required input fields exist
    - Inputs: CR slides ingested by ingestPPTX.py into memory. 
    - initializes loop counters if absent

    Required inputs for this PoC:
    - CR Excel filepath
    - slides filepath

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

    required = ["CR_rows", "slides_path"]
    missing = [field for field in required if field not in inputs]

    if missing:
        add_error(state, "ingest_inputs", f"Missing required input fields: {missing}")

    add_event(state, "ingest_inputs", "Extraction Phase Started: Inputs validated, ingested.")
    

    slides_path = inputs['slides_path']
    
    # creates the list of dicts to save in state 
    slides_data = parse_text_from_pptx(slides_path)  
    
    # attach image paths into the slides_data dict. 
    extract_and_attach_full_images(slides_data, slides_path,  "C:\NUS WORK\Y3S2\Synapxe\gross-estimation-project\images"+os.datetime()) 
    
    
    extract_and_append_flowchart_elements_with_docling(slides_data)

    # Saving into state
    for index in range(len(slides_data)): 
        state["inputs_parsed"][index] = slides_data[index] 

    return state


### Run Ingest_PPTX pipeline nodes 
# 1. parse_text_from_pptx()  ; llm call 


# 2. render_full_slide_images() 



# 3. extract_visual_elements_with_docling()


# 4. analyze_slide_visuals_with_local_vlm  : dont need this since nodes are doing this
#   - using multimodal model 