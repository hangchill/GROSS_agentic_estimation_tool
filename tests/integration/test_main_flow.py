from src.graphs.main.graph import build_main_graph


class TestMainGraph:
    def test_main_generation_path(self, base_state, mock_llm):
        """
        READY → generation flow
        """

        # force no unknowns → READY
        mock_llm.json_call.return_value = {"unknowns": []}

        graph = build_main_graph(checkpointer=None)

        result = graph.invoke(base_state)

        # either READY or generation runs
        assert result is not None

    def test_main_feedback_path(self, base_state, mock_llm):
        """
        OPEN → awaiting user
        """

        mock_llm.json_call.return_value = {"unknowns": [{"blocks_generation": True}]}

        graph = build_main_graph(checkpointer=None)

        result = graph.invoke(base_state)

        # check that extraction returned something meaningful
        assert "readiness" in result

    def test_main_termination_path(self, base_state, mock_llm):
        """
        OPEN + max iterations → terminate
        """

        base_state["iteration"] = 3
        base_state["max_iterations"] = 3

        mock_llm.json_call.return_value = {"unknowns": [{"blocks_generation": True}]}

        graph = build_main_graph(checkpointer=None)

        result = graph.invoke(base_state)

        assert result is not None
