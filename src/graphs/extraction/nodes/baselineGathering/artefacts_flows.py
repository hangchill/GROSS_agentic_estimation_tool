from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 2 : By indiv FCUs, 1) capture artifacts 2) Identify user flow step that it supports
 # 3) Finally produce the overall user flow for a functionality
### Detail Collection for FCU

SYSTEM_PROMPT = """
You are extracting UI artefacts and the overall user flow(s) that the FCU supports, from the CR requirement slides.
 
Rules:
- User flows are defined as sequences of user actions and system responses that achieve a specific goal. They may include decision points and branching logic. 
- An Artefact is a named item that may appear in any of the intermediate steps or the final output referenced in the slides as part of the user flow, such as a page, screen, data field, or document.
- Use only provided slide text and FCU context to identify artifacts or description of flow steps. 
- Do not invent names or artifacts. 
- Preserve slide references.
- Return JSON only.
"""


def artefacts_flows(state: GrossState) -> GrossState:
    """
    Extract artefact inventory and user flow steps per FCU.

    This node represents the "Artefacts & Flows" step of extraction.

    Expected output shape:
    {
      "artefacts_by_fcu": [
        {
          "fcu_id": "FCU1",
          "artefacts": [],
          "user_flow": []
        }
      ],
      "unknowns": []
    }

    Writes:
        - state["truth_pack"]["artefacts_flows"]

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
  "artefacts_by_fcu": [
    {{
      "fcu_id": "FCU1",
      "artefacts": [
        {{
          "name": "...",
          "type": "page/screen/card/popup/cta/state/flow_step",
          "role": "...",
          "slide_refs": ["S1"]
        }}
      ],
      "user_flow": [
        {{
          "step_no": 1,
          "screen_or_state": "...",
          "user_action": "...",
          "system_response": "...",
          "decision_logic": "...",
          "slide_refs": ["S1"]
        }}
      ]
    }}
  ],
  "unknowns": []
}}
"""
    logger.info("[ARTEFACT FLOWS] Extracting pages/screens/cards/flow steps...")
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state.setdefault("truth_pack", {})["artefacts_flows"] = result

    add_event(state, "artefacts_flows", "Artefacts and flows extracted.")
    return state
