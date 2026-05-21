from unittest.mock import MagicMock

import pytest


@pytest.fixture
def base_state():
    return {
        "inputs": {
            "target_dm": "DM1",
            "functionality_description": "Test functionality",
            "slides": [
                {"slide_index": "S1", "title": "Test Slide", "text": "Sample content"}
            ],
        },
        "iteration": 1,
        "max_iterations": 3,
        "verification_attempts": 0,
        "max_verification_attempts": 2,
        "truth_pack": {},
        "events": [],
        "errors": [],
    }


@pytest.fixture(autouse=True)
def mock_llm(mocker):
    """
    Patch ALL node-level LLMClient usages.

    This ensures NO real API calls happen.
    """

    mock_instance = MagicMock()
    mock_instance.json_call.return_value = {}

    # Extraction nodes
    mocker.patch(
        "src.graphs.extraction.nodes.structure_scope.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.extraction.nodes.artefacts_flows.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.extraction.nodes.systems_interfaces.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.extraction.nodes.variant_axes.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.extraction.nodes.backend_ipo.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.extraction.nodes.synth_unknowns.LLMClient",
        return_value=mock_instance,
    )

    # Generation nodes
    mocker.patch(
        "src.graphs.generation.nodes.scope_filter.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.generation.nodes.groupings_seta.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.generation.nodes.correct_setb.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.generation.nodes.verify_cove.LLMClient",
        return_value=mock_instance,
    )
    mocker.patch(
        "src.graphs.generation.nodes.finalize_setc.LLMClient",
        return_value=mock_instance,
    )

    return mock_instance
