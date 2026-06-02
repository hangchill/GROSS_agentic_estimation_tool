from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 6 : Synthesize all extracted data from prev steps into a unified truth pack that will be used for generation
 # Merge all data into one databank source of "Truth" for system to know what it knows and unknowns
 ## Unknowns are registered as gaps ; Gaps are used as an anchor during feedback session later. 

SYSTEM_PROMPT = """
Synthesize extracted requirement data into a unified truth pack.
 
Rules:
- Merge duplicate names.
- Keep evidence-bound data.
- Register unknowns explicitly.
- Do not invent missing details.
- Return JSON only.
"""


def synth_unknowns(state: GrossState) -> GrossState:
    """
    Consolidate extraction outputs and register unknowns.

    Writes:
        - state["truth_pack"]["synthesis"]
        - state["truth_pack"]["unknowns"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Truth Pack So Far:
{state.get("truth_pack", {})}
 
Return JSON:
{{
  "functionality_feature_registry": [
    {{
      "fid": "F1",
      "name": "...",
      "fcus": ["FCU1"],
      "artefacts": [],
      "interfaces": [],
      "variant_axes": [],
      "backend_capabilities": [],
      "summary": "..."
    }}
  ],
  "unknowns": [
    {{
      "scope": "FCU1/F1/DM",
      "missing_field": "...",
      "reason": "...",
      "blocks_generation": true
    }}
  ]
}}
"""
    logger.info(
        "[SYNTH UNKNOWNS] Merging all extracted facts into a truth pack and listing unknowns..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)

    truth_pack = state.setdefault("truth_pack", {})
    truth_pack["synthesis"] = result
    truth_pack["unknowns"] = result.get("unknowns", [])

    add_event(state, "synth_unknowns", "Truth pack synthesis completed.")
    return state
