from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
Finalise Set C development effort estimates.
 
Rules:
- Use Set B and verification.
- Apply audit corrections if needed.
- Return JSON only.
"""


def finalize_setc(state: GrossState) -> GrossState:
    """
    Produce final Set C development effort groupings.

    This node represents the "Final Judgment" / final Set C step.

    Expected output shape:
    {
      "effort_final": [
        {
          "worktype": "...",
          "complexity": "s/m/c",
          "count": 1,
          "description": "...",
          "notes": "..."
        }
      ]
    }

    Writes:
        - state["effort_final"]
        - state["phase"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Set B:
{state.get("set_b", [])}
 
Verification:
{state.get("verification", {})}
 
Return JSON:
{{
  "effort_final": [
    {{
      "worktype": "...",
      "complexity": "s/m/c",
      "count": 1,
      "description": "...",
      "notes": "..."
    }}
  ]
}}
"""
    logger.info("[FINALIZE SETC] Producing final development effort estimates...")
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)

    state["effort_final"] = result.get("effort_final", [])
    state["phase"] = "DONE"

    add_event(state, "finalize_setc", "Final Set C produced.")
    return state
