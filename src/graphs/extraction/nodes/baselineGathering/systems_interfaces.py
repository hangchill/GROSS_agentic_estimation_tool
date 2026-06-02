from __future__ import annotations

from src.graphs.node_utils import add_event, slides_to_text
from src.llm.client import LLMClient
from src.memory.mem0_client import (
    search_team_context,
)
from src.memory.utils import mem_results_to_text
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 3 : Interfaces for any data action needed for each FCU

SYSTEM_PROMPT = """
You are identifying systems and interfaces.
 
Use the following known system glossary and context:
 
{memory_text}

Rules:
- One named system equals one interface entry unless explicitly stated otherwise.
- For each distinct data or action involved, capture the FCU it supports and the interface required
- Capture purpose and evidence.
- Do not invent system names.
- Return JSON only.
"""


def systems_interfaces(state: GrossState) -> GrossState:
    """
    Extract interface list per FCU.

    This node represents the "Systems & Interfaces" step of extraction.

    Expected output shape:
    {
      "interfaces_by_fcu": [
        {
          "fcu_id": "FCU1",
          "interfaces": [
            {
              "system": "...",
              "purpose": "...",
              "data_or_action": "...",
              "slide_refs": ["S1"],
              "evidence": "..."
            }
          ]
        }
      ],
      "unknowns": []
    }

    Writes:
        - state["truth_pack"]["systems_interfaces"]

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
  "interfaces_by_fcu": [
    {{
      "fcu_id": "FCU1",
      "interfaces": [
        {{
          "system": "...",
          "purpose": "...",
          "data_or_action": "...",
          "slide_refs": ["S1"],
          "evidence": "..."
        }}
      ]
    }}
  ],
  "unknowns": []
}}
"""
    mem = search_team_context(
        "system names acronyms healthcare systems integrations", top_k=5
    )

    memory_text = mem_results_to_text(mem)
    populated_system_prompt = SYSTEM_PROMPT.format(memory_text=memory_text)

    logger.info("[SYSTEM INTERFACES] Listing named systems and interface purposes...")
    result = LLMClient().json_call(populated_system_prompt, user_prompt)
    state.setdefault("truth_pack", {})["systems_interfaces"] = result

    add_event(state, "systems_interfaces", "Systems and interfaces extracted.")
    return state
