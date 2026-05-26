# CONFIGURATION — What You Can Change (and Where)
 
This document is a **practical map** of everything you can configure or swap in this repo without needing to rewrite workflow logic. It is meant for someone reading the codebase for the first time.
 
The workflow implements:
- Extraction → Readiness + Feedback loop → Generation → Verification → Final output 
- Memory blocks (team context, glossary/rubrics, historical CR patterns) via Mem0 
 
---
 
## 1) Model Configuration (LLM used by workflow)
 
### 1.1 Main LLM model for node execution
**Where to change**
- `src/llm/client.py` (primary control point)
- Environment variable `OPENAI_MODEL` (recommended for ops)
 
**What to change**
- Set model via environment:
 
    export OPENAI_MODEL="gpt-4o-mini"
 
This keeps code unchanged and allows switching per environment (demo vs dev vs CI).
 
**Notes**
- Node code calls `LLMClient().json_call(...)` everywhere; `LLMClient` is the single gateway.
 
---
 
## 2) Memory Configuration (Mem0)
 
This repo uses Mem0 as memory store (agent memory), separated into three partitions (stored via filters/user_id):
 
- `team_context` — acronyms, canonical system names, terminology conventions 
- `worktype_glossary` — worktype definitions + complexity rubric 
- `historical_cr` — historical CR context used for sanity checks / ambiguity detection (not direct estimation)  
 
### 2.1 Mem0 model configuration (important)
Mem0 uses an LLM + embeddings internally. If you don’t explicitly configure it, Mem0 may use defaults. Mem0 supports explicit configuration via `Memory.from_config(...)`, and config values take precedence over env vars and defaults.
 
**Where to change**
- `src/memory/mem0_client.py`
 
**What to change**
- The model Mem0 uses for its internal processing (set explicitly in config)
- Keep this aligned with your available OpenAI model(s)
 
### 2.2 Memory seed documents (the content you “teach” the system)
**Where to change**
- `data/memory_seed/team_context.md`
- `data/memory_seed/worktype_glossary.md`
- `data/memory_seed/historical_crs.md`
 
**What to change**
- Add new acronyms / canonical system names to `team_context.md` 
- Update worktypes or complexity rubric in `worktype_glossary.md` 
- Add new historical CR patterns/records in `historical_crs.md` (used for sanity checks only) 
 
### 2.3 Re-bootstrap memory after editing seed files
Whenever you edit any `data/memory_seed/*.md`, re-run:
 
    python -m scripts.memory_bootstrap_mem0
 
(Optional) verify retrieval:
 
    python -m scripts.memory_test_mem0
 
This keeps memory aligned with the latest seed docs.
 
---
 
## 3) Feedback Loop Controls (iterations)
 
Your workflow specification includes an iteration cap (max feedback iterations). 
 
### 3.1 Where iteration cap is set
**Primary places to edit**
- `scripts/run_demo.py` (initial state seed)
- `src/graphs/extraction/nodes/ingest.py` (default initialization if missing)
- `src/graphs/main/routing.py` (controls route to terminate vs await user) 
 
**What to change**
- `max_iterations` (e.g., default is 3)
 
Example (in the initial state creation):
 
    "iteration": 1,
    "max_iterations": 3,
 
This matches the process control gate described in the workflow spec.
 
---
 
## 4) Generation Verification Loop Controls (retries)
 
Your generation design includes verification (PASS/FAIL) and bounded retries to prevent infinite loops. 
 
**Where to change**
- `scripts/run_demo.py` (initial state seed)
- `src/graphs/main/graph.py` (defaults for verification_attempts / max_verification_attempts)
- `src/graphs/generation/routing.py` (verification failed → loop or finalize) 
**What to change**
- `max_verification_attempts` (default commonly 2)
 
Example:
 
    "verification_attempts": 0,
    "max_verification_attempts": 2,
 
---
 
## 5) Sample Inputs / Demo Data
 
### 5.1 Where sample inputs live
- `data/samples/` (JSON inputs and answer templates)
 
Common files:
- `data/samples/demo_input.json`
- `data/samples/sample_answers.md`
 
### 5.2 Where the demo script reads inputs
- `scripts/run_demo.py`
 
**What to change**
- Input file path(s)
- Answer file path(s)
- Thread ID (if you want multiple separate runs) 
 
This is the easiest way to create multiple demo scenarios without touching code logic.
 
---
 
## 6) Prompts (how the LLM is instructed)
 
Prompts are embedded per node (each node has `SYSTEM_PROMPT` and a user prompt).
 
**Where to change**
- Extraction prompts:
  - `src/graphs/extraction/nodes/*.py`
- Generation prompts:
  - `src/graphs/generation/nodes/*.py`
 
**Recommended practice**
- If you anticipate frequent prompt edits, move prompts into a dedicated directory (e.g., `src/prompts/`) and load them from files. This reduces merge conflicts and makes versioning easier (optional future improvement). 
 
---
 
## 7) Logging (verbosity and what gets printed)
 
### 7.1 Where logging is configured
- `src/utils/logger.py` (if you created it)
- or node-local loggers inside each node file
 
### 7.2 What to change
- Log level (INFO/DEBUG)
- Whether to print raw JSON results vs pretty output
 
### 7.3 Demo printing (user-friendly output)
- `scripts/run_demo.py` typically contains pretty-print helpers to show final estimates cleanly.
 
---
 
## 8) Checkpointing / Resume
 
Checkpointing is what enables “pause for feedback, then resume after user answers”.
 
**Where to change**
- `src/graphs/checkpoints.py` (sqlite path and config builder)
 
**What to change**
- checkpoint database location (e.g. `.checkpoints/langgraph.sqlite3`)
- thread_id naming conventions (how you segment runs)
 
This matches the workflow’s pause/resume requirement for feedback loops. 
 
---
 
## 9) Tests (what is safe to change)
 
### 9.1 LLM mocking in tests
**Where to change**
- `tests/conftest.py`
 
This is where LLM calls are mocked so tests run without consuming quota.
 
### 9.2 Adding new nodes
If you add a new node:
- create a unit test in `tests/unit/test_extraction_nodes.py` or `tests/unit/test_generation_nodes.py`
- if it changes routing, add/adjust `test_*_graph.py` tests
 
---
 
## 10) Quick “Knobs Checklist” (most commonly edited)
 
If you only remember one section, remember this list:
 
- Model used by workflow:
  - `OPENAI_MODEL` env var
  - `src/llm/client.py`
 
- Mem0 seed memory content:
  - `data/memory_seed/team_context.md`
  - `data/memory_seed/worktype_glossary.md`
  - `data/memory_seed/historical_crs.md`
  - re-run `python -m scripts.memory_bootstrap_mem0`
 
- Feedback loop cap:
  - `max_iterations` in `scripts/run_demo.py` (and defaults in ingest/routing) 
 
- Verification retries:
  - `max_verification_attempts` in `scripts/run_demo.py` and generation routing 
 
- Demo inputs:
  - `data/samples/*.json`
  - `scripts/run_demo.py`
 
---
 
## 11) Suggested edit workflow (recommended)
 
When making configuration changes:
 
1) Update the relevant file (seed doc, env var, demo input).
2) If memory seed doc changed → run:
 
    python -m scripts.memory_bootstrap_mem0
 
3) Run a demo:
 
    python -m scripts.run_demo
 
4) Run tests:
 
    pytest -q



 