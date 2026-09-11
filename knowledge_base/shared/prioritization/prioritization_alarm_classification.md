# Alarm Classification

## Purpose

An alarm or fault does **not** have an intrinsic priority.

Its urgency is determined by its **impact on the availability of the equipment**, not simply by the alarm code itself.

The dispatcher must determine how the alarm affects the generator before assigning a priority.

---

# Alarm Levels

| Alarm Level | Definition | Typical Priority |
|--------------|------------|------------------|
| **Blocking Alarm** | The generator cannot start or cannot accept load. Examples include active shutdowns, failed start attempts, ATS transfer failures, or any condition that makes the unit unavailable. | **P1** for C1–C2 customers without redundancy or with safety impact; **P2** for C3–C4 customers. |
| **Reliability Alarm** | The generator continues to operate but its ability to support a future outage is compromised. Examples include battery charger failures, low fuel level, defective block heater, coolant leak, etc. | **P2** for C1–C2 customers; **P3** for C3–C4 customers. |
| **Minor Alarm** | No immediate impact on equipment availability. Examples include sensor faults, reminder lamps, or maintenance notifications. | Service Call (Non-Urgent): **P3** (C1–C3) or **P5** (C4). |

---

# Dispatcher Decision Process

The primary question is:

> **If utility power fails right now, will the generator start and carry the load?**

| Answer | Alarm Classification |
|---------|----------------------|
| No, or uncertain | Blocking Alarm |
| Yes, but with increased risk | Reliability Alarm |
| Yes, with no significant risk | Minor Alarm |

This single question should guide the initial classification before determining the final priority.

---

# Additional Considerations

Alarm classification should also consider the probability that the equipment could fail before the next maintenance opportunity.

Factors may include:

- Oil pressure
- Engine temperature
- Fuel level
- Battery condition
- Coolant leaks
- Site redundancy
- Whether the entire facility depends on the generator
- Criticality of the customer's operation

The coordinator should ask enough questions to determine whether the generator is:

- Completely shut down (`Shutdown`)
- Operating with reduced reliability (`Warning`)
- Operating normally with only informational notifications

---

# Typical Shutdown Conditions

The following shutdown events are generally treated as **Blocking Alarms** because they directly affect equipment availability.

| Shutdown Event | Classification |
|----------------|----------------|
| Low Oil Pressure | Blocking Alarm |
| High Engine Temperature | Blocking Alarm |
| Low Engine Temperature (when preventing operation) | Blocking Alarm |
| Overspeed | Blocking Alarm |
| Low Coolant Level | Blocking Alarm |
| Overcrank | Blocking Alarm |

> **Note:** The alarm code alone does not determine the priority. The dispatcher must always confirm the actual operational status of the generator before assigning a priority.