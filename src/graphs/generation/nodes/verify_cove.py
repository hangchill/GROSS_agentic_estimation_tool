from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
Verify Set B effort groupings.
 
Check:
- description correctness
- count
- worktype
- complexity
- non-invention
 
Return JSON only.
"""


def verify_cove(state: GrossState) -> GrossState:
    """
    Run CoVE-style verification on Set B.

    This node represents the "CoVE Verification" step.

    Expected output shape:
    {
      "overall_status": "PASS",
      "audits": [
        {
          "grouping_index": 0,
          "status": "PASS",
          "issue": "",
          "required_correction": ""
        }
      ]
    }

    Writes:
        - state["verification"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Set B:
{state.get("set_b", [])}
 
Truth Pack:
{state.get("truth_pack", {})}
 
Generation Scope:
{state.get("generation_scope", {})}
 
Return JSON:
{{
  "overall_status": "PASS",
  "audits": [
    {{
      "grouping_index": 0,
      "status": "PASS",
      "issue": "",
      "required_correction": ""
    }}
  ]
}}
"""
    logger.info(
        "[VERIFY COVE] Verifying if Set B is consistent with truth pack and generation rules..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state["verification"] = result

    add_event(state, "verify_cove", "Verification completed.")
    return state
