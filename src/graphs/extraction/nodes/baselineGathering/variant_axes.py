from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 4 : Variant Axes ie variation points of a FCU 
### Detail Collection for FCU

SYSTEM_PROMPT = """
You are extracting variant axes from CR requirement slides.
 
A variant axis represents a dimension of variation across FCUs. It indicates where and how different FCUs diverge. 

A valid variant axis exists only if the slides show different:
- UI artefact instances
- user flows
- rules
- interfaces
- build artefacts
 
Allowed divergence labels:
- ArtifactInstanceDivergence
- FlowDivergence
- InterfaceDivergence
- RuleDivergence

For each axis, identify the variant value(s). 

Example for Variant Value : If an FCU requires a screen serving the same purpose to be implemented but with different page titles, the axis could be "Page Title" with values "Title A" and "Title B". 
 
Return JSON only.
"""


def variant_axes(state: GrossState) -> GrossState:
    """
    Extract variant axis registry per FCU.

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
  "variant_axes_by_fcu": [
    {{
      "fcu_id": "FCU1",
      "axes": [
        {{
          "axis_name": "...",
          "axis_values": ["..."],
          "divergence_types": ["FlowDivergence"],
          "applicability_constraints": "...",
          "instantiation_signal": "shared-template/one-per-variant/unknown",
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
