from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.memory.mem0_client import (
    search_team_context,
)
from src.memory.utils import mem_results_to_text
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 1 : ID functionality, FCUs under a DM  & the description of each
### Identify high level points for a DM
### DOES THE VISUAL VLM ANALYSIS of the inputs ingested. 

SYSTEM_PROMPT = """
You are a Senior Product Analyst and Systems Architect.
 
Task:
Extract high-level structure and scope for each DM present in a set of CR requirement slides. 

Context: 
For each slide in the deck, you are provided with: 
1. Raw markdown text, 
2. an image of the whole slide (which may contain diagrams, tables, or other visual information that is not fully captured in the markdown text)
3. Any Cropped images present in the slide, for a more detailed view of certain sections in the slide. (Mostly to capture the description/explanation of requirements since the whole slide image is reduced in pixel size and so details may not be legible). 
 
Follow naming conventions: 
{memory_text}

Rules:
- Group functionalities and FCUs (Feature Control Units) by the DM (Demand Module) they belong to.
- Do not invent functionality.
- Use only the provided slide text.
- Identify functionalities and FCUs in first-seen order in the slides. 
- Once a Functionality or FCU is identified,
    - Produce a summary or description that captures its essence and purpose.
    - Allocate a unique ID (e.g. F1, F2 for functionalities, FCU1, FCU2 for FCUs). 
- FCUs should represent distinct feature or capability requirements that can be estimated separately, in order to produce the functionalilty
- An FCU identified needs to be mapped to a identified functionality that it supports.  
- Preserve slide references.
- Return JSON only.
"""


def structure_scope(state: GrossState) -> GrossState:
    """
    Extract DM, functionality, and FCU structure from slide text.

    This node represents the "Structure & Scope" step of extraction.

    Expected output shape:
    {
      "target_dm": "...",
      "functionalities": [
        {
          "fid": "F1",
          "name": "...",
          "summary": "...",
          "slide_refs": ["S1"]
        }
      ],
      "fcu_registry": [
        {
          "fcu_id": "FCU1",
          "fcu_name": "...",
          "feature_outlined": "...",
          "slide_refs": ["S1"],
          "fid_membership": "F1"
        }
      ],
      "unknowns": []
    }

    Writes:
        - state["truth_pack"]["structure_scope"]
        - state["fcu_registry"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    logger.info("[STRUCTURE SCOPE] Identifying target DM, functionalities and FCU...")
    inputs = state.get("inputs", {})
    deck_text = slides_to_text(state)

    user_prompt = f"""
Target DM:
{inputs.get("target_dm")}
 
Project Description:
{inputs.get("project_description", "")}
 
Functionality Description:
{inputs.get("functionality_description", "")}
 
Slides:
{deck_text}
 
Return JSON:
{{
  "target_dm": "...",
  "functionalities": [
    {{
      "fid": "F1",
      "name": "...",
      "summary": "...",
      "slide_refs": ["S1"]
    }}
  ],
  "fcu_registry": [
    {{
      "fcu_id": "FCU1",
      "fcu_name": "...",
      "feature_outlined": "...",
      "slide_refs": ["S1"],
      "fid_membership": "F1"
    }}
  ],
  "unknowns": []
}}
"""
    mem = search_team_context("terminology naming convention FCU System naming", 3)

    memory_text = mem_results_to_text(mem)

    populated_system_prompt = SYSTEM_PROMPT.format(memory_text=memory_text)

    result = LLMClient().json_call(populated_system_prompt, user_prompt)

    truth_pack = state.setdefault("truth_pack", {})
    truth_pack["structure_scope"] = result
    state["fcu_registry"] = result.get("fcu_registry", [])

    add_event(state, "structure_scope", "Structure and FCU registry extracted.")
    return state
