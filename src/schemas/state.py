from typing import Any, Dict, List, Literal, Optional, TypedDict

Phase = Literal[
    "INITIALIZING", "EXTRACTION", "AWAITING_USER_INPUT", "GENERATION", "DONE"
]


class GrossState(TypedDict):
    # ----- Identity and Run Control -----
    thread_id: str  # for persistent threads
    run_id: str
    phase: Phase
    iteration: int  # feedback iteration counter (starts from 1)
    max_iterations: int  # coded to stop at 3

    # ----- Input Values -----
    inputs: Dict[str, Any]  # contains text/parsed slides + CRA context + user query

    # ----- Extraction Outputs -----
    fcu_registry: List[Dict[str, Any]]
    truth_pack: Dict[str, Any]
    readiness: Dict[str, Any]
    feedback_template_md: Optional[str]
    user_answers_md: Optional[str]  # raw pasted user answers
    pfr: Dict[str, Any]  # stands for Permanent Feedback Repository

    # ----- Generation Outputs -----
    effort_final: List[
        Dict[str, Any]
    ]  # final Set C-like lines (worktype/complexity/count/description)

    # ----- Memory Context -----
    team_memory: List[Dict[str, Any]]

    # ---- Audit / Telemetry ----
    events: List[Dict[str, Any]]  # node events / warnings
    errors: List[Dict[str, Any]]  # error records (if any)
