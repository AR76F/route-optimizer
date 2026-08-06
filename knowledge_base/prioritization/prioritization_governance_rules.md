# Business Rules

## Overview

The following business rules complement the prioritization model. They define how the priority grid is applied in specific operational situations and ensure consistent scheduling decisions across the Service and Project Management (PM) departments.

---

## Rule 1 — Equipment Failure Takes Precedence

A generator that is unavailable takes precedence over all other work, regardless of the client's class.

**Example**

- A C1 customer's generator is operational.
- A C3 customer's generator is down.

The C3 customer is served first because equipment failure always takes precedence over planned work.

---

## Rule 2 — Commissioning is P1, with an Exception

Commissioning and startup activities are assigned **Priority P1** by default because they are:

- Planned activities
- Contractual commitments
- Frequently performed with the customer and subcontractors on site

### Exception

If a commissioning job has **two or more technicians assigned** and a **P1 equipment failure** occurs, one technician may be reassigned to respond to the failure while commissioning continues with reduced staffing.

A commissioning activity should **never be completely abandoned**.

If only one technician is assigned, that technician remains on site and the equipment failure must be covered by another technician, on-call personnel, or additional resources.

---

## Rule 3 — Preventive Maintenance Priority Ceiling

The priority grid establishes a maximum priority for preventive maintenance activities.

- **Critical Preventive Maintenance (P4)** ranks below **C1–C3 non-urgent service calls (P3)**.
- It ranks above **C4 or residential non-urgent service calls (P5)**.
- **Routine Preventive Maintenance (P6)** always remains at the lowest priority.

Only the Preventive Maintenance escalation rule (Rule 4) allows a PM activity to move above its natural priority.

---

## Rule 4 — Automatic Preventive Maintenance Escalation (Anti-Backlog)

To prevent preventive maintenance activities from being postponed indefinitely, each reschedule automatically increases their priority.

| Number of Reschedules | Priority |
|------------------------|----------|
| Never rescheduled | Natural priority (P4 or P6) |
| Rescheduled once | P4 |
| Rescheduled two or more times | P3 |

A preventive maintenance activity that reaches **P3** becomes equivalent to a typical non-urgent service call but never reaches the priority of an equipment failure.

Once a PM has been rescheduled twice, it may not be postponed again without supervisor approval.

Each reschedule increases the priority by one level. No preventive maintenance activity should be postponed more than two times.

---

## Rule 5 — Customer Ranking

When two jobs have the same Priority Level and the same Client Class, customer ranking is used as the final business tie-breaker.

Customer ranking is based on the organization's sales and margin classification.

The current customer ranking is maintained in the Power BI report:

- **Customer Ranking — Sales & Margins (Power BI)**

---

## Summary

These business rules supplement the core prioritization engine and ensure that exceptional operational situations are handled consistently while maintaining a common prioritization model across the organization.