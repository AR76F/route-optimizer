# Service Assistant — Pilot Feedback Tracker

**Pilot Version:** v1.0  
**Pilot Start:** YYYY-MM-DD  
**Last Updated:** YYYY-MM-DD  
**Project Owner:** <Name>

---

## Purpose

This document tracks feedback collected during the Service Assistant pilot.

The objective is to identify recurring issues, improve the assistant during the pilot when appropriate, and provide evidence for future development decisions.

Feedback should include both **problems and successful use cases**.

---

# Feedback Categories

| Code | Category | Description |
|---|---|---|
| `KG` | Knowledge Gap | Required information is missing from the knowledge base |
| `RF` | Retrieval Failure | Information exists but the assistant did not retrieve it correctly |
| `RI` | Reasoning Issue | Relevant information was available, but the assistant reached an incorrect or weak conclusion |
| `DQ` | Data Quality | Source information is incorrect, incomplete, or outdated |
| `UX` | UX / Prompting | Difficulty caused by the interface, instructions, or how the user interacted with the assistant |
| `BUG` | Technical Bug | Application or feature malfunction |
| `FR` | Feature Request | Request for a new capability or improvement |
| `SUCCESS` | Successful Use Case | Interaction demonstrating meaningful value |

---

# Priority Levels

## P0 — Critical

Examples:

- Safety concern
- Seriously incorrect operational guidance
- Security/privacy concern
- Application unavailable

**Action:** Investigate immediately.

## P1 — High

Examples:

- Common workflow is unreliable
- Significant knowledge or retrieval problem
- Multiple users affected

**Action:** Address during the pilot when possible.

## P2 — Normal

Examples:

- Minor retrieval issue
- Missing secondary information
- UX improvement
- Isolated issue

**Action:** Review and address when practical.

## P3 — Enhancement

Examples:

- New feature
- Automation request
- Integration idea
- Nice-to-have improvement

**Action:** Add to the post-pilot backlog for evaluation.

---

# Active Feedback

| ID | Date | Category | Priority | Short Description | Status |
|---|---|---|---|---|---|
| | | | | | |

### Status

Use:

- `New`
- `Investigating`
- `Planned`
- `In Progress`
- `Testing`
- `Resolved`
- `Backlog`
- `Won't Fix`

---

# Feedback Details

Copy the following template for each significant feedback item.

---

## <ID> — <Short Description>

**Date:** YYYY-MM-DD  
**Category:** KG / RF / RI / DQ / UX / BUG / FR / SUCCESS  
**Priority:** P0 / P1 / P2 / P3  
**Status:** New  
**Reported by:** <Optional>

### User Question / Scenario

> Exact or approximate question asked by the user.

### Assistant Response

> Relevant portion of the assistant's response.

### User Feedback

What did the user report?

### Expected Behavior

What should the assistant have returned or done?

### Supporting Information

Relevant procedure, documentation, technician profile, screenshot, or other source:

- ...

### Investigation

What caused the issue?

- [ ] Knowledge gap
- [ ] Retrieval failure
- [ ] Reasoning issue
- [ ] Data quality
- [ ] Prompt/context issue
- [ ] Technical issue
- [ ] Unknown

### Action Taken

Describe any modification made to:

- Knowledge base
- Retrieval
- Prompting
- Application
- UI
- Documentation
- Other

### Validation

Retest the **original user question** after making the change.

**Original prompt:**

> ...

**Result:** Pass / Fail / Partial

Also test variations when appropriate:

1. ...
2. ...
3. ...

### Resolution

**Resolved:** YYYY-MM-DD  
**Version:** `<version>`

**Notes:**

...

---

# Knowledge Gaps

| ID | Topic | Missing Information | Frequency | Priority | Status |
|---|---|---|---:|---|---|
| KG-001 | | | 1 | | |

---

# Retrieval Failures

Cases where the required information exists in the knowledge base but was not retrieved correctly.

| ID | Query | Expected Source | Actual Result | Status |
|---|---|---|---|---|
| RF-001 | | | | |

These cases should be considered candidates for the regression test set.

---

# Reasoning Issues

Cases where the assistant had access to relevant information but produced an incorrect or questionable conclusion.

| ID | Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| RI-001 | | | | |

---

# Data Quality Issues

Problems originating from the underlying documentation rather than the AI itself.

| ID | Source | Problem | Required Update | Status |
|---|---|---|---|---|
| DQ-001 | | | | |

---

# UX / Prompting Feedback

| ID | Observation | Frequency | Potential Improvement | Status |
|---|---|---:|---|---|
| UX-001 | | 1 | | |

Potential patterns to watch for:

- Questions do not contain enough context
- Users do not know what information the assistant has access to
- Users expect autonomous actions
- Users struggle with file uploads
- Users do not know how to reset conversations
- Users misunderstand temporary notes
- Users have difficulty finding the prioritization tool
- Users expect copy/paste image support

---

# Technical Bugs

| ID | Date | Feature | Description | Priority | Status |
|---|---|---|---|---|---|
| BUG-001 | | | | | |

When possible, include:

- Steps to reproduce
- Error message
- Screenshot
- Application version
- Browser/environment

---

# Feature Requests

Feature requests should be recorded without automatically committing to development.

| ID | Request | Requested By | Frequency | Potential Value | Status |
|---|---|---:|---:|---|---|
| FR-001 | | | 1 | | Backlog |

Potential status:

- Backlog
- Under Review
- Planned
- Rejected
- Implemented

---

# Successful Use Cases

Successful interactions are important evidence for evaluating the pilot.

Record cases where the assistant:

- Saved meaningful time
- Found difficult-to-locate information
- Helped resolve a real Service request
- Provided a useful technician recommendation
- Successfully interpreted an image or PDF
- Helped prioritize a request
- Received particularly positive user feedback

---

## SUCCESS-001 — <Short Description>

**Date:** YYYY-MM-DD  
**User / Team:** <Optional>

### Scenario

What was the user trying to accomplish?

### Previous Workflow

How would the user normally have completed this task?

### Assistant Workflow

How did the Service Assistant help?

### Result

What was the outcome?

### User Feedback

> Optional direct feedback.

### Estimated Benefit

Examples:

- Time saved
- Fewer documents searched
- Faster decision
- Information discovered
- Reduced dependency on another employee

---

# Recurring Patterns

Individual feedback is useful, but repeated patterns should drive development priorities.

| Pattern | Category | Occurrences | Impact | Recommended Action |
|---|---|---:|---|---|
| | | | | |

A feature request or problem reported repeatedly should generally receive more attention than an isolated request.

---

# Regression Test Candidates

Real pilot failures should gradually become evaluation cases.

| Test ID | Source Feedback | Test Question | Expected Behavior | Status |
|---|---|---|---|---|
| TEST-001 | RF-001 | | | |

When an issue is resolved, preserve the original question whenever possible.

This helps verify that future changes do not reintroduce previously fixed problems.

---

# Feedback Summary

Update periodically during the pilot.

| Category | Open | Resolved | Total |
|---|---:|---:|---:|
| Knowledge Gaps | | | |
| Retrieval Failures | | | |
| Reasoning Issues | | | |
| Data Quality | | | |
| UX / Prompting | | | |
| Technical Bugs | | | |
| Feature Requests | | | |
| Successful Use Cases | — | — | |
| **Total** | | | |

---

# Pilot Insights

Use this section for observations that emerge from the feedback as a whole.

## What Users Find Most Valuable

- ...

## Most Common Problems

- ...

## Most Requested Features

- ...

## Knowledge Base Improvements Needed

- ...

## Unexpected Use Cases

- ...

## Development Priorities Emerging From the Pilot

1. ...
2. ...
3. ...

---

# Relationship With Other Pilot Documentation

### `PILOT_FEEDBACK.md`

Detailed operational feedback tracker.

**Question answered:**  
> What are users experiencing?

### `PILOT_LOG.md`

Chronological record of important events, changes, decisions, releases, and observations.

**Question answered:**  
> What happened during the pilot?

### `evaluation/regression_cases.md`

Reusable test cases created from real pilot interactions.

**Question answered:**  
> Can the assistant still correctly handle previously identified scenarios?

### `evaluation/known_issues.md`

Current known limitations and unresolved problems.

**Question answered:**  
> What do we already know is not working correctly?

---

> **Important:** Not every piece of feedback requires an immediate change. The purpose of the pilot is also to identify patterns and determine which improvements provide the greatest value to Service users.