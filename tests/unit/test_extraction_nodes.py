from src.graphs.extraction.nodes.artefacts_flows import artefacts_flows
from src.graphs.extraction.nodes.backend_ipo import backend_ipo
from src.graphs.extraction.nodes.feedback_template import feedback_template
from src.graphs.extraction.nodes.ingest import ingest_inputs
from src.graphs.extraction.nodes.pfr_merge import pfr_merge
from src.graphs.extraction.nodes.readiness_big3 import readiness_big3
from src.graphs.extraction.nodes.structure_scope import structure_scope
from src.graphs.extraction.nodes.synth_unknowns import synth_unknowns
from src.graphs.extraction.nodes.systems_interfaces import systems_interfaces
from src.graphs.extraction.nodes.variant_axes import variant_axes


class TestExtractionNodes:
    def test_ingest_inputs(self, base_state):
        result = ingest_inputs(base_state)

        assert result["phase"] == "EXTRACTION"
        assert result["iteration"] == 1

    def test_structure_scope(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {
            "target_dm": "DM1",
            "functionalities": [],
            "fcu_registry": [{"fcu_id": "FCU1"}],
            "unknowns": [],
        }

        result = structure_scope(base_state)

        assert "structure_scope" in result["truth_pack"]
        assert result["fcu_registry"][0]["fcu_id"] == "FCU1"

    def test_artefacts_flows(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"artefacts_by_fcu": [], "unknowns": []}

        base_state["fcu_registry"] = [{"fcu_id": "FCU1"}]

        result = artefacts_flows(base_state)

        assert "artefacts_flows" in result["truth_pack"]

    def test_systems_interfaces(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"interfaces_by_fcu": [], "unknowns": []}

        base_state["fcu_registry"] = [{"fcu_id": "FCU1"}]

        result = systems_interfaces(base_state)

        assert "systems_interfaces" in result["truth_pack"]

    def test_variant_axes(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"variant_axes_by_fcu": [], "unknowns": []}

        base_state["fcu_registry"] = [{"fcu_id": "FCU1"}]

        result = variant_axes(base_state)

        assert "variant_axes" in result["truth_pack"]

    def test_backend_ipo(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {
            "backend_capabilities_by_fcu": [],
            "unknowns": [],
        }

        result = backend_ipo(base_state)

        assert "backend_ipo" in result["truth_pack"]

    def test_synth_unknowns(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {
            "functionality_feature_registry": [],
            "unknowns": [{"blocks_generation": True}],
        }

        result = synth_unknowns(base_state)

        assert "unknowns" in result["truth_pack"]

    def test_pfr_merge_empty(self, base_state):
        result = pfr_merge(base_state)

        assert "pfr" in result

    def test_readiness(self):
        state = {"truth_pack": {"unknowns": [{"blocks_generation": True}]}}

        result = readiness_big3(state)

        assert result["readiness"]["status"] == "OPEN"

    def test_feedback_template(self):
        state = {
            "readiness": {
                "any_open": True,
                "blocking_unknowns": [
                    {"scope": "FCU1", "missing_field": "system", "reason": "missing"}
                ],
            }
        }

        result = feedback_template(state)

        assert result["feedback_template_md"] is not None
