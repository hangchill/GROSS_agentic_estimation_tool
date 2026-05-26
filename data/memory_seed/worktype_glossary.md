# Worktype & Complexity Glossary (Seed)
 
## Purpose
 
Defines:
- standard worktypes
- effort complexity rubric (S / M / C)
 
Used during **generation phase**.
 
---
 
## Worktypes
 
Page 
A full user-facing page or screen.
 
UI 
Smaller UI element (card/component change).
 
Mobile 
Mobile-specific UI or logic.
 
Interface 
Integration with an external system.
(1 system = 1 interface)
 
Component 
Backend capability or business logic.
 
Entity 
Data model / storage structure.
 
Config 
Configuration (feature flags, routing).
 
Query 
Data retrieval / aggregation.
 
Report 
Formatted data output.
 
Batch 
Scheduled / background job.
 
Framework 
Cross-cutting technical layer.
 
Application 
Entire module/app change.
 
---
 
## Complexity Rubric
 
### Small (S)
- Single screen or integration
- minimal logic/rules
- simple flow
 
### Medium (M)
- multiple steps or states
- some branching rules
- 1–2 integrations
 
### Complex (C)
- multi-journey flows
- multiple integrations
- complex orchestration
- many edge cases
 
---
 
## Count Guidelines
 
- Increase count when:
  - multiple similar instances exist (e.g., per variant)
 
- Do NOT:
  - inflate complexity unnecessarily
 