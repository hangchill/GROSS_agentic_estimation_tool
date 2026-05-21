from __future__ import annotations

from src.graphs.node_utils import add_event
from src.llm.client import LLMClient
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
You are an Expert Technical Project Manager and Lead Systems Architect.
 
Generate Set A initial development effort groupings.
 
Rules:
- Use only generation scope and derived impacts.
- Valid worktypes:
  Interface, Component, Mobile, Entity, Config, Page, Application, Batch,
  Framework, Report, UI, Query
- Descriptions must be capability-level, not implementation detail.
- Return JSON only.
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
    logger.info("[GROUPINGS SETA] Producing initial draft effort groupings...")
    result = LLMClient().json_call(SYSTEM_PROMPT, user_prompt)
    state["set_a"] = result.get("set_a", [])

    add_event(state, "groupings_seta", "Set A generated.")
    return state
