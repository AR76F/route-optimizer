# Job Comparison Rules

## Overview

Every work item is assigned a standardized priority code in the following format:

```text
P#-C#
```

Jobs are always compared **from left to right**. The first value that differs determines which job has higher priority.

This approach guarantees that two coordinators comparing the same schedule will always reach the same conclusion.

---

# Comparison Process

When comparing two jobs, evaluate the following criteria in order:

1. Priority Level (P)
2. Client Class (C)
3. Job Type (if both codes are identical)
4. Job Age (Service calls only, when all other criteria are equal)

The comparison stops as soon as a difference is found.

---

# Rule 1 – Compare the Priority Level

The **Priority Level (P)** is always evaluated first.

A lower priority number represents a higher priority.

| Job A | Job B | Result |
|--------|--------|--------|
| P2-C2 | P5-C1 | **P2-C2 wins** |

Since the Priority Level differs, the Client Class is **not evaluated**.

---

# Rule 2 – Compare the Client Class

If both jobs share the same Priority Level, compare the Client Class.

A lower Client Class number represents a higher business priority.

| Job A | Job B | Result |
|--------|--------|--------|
| P3-C1 | P3-C3 | **P3-C1 wins** |

---

# Rule 3 – Compare the Job Type

If both the Priority Level and Client Class are identical, compare the type of work.

For Preventive Maintenance, the recommended precedence is:

1. Five-Year Maintenance (ATS / Inverter)
2. Annual CSA Maintenance
3. Standard Annual Maintenance
4. Full Inspection
5. Generator Inspection

For Service Calls, the oldest request receives priority.

---

# Rule 4 – Existing Business Rules

Additional business-specific tie-breakers may be applied when required, such as:

- Customer commitments (total sales volumes)
- Contractual obligations
- Approved management exceptions

These rules should remain exceptional and be documented separately.

---

# Which Job Is Rescheduled?

When a new job enters the schedule, the job with the **lowest overall priority** is the one that should be moved.

In practice:

- Compare the two priority codes from left to right.
- The job with the **greater value** loses the comparison.
- That job is the one that is rescheduled.

Example:

| Existing Job | New Job | Result |
|--------------|---------|--------|
| P5-C1 | P2-C2 | P5-C1 is rescheduled |

---

# Worked Examples

The following examples illustrate how the comparison rules are applied in situations that are commonly questioned.

---

## P6-C1 vs P2-C4

| Job | Result |
|------|--------|
| P6-C1 | loss |
| P2-C4 | win |

The comparison stops at the first character.

Since **P2** has higher priority than **P6**, the Client Class is never evaluated.

**Conclusion:** A routine preventive maintenance visit for a C1 customer never takes precedence over a breakdown, regardless of customer class.

---

## Non-Urgent Service vs PM Rescheduled Twice

| Job | Priority |
|------|----------|
| Non-Urgent Service | P3 |
| PM Rescheduled Twice | P3 |

Because both jobs share the same Priority Level:

1. Compare Client Class.
2. If still equal, compare Job Type.

The PM escalation makes it equivalent to a typical non-urgent service call, but it never reaches the priority of a breakdown.

---

## P3 Service vs P4 Critical Preventive Maintenance

| Job | Result |
|------|--------|
| P3-C1 | win |
| P4-C1 | loss |

A lower Priority Level always wins.

Even critical preventive maintenance does not take precedence over a higher-priority service call.

---

## Residential Customer with Health or Safety Risk

As always, Health and safety considerations override the normal client classification.

The job is escalated to **P1**, regardless of whether the customer would normally be classified as C4.

# Deterministic Scheduling

Because every comparison follows the same sequence:

```text
Priority Level
      ↓
Client Class
      ↓
Job Type
      ↓
Job Age
```

every planner, dispatcher, or software application will produce the same scheduling decision when evaluating the same set of jobs.

This deterministic approach removes subjective decision-making and establishes a single, consistent prioritization model across the organization.