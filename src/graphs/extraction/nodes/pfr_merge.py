from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.graphs.node_utils import add_event
from src.schemas.state import GrossState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def pfr_merge(state: GrossState) -> GrossState:
    """
    Merge user clarification answers into PFR and apply them to unknowns.

    If the user answers "Unknown", the gap is resolved as unknown.
    """
    logger.info(
        "[PFR MERGE] Applying user feedback from previous loops into truth pack..."
    )
    raw_answers = state.get("user_answers_raw")

    if not raw_answers or not raw_answers.strip():
        state.setdefault("pfr", _empty_pfr())
        add_event(state, "pfr_merge", "No user answers provided; merge skipped.")
        return state

    parsed_answers = _parse_user_answer_template(raw_answers)
    pfr = state.setdefault("pfr", _empty_pfr())

    merge_time = datetime.now(timezone.utc).isoformat()

    pfr.setdefault("iterations", []).append(
        {
            "iteration": state.get("iteration", 1),
            "merged_at": merge_time,
            "answer_count": len(parsed_answers),
            "raw": raw_answers,
        }
    )
    pfr.setdefault("answers_by_qid", {})

    for answer in parsed_answers:
        qid = answer["qid"]
        normalized = _normalize_answer(answer.get("answer", ""))

        pfr["answers_by_qid"][qid] = {
            "qid": qid,
            "category": answer.get("category", ""),
            "question": answer.get("question", ""),
            "answer": answer.get("answer", ""),
            "normalized_answer": normalized,
            "iteration": state.get("iteration", 1),
            "merged_at": merge_time,
        }

    _apply_answers_to_unknowns(state, parsed_answers)

    add_event(state, "pfr_merge", f"Merged {len(parsed_answers)} answer(s).")
    return state


def _empty_pfr() -> dict[str, Any]:
    return {"iterations": [], "answers_by_qid": {}}


def _parse_user_answer_template(raw: str) -> list[dict[str, str]]:
    answers: list[dict[str, str]] = []
    current_qid: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()

        qid_match = re.search(r"QID\s+([A-Za-z0-9_-]+)", stripped)
        if qid_match:
            current_qid = qid_match.group(1)
            continue

        if not current_qid:
            continue

        if not stripped.startswith("|"):
            continue

        if "---" in stripped:
            continue

        lower = stripped.lower()
        if "big 3 element category" in lower and "your answer" in lower:
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]

        if len(cells) < 3:
            continue

        category, question, answer = cells[0], cells[1], cells[2]

        if not answer.strip():
            continue

        answers.append(
            {
                "qid": current_qid,
                "category": category,
                "question": question,
                "answer": answer,
            }
        )

    return answers


def _normalize_answer(answer: str) -> str:
    cleaned = answer.strip()

    if cleaned.lower() in {"unknown", "unk", "not sure", "n/a", "na"}:
        return "Unknown"

    return cleaned


def _apply_answers_to_unknowns(
    state: GrossState,
    parsed_answers: list[dict[str, str]],
) -> None:
    truth_pack = state.setdefault("truth_pack", {})
    unknowns = truth_pack.setdefault("unknowns", [])
    augmentations = truth_pack.setdefault("pfr_augmentations", [])

    qid_to_unknown_index = _build_qid_to_unknown_index(
        state.get("feedback_questions", []),
        unknowns,
    )

    for parsed in parsed_answers:
        qid = parsed["qid"]
        normalized = _normalize_answer(parsed.get("answer", ""))
        unknown_index = qid_to_unknown_index.get(qid)

        if unknown_index is None or unknown_index >= len(unknowns):
            augmentations.append(
                {
                    "qid": qid,
                    "answer": normalized,
                    "applied_to": None,
                    "note": "Could not map QID to unknown.",
                }
            )
            continue

        unknown = unknowns[unknown_index]
        unknown["blocks_generation"] = False
        unknown["resolved_by_pfr"] = True
        unknown["pfr_qid"] = qid
        unknown["pfr_answer"] = normalized

        augmentations.append(
            {
                "qid": qid,
                "scope": unknown.get("scope"),
                "missing_field": unknown.get("missing_field"),
                "answer": normalized,
                "applied_to": "truth_pack.unknowns",
                "unknown_index": unknown_index,
            }
        )


def _build_qid_to_unknown_index(
    feedback_questions: list[dict[str, Any]],
    unknowns: list[dict[str, Any]],
) -> dict[str, int]:
    mapping: dict[str, int] = {}

    for item in feedback_questions:
        qid = item.get("qid")
        index = item.get("unknown_index")

        if qid is not None and isinstance(index, int):
            mapping[str(qid)] = index

    if mapping:
        return mapping

    return {f"Q{idx}": idx - 1 for idx, _ in enumerate(unknowns, start=1)}
