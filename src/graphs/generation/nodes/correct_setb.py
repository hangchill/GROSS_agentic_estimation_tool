from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
Correct Set A into Set B.
 
Apply:
- prevent over-decomposition
- fix frontend vs backend count normalization
- avoid inflating complexity instead of count
- keep descriptions capability-level
 
Return JSON only.
"""


def correct_setb(state: GrossState) -> GrossState:
    """
    Apply correction rules to produce Set B.

    This node represents the "CCoT Correction" / Set B step.

    It also increments verification_attempts so the generation verification loop
    cannot run forever.

    Expected output shape:
    {
      "set_b": [
        {
          "worktype": "...",
          "complexity": "s/m/c",
          "count": 1,
          "description": "...",
          "correction_note": "..."
        }
      ]
    }

    Writes:
        - state["set_b"]
        - state["verification_attempts"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Set A:
{state.get("set_a", [])}
 
Existing Set B:
{state.get("set_b", [])}
 
Generation Scope:
{state.get("generation_scope", {})}
 
Return JSON:
{{
  "set_b": [
    {{
      "worktype": "...",
      "complexity": "s/m/c",
      "count": 1,
      "description": "...",
      "correction_note": "..."
    }}
  ]
}}
"""
    logger.info("[CORRECT SETB] Applying correction logic...")
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state["set_b"] = result.get("set_b", [])

    state["verification_attempts"] = state.get("verification_attempts", 0) + 1

    add_event(state, "correct_setb", "Set B correction completed.")
    return state
