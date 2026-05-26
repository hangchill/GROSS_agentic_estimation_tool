# GROSS Estimation Workflow 
 
## 1) Project Description
 
This repo implements a **stateful GenAI workflow** that turns high-level requirement inputs (e.g., slide text) into **structured development effort estimates**. It does this in two main phases:
 
- **Extraction**: convert unstructured requirements into structured “requirements data” (truth pack), detect gaps, and determine readiness.
- **Generation**: produce effort groupings (worktype / complexity / count / description), apply corrections, verify, and finalize.
 
The workflow includes a **feedback loop** when extraction is incomplete and only proceeds to generation when requirements are ready. This follows the workflow design you provided (extraction → readiness gating → generation → verification).
---
 
## 2) Quickstart 
 
### 2.1 Set environment
 
You need an OpenAI API key (used by the LLM calls and also by Mem0 embeddings).
 
    export OPENAI_API_KEY="YOUR_KEY_HERE"
 
Optional (model override):
 
    export OPENAI_MODEL="gpt-4o-mini"
 
### 2.2 (One-time) Bootstrap Mem0 memory
 
This loads your seed memory documents (team context, glossary, historical CR patterns) into Mem0.
 
    python -m scripts.memory_bootstrap_mem0
 
(Optional) Validate memory retrieval:
 
    python -m scripts.memory_test_mem0
 
Mem0 is used as the memory store as per your workflow’s memory concept: team context, glossary/rubrics, and historical CR patterns. 

### 2.3 Run the end-to-end workflow demo
 
    python -m scripts.run_demo
 
The demo script runs the main workflow graph and prints:
- a short run summary
- a clean final estimate output (worktype/complexity/count)
 
---
 
## 3) Inputs and outputs
 
### 3.1 Input format (JSON)
 
The workflow expects an input JSON with:
- target DM (optional but recommended)
- functionality_description
- slides[] (each slide has index/title/text)
 
Example:
 
    {
      "target_dm": "HealthPlan DM",
      "functionality_description": "User views and selects a plan",
      "slides": [
        { "slide_index": "S1", "title": "Plan Listing", "text": "User sees available plans." },
        { "slide_index": "S2", "title": "Plan Selection", "text": "User selects a plan and data is retrieved from Health API." }
      ]
    }
 
This mirrors the workflow’s assumption that requirements are provided via a deck (represented as text for this PoC). 
 
### 3.2 Output format (final estimates)
 
Final output is a list of effort groupings:
 
    Worktype (Complexity x Count)
    → Description
 
Example:
 
    Page (S x 1)
    → View available health plans
 
    Interface (S x 1)
    → Retrieve plan data from Health API
 
    Component (M x 1)
    → Implement backend capability for plan selection
 
This matches the effort grouping format described in the project material.
---
 
## 4) Repo structure 
 
Recommended Route:
 
1) src/schemas/state.py
2) src/llm/client.py
3) src/graphs/extraction/graph.py + routing.py
4) src/graphs/generation/graph.py + routing.py
5) src/graphs/main/graph.py + routing.py
6) src/memory/mem0_client.py
7) scripts/run_demo.py
 
Directory overview:
 
    src/
      schemas/
        state.py
      llm/
        client.py
      graphs/
        extraction/
          nodes/
          routing.py
          graph.py
        generation/
          nodes/
          routing.py
          graph.py
        main/
          routing.py
          graph.py
        checkpoints.py
        node_utils.py
      memory/
        mem0_client.py
 
    scripts/
      run_demo.py
      memory_bootstrap_mem0.py
      memory_test_mem0.py
 
    data/
      samples/
      memory_seed/
 
    tests/
      conftest.py
      unit/
 
---
 
## 5) Conceptual Understanding of each Phase
 
### 5.1 Extraction Phase (slides → truth pack + readiness)
 
Extraction decomposes requirements into:
- structure/scope (DM, functionalities, FCUs)
- artefacts and flows
- systems and interfaces
- variant axes
- backend I/P/O capabilities
- synthesis + explicit unknowns
- readiness assessment
- feedback questions if incomplete
 
This corresponds to the extraction steps described in your workflow spec. 
 
### 5.2 Generation phase (truth pack → Set A → Set B → verify → Set C)
 
Generation does:
- scope filter (select relevant slice of truth pack)
- derive impacts (UI / interface / backend)
- Set A (initial draft effort groupings)
- Set B (correction/consolidation)
- CoVE verification (PASS/FAIL)
- finalize Set C output
 
This corresponds to the generation steps described in your workflow spec.
 
---
 
## 6) Memory (Mem0) 
 
This repo uses Mem0 to store and retrieve three memory partitions:
 
- team_context
  - canonical system names, acronyms, terminology conventions
- worktype_glossary
  - worktype definitions and complexity rubric
- historical_cr
  - historical CR context used for sanity checks / ambiguity detection (not direct estimation)
 
Seed documents are in:
 
    data/memory_seed/
      team_context.md
      worktype_glossary.md
      historical_crs.md
 
Mem0 is configured explicitly in src/memory/mem0_client.py (so it does not use any default “future” model), and bootstrap scripts load the seed docs. Mem0 configuration follows the documented config override approach.
 
---
 
## 7) Tests
 
Run tests:
 
    pytest -q
 
Tests are written to avoid calling the real LLM by mocking LLMClient, and include:
- node-level tests (extraction + generation)
- graph-level tests (subgraphs + main graph)
 
---
 
## 8) Documentation
 
- [DESIGN.md](./docs/DESIGN.md) explains architecture, routing logic, and node interactions in detail.
- [CONFIGURATION.md](./docs/CONFIGURATION.md) provides details for all configurable knobs (model, memory seeds, demo inputs, iteration/retry caps, logging).
 