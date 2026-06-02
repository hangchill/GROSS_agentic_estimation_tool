from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Number 5 : For a FCU, extract/express the capability in terms of Input, Process and Output
  # Functionality is made of FCUs: 
  ## this step is done such that the user flow of the functionality is clearly mapped in terms of backend requirements

SYSTEM_PROMPT = """
Extract backend capabilities as black-box in terms of Input, Process and Output.
 
Rules:
- Keep to capability-level.
- Do not invent component names.
- Link capability to the bigger picture user flow that it supports.
- Preserve slide numbers for all references and evidence used to arrive at extracted information. 

- Return JSON only.
"""


def backend_ipo(state: GrossState) -> GrossState:
    """
    Extract backend I/P/O capabilities per FCU.

    Writes:
        - state["truth_pack"]["backend_ipo"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Truth Pack So Far:
{state.get("truth_pack", {})}
 
Slides:
{slides_to_text(state)}
 
Return JSON:
{{
  "backend_capabilities_by_fcu": [
    {{
      "fcu_id": "FCU1",
      "capabilities": [
        {{
          "capability": "...",
          "input": "...",
          "process": "...",
          "output": "...",
          "supports_artefact_or_flow": "...",
          "slide_refs": ["S1"],
          "evidence": "..."
        }}
      ]
    }}
  ],
  "unknowns": []
}}
"""
    logger.info(
        "[BACKEND IPO] Extracting backend capabilities as Input/Process/Output..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state.setdefault("truth_pack", {})["backend_ipo"] = result

    add_event(state, "backend_ipo", "Backend I/P/O capabilities extracted.")
    return state
