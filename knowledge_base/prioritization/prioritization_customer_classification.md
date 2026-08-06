# Client Classes (C1–C4)

## Overview

The **Client Class (C)** is the second component of the prioritization code (`P#-C#`).

It is used **only when comparing two jobs that share the same Priority Level (P)**.

Because the priority code is evaluated from left to right, the Priority Level always takes precedence. Client Class serves as the tie-breaker.

Example:

| Job | Priority Code |
|------|---------------|
| Customer A | P2-C1 |
| Customer B | P2-C3 |

Since both jobs are **P2**, the client class determines which job receives priority. In this example, **P2-C1** is scheduled before **P2-C3**.

---

# Client Classes

| Class | Definition | Typical Examples |
|--------|------------|------------------|
| **C1** | Mission-critical customers where power availability directly affects public safety, government operations, healthcare, or essential digital infrastructure. | Government facilities (PWGS, BGIS), hospitals, data centers (Vantage, Cologix, eStruxture), other critical infrastructure |
| **C2** | Telecommunications providers whose services are essential for communication networks. | Vidéotron, Bell, Rogers, Telus |
| **C3** | Customers covered by an active maintenance agreement (CSA). | Monthly CSA contracts, annual CSA contracts |
| **C4** | Customers without a maintenance contract, one-time service calls, or residential customers. | Commercial one-time calls, residential customers |

---

# Comparison Rules

Client Class is evaluated only after the Priority Level.

Priority order:

```
Priority Level (P)
        ↓
Client Class (C)
```

Example comparisons:

| Job A | Job B | Higher Priority |
|--------|--------|----------------|
| P1-C4 | P2-C1 | P1-C4 |
| P3-C2 | P3-C4 | P3-C2 |
| P4-C3 | P4-C1 | P4-C1 |

---

# Special Cases

## Health and Safety

Health and safety considerations always override the standard client classification.

Examples include:

- Individuals dependent on medical equipment
- Buildings where loss of power presents an immediate safety risk
- Heating failures during severe winter conditions
- Any situation where human safety is compromised

In these cases, the work should be escalated to **Priority Level P1**, regardless of the assigned Client Class.

---

# Summary

The Client Class reflects the business importance of the customer and is used only to distinguish between jobs that already have the same Priority Level.

Final priority is always determined using the complete prioritization code:

```
P#-C#
```

where:

- **P** = Priority Level
- **C** = Client Class