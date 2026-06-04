from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 4 : Variant Axes ie variation points of a Functionality 
### DO NOT Do this on a FCU level. In the original prompt, it does it on functionality level.. 
### 
### Detail Collection for FCU

SYSTEM_PROMPT = """
You are extracting variant axes from CR requirement slides.
 
A Variant Axis represents a specific dimension where a main functional requirement or wireframe branches into distinct implementation paths. It defines exactly where and how a capability diverges based on distinct conditions, user types, or data scenarios.

A Variant Axis is valid only when explicit deck evidence mandates that the implementation must branch in one or more of the following ways: 
- UI artefact instances 
- user flows
- rules
- interfaces
- build artefacts

Example for naming a variant axis:   
Imagine the Functionality being assessed : Outpatient Clinic Booking.
You have access to the following text about the functionality : 
"The booking journey changes based on the clinic's system. For HAS-enabled clinics (like Polys), the user selects a live time-slot from the calendar. 
For Non-HAS clinics (private GPs), the user submits a preferred date range, and the clinic calls them back."

An appropriate variant axis is a dimension, and not a feature, such as "Clinic HAS Integration Status" 
instead of naming it something localized like "Calendar Flow" or "Private GP button". The axis name defines the variable that causes the split.

For each variant axis identified, identify the most appropriate divergence label. 
Allowed divergence labels:
- ArtifactInstanceDivergence : UI component changes while the flow remains the same (eg. A standard user and an admin go through the exact same login flow, but the dashboard artifact they land on is fundamentally different.)
- FlowDivergence : User journey branches into different steps or screens.
- InterfaceDivergence : UI and flow are identical but the backend data source or integration path changes based on a condition. (eg. Pulling a record from source A if registered to a certain type, and source B if registered to another)
- RuleDivergence : UI, flow, and integrations are identical, but business logic or computation changes (Eg. A validation rule that requires a signature is needed if the patient's age is below 18. )

For each axis, identify the variant value(s) as well. 
A variant value is a specific named option along a variant axis that the data explicitly distinguishes and can classify the divergence into a distinct case. 

Example for what is a Variant Value : If a functionality requires a screen serving the same purpose to be implemented but with different page titles, the axis could be "Page Title" with values "Title A" and "Title B". 
 
You are also required to reason the following: 
1. Instantiation signal: The context for which the variant axis will trigger. 



2. Differences vs base capability flow: a specific breakdown of exactly what changes for each individual variant value compared to the standard (or "base") behavior of that feature.
What difference vs base capability flow asks for: 
While the "Impact Signature" (e.g., FlowDivergence) tells you how the feature branches category-wise, this section explains the actual mechanics of the branch. For every variant value on the axis, you must explicitly state the delta.

Example from the Booking Flow:
Base Capability: The user books an appointment at a clinic.
Differences vs base flow:
Value A (HAS-Enabled): Renders a live calendar UI; triggers real-time API confirmation.
Value B (Non-HAS): Renders a static date-request form; triggers an asynchronous "callback" status.

Return JSON only.
"""


def variant_axes(state: GrossState) -> GrossState:
    """
    Extract variant axis registry per functionality.

    This node represents the "Variant Axes" step of extraction.

    Writes:
        - state["truth_pack"]["variant_axes"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
FCU Registry:
{state.get("fcu_registry", [])}
 
Slides:
{slides_to_text(state)}
 
Return JSON:
{{
  "variant_axes_by_functionality": [
    {{
      "fid": "F1",
      "axes": [
        {{
          "axis_name": "...",
          "axis_values": ["..."],
          "divergence_type": ["FlowDivergence"],
          "difference_vs_base_flow": "...",
          "instantiation_signal": "...",   
          "evidence": "...",
          "slide_refs": ["S1"]
        }}
      ]
    }}
  ],
  "unknowns": []
}}
"""
    logger.info(
        "[VARIANT AXES] Identifying variation dimensions and divergence types..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state.setdefault("truth_pack", {})["variant_axes"] = result

    add_event(state, "variant_axes", "Variant axes extracted.")
    return state
