from src.graphs.generation.graph import build_generation_subgraph


class TestGenerationGraph:
    def test_generation_pass_flow(self, base_state, mock_llm):
        """
        Test generation completes when verification passes.
        """

        def mock_response(system, user):
            # simulate different responses per stage

            if "Set A" in user:
                return {"set_a": [{"worktype": "Page"}]}

            if "Set B" in user:
                return {"set_b": [{"worktype": "Page"}]}

            if "Verify" in user or "overall_status" in user:
                return {"overall_status": "PASS"}

            if "effort_final" in user or "Finalise" in user:
                return {"effort_final": [{"worktype": "Page"}]}

            return {}

        mock_llm.json_call.side_effect = mock_response

        graph = build_generation_subgraph()

        result = graph.invoke(base_state)

        assert result["phase"] == "DONE"
        assert "effort_final" in result

    def test_generation_retry_loop(self, base_state, mock_llm):
        """
        Test FAIL → retry → PASS loop.
        """

        calls = {"count": 0}

        def mock_response(system, user):
            if "Set A" in user:
                return {"set_a": [{"worktype": "Page"}]}

            if "Set B" in user:
                return {"set_b": [{"worktype": "Page"}]}

            if "Verify" in user:
                calls["count"] += 1

                if calls["count"] == 1:
                    return {"overall_status": "FAIL"}
                else:
                    return {"overall_status": "PASS"}

            if "effort_final" in user:
                return {"effort_final": [{"worktype": "Page"}]}

            return {}

        mock_llm.json_call.side_effect = mock_response

        graph = build_generation_subgraph()

        result = graph.invoke(base_state)

        assert result["phase"] == "DONE"
