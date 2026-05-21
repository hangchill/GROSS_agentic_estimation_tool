from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
You are a Senior Product Analyst and Systems Architect.
 
Task:
Extract high-level structure and scope from CR requirement slide text.
 
Rules:
- Do not invent functionality.
- Use only the provided slide text.
- Identify functionalities and FCUs in first-seen order.
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

    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)

    truth_pack = state.setdefault("truth_pack", {})
    truth_pack["structure_scope"] = result
    state["fcu_registry"] = result.get("fcu_registry", [])

    add_event(state, "structure_scope", "Structure and FCU registry extracted.")
    return state
