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

## Step 3 in setGeneration

## Number 9 in overall generation 

## After SetB obtained (Number )
# CoVE : 
  # 1. From Initial Response (ie Set B which is done already) 
  # 2. Analyse and generate list of specific questions to verify the factual claims 
#        i. Find the proof autonomously to support them 
#       Claims in each effort grouping: 
#      a.  "description": "..."
#      b.  "worktype": "..."
#      c. "complexity": "s/m/c"
#      d.  "count": 1
  
  # 3. Answer verification questions independently  
     
  #     What is available to this independent agent 
  #       i. "W/O relying on the previous context used" built up for the Set B Generation;
  #        ie.   
  #       ii. 

  # 4. Set C: Revision of SetB by removing inaccuracies and applying the newly verified facts
  #      to whichever grps in setB that failed CoVe questions. 


SYSTEM_PROMPT = """
Role: You are now a Expert Systems Architect.

You are provided with: 
1. Project Description
2. Service
3. Functionality description
4. Set B (a proposed list of effort groupings that is required to implement the provided functionality description)
5. 

Objective: To be able to substantiate all claims made in each grouping in set B. 





Reference these historical patterns:

{memory_text}
 
Check:
- description correctness
- count
- worktype
- complexity
- non-invention

Rules:
- DO NOT INVENT ANYTHING in order to align to anything you try to substantiate.
- Proof of valid substantiation must be supported and only be from the data available.     
- Check if expected components are missing
- Detect unusual or incomplete estimates
- Do NOT copy from memory
- Use memory only for sanity checking
 
Return JSON only.
"""


def verify_cove(state: GrossState) -> GrossState:
    """
    Run CoVE-style verification on each grouping available in Set B.

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
