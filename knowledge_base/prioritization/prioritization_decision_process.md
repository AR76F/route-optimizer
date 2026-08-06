# Decision Process

## Overview

The Prioritization Engine determines a job's priority by evaluating a series of business questions in a predefined order.

The first matching condition establishes the **Priority Level (P)**. Once the Priority Level has been determined, the **Client Class (C)** is applied to generate the final prioritization code.

```text
Priority Level (P)
        +
Client Class (C)
        ↓
     P#-C#
```

This decision process is implemented in the interactive Prioritization Engine and is shared by both the Service and Project Management (PM) departments.

---

# Decision Sequence

The engine evaluates the following business conditions in order.

## Step 1 — Equipment Availability

**Question**

> Is the unit unavailable or out of service?

This includes situations such as:

- Active shutdown alarms
- Failure to start
- Automatic Transfer Switch (ATS) failures
- Any condition preventing the generator from accepting load

### Decision

- **P1**
  - Client Class C1 or C2
  - Sites without redundancy
  - Health or safety impact

- **P2**
  - Client Class C3 or C4

If this condition is met, the evaluation ends.

---

## Step 2 — Active Alarm or Defect

**Question**

> Is there an active alarm or fault while the unit remains operational?

The engine determines whether the condition is classified as:

- Reliability Alarm
- Minor Alarm

### Decision

**Reliability Alarm**

- C1–C2 → **P2**
- C3–C4 → **P3**

**Minor Alarm**

Handled as a non-urgent service call and evaluated using the Service Call rules.

---

## Step 3 — Commissioning

**Question**

> Is this a commissioning or startup activity?

### Decision

Commissioning is assigned:

- **P1**

Business exception:

If two or more technicians are assigned and a P1 breakdown occurs, one technician may be reassigned while commissioning continues with reduced staffing.

A commissioning activity is never completely abandoned.

---

## Step 4 — Preventive Maintenance Escalation

**Question**

> Has the preventive maintenance activity already been rescheduled?

### Decision

| Number of Reschedules | Priority |
|------------------------|----------|
| 2 or more | P3 |
| 1 | P4 |
| None | Continue to Step 6 |

This mechanism prevents preventive maintenance from remaining indefinitely in the backlog.

---

## Step 5 — Service Call

**Question**

> Is this a service call?

### Decision

| Customer Class | Priority |
|----------------|----------|
| C1–C3 | P3 |
| C4 / Residential | P5 |

Minor alarms are evaluated using this same logic.

---

## Step 6 — Preventive Maintenance

**Question**

> Is this a preventive maintenance activity?

### Decision

Critical preventive maintenance receives:

- Five-year maintenance
- Monthly maintenance
- Customer-committed maintenance windows
- Annual CSA maintenance

→ **P4**

Routine preventive maintenance receives:

- Annual maintenance
- Full inspection
- Generator inspection

→ **P6**

---

# Client Class Assignment

Once the Priority Level has been determined, the Client Class is assigned according to the Client Classification rules.

The final prioritization code is generated as:

```text
P#-C#
```

Examples:

- P1-C1
- P2-C3
- P4-C2

---

# Comparison with Existing Work

After generating the prioritization code, the job is compared against all existing scheduled work using the comparison rules documented in:

- **Comparison Rules**

The comparison is always performed from left to right:

1. Priority Level
2. Client Class
3. Job Type
4. Customer Ranking (when applicable)
5. Additional business tie-breakers

---

# Relationship to the Prioritization Engine

This document describes the business decision process used to determine a job's priority.

The interactive Prioritization Engine implements this process by presenting the appropriate questions to the user, evaluating the responses according to the documented business rules, and automatically generating the corresponding prioritization code.

The software implementation may evolve over time, but any changes to the decision logic should remain consistent with the business rules documented in this repository.