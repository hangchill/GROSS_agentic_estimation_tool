from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.memory.mem0_client import (
    search_historical_cr,
)
from src.memory.utils import mem_results_to_text
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
Verify Set B effort groupings.

Reference these historical patterns:

{memory_text}
 
Check:
- description correctness
- count
- worktype
- complexity
- non-invention

Rules:
- Check if expected components are missing
- Detect unusual or incomplete estimates
- Do NOT copy from memory
- Use memory only for sanity checking
 
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

    func_desc = (
        (state.get("inputs", {}) or {}).get("functionality_description", "").strip()
    )

    if func_desc:
        mem = search_historical_cr(func_desc, 3)
        memory_text = mem_results_to_text(mem)
    else:
        memory_text = ""

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
    populated_system_prompt = SYSTEM_PROMPT.format(memory_text=memory_text)

    logger.info(
        "[VERIFY COVE] Verifying if Set B is consistent with truth pack and generation rules..."
    )
    result = LLMClient().json_call(populated_system_prompt, user_prompt)
    state["verification"] = result

    add_event(state, "verify_cove", "Verification completed.")
    return state
