from __future__ import annotations

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def feedback_template(state: GrossState) -> GrossState:
    """
    Generate user-facing feedback questions for unresolved readiness gaps.

    Writes:
        - feedback_template_md
        - feedback_questions
    """
    logger.info("[FEEDBACK TEMPLATE] Creating clarification questions...")
    readiness = state.get("readiness", {})
    unknowns = readiness.get("blocking_unknowns", [])

    if not readiness.get("any_open", False):
        state["feedback_template_md"] = None
        state["feedback_questions"] = []
        add_event(state, "feedback_template", "No feedback required.")
        return state

    sections = ["# FEEDBACK LOOP REQUIRED\n"]
    feedback_questions: list[dict] = []

    for idx, unknown in enumerate(unknowns, start=1):
        qid = f"Q{idx}"
        scope = unknown.get("scope", "Unknown scope")
        missing = unknown.get("missing_field", "Unknown field")
        reason = unknown.get("reason", "")

        feedback_questions.append(
            {
                "qid": qid,
                "scope": scope,
                "missing_field": missing,
                "reason": reason,
                "unknown_index": idx - 1,
            }
        )

        sections.append(f"## Section {idx} — QID {qid}\n")
        sections.append(f"**Scope:** {scope}\n")
        sections.append("**Existing issue:**\n")
        sections.append(f"- Missing field: {missing}\n")
        sections.append(f"- Reason: {reason}\n\n")
        sections.append("| Big 3 element category | Question | Your Answer |\n")
        sections.append("|---|---|---|\n")
        sections.append(
            f"| Implementation details / Current vs To-Be | "
            f"Please clarify `{missing}` for `{scope}`. If unknown, write Unknown. | |\n\n"
        )

    state["feedback_template_md"] = "\n".join(sections)
    state["feedback_questions"] = feedback_questions

    add_event(state, "feedback_template", "Feedback template generated.")
    return state
