# Priority Levels (P1–P6)

## Overview

The **Priority Level (P)** is the first component of the prioritization code (`P#-C#`) and is always evaluated before the Client Class (`C#`).

A single priority grid is shared between both the **Service** and **Project Management (PM)** departments. Every scheduled job receives a priority code using the following format:

```
P#-C#
```

Examples:

- `P2-C1`
- `P4-C3`
- `P6-C2`

When comparing two jobs, the **Priority Level always takes precedence** over the Client Class.

---

## Priority Matrix

| Priority | Work Type (Service & PM) | Target Response |
|-----------|--------------------------|-----------------|
| **P1** | Equipment failure or unavailable unit (including blocking alarms) for C1–C2 customers, sites without redundancy, or health/safety impact. Commissioning and initial startup work orders have P1 priority by default. | **Immediate** |
| **P2** | Equipment failure or unavailable unit for C3–C4 customers. Reliability alarm for C1–C2 customers. | Same day / within 24 hours |
| **P3** | Reliability alarm for C3–C4 customers. Non-urgent service call (including minor alarms) for C1–C3 customers. Preventive maintenance rescheduled two or more times. | 1–2 days |
| **P4** | Critical preventive maintenance including five-year maintenance (quinquennal), monthly maintenance, customer-committed maintenance window, annual CSA maintenance, or preventive maintenance rescheduled once. | Committed maintenance window |
| **P5** | Non-urgent service call (including minor alarms) for C4 or residential customers. | 2–3 days |
| **P6** | Standard preventive maintenance including annual maintenance, full inspections, and generator inspections. | Scheduled within the monthly maintenance window |

---

## Priority Order

Priority is evaluated from highest to lowest:

```
P1
↓
P2
↓
P3
↓
P4
↓
P5
↓
P6
```

A lower priority number always supersedes a higher one.

---

## Notes

- Priority Level is always evaluated before Client Class.
- Client Class is used only when two jobs share the same Priority Level.
- The complete prioritization code is described in the Priority Model documentation.