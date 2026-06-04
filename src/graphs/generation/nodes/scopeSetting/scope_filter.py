from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Number 1 : For ONE row in CRA, Identify the respective CORRECT functionality in truth pack to use as basis of generation later
 # NOTE : User preference is from the users feedback from ambiguity_resolver.py aand also user_satisfaction in the post generation phase...  

SYSTEM_PROMPT = """
You are selecting the relevant extracted requirements for effort estimation.
 
You are provided with: 
1. Truth pack 
2. User preference (could be empty) 

Rules:
- Use only the truth_pack and user preference (if available) 
- Always keep in mind the project description as the authoritative guide for evaluation of relevance of the selectd information. 
- Always try to select a subset of the truth_pack that is most relevant to the functionality description provided, rather than selecting everything. The goal is to narrow down to the most pertinent information for estimation.
- Do not invent new requirements.
- Return JSON only.

Steps: 
- First identify the specific functionality present in the truth_pack for a DM that best matches the provided functionality description
- Then select the FCUs required to produce the functionality description as closely as specified provided, in order to produce the service.   
- Return the 
"""


def scope_filter(state: GrossState) -> GrossState:
    """
    Select in-scope extracted requirement data for generation.

    This node represents the "Scope Filter" step of the generation layer.

    It narrows the extracted truth pack down to the specific functionality slice
    being estimated, rather than letting downstream generation reason over the
    entire extracted dataset.

    Expected output shape:
    {
      "selected_fcus": ["FCU1"],
      "selected_artefacts": [],
      "selected_interfaces": [],
      "selected_variant_axes": [],
      "selected_backend_capabilities": [],
      "scope_notes": []
    }

    Writes:
        - state["generation_scope"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""

Project Description: Get from the CRA excel (tab)
{state.get("inputs", {}).get("project_description", "")}

Service: Get from the CRA excel (rowwise)
{state.get("inputs", {}).get("service", "")}

Functionality Description: Get from CRA excel (rowwise)
{state.get("inputs", {}).get("functionality_description", "")}
 
Truth Pack:
{state.get("truth_pack", {})}

User Preference: 
{state.get("user_preference")}
 
Return JSON:
{{
  "selected_fcus": ["FCU1"],
  "selected_artefacts": [],
  "selected_interfaces": [],
  "selected_variant_axes": [],
  "selected_backend_capabilities": [],
  "scope_notes": []
}}
"""
    logger.info(
        "[SCOPE FILTER] Selecting in-scope extracted data for the requested functionality..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state["generation_scope"] = result

    add_event(state, "scope_filter", "Generation scope selected.")
    return state
