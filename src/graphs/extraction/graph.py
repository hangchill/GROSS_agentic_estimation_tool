from langgraph.graph import END, START, StateGraph

from src.graphs.extraction.nodes.feedback_template import feedback_template
from src.graphs.extraction.nodes.ingest import ingest_inputs
from src.graphs.extraction.nodes.readiness_big3 import readiness_big3
from src.graphs.extraction.nodes.structure_scope import structure_scope
from src.schemas.state import GrossState


def build_extraction_subgraph() -> StateGraph:
    extraction_graph = StateGraph(GrossState)

    extraction_graph.add_node("ingest_inputs", ingest_inputs)
    extraction_graph.add_node("structure_scope", structure_scope)
    extraction_graph.add_node("readiness_big3", readiness_big3)
    extraction_graph.add_node("feedback_template", feedback_template)

    extraction_graph.add_edge(START, "ingest_inputs")
    extraction_graph.add_edge("ingest_inputs", "structure_scope")
    extraction_graph.add_edge("structure_scope", "readiness_big3")
    extraction_graph.add_edge("readiness_big3", "feedback_template")
    extraction_graph.add_edge("feedback_template", END)

    return extraction_graph.compile()
