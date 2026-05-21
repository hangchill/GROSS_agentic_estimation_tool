from __future__ import annotations

from src.schemas.state import GrossState


def add_event(state: GrossState, node: str, message: str) -> None:
    """
    Append a trace event to the workflow state.

    Args:
        state (GrossState): Current workflow state.
        node (str): Node name.
        message (str): Human-readable event message.
    """
    state.setdefault("events", []).append(
        {
            "node": node,
            "message": message,
        }
    )


def add_error(state: GrossState, node: str, message: str) -> None:
    """
    Append an error entry to the workflow state.

    Args:
        state (GrossState): Current workflow state.
        node (str): Node name.
        message (str): Error message.
    """
    state.setdefault("errors", []).append(
        {
            "node": node,
            "message": message,
        }
    )


def slides_to_text(state: GrossState) -> str:
    """
    Convert input slides into a compact text block for prompts.

    Expected slide structure:
        {
            "slide_index": "S1",
            "title": "...",
            "text": "..."
        }

    Args:
        state (GrossState): Current workflow state.

    Returns:
        str: Concatenated slide text.
    """
    inputs = state.get("inputs", {})
    slides = inputs.get("slides", [])

    chunks: list[str] = []

    for idx, slide in enumerate(slides, start=1):
        slide_index = slide.get("slide_index") or f"S{idx}"
        title = slide.get("title", "")
        text = slide.get("text", "")
        chunks.append(f"[{slide_index}] {title}\n{text}")

    return "\n\n".join(chunks)
