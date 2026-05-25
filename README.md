# GROSS Estimation Project
 
## Overview
 
This project is a GenAI-powered workflow that generates development effort estimates from high-level requirement inputs.
 
In software projects:
- A Change Request (CR) is broken into Demand Modules (DMs)
- Each DM contains functionalities (features)
- Each functionality needs an effort estimate
 
This system automates that process using a structured workflow instead of a single prompt.
 
---
 
## What This System Does
 
The system behaves like a junior engineer:
 
- Reads requirement inputs (slides)
- Structures them into organised data
- Detects missing information
- Generates clarification questions if needed
- Produces effort estimates
- Verifies and refines results
 
---
 
## Workflow
 
The system follows this flow:
 
- Input
- Extraction
- Feedback loop (if required)
- Generation
- Final output
 
---
 
## Project Structure
 
    src/
      graphs/
        extraction/
          nodes/
            ingest.py
            structure_scope.py
            artefacts_flows.py
            systems_interfaces.py
            variant_axes.py
            backend_ipo.py
            synth_unknowns.py
            pfr_merge.py
            readiness_big3.py
            feedback_template.py
          routing.py
          graph.py
 
        generation/
          nodes/
            scope_filter.py
            impacts_ui.py
            impacts_interfaces.py
            impacts_backend.py
            groupings_seta.py
            correct_setb.py
            verify_cove.py
            finalize_setc.py
          routing.py
          graph.py
 
        main/
          routing.py
          graph.py
 
        checkpoints.py
        node_utils.py
 
      llm/
        client.py
 
      schemas/
        state.py
 
      utils/
        logger.py
 
    scripts/
      run_demo.py
 
    data/
      samples/
        sample_input_incomplete.json
        sample_input_minimal.json
        sample_answers.md
 
    tests/
      unit/
 
---
 
## Setup
 
Create virtual environment:
 
    python3 -m venv venv
    source venv/bin/activate
 
Install dependencies:
 
    pip install -r requirements.txt
 
Set OpenAI API key:
 
    export OPENAI_API_KEY="YOUR_API_KEY"
 
(Optional)
 
    export OPENAI_MODEL="gpt-4o-mini"
 
---
 
## Running the Demo
 
Run:
 
    python -m scripts.run_demo
 
This will:
- Run a first pass using input JSON
- Then simulate a resume flow using answers
 
---
 
## Sample Input (Minimal)
 
    {
      "target_dm": "HealthPlan DM",
      "project_description": "Enhancement to health plan portal",
      "functionality_description": "User views plan details and selects a plan",
      "slides": [
        {
          "slide_index": "S1",
          "title": "Plan Listing Page",
          "text": "User sees a list of available plans"
        },
        {
          "slide_index": "S2",
          "title": "Selection",
          "text": "User selects a plan and details are retrieved"
        }
      ]
    }
 
Expected:
- Goes directly to generation
- Produces final estimation output
 
---
 
## Sample Input (Triggers Feedback)
 
    {
      "target_dm": "HealthPlan DM",
      "functionality_description": "User views plan",
      "slides": [
        {
          "slide_index": "S1",
          "title": "Page",
          "text": "User views something"
        }
      ]
    }
 
Expected:
- Extraction runs
- Missing info detected
- System pauses (AWAITING_USER)
 
---
 
## Sample Answers
 
    ## Section 1 — QID Q1
 
    | Category | Question | Answer |
    |---|---|---|
    | Implementation | Which system provides data? | Health API |
 
Expected:
- Answers merged
- Extraction re-run
- Generation triggered
 
---
 
## Extraction Nodes
 
These convert raw input into structured data.
 
- ingest_inputs
  - Validates inputs
 
- structure_scope
  - Identifies DM, functionalities, FCUs
 
- artefacts_flows
  - Extracts UI elements and flows
 
- systems_interfaces
  - Identifies systems and integrations
 
- variant_axes
  - Detects variations (user types, conditions)
 
- backend_ipo
  - Extracts backend logic (Input, Process, Output)
 
- synth_unknowns
  - Combines all extracted data
  - Identifies gaps
 
- pfr_merge
  - Applies user answers
 
- readiness_big3
  - Determines READY or OPEN
 
- feedback_template
  - Generates clarification questions
 
---
 
## Generation Nodes
 
These create effort estimates.
 
- scope_filter
  - Selects relevant data
 
- impacts_ui
  - UI/frontend work
 
- impacts_interfaces
  - Integration work
 
- impacts_backend
  - Backend logic work
 
- groupings_seta
  - Initial estimate
 
- correct_setb
  - Refines estimate
 
- verify_cove
  - Validates correctness
 
- finalize_setc
  - Produces final output
 
---
 
## Output Example
 
    Page (S x 1)
    → View available plans
 
    Interface (S x 1)
    → Retrieve data from API
 
    Component (M x 1)
    → Backend processing
 
---
 
## Testing
 
Run tests:
 
    pytest -q
 
Includes:
- Node tests
- Graph tests
- Mocked LLM calls
 
---
 
## Logging
 
The system logs:
- node execution
- key inputs/outputs
- routing decisions
 
This helps debugging and demos.
 
---
 
## Demo Tips
 
To show feedback loop:
- run incomplete input
- show pause
- then resume with answers
 
To show full pipeline:
- run minimal input
- show final output
 
---
 
## Summary
 
This project demonstrates a production-style GenAI workflow with:
 
- Structured reasoning
- Multi-step execution
- Feedback loops
- Verification mechanisms
- Real-world engineering practices