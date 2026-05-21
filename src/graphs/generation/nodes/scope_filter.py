from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
You are selecting the relevant extracted requirements for effort estimation.
 
Rules:
- Use only the truth_pack.
- Select FCUs, artefacts, interfaces, variants, and backend capabilities relevant
  to the provided functionality description.
- Do not invent new requirements.
- Return JSON only.
"""


def scope_filter(state: GrossState) -> GrossState:
    """
    Select in-scope extracted requirement data for generation.

    This node represents the "Scope Filter" step of the generation layer.

    It narrows the extracted truth pack down to the specific functionality slice
    being estimated, rather than letting downstream generation reason over the
    entire extracted dataset.

    Expected output shape:
    {
      "selected_fcus": ["FCU1"],
      "selected_artefacts": [],
      "selected_interfaces": [],
      "selected_variant_axes": [],
      "selected_backend_capabilities": [],
      "scope_notes": []
    }

    Writes:
        - state["generation_scope"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    user_prompt = f"""
Functionality Description:
{state.get("inputs", {}).get("functionality_description", "")}
 
Truth Pack:
{state.get("truth_pack", {})}
 
Return JSON:
{{
  "selected_fcus": ["FCU1"],
  "selected_artefacts": [],
  "selected_interfaces": [],
  "selected_variant_axes": [],
  "selected_backend_capabilities": [],
  "scope_notes": []
}}
"""
    logger.info(
        "[SCOPE FILTER] Selecting in-scope extracted data for the requested functionality..."
    )
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state["generation_scope"] = result

    add_event(state, "scope_filter", "Generation scope selected.")
    return state
