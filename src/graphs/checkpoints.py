from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


def make_sqlite_checkpointer(
    db_path: str | Path = ".checkpoints/langgraph.sqlite3",
) -> SqliteSaver:
    """
    Create a SQLite-backed LangGraph checkpointer.

    Use this in local runs / CLI.
    In tests, pass `checkpointer=None` to the main graph instead.

    Args:
        db_path (str | Path): Path to SQLite checkpoint database.

    Returns:
        SqliteSaver: LangGraph-compatible checkpoint saver.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return SqliteSaver(conn)


def make_config(thread_id: str) -> dict:
    """
    Create LangGraph runtime config using a thread_id.

    LangGraph persistence associates checkpoints with a thread via
    `configurable.thread_id`. 【3-fd6864】【4-0d5679】

    Args:
        thread_id (str): Workflow thread identifier.

    Returns:
        dict: LangGraph config dictionary.
    """
    return {"configurable": {"thread_id": thread_id}}
