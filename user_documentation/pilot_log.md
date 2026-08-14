# Service Assistant — Pilot Log

**Pilot Version:** v1.0.0  
**Pilot Start:** 2026-08-13 
**Pilot End:** TBD  
**Project Owner:** AR76F and UD016

---

## Purpose

This log records significant events, observations, decisions, issues, and improvements made during the Service Assistant pilot.

Detailed feedback and individual issues may be tracked separately.

---

# Pilot Baseline

## Launch Capabilities

- Conversational knowledge retrieval
- Service procedure lookup
- Technician lookup and recommendations
- Prioritization tool
- Image/OCR analysis
- PDF/document analysis
- Conversation memory
- Temporary notes
- English and French interaction

## Known Limitations at Launch

- No autonomous actions
- No automatic dispatch
- No direct BMS actions
- No live technician availability
- No work order creation
- Image upload required for OCR
- Retrieval quality depends on available knowledge and user context

## Launch Version

**Git Version / Tag:** `pilot-v1.0.0`

**Knowledge Base Version:** `<TBD>`

**Model:** `gpt-5.6-sol, gpt-5.6-terra, or gpt-5.6-luna`

---

# Pilot Timeline

## 2026-08-13 — Pilot Launch

### Event

Demo of Service Assistant to the initial Service pilot group.

### Observations

- Generally good first impressions
- Employee CI690 was impressed and would like to bring the platform to the Pointe-Claire branch.
- Employee BB44Y liked it too and asked whether it would be made available soon. He needs it more than others to jumpstart his learnings.

### Issues

- None for now.

### Actions

- To be made accessible whether through Route Optimizer or another method.

---

## YYYY-MM-DD — Example Entry

### Observation

Several users asked very short technician recommendation questions without providing location or equipment information.

### Classification

UX / Prompting

### Impact

Medium

### Decision

Improve interface guidance to encourage users to provide:

- Location
- Equipment
- Fault/problem
- Customer/site context

### Action

Added example prompt to the interface.

### Validation

To be evaluated during the following week.

---

# Feedback Summary

## Knowledge Gaps

| ID | Description | Status |
|---|---|---|
| KG-001 | | Open |

## Retrieval Failures

| ID | Description | Status |
|---|---|---|
| RF-001 | | Open |

## Reasoning Issues

| ID | Description | Status |
|---|---|---|
| RI-001 | | Open |

## Technical Issues

| ID | Description | Status |
|---|---|---|
| BUG-001 | | Open |

## Feature Requests

| ID | Request | Frequency | Status |
|---|---|---:|---|
| FR-001 | | 1 | Backlog |

---

# Successful Use Cases

Record particularly valuable examples here.

## SUCCESS-001

**Date:**  
**Use case:**  
**Previous workflow:**  
**Assistant workflow:**  
**User feedback:**  
**Estimated benefit:**  

---

# Changes During Pilot

## v1.0.1 — YYYY-MM-DD

### Fixed

- ...

### Knowledge Base

- Added ...
- Updated ...

### Retrieval

- ...

### UI

- ...

---

# Decisions

## DEC-001 — <Decision>

**Date:** YYYY-MM-DD

**Context:**  
...

**Decision:**  
...

**Reason:**  
...

---

# Recurring Patterns

Patterns observed across multiple users should be recorded here rather than reacting to individual cases.

### Example

**Pattern:** Users frequently ask for technician recommendations without providing enough context.

**Frequency:** 6 occurrences

**Potential response:**

- Improve prompt guidance
- Ask structured follow-up questions
- Modify retrieval behavior

---

# Pilot Metrics

| Metric | Result |
|---|---:|
| Active pilot users | |
| Total interactions | |
| Feedback reports | |
| Successful use cases | |
| Knowledge gaps | |
| Retrieval failures | |
| Reasoning failures | |
| Technical bugs | |
| Feature requests | |

---

# End-of-Pilot Findings

_To be completed at the end of the pilot._

## What Worked

- ...

## What Didn't

- ...

## Most Valuable Use Cases

- ...

## Main Limitations

- ...

## Recommended Improvements

- ...

## Recommended Next Steps

- ...

---

# Pilot Outcome

**Recommendation:**

- [ ] Stop
- [ ] Extend pilot
- [ ] Continue development
- [ ] Expand deployment
- [ ] Prepare for production deployment

### Rationale

...