from typing import Any, Dict, List, Literal, Optional, TypedDict

Phase = Literal[
    "INIT",
    "EXTRACTION",
    "AWAITING_USER",
    "GENERATION",
    "DONE",
    "TERMINATED_INSUFFICIENT_DATA",
]


class GrossState(TypedDict, total=False):
    """
    Shared state passed between all graph nodes.

    This acts as case working memory for the workflow. It stores:
    - runtime inputs
    - extracted requirement data
    - readiness / feedback loop information
    - generation outputs
    - trace events and errors

    """

    # Workflow identity / control
    thread_id: str
    run_id: str
    phase: Phase

    # Extraction feedback loop control
    iteration: int
    max_iterations: int  # ideally set to 3

    # Generation verification loop control
    verification_attempts: int
    max_verification_attempts: int

    # Runtime input payload
    inputs: Dict[str, Any]

    # Extraction outputs
    truth_pack: Dict[str, Any]
    fcu_registry: List[Dict[str, Any]]

    # Readiness + feedback
    readiness: Dict[str, Any]
    feedback_template_md: Optional[str]
    feedback_questions: List[Dict[str, Any]]
    user_answers_raw: Optional[str]
    pfr: Dict[str, Any]

    # Generation intermediate + final outputs
    generation_scope: Dict[str, Any]
    ui_impacts: List[Dict[str, Any]]
    interface_impacts: List[Dict[str, Any]]
    backend_impacts: List[Dict[str, Any]]
    set_a: List[Dict[str, Any]]
    set_b: List[Dict[str, Any]]
    verification: Dict[str, Any]
    effort_final: List[Dict[str, Any]]

    # Team memory / reusable context
    team_memory: List[Dict[str, Any]]

    # Traceability
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
