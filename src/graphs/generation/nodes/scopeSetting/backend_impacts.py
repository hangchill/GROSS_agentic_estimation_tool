from __future__ import annotations

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 3 : Backend capabilities for relevant FCUs from scope_filter node. 
## 

def impacts_backend(state: GrossState) -> GrossState:
    """
    Derive backend impact statements from selected backend capabilities.

    This node represents the "Backend Impact" step of generation.

    It calls the LLM, to reshape details in FCUs that are present in the scope filter acquired earlier.  
    into a list of workable UI impacts statements (feature descriptions) that later Set A generation can reason over (Effort classification of feature descriptions).

    Writes:
        - state["backend_impacts"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    logger.info("[IMPACTS BACKEND] Deriving backend capability impacts...")
    scope = state.get("generation_scope", {})
    capabilities = scope.get("selected_backend_capabilities", [])

    backend_impacts = []

    for item in capabilities:
        if isinstance(item, dict):
            capability = item.get("capability", "Unnamed capability")
            supports = item.get("supports_artefact_or_flow", "")
            bound_variants = item.get("bound_variant_axes", [])
        else:
            capability = str(item)
            supports = ""
            bound_variants = []

        backend_impacts.append(
            {
                "impact_type": "backend",
                "capability": capability,
                "description": f"Implement backend capability: {capability}",
                "supports": supports,
                "bound_variant_axes": bound_variants,
            }
        )

    state["backend_impacts"] = backend_impacts

    add_event(state, "impacts_backend", "Backend impacts derived.")
    return state
