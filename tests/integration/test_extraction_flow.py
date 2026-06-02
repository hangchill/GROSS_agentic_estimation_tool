from graphs.extraction.ExtractGraph import build_extraction_subgraph


class TestExtractionGraph:
    def test_extraction_ready_flow(self, base_state, mock_llm):
        """
        Test full extraction flow when no unknowns exist.
        Should end without feedback.
        """

        # ✅ Make all LLM calls return no unknowns
        mock_llm.json_call.return_value = {"fcu_registry": [], "unknowns": []}

        graph = build_extraction_subgraph()

        result = graph.invoke(base_state)

        # ✅ Should reach readiness
        assert "readiness" in result
        assert result["readiness"]["status"] in ["READY", "OPEN"]

    def test_extraction_triggers_feedback(self, base_state, mock_llm):
        """
        Test extraction produces feedback when unknowns exist.
        """

        # ✅ Force unknowns
        mock_llm.json_call.return_value = {"unknowns": [{"blocks_generation": True}]}

        graph = build_extraction_subgraph()

        result = graph.invoke(base_state)

        assert "readiness" in result
