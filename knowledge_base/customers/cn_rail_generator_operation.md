# Customer - CN Rail Generator Operation

# Version 1.0.0

# Last Updated: 2026-07-23

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Creation of initial document based on the customer operating guide.
- Initial version to be refined as additional site information becomes available.

## Purpose

This document outlines the normal operating procedure for the CN Rail dual-generator installation.

It is intended to assist operators and Service Coordinators with the normal startup, shutdown, and fault reset procedures for this specific installation.

> **Important**
>
> This procedure applies only to the documented CN Rail generator installation and should not be assumed to apply to other customer sites.

---

# Site Information

**Customer**

- CN Rail

**Generator Configuration**

- Dual Generator System

**Generator Model**

- DSGAC

**Prime Rating**

- 135 kW

**Voltage**

- 480 Volts

---

# Emergency Contact

Cummins Service

```text
1-800-361-7673
```

After Hours

```text
514-951-8260
```

---

# Generator Control Selector

The generator controller uses the following selector positions:

```text
OFF
HAND
AUTO
```

Under normal operating conditions:

- **AUTO** is used for automatic operation.
- **HAND** is intended for manual operation during maintenance only.
- **OFF** is used when stopping or resetting the controller.

---

# Starting the Generators

## Procedure

1. Verify that both generator control selectors are in:

```text
AUTO
```

2. Verify that the **main breakers** on both generators are in the:

```text
ON
```

position.

3. Both generators will start.

4. After approximately **5 minutes**:

- One generator will automatically shut down.
- The second generator will continue operating.

5. The operating generator will continue running until the programmed **8-hour operating cycle** has been completed.

6. After the 8-hour cycle:

- The operating generator will automatically shut down.
- The second generator will automatically start and continue operating for the next 8-hour cycle.

This alternating sequence is the normal operating mode for this installation.

---

# Stopping the Generators

## Important

> **Never stop the generators using the Emergency Stop (E-STOP) button during normal operation.**

The Emergency Stop should only be used during an actual emergency.

---

## Shutdown Procedure

1. Turn the selector switch to:

```text
OFF
```

on the generator that is **not currently running**.

2. On the generator that is currently operating:

Place the **main breaker** in the:

```text
OFF
```

position.

3. Allow the generator to continue running **without load** for approximately:

```text
5 minutes
```

to complete its cooldown period.

4. After the cooldown period:

Turn the controller selector to:

```text
OFF
```

The generator will shut down safely.

---

# Resetting a Fault

If the controller displays a fault:

1. Turn the selector switch to:

```text
OFF
```

2. The fault will automatically reset.

3. Return the selector switch to either:

```text
AUTO
```

or

```text
OFF
```

depending on the desired operating condition.

> **Note**
>
> The **HAND** position is intended strictly for manual operation during maintenance activities.

---

# Normal Operating Sequence

```text
AUTO
      ↓
Main Breakers ON
      ↓
Both Generators Start
      ↓
5 Minutes
      ↓
One Generator Stops
      ↓
One Generator Runs
      ↓
8 Hours
      ↓
Operating Generator Stops
      ↓
Second Generator Starts
      ↓
Repeat
```

---

# Troubleshooting

## Generator Does Not Start

Verify:

- Controller selector is in **AUTO**.
- Main breaker is **ON**.
- No active controller faults are present.

If the generator still does not start:

Contact Cummins Service.

---

## Fault Alarm Present

If a fault alarm is displayed:

- Turn the selector to **OFF**.
- Allow the controller to reset.
- Return the selector to **AUTO**.
- Attempt normal operation again.

If the fault returns:

Contact Cummins Service.

---

# Safety Notes

- Never use the Emergency Stop as part of the normal shutdown procedure.
- Always allow the generator to complete the recommended cooldown period before shutting it down.
- Use the **HAND** position only during maintenance or manual testing.
- Follow all customer-specific safety procedures before operating the equipment.

---

# Best Practices

- Verify the controller selector position before troubleshooting.
- Confirm breaker position before assuming a generator fault.
- Record any controller fault messages before resetting the system.
- Allow the automatic alternating sequence to operate normally.
- Contact Cummins Service if abnormal behavior persists after following this procedure.

---

# Common Mistakes

## Emergency Stop Used for Normal Shutdown

The Emergency Stop is intended for emergencies only.

Normal shutdown should always follow the standard shutdown procedure.

---

## Breaker Left OFF

A generator will not operate normally if the main breaker has not been returned to the ON position.

---

## Manual Mode Left Selected

After maintenance activities, ensure the selector has been returned to **AUTO**.

Leaving the controller in **HAND** prevents normal automatic operation.

---

## Repeated Fault Resets

Repeatedly resetting the same fault without investigating the cause may hide an underlying issue.

If faults continue to reoccur, contact Cummins Service.