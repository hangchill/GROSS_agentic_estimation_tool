# WORKFLOW TRACE - Complete Example End-to-End

## Overview
This document traces **ONE complete execution** through the entire workflow with a **concrete example**.

Input → Extraction (8 nodes) → Readiness Check → Generation (7 nodes) → Verification → Output

---

## EXAMPLE INPUT

```json
{
  "target_dm": "HealthPlan DM",
  "functionality_description": "User views and selects a health insurance plan",
  "slides": [
    {
      "slide_index": "S1",
      "title": "Plan Listing Page",
      "text": "User lands on a page that displays available health plans with summary details"
    },
    {
      "slide_index": "S2",
      "title": "Plan Selection",
      "text": "User selects a plan and system retrieves plan details from Health API"
    }
  ]
}
```

---

# PHASE 1: EXTRACTION (Main Graph calls Extraction Subgraph)

## Node 1: `ingest_inputs`
**File:** `src/graphs/extraction/nodes/ingest.py`

**What it does:**
- Takes raw input JSON
- Seeds the state with initial values
- Initializes iteration counters, empty lists, etc.

**Input (user provides):**
```json
{
  "target_dm": "HealthPlan DM",
  "functionality_description": "User views and selects a health insurance plan",
  "slides": [...]
}
```

**State after this node:**
```python
state = {
    "inputs": {...},           # stored as-is
    "truth_pack": {},          # empty, will be filled by subsequent nodes
    "fcu_registry": [],        # empty unknown-tracking list
    "iteration": 1,
    "max_iterations": 3,
    "phase": "EXTRACTION",
    "events": [
        {"node": "ingest_inputs", "timestamp": "...", "message": "Ingested 2 slides"}
    ]
}
```

---

## Node 2: `structure_scope`
**File:** `src/graphs/extraction/nodes/structure_scope.py`

**What it does:**
- Calls LLM to understand the target domain model (HealthPlan DM)
- Identifies the "scope" of this change
- Produces: domain focus, change context, assumptions

**LLM Call:**
```
SYSTEM: You are a requirements analyst. Analyze the domain model and functionality.
USER: 
  Target: HealthPlan DM
  Functionality: User views and selects a health insurance plan
  Slides: [S1: listing page, S2: selection + Health API retrieval]

Produce JSON with: domain_focus, change_context, assumptions
```

**LLM Returns:**
```json
{
  "domain_focus": "Health plan selection workflow for insurance platform",
  "change_context": "New user-facing feature to browse and select plans",
  "assumptions": [
    "Health API is already available",
    "Plan data is pre-loaded into system",
    "User session exists"
  ]
}
```

**State after this node:**
```python
state["truth_pack"] = {
    "domain_focus": "Health plan selection workflow for insurance platform",
    "change_context": "New user-facing feature to browse and select plans",
    "assumptions": [...]
}
state["events"].append({"node": "structure_scope", "message": "Structured scope"})
```

---

## Node 3: `artefacts_flows`
**File:** `src/graphs/extraction/nodes/artefacts_flows.py`

**What it does:**
- Identifies **UI flows** and **data flows** from the requirement text
- Finds screens, pages, transitions, data movements

**LLM Call (uses slides + scope from truth_pack):**
```
SYSTEM: Identify user flows and data flows from requirements.
USER:
  Scope: {domain_focus, change_context, assumptions}
  Slides:
    S1: User lands on page displaying available health plans
    S2: User selects plan, system retrieves plan details from Health API
```

**LLM Returns:**
```json
{
  "ui_flows": [
    {
      "name": "view_plans",
      "screens": ["PlanListingPage"],
      "transitions": ["PlanListingPage -> PlanDetailPage (on selection)"]
    }
  ],
  "data_flows": [
    {
      "name": "fetch_plans",
      "source": "HealthAPI",
      "destination": "PlanListingPage",
      "trigger": "page load"
    },
    {
      "name": "fetch_plan_details",
      "source": "HealthAPI",
      "destination": "PlanDetailPage",
      "trigger": "user selection"
    }
  ]
}
```

**State after this node:**
```python
state["truth_pack"].update({
    "ui_flows": [...],
    "data_flows": [...]
})
state["events"].append({"node": "artefacts_flows", "message": "Identified 2 data flows"})
```

---

## Node 4: `systems_interfaces`
**File:** `src/graphs/extraction/nodes/systems_interfaces.py`

**What it does:**
- Identifies **external systems** that are accessed
- For each external system, flags it as an "interface" requirement

**LLM Call (uses data flows):**
```
SYSTEM: Extract all external system integrations mentioned.
USER: 
  Data flows: [fetch_plans from HealthAPI, fetch_plan_details from HealthAPI]
  
Produce JSON with: external_systems, integrations
```

**LLM Returns:**
```json
{
  "external_systems": ["HealthAPI"],
  "integrations": [
    {
      "system": "HealthAPI",
      "calls": [
        {"name": "get_plans", "method": "GET /plans"},
        {"name": "get_plan_details", "method": "GET /plans/{id}"}
      ]
    }
  ]
}
```

**State after this node:**
```python
state["truth_pack"].update({
    "external_systems": ["HealthAPI"],
    "integrations": [...]
})
state["events"].append({"node": "systems_interfaces", "message": "Found 1 external system: HealthAPI"})
```

---

## Node 5: `variant_axes`
**File:** `src/graphs/extraction/nodes/variant_axes.py`

**What it does:**
- Identifies **variations** or **conditional logic** (e.g., "if user is mobile", "if plans > X")
- Finds feature flags, A/B testing, multiple paths

**LLM Call:**
```
SYSTEM: Identify any variants, conditionals, or variations mentioned.
USER: [slides text + truth pack]
```

**LLM Returns:**
```json
{
  "variants": [
    {
      "axis": "device_type",
      "values": ["desktop", "mobile"],
      "note": "Plan listing may need mobile optimization"
    }
  ],
  "conditionals": [
    "If plan is unavailable in region, show message"
  ]
}
```

**State after this node:**
```python
state["truth_pack"].update({
    "variants": [...],
    "conditionals": [...]
})
```

---

## Node 6: `backend_ipo`
**File:** `src/graphs/extraction/nodes/backend_ipo.py`

**What it does:**
- Identifies **backend capabilities** required
- Maps: INPUT → PROCESS → OUTPUT for each backend operation

**LLM Call:**
```
SYSTEM: For each backend operation, identify Input / Process / Output.
USER: [truth pack + integrations]
```

**LLM Returns:**
```json
{
  "backend_operations": [
    {
      "name": "fetch_available_plans",
      "input": "user_id, region",
      "process": "Query HealthAPI, filter by region, check coverage",
      "output": "List[Plan]",
      "data_dependencies": ["HealthAPI"]
    },
    {
      "name": "select_plan",
      "input": "user_id, plan_id",
      "process": "Validate plan availability, create enrollment record",
      "output": "enrollment_confirmation",
      "data_dependencies": ["Plan", "HealthAPI"]
    }
  ]
}
```

**State after this node:**
```python
state["truth_pack"].update({
    "backend_operations": [...]
})
```

---

## Node 7: `synth_unknowns`
**File:** `src/graphs/extraction/nodes/synth_unknowns.py`

**What it does:**
- **Synthesizes** unknowns from the extracted data
- Looks for **gaps** or **ambiguities**
- Creates "Fully Clarified Unknowns" (FCUs) — things that are unclear

**LLM Call:**
```
SYSTEM: Identify what is NOT mentioned but should be clarified.
USER: [all truth pack data collected so far]

Look for gaps in: UI details, data validation, error handling, 
business rules, performance requirements, etc.
```

**LLM Returns:**
```json
{
  "unknowns": [
    {
      "id": "FCU-1",
      "question": "What happens if HealthAPI call fails? Retry? Offline mode?",
      "context": "backend_ipo::fetch_available_plans",
      "severity": "HIGH"
    },
    {
      "id": "FCU-2",
      "question": "Should plan list be paginated? If so, page size?",
      "context": "ui_flows::view_plans",
      "severity": "MEDIUM"
    },
    {
      "id": "FCU-3",
      "question": "What is the expected latency for plan retrieval?",
      "context": "performance",
      "severity": "LOW"
    }
  ]
}
```

**State after this node:**
```python
state["truth_pack"].update({
    "unknowns": [...]
})
state["fcu_registry"] = [
    {"id": "FCU-1", "question": "...", "severity": "HIGH"},
    {"id": "FCU-2", "question": "...", "severity": "MEDIUM"},
    {"id": "FCU-3", "question": "...", "severity": "LOW"}
]
state["events"].append({"node": "synth_unknowns", "message": "Synthesized 3 unknowns"})
```

---

## Node 8: Check for User Answers (Routing Decision)
**File:** `src/graphs/extraction/routing.py`

**Question:** Does `state["user_answers_raw"]` exist?

**Answer:** NO (this is first iteration, user hasn't been asked yet)

**Routing:** Go to `readiness_big3` node

---

## Node 9: `readiness_big3`
**File:** `src/graphs/extraction/nodes/readiness_big3.py`

**What it does:**
- Computes a **readiness score** based on unknowns
- Rule: If ANY FCU exists → OPEN (incomplete)
- Rule: If NO FCUs → READY (complete)

**LLM Call (optional, for readiness reasoning):**
```
SYSTEM: Assess readiness based on unknowns.
USER: 
  FCUs found: 3
  Severity breakdown: 1 HIGH, 1 MEDIUM, 1 LOW
```

**Readiness Result:**
```json
{
  "status": "OPEN",
  "reason": "3 unknowns identified (1 HIGH, 1 MEDIUM, 1 LOW)",
  "critical_gaps": ["FCU-1: Error handling for HealthAPI"],
  "can_proceed_to_generation": false,
  "needs_feedback": true
}
```

**State after this node:**
```python
state["readiness"] = {
    "status": "OPEN",
    "reason": "3 unknowns identified",
    "critical_gaps": [...]
}
state["phase"] = "AWAITING_USER"
state["events"].append({"node": "readiness_big3", "message": "Status: OPEN (3 FCUs)"})
```

---

## Node 10: Check Readiness + Iteration (Main Routing)
**File:** `src/graphs/main/routing.py`

**Decision Gate:**
```
Is readiness.status == "READY"?  → NO
Is iteration <= max_iterations?  → YES (iteration=1, max=3)
```

**Routing:** Go to `feedback_template` node

---

## Node 11: `feedback_template`
**File:** `src/graphs/extraction/nodes/feedback_template.py`

**What it does:**
- Generates a **markdown template** with clarifying questions
- Based on unknowns (FCUs)
- Formatted for user to fill in

**LLM Call:**
```
SYSTEM: Generate a feedback template (markdown) based on unknowns.
USER: [3 FCUs]
```

**Template Generated:**
```markdown
# Feedback Questions for Health Plan Selection Feature

## Critical Questions

**FCU-1: Error Handling**
- **Question:** What happens if the HealthAPI call fails? 
  - Should the system retry automatically? 
  - How many retries?
  - Should we show an offline mode or error message?
- **Answer:** [FILL IN]

## Medium Priority

**FCU-2: Pagination**
- **Question:** Should the plan list be paginated?
  - If yes, what page size?
  - Load more or traditional pagination?
- **Answer:** [FILL IN]

## Low Priority

**FCU-3: Performance**
- **Question:** What is the expected latency for plan retrieval?
  - Target response time?
  - Acceptable max latency?
- **Answer:** [FILL IN]
```

**State after this node:**
```python
state["feedback_template_md"] = "# Feedback Questions...\n..."
state["feedback_questions"] = [
    {
        "fcu_id": "FCU-1",
        "question": "What happens if HealthAPI call fails?",
        "severity": "HIGH"
    },
    ...
]
state["events"].append({"node": "feedback_template", "message": "Generated feedback template"})
```

---

## Node 12: Await User Feedback
**File:** `scripts/run_demo.py` or external input

**In the demo script:**
```python
state["user_answers_raw"] = """
FCU-1: Retry up to 3 times with exponential backoff. If all retries fail, show error message.

FCU-2: Yes, paginate with page size = 10. Use infinite scroll or "Load More" button.

FCU-3: Target latency is 500ms for plan list retrieval. Acceptable max is 2 seconds.
"""
```

---

## Node 13 (Loop Back): `ingest_inputs` → ... → `synth_unknowns` → `pfr_merge`
**File:** `src/graphs/extraction/nodes/pfr_merge.py`

**What it does:**
- Takes `user_answers_raw` (user's feedback)
- Parses it into a structured dict (PFR = Parsed Feedback Response)
- **Merges** the answers back into `truth_pack`

**LLM Call:**
```
SYSTEM: Parse and merge user feedback into the requirements.
USER:
  Original FCUs: [3 unknowns]
  User answers: [responses above]
  
Merge answers back and update truth_pack with clarifications.
```

**PFR (Parsed Feedback Response):**
```json
{
  "FCU-1_error_handling": {
    "strategy": "retry",
    "retry_count": 3,
    "backoff": "exponential",
    "failure_mode": "error_message"
  },
  "FCU-2_pagination": {
    "enabled": true,
    "page_size": 10,
    "style": "infinite_scroll_or_load_more"
  },
  "FCU-3_latency": {
    "target_latency_ms": 500,
    "acceptable_max_ms": 2000
  }
}
```

**State after merge:**
```python
state["pfr"] = {...}
state["truth_pack"].update({
    "error_handling": {...},
    "pagination": {...},
    "performance_targets": {...}
})
state["iteration"] = 2  # increment iteration
state["user_answers_raw"] = None  # clear for next cycle
state["events"].append({"node": "pfr_merge", "message": "Merged 3 user responses"})
```

---

## Node 14: Loop Back to `readiness_big3` (2nd iteration)

**LLM Call:**
```
SYSTEM: Re-assess readiness after merging user feedback.
USER: 
  Updated truth pack with clarifications
  Any remaining unknowns?
```

**LLM Returns:**
```json
{
  "status": "READY",
  "reason": "All critical unknowns resolved with user feedback",
  "critical_gaps": [],
  "can_proceed_to_generation": true
}
```

**State after node:**
```python
state["readiness"]["status"] = "READY"
state["phase"] = "GENERATION"
state["events"].append({"node": "readiness_big3", "message": "Status: READY (iteration 2)"})
```

---

## Node 15: Main Routing Decision (2nd Time)

**Decision Gate:**
```
Is readiness.status == "READY"?  → YES
```

**Routing:** Call Generation Subgraph

---

# PHASE 2: GENERATION (Main Graph calls Generation Subgraph)

## Node 16: `scope_filter`
**File:** `src/graphs/generation/nodes/scope_filter.py`

**What it does:**
- Filters `truth_pack` to identify what actually needs to be **built**
- Removes assumptions, keeps scope
- Produces: filtered scope for estimation

**LLM Call:**
```
SYSTEM: From the truth pack, extract what actually needs to be built.
USER: [complete truth_pack after pfr_merge]
```

**LLM Returns:**
```json
{
  "items_to_build": [
    {
      "name": "PlanListingPage",
      "type": "UI",
      "description": "Page displaying available plans (10 per page, infinite scroll)"
    },
    {
      "name": "fetch_available_plans",
      "type": "backend_operation",
      "description": "Query HealthAPI with retry logic (3 retries, exponential backoff)"
    },
    {
      "name": "PlanDetailPage",
      "type": "UI",
      "description": "Page showing selected plan details"
    },
    {
      "name": "select_plan",
      "type": "backend_operation",
      "description": "Create enrollment record after plan selection"
    },
    {
      "name": "HealthAPI integration",
      "type": "Interface",
      "description": "API integration with error handling and retry"
    }
  ]
}
```

**State after this node:**
```python
state["generation_scope"] = {
    "items_to_build": [...]
}
state["events"].append({"node": "scope_filter", "message": "Filtered to 5 buildable items"})
```

---

## Node 17-19: `impacts_ui`, `impacts_interfaces`, `impacts_backend`
**Files:**
- `src/graphs/generation/nodes/impacts_ui.py`
- `src/graphs/generation/nodes/impacts_interfaces.py`
- `src/graphs/generation/nodes/impacts_backend.py`

**What they do:**
- For each item in scope, produce an **impact analysis**
- Impact = effort required to build/modify

### impacts_ui

**LLM Call:**
```
SYSTEM: Estimate UI effort for each page/component.
USER: [filtered scope for UI items]
```

**LLM Returns:**
```json
{
  "ui_impacts": [
    {
      "name": "PlanListingPage",
      "complexity": "MEDIUM",
      "effort_points": 5,
      "breakdown": "Layout (1pt) + Plan cards (2pt) + Pagination (2pt)"
    },
    {
      "name": "PlanDetailPage",
      "complexity": "SMALL",
      "effort_points": 3,
      "breakdown": "Layout (1pt) + Data display (2pt)"
    }
  ]
}
```

**State after:**
```python
state["ui_impacts"] = [...]
```

### impacts_interfaces

**LLM Call:**
```
SYSTEM: Estimate effort for external system integrations.
USER: [filtered scope for Interface items]
```

**LLM Returns:**
```json
{
  "interface_impacts": [
    {
      "name": "HealthAPI integration",
      "complexity": "MEDIUM",
      "effort_points": 5,
      "breakdown": "SDK setup (1pt) + Error handling (2pt) + Retry logic (2pt)"
    }
  ]
}
```

**State after:**
```python
state["interface_impacts"] = [...]
```

### impacts_backend

**LLM Call:**
```
SYSTEM: Estimate effort for backend operations.
USER: [filtered scope for backend items]
```

**LLM Returns:**
```json
{
  "backend_impacts": [
    {
      "name": "fetch_available_plans",
      "complexity": "MEDIUM",
      "effort_points": 5,
      "breakdown": "Query logic (2pt) + Pagination (2pt) + Caching (1pt)"
    },
    {
      "name": "select_plan",
      "complexity": "SMALL",
      "effort_points": 3,
      "breakdown": "Enrollment logic (2pt) + Validation (1pt)"
    }
  ]
}
```

**State after:**
```python
state["backend_impacts"] = [...]
```

---

## Node 20: `groupings_seta` (Set A: Initial Groupings)
**File:** `src/graphs/generation/nodes/groupings_seta.py`

**What it does:**
- Takes all impacts (UI + Interface + Backend)
- Groups them by **worktype** (Page, Component, Interface, etc.)
- Produces **Set A** — initial effort groupings

**LLM Call:**
```
SYSTEM: Group impacts by worktype. Use memory for worktype definitions.
USER: 
  UI impacts: [...]
  Backend impacts: [...]
  Interface impacts: [...]
  
Use: Page, UI, Component, Interface worktype definitions.
Group and count items by complexity.
```

**LLM Returns (Set A):**
```json
{
  "set_a": [
    {
      "worktype": "Page",
      "complexity": "M",
      "count": 2,
      "items": ["PlanListingPage", "PlanDetailPage"],
      "description": "Plan browsing and detail pages"
    },
    {
      "worktype": "Interface",
      "complexity": "M",
      "count": 1,
      "items": ["HealthAPI integration"],
      "description": "Health API integration with retry logic"
    },
    {
      "worktype": "Component",
      "complexity": "M",
      "count": 2,
      "items": ["fetch_available_plans", "select_plan"],
      "description": "Backend operations for plan retrieval and selection"
    }
  ]
}
```

**State after this node:**
```python
state["set_a"] = [...]
state["events"].append({"node": "groupings_seta", "message": "Created Set A: 3 groupings"})
```

---

## Node 21: `correct_setb` (Set B: Apply Corrections)
**File:** `src/graphs/generation/nodes/correct_setb.py`

**What it does:**
- Takes Set A groupings
- Applies **correction rules** (business rules, team conventions)
- May adjust complexity, split/merge groups, add tasks
- Produces **Set B** — corrected groupings

**Corrections applied:**
- "Pages with pagination should include a UI component for pagination control"
- "API integrations with retry logic may need a retry service component"

**LLM Call:**
```
SYSTEM: Apply correction rules to Set A groupings.
USER:
  Set A: [3 groupings]
  Rules to check:
    1. Pages with pagination → add UI component
    2. Interfaces with retry → add Component
    3. Check for missing cross-cutting items (logging, monitoring)
```

**LLM Returns (Set B):**
```json
{
  "set_b": [
    {
      "worktype": "Page",
      "complexity": "M",
      "count": 2,
      "description": "Plan browsing and detail pages with pagination"
    },
    {
      "worktype": "UI",
      "complexity": "S",
      "count": 1,
      "description": "Pagination control component (Load More button)"
    },
    {
      "worktype": "Component",
      "complexity": "M",
      "count": 2,
      "description": "Plan retrieval and selection operations"
    },
    {
      "worktype": "Component",
      "complexity": "S",
      "count": 1,
      "description": "Retry handler service for HealthAPI calls"
    },
    {
      "worktype": "Interface",
      "complexity": "M",
      "count": 1,
      "description": "Health API integration"
    }
  ]
}
```

**State after this node:**
```python
state["set_b"] = [...]
state["events"].append({"node": "correct_setb", "message": "Applied corrections: Set B has 5 groupings"})
```

---

## Node 22: `verify_cove` (Verification)
**File:** `src/graphs/generation/nodes/verify_cove.py`

**What it does:**
- Validates Set B against business rules
- Checks: completeness, feasibility, consistency
- Returns: PASS or FAIL

**LLM Call:**
```
SYSTEM: Verify Set B groupings against quality checklist.
USER:
  Set B: [5 groupings]
  
Check:
  1. All effort items accounted for?
  2. No missing cross-cutting concerns?
  3. Complexity levels reasonable?
  4. Groupings make sense from effort perspective?
```

**LLM Returns:**
```json
{
  "verification_status": "PASS",
  "reasons": [
    "All UI, Interface, and Backend items accounted for",
    "Pagination and retry handling properly separated",
    "Complexity levels are internally consistent",
    "Groupings align with team's worktype definitions"
  ],
  "warnings": []
}
```

**State after this node:**
```python
state["verification"] = {
    "status": "PASS",
    "reasons": [...]
}
state["events"].append({"node": "verify_cove", "message": "Verification: PASS"})
```

---

## Node 23: Verification Check (Routing)
**File:** `src/graphs/generation/routing.py`

**Decision:**
```
Is verification.status == "PASS"?  → YES
Are verification_attempts > 0?     → (not needed, already passed)
```

**Routing:** Go to `finalize_setc` node

---

## Node 24: `finalize_setc` (Set C: Final Output)
**File:** `src/graphs/generation/nodes/finalize_setc.py`

**What it does:**
- Takes Set B (now verified)
- Formats for final output
- Produces **Set C** — clean, deliverable estimates

**LLM Call:**
```
SYSTEM: Format Set B into final, presentation-ready estimates.
USER: [Set B with verification PASS]

For each grouping, produce:
- worktype
- complexity
- count
- description (user-friendly)
```

**LLM Returns (Set C / Final):**
```json
{
  "effort_final": [
    {
      "worktype": "Page",
      "complexity": "M",
      "count": 2,
      "description": "Plan listing and detail pages with pagination support"
    },
    {
      "worktype": "UI",
      "complexity": "S",
      "count": 1,
      "description": "Pagination control component (Load More button)"
    },
    {
      "worktype": "Component",
      "complexity": "M",
      "count": 2,
      "description": "Backend operations for plan retrieval and selection with error handling"
    },
    {
      "worktype": "Component",
      "complexity": "S",
      "count": 1,
      "description": "Retry handler service for external API calls"
    },
    {
      "worktype": "Interface",
      "complexity": "M",
      "count": 1,
      "description": "Health API integration with exponential backoff and retry logic"
    }
  ]
}
```

**State after this node:**
```python
state["effort_final"] = [...]
state["phase"] = "DONE"
state["events"].append({"node": "finalize_setc", "message": "Final estimates ready"})
```

---

# FINAL OUTPUT

## Printed to User

```
==============================
✅ FINAL ESTIMATION OUTPUT
==============================

Page (M x 2)
→ Plan listing and detail pages with pagination support

UI (S x 1)
→ Pagination control component (Load More button)

Component (M x 2)
→ Backend operations for plan retrieval and selection with error handling

Component (S x 1)
→ Retry handler service for external API calls

Interface (M x 1)
→ Health API integration with exponential backoff and retry logic

==============================
```

## Phase Summary

```
📊 WORKFLOW SUMMARY
------------------------------
Phase: DONE
Iteration: 2 (used 1 feedback loop)
Verification attempts: 1
------------------------------
```

---

# KEY STATE TRANSFORMATIONS

## State Journey Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT (JSON)                                                    │
│ {target_dm, functionality_description, slides}                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ AFTER EXTRACTION (complete first time, then pfr_merge)          │
│ truth_pack = {                                                  │
│   domain_focus, change_context, assumptions,                   │
│   ui_flows, data_flows, external_systems,                      │
│   integrations, variants, backend_operations,                  │
│   unknowns, [after pfr_merge:]                                 │
│   error_handling, pagination, performance_targets              │
│ }                                                               │
│ readiness.status = "READY"                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ AFTER GENERATION                                                │
│ set_a = initial groupings by worktype                           │
│ set_b = after corrections                                       │
│ verification.status = "PASS"                                    │
│ effort_final = [                                                │
│   {worktype, complexity, count, description},                  │
│   ...                                                           │
│ ]                                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ FINAL DELIVERABLE                                               │
│ 5 effort groupings with worktype/complexity/count               │
│ Ready for estimation meeting                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

# ALTERNATE PATH: What If Verification Failed?

If `verify_cove` had returned FAIL:

```json
{
  "verification_status": "FAIL",
  "issues": [
    "Missing Entity worktype for Plan data model",
    "Complexity mismatch: Interface should be Small, not Medium"
  ]
}
```

**Then:**
1. Increment `verification_attempts` (1 → 2)
2. Check: `verification_attempts <= max_verification_attempts` (2 <= 3) ✓
3. **Loop back** to `correct_setb` with feedback about issues
4. `correct_setb` adjusts Set B based on issues
5. `verify_cove` re-validates
6. If still FAIL and `verification_attempts >= 3`, go to `finalize_setc` anyway (give best effort)

---
