# Historical CR / Dev Effort Memory (Seed)
 
## Purpose
 
Provides past CR patterns for:
- sanity checking
- ambiguity detection
 
NOT used for direct estimation.
 
---
 
## Record 1 — HealthierSG Module
 
### Project Description
 
Implementation of a new module "Healthier SG" in HealthHub.
 
Key features include:
- Enrollment process for resident
- Check NEHR opt-out
- Display PCP locations (maps integration)
- Change PCP
- Caregiver enrollment
- View resident health plan
- Submit health questionnaires
- View BMI / smoking status
- View CHAS status
- View health indicators
- View educational content
- Book appointments (HAS integration)
- Track health goals
- Launch to H365
 
---
 
### Category
Health Plan
 
### Service
HSG - Manage Health Plan
 
---
 
### Example Functionality
 
Allow caregiver to:
- view on behalf
- switch profiles
 
---
 
### Observed Patterns
 
- Most features include:
  - Page (UI)
  - Interface (integration)
  - Component (backend logic)
 
- Integrations (HAS, Maps) appear as Interface work
 
- Backend logic often processes:
  - eligibility
  - retrieval
  - transformation of data
 
---
 
## Usage Notes
 
Use this memory to:
- detect missing components
- check if estimate structure is reasonable
- flag anomalies (NOT to directly copy estimates)
 