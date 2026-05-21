import json
import uuid
from pathlib import Path

from src.graphs.checkpoints import make_config, make_sqlite_checkpointer
from src.graphs.main.graph import build_main_graph


# ✅ ✅ pretty output (THIS is the key upgrade)
def pretty_print_result(result):
    print("\n==============================")
    print("✅ FINAL ESTIMATION OUTPUT")
    print("==============================\n")

    effort = result.get("effort_final", [])

    if not effort:
        print("⚠️ No estimation produced\n")
        return

    for item in effort:
        worktype = item.get("worktype", "Unknown")
        complexity = item.get("complexity", "").upper()
        count = item.get("count", 0)
        desc = item.get("description", "")

        print(f"{worktype} ({complexity} x {count})")
        print(f"→ {desc}\n")

    print("==============================\n")


# ✅ optional: show phase summary
def print_phase_summary(result):
    print("\n📊 WORKFLOW SUMMARY")
    print("------------------------------")
    print(f"Phase: {result.get('phase')}")
    print(f"Iteration: {result.get('iteration')}")
    print(f"Verification attempts: {result.get('verification_attempts')}")
    print("------------------------------\n")


# ✅ helper: run new case
def run_case(input_file: str, debug: bool = False):
    print("\n🚀 Running workflow...\n")

    inputs = json.loads(Path(input_file).read_text())

    state = {
        "thread_id": "demo-thread",
        "run_id": str(uuid.uuid4()),
        "phase": "INIT",
        "iteration": 1,
        "max_iterations": 3,
        "verification_attempts": 0,
        "max_verification_attempts": 2,
        "inputs": inputs,
        "events": [],
        "errors": [],
    }

    checkpointer = make_sqlite_checkpointer()
    graph = build_main_graph(checkpointer=checkpointer)
    config = make_config(state["thread_id"])

    result = graph.invoke(state, config=config)

    # ✅ show clean summary
    print_phase_summary(result)

    # ✅ show clean result
    if result.get("phase") == "DONE":
        pretty_print_result(result)
    else:
        print("\n⚠️ Awaiting user input (feedback loop triggered)\n")

    # ✅ optional debug (raw JSON)
    if debug:
        print("\n=== DEBUG RAW OUTPUT ===")
        print(json.dumps(result, indent=2))

    print("\n✅ Workflow complete!\n")

    return state


# ✅ helper: resume with answers
def resume_case(state, answers_file: str, debug: bool = False):
    print("\n🔁 Resuming workflow with user answers...\n")

    answers = Path(answers_file).read_text()

    checkpointer = make_sqlite_checkpointer()
    graph = build_main_graph(checkpointer=checkpointer)
    config = make_config(state["thread_id"])

    snapshot = graph.get_state(config)
    state = snapshot.values

    state["iteration"] = state.get("iteration", 1) + 1
    state["user_answers_raw"] = answers

    result = graph.invoke(state, config=config)

    # ✅ summary
    print_phase_summary(result)

    # ✅ final result
    pretty_print_result(result)

    if debug:
        print("\n=== DEBUG RAW OUTPUT ===")
        print(json.dumps(result, indent=2))

    print("\n✅ Resume complete!\n")

    return result


# ✅ ✅ ENTRYPOINT
if __name__ == "__main__":
    # state = run_case("data/samples/sample_input_incomplete.json")

    # resume_case(state, "data/samples/sample_answers.md")
    state = run_case("data/samples/demo_input.json")
