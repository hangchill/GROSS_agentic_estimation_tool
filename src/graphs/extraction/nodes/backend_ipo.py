from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
Extract backend capabilities as black-box Input / Process / Output.
 
Rules:
- Keep capability-level.
- Do not invent component names.
- Link capability to artefact or flow it supports.
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
