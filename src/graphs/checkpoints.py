"""
Checkpointing (every node) + threads ('thread_id')

LangGraph persistence:
- saves a snapshot of the graph state at every step when compiled with a checkpointer
- organizes checkpoints into threads keyed by 'thread_id'

This enables human-in-the-loop pause/resume and memory across interactions
"""

from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


def make_checkpointer(
    db_path: str | Path = ".checkpoints/langgraph.sqlite3",
) -> SqliteSaver:
    """
    Creates a SQLite-backed checkpointer that LangGraph can use to save a snapshot of the graph state after each node (since graph is compiled with this checkpointer)
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(
        parents=True, exist_ok=True
    )  # first two lines is simply to create the checkpoints/ folder
    return SqliteSaver.from_conn_string(
        str(db_path)
    )  # actual connection of database to SQLite


def make_config(thread_id: str) -> dict:
    """
    Simple function to create LangGraph runtime config to save/read checkpoints under this 'thread_id'
    """
    return {"configurable": {"thread_id": thread_id}}
