from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.memory.mem0_client import (
    search_worktype_glossary,
)
from src.memory.utils import mem_results_to_text
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


## Step 1 in setGeneration


# Number 7 POSSIBLY; AFTER functional objects/feature description statements are synthesized 
#         - To assign worktype, complexity and count 
## NOTE: 
#   IN OG PROMPT: should be ChECKPOINTING after each step here (need to figure out how to do this)

## NOTE to improve :  
#   

SYSTEM_PROMPT = """
You are an Expert Technical Project Manager and Lead Systems Architect.

You are provided with: 
1. List of feature descriptions for assessment 
2. Worktype definitions 
3. Complexity definitions associated with each worktype 

Task: 
Generate Set A : ie. first generation of development effort groupings for each feature description provided in the   

Use the following worktype definitions and complexity rules: 
{memory_text}
to infer the most likely worktype and complexity respectively. 

Rules:
- Use only generation scope and derived impacts.
- Assign correct worktypes and complexity levels based on the provided memory of worktype definitions and complexity rules.
- Count

- Return JSON only.

Steps: 
For each feature description in the list you are provided with:  
1. Determine worktype 
2. Determine complexity 
3. Determine the count (ie. number of instances at the assigned worktype-complexity classification) needed to implement the feature as described. 

"""


def groupings_seta(state: GrossState) -> GrossState:
    """
    Generate Set A initial development effort groupings.

    This node represents the "Generation of effort descriptions" and Set A step
    of the generation workflow.

    Expected output shape:
    {
      "set_a": [
        {
          "worktype": "Page",
          "complexity": "s",
          "count": 1,
          "description": "Capability-level noun phrase",
          "justification": "Short evidence-based reason"
        }
      ]
    }

    Writes:
        - state["set_a"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Functionality Description:
{state.get("inputs", {}).get("functionality_description", "")}
 
Generation Scope:
{state.get("generation_scope", {})}
 
UI Impacts:
{state.get("ui_impacts", [])}
 
Interface Impacts:
{state.get("interface_impacts", [])}
 
Backend Impacts:
{state.get("backend_impacts", [])}
 
Return JSON:
{{
  "set_a": [
    {{
      "worktype": "Page",
      "complexity": "s",
      "count": 1,
      "description": "Capability-level noun phrase",
      "justification": "Short evidence-based reason"
    }}
  ]
}}
"""
    mem = search_worktype_glossary("worktype definitions complexity S M C rules", 5)

    memory_text = mem_results_to_text(mem)

    populated_system_prompt = SYSTEM_PROMPT.format(memory_text=memory_text)

    logger.info("[GROUPINGS SETA] Producing initial draft effort groupings...")
    result = LLMClient().json_call(populated_system_prompt, user_prompt)
    state["set_a"] = result.get("set_a", [])

    add_event(state, "groupings_seta", "Set A generated.")
    return state
