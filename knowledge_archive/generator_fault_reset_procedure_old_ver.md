# Initial Generator Troubleshooting and Reset Procedure

# Version 1.0.0

# Last Updated: 2026-07-23

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Creation of initial document based on internal troubleshooting guidance.
- Initial version to be refined as additional technical guidance becomes available.

## Purpose

This procedure outlines a basic troubleshooting and fault reset process that may be performed before dispatching a technician.

It is intended to determine whether a generator fault can be cleared through a simple reset procedure or whether a service call is required.

> **Important**
>
> This procedure is intended as an initial troubleshooting guide only.
>
> If the generator cannot be safely operated, or if unsafe conditions exist, stop the procedure immediately and arrange for service.

---

# Workflow Overview

```text
Generator Fault
        ↓
Turn Generator OFF
        ↓
Reset / Fault Acknowledge
        ↓
Review Active & Historical Fault Codes
        ↓
Record Fault Information
        ↓
Record Operating Hours
        ↓
Clear Fault Codes
        ↓
Return Controller to MANUAL
        ↓
Attempt to Start Generator
        │
        ├── Starts Successfully
        │       ↓
        │   Monitor Operation
        │
        └── Does Not Start
                ↓
          Contact Service
```

---

# Step 1 – Turn the Generator OFF

Place the generator in the **OFF** position.

Confirm that the controller has completely stopped the generator before continuing.

---

# Step 2 – Perform a Fault Reset

Using the generator controller:

Perform a:

```text
RESET / Fault Acknowledge
```

This acknowledges any active alarms currently stored in the controller.

---

# Step 3 – Review Fault Codes

Before clearing any alarms:

Review all available fault information.

Verify:

- Active fault codes
- Cleared (historical) fault codes
- Associated operating hours (when available)

> **Important**
>
> Record all fault information before clearing the controller.
>
> This information may assist technicians if a service call becomes necessary.

---

# Step 4 – Clear the Fault Codes

After recording the fault information:

Clear the fault code(s) from the controller.

Confirm that the controller no longer displays active alarms before continuing.

---

# Step 5 – Return the Controller to Manual Mode

Place the generator controller into:

```text
MANUAL
```

mode.

---

# Step 6 – Attempt to Start the Generator

Attempt to start the generator.

---

# Evaluate the Result

## Generator Starts Successfully

If the generator starts normally:

- Continue monitoring operation.
- Verify that no new fault codes become active.
- Confirm normal operating conditions before returning the generator to service.

---

## Generator Does Not Start

If the generator does not start:

- Do not continue attempting repeated resets.
- Record the fault codes displayed.
- Contact the Service Department.
- Schedule a technician if required.

---

# Information to Record

Before contacting the Service Department, record as much information as possible.

Recommended information includes:

- Active fault codes
- Historical fault codes
- Generator operating hours
- Alarm descriptions
- Whether the generator started after the reset
- Any abnormal observations

Examples:

- FC1223
- Low Coolant
- High Engine Temperature
- Battery Voltage Low

---

# Safety Considerations

Do not continue troubleshooting if:

- Unsafe working conditions exist.
- Electrical hazards are present.
- Fuel leaks are observed.
- Smoke or fire is present.
- The customer requests work to continue under unsafe conditions.

Refer to the **Stop Work Authority** policy whenever safety concerns are identified.

---

# Best Practices

- Record all fault information before clearing alarms.
- Limit fault resets to basic troubleshooting purposes.
- Verify generator operation after every reset.
- Escalate recurring or unresolved faults to the Service Department.
- Document all observations for the assigned technician.

---

# Common Mistakes

## Clearing Fault Codes Too Early

Always record the active and historical fault codes before clearing them.

Failure to do so may remove valuable diagnostic information.

---

## Multiple Reset Attempts

Repeatedly clearing the same fault without identifying the underlying issue is not recommended.

If the fault immediately returns, arrange for service.

---

## Skipping Manual Mode

Ensure the controller has been returned to **MANUAL** mode before attempting to start the generator.

---

## Missing Fault Information

Whenever possible, provide the Service Department with:

- Fault code
- Alarm description
- Generator hours
- Observed symptoms

This information significantly improves troubleshooting efficiency.

---

# Future Improvements

This procedure should be expanded as additional technical guidance becomes available.

Potential additions include:

- Controller-specific reset procedures (PCC2100, PCC3100, PCC3300, etc.)
- Common fault code examples
- Customer troubleshooting steps
- Decision trees for common alarms
- Supporting photographs and controller screenshots