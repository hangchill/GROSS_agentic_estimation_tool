from __future__ import annotations

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Number 4 : UI/Frontend impact candidates derived from selected artefacts in scope filter node.

def impacts_ui(state: GrossState) -> GrossState:
    """
    Derive UI/frontend impact statements present in the scope identified.

    This node represents the "UI/Frontend Impact" step of the generation layer.

    It calls the LLM, to reshape details in FCUs that are present in the scope filter acquired earlier.  
    into a list of workable UI impacts statements that later Set A generation can reason over (Effort classification of feature descriptions).

    Writes:
        - state["ui_impacts"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """

    
    logger.info(
        "[IMPACTS UI] Deriving UI/frontend build impacts from FCUs..."
    )
    scope = state.get("generation_scope", {})
    artefacts = scope.get("selected_artefacts", [])

    ui_impacts = []

    for item in artefacts:
        if isinstance(item, dict):
            name = item.get("name", "Unnamed artefact")
            role = item.get("role", "")
            bound_variants = item.get("bound_variant_axes", [])
        else:
            name = str(item)
            role = ""
            bound_variants = []

        ui_impacts.append(
            {
                "impact_type": "ui",
                "artefact": name,
                "description": f"Build or update UI artefact: {name}",
                "role": role,
                "bound_variant_axes": bound_variants,
            }
        )

    state["ui_impacts"] = ui_impacts

    add_event(state, "impacts_ui", "UI impacts derived.")
    return state
