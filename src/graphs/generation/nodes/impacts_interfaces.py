from __future__ import annotations

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def impacts_interfaces(state: GrossState) -> GrossState:
    """
    Derive interface impact candidates from selected interfaces.

    This node represents the "data source / Interface Impact" step of generation.

    It reshapes selected interfaces into simplified integration impact records for
    downstream effort generation.

    Writes:
        - state["interface_impacts"]

    Args:
        state (GrossState): Current workflow state.

    Returns:
        GrossState: Updated workflow state.
    """
    logger.info("[IMPACTS INTERFACES] Deriving interface/integration impacts...")
    scope = state.get("generation_scope", {})
    interfaces = scope.get("selected_interfaces", [])

    interface_impacts = []

    for item in interfaces:
        if isinstance(item, dict):
            system = item.get("system", "Unnamed system")
            purpose = item.get("purpose", "")
            bound_variants = item.get("bound_variant_axes", [])
        else:
            system = str(item)
            purpose = ""
            bound_variants = []

        interface_impacts.append(
            {
                "impact_type": "interface",
                "system": system,
                "description": f"Exchange data with {system}",
                "purpose": purpose,
                "bound_variant_axes": bound_variants,
            }
        )

    state["interface_impacts"] = interface_impacts

    add_event(state, "impacts_interfaces", "Interface impacts derived.")
    return state
