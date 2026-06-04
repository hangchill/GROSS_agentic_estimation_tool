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


Incorrect Reasoning Demonstrations: 
Use the Demonstrations below to understand and how to self-correct effort groupings that are wrong based on flawed reasoning that you SHOULD NOT employ using the correct reasoning as a guide. 
These demonstrations are independent, and the priority should not be taken in order of the demonstrations given. The numbering is just to give a identity number for a particular demonstration. 
1. Over-Decomposition:  
[Incorrect CoT]: Reasoning: Observing the feature description, I should separate every minute technical detail (eg. Thresholds, Routing, UI, results visualisation) of how to actually implement a certain functionality into individual effort groupings. 
Result: component-s x 1 + component-m x 1 + mobile-page-m x 1 + component-m x 1 
[Correct CoT]: Reasoning: Certain elements are considered standard infrastructure overhead for each worktype. There SHOULD NOT BE AN INDIVIDUAL effort grouping for each low level details of the work needed in order for this feature to be completed. Embed these into a larger effort grouping for this particular feature. 
Result: another existing RELATED effort grouping should absorb the relevant minute details seen here. Only keep one effort grouping that describes the main functionality to be built. 

2. Failure to consider Variant Axis in determining Count for Frontend Impact work: 
[Incorrect CoT]: Reasoning: Generated groupings that classified the effort for a Consolidated estimate for details of mobile pages with a project context that the feature to be developed is known to have a variant axis of 3 axis values into mobile-m x 1. The reasoning is by assuming that the work done with 1 mobile-m effort classification can be reused for all 3. 
Result : the effort classification for this feature grouping is mobile-m x 1 
[Correct CoT]: Reasoning : ONLY FOR A FRONTEND UI PAGE there is a special consideration, In this case, this particular variant axis has 3 values that logically will require work on 3 different mobile pages.
Result : The effort classification for this feature grouping should have been mobile-m x 3. 

3. Failure to consider Variant Axis in determining Count for Backend Impact work
[Incorrect CoT]: Reasoning: Generated a feature grouping to implement a backend functionality that has a variant axis with 3 axis values (eg. to provide service for 3 different applications) that shares the same workflow. This is as the underlying reasoning has assumed that the work done with cannot be reused for all 3 axis value instances. 
Result : The effort classification for this feature grouping is Component-m x 3 
[Correct CoT]: Reasoning: With the same project context established above, FOR A BACKEND IMPACT worktype, it is possible that the 3 axis value instances to be developed can be implemented sharing the same effort that produced the component elements for this work classified as component-m. The FACTS from the requirements data has greater hierarchical priority over this common tendency. If there are contradictions (eg. If the flowchart differs between axis value instances), please use your expertise to weigh what count is more appropriate accordingly. 
Result : Component-m x 1 is sufficient. 

4. Mindset in determining Count
[Incorrect CoT]: Reasoning: A feature grouping that describes a functionality that considers a variant axis of 3 axis values into one ‘complex’-complexity classification for cost efficiency reasons. 
Result: the effort classification for this feature grouping is component-c x 1. 
[Correct CoT]: Reasoning: the 3 fundamentally different medical logic sets. Maintain count (x 3) to reflect unique rule implementations and the variant axis. 
Result: component-m x 3. 


Rules:
- Use only generation scope and derived impacts.
- Assign correct worktypes and complexity levels based on the provided memory of worktype definitions and complexity rules.
- During reasoning and determination of either worktype, complexity or count, use the Incorrect Reasoning Demonstrations to correct any possible incorrect results.  
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
