from graphs.generation.nodes.setGenerating.correct_setb import correct_setb
from graphs.generation.nodes.setGenerating.finalize_setc import finalize_setc
from graphs.generation.nodes.setGenerating.gen_setA import groupings_seta
from graphs.generation.nodes.scopeSetting.backend_impacts import impacts_backend
from graphs.generation.nodes.scopeSetting.interfaces_impacts import impacts_interfaces
from graphs.generation.nodes.scopeSetting.frontend_impact import impacts_ui
from graphs.generation.nodes.scopeSetting.scope_filter import scope_filter
from graphs.generation.nodes.setGenerating.verify_cove import verify_cove


class TestGenerationNodes:
    def test_scope_filter(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"selected_fcus": ["FCU1"]}

        result = scope_filter(base_state)

        assert result["generation_scope"]["selected_fcus"] == ["FCU1"]

    def test_impacts_ui(self, base_state):
        base_state["generation_scope"] = {"selected_artefacts": [{"name": "Page"}]}

        result = impacts_ui(base_state)

        assert len(result["ui_impacts"]) == 1

    def test_impacts_interfaces(self, base_state):
        base_state["generation_scope"] = {"selected_interfaces": [{"system": "API"}]}

        result = impacts_interfaces(base_state)

        assert len(result["interface_impacts"]) == 1

    def test_impacts_backend(self, base_state):
        base_state["generation_scope"] = {
            "selected_backend_capabilities": [{"capability": "Process"}]
        }

        result = impacts_backend(base_state)

        assert len(result["backend_impacts"]) == 1

    def test_groupings_seta(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"set_a": [{"worktype": "Page"}]}

        result = groupings_seta(base_state)

        assert result["set_a"][0]["worktype"] == "Page"

    def test_correct_setb(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"set_b": [{"worktype": "Page"}]}

        base_state["set_a"] = []

        result = correct_setb(base_state)

        assert result["verification_attempts"] == 1

    def test_verify_cove(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"overall_status": "PASS"}

        result = verify_cove(base_state)

        assert result["verification"]["overall_status"] == "PASS"

    def test_finalize_setc(self, base_state, mock_llm):
        mock_llm.json_call.return_value = {"effort_final": [{"worktype": "Page"}]}

        result = finalize_setc(base_state)

        assert result["phase"] == "DONE"
