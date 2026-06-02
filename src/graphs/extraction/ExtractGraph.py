from __future__ import annotations

from langgraph.graph import END, StateGraph

# Baseline Gathering of information Nodes 
from graphs.extraction.nodes.baselineGathering.ingest import ingest_inputs
from graphs.extraction.nodes.baselineGathering.structure_scope import structure_scope
from graphs.extraction.nodes.baselineGathering.artefacts_flows import artefacts_flows
from graphs.extraction.nodes.baselineGathering.systems_interfaces import systems_interfaces
from graphs.extraction.nodes.baselineGathering.variant_axes import variant_axes
from graphs.extraction.nodes.baselineGathering.backend_capabilities import backend_ipo
from graphs.extraction.nodes.baselineGathering.synth_unknowns import synth_unknowns

## Feedback Nodes
from graphs.extraction.nodes.feedbackMechanisms.readiness_big3 import readiness_big3
from graphs.extraction.nodes.feedbackMechanisms.pfr_merge import pfr_merge
from graphs.extraction.ExtractRouting import route_after_readiness, route_after_synthesis
from graphs.extraction.nodes.feedbackMechanisms.feedback_template import feedback_template


from src.schemas.state import GrossState


def build_extraction_subgraph():
    """
    Build the extraction subgraph.

    Extraction flow:
        ingest_inputs (Checks inputs ; uses ingestPPTX )
        -> structure_scope (Scoping of Functionality, FCUs for a DM)
        -> artefacts_flows (FCU : Identify artefacts and flows)
        -> systems_interfaces (FCU : Identify data interfaces for a data action required)
        -> variant_axes (FCU : Identify variant axes and values for variability in FCU)
        -> backend_ipo 
        -> synth_unknowns
        -> (optional) pfr_merge
        -> readiness_big3
        -> (optional) feedback_template
        -> END

    Notes:
    - If user clarification answers exist, pfr_merge is applied after synthesis.
    - If readiness is READY, extraction ends without generating feedback.
    - If readiness is OPEN and max iterations are not yet reached, feedback_template
      is generated and extraction ends in a feedback-ready state.
    - If readiness is OPEN and max iterations are reached, extraction ends without
      new feedback so the outer workflow can terminate.
    """
    g = StateGraph(GrossState)

    # ---- extraction nodes ----
    g.add_node("ingest_inputs", ingest_inputs)
    g.add_node("structure_scope", structure_scope)
    g.add_node("artefacts_flows", artefacts_flows)
    g.add_node("systems_interfaces", systems_interfaces)
    g.add_node("variant_axes", variant_axes)
    g.add_node("backend_ipo", backend_ipo)
    g.add_node("synth_unknowns", synth_unknowns)
    g.add_node("pfr_merge", pfr_merge)
    g.add_node("readiness_big3", readiness_big3)
    g.add_node("feedback_template", feedback_template)

    # ---- entry point ----
    g.set_entry_point("ingest_inputs")

    # ---- deterministic extraction path ----
    g.add_edge("ingest_inputs", "structure_scope")
    g.add_edge("structure_scope", "artefacts_flows")
    g.add_edge("artefacts_flows", "systems_interfaces")
    g.add_edge("systems_interfaces", "variant_axes")
    g.add_edge("variant_axes", "backend_ipo")
    g.add_edge("backend_ipo", "synth_unknowns")

    # ---- after synthesis: decide whether to apply PFR merge ----
    g.add_conditional_edges(
        "synth_unknowns",
        route_after_synthesis,
        {
            "pfr_merge": "pfr_merge",
            "readiness_big3": "readiness_big3",
        },
    )

    # ---- if PFR merge happens, re-check readiness afterwards ----
    g.add_edge("pfr_merge", "readiness_big3")

    # ---- after readiness: either generate feedback or end extraction ----
    g.add_conditional_edges(
        "readiness_big3",
        route_after_readiness,
        {
            "feedback_template": "feedback_template",
            "end": END,
        },
    )

    # ---- if feedback template is generated, extraction ends here ----
    g.add_edge("feedback_template", END)

    return g.compile()
