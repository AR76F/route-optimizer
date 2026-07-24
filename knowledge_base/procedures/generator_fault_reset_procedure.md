# Customer - Generator Does Not Start During a Power Outage

# Version 1.0.0

# Last Updated: 2026-07-23

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Creation of initial document.

## Purpose

This procedure provides Service Coordinators with a simple troubleshooting workflow to guide customers whose generator does not automatically start during a utility power outage.

The objective is to determine whether the issue can be resolved through basic operator actions before dispatching a technician.

> **Important**
>
> This procedure is intended for basic customer troubleshooting only.
>
> This procedure is intended for Cummins/Onan generators only.
>
> Customers should never perform work that exposes them to electrical hazards or unsafe conditions.
>
> If at any point the customer is uncomfortable performing a step, discontinue the procedure and schedule service.

---

# Workflow Overview

```text
Generator Does Not Start
        ↓
Verify AUTO Position
        ↓
Generator in Alarm?
        ↓
Yes ---------------- No
 ↓                    ↓
Reset Alarm       Manual Start
 ↓                    ↓
Starts?          Starts?
 ↓                    ↓
Yes      No      Yes      No
 ↓        ↓       ↓        ↓
Resolved  Call    Leave    Call
          Service Running  Service
```

---

# Step 1 – Verify the Controller Position

Ask the customer to verify that the generator controller **AUTO MANUAL / STOP** selector is in:

```text
AUTO
```

### If the selector is NOT in AUTO

Ask the customer to:

1. Turn the selector to **AUTO**.
2. The generator should start.

If the selector was accidentally left in another position, this may resolve the issue.

If the selector was already in **AUTO**, continue to **Step 2 - Check for Active Alarms**.

---

# Step 2 – Check for Active Alarms

Ask the customer whether the generator controller displays any **WARNING-SHUTDOWN** lights:

- Warning lights
- Shutdown lights
- Alarm messages
- Fault codes

If an alarm is present:

- Record the fault code displayed on the **DIGITAL DISPLAY** if visible.
- Record the operating hours at when the fault code appeared.
- Pull out the red **EMERGENCY STOP** button.
- Continue to Step 3.

If no alarms are present:

Proceed directly to **Step 4 – Manual Start**.

---

# Step 3 – Reset the Alarm

If the controller is in alarm:

### 3.1

Turn the **AUTO MANUAL / STOP** selector to:

```text
OFF
```

### 3.2

Press the white square

```text
FAULT ACKNOWLEDGE / RESET
```

button.

This clears acknowledged fault alarms.

### 3.3

Return the **AUTO MANUAL / STOP** selector to:

```text
AUTO
```

Observe whether the generator starts.

---

## Generator Starts

If the generator starts after the reset:

The issue has likely been resolved.

Continue monitoring the generator during normal operation.

If the alarm returns, contact Cummins Service.

---

## Generator Does Not Start

Proceed to **Step 4**.

---

# Step 4 – Manual Start

Ask the customer to place the controller **AUTO MANUAL / STOP** selector in:

```text
MANUAL
```

Then press the white square

```text
MANUAL RUN / STOP
```
button.

Attempt to manually start the generator.

---

## Generator Starts

If the generator starts successfully:

Allow the generator to continue operating until utility power has been restored.

Although the immediate issue has been resolved, recommend that the customer contact Cummins Service to investigate why the generator did not automatically start during the outage.

---

## Generator Does Not Start

If the generator still does not start:

Do not continue attempting repeated resets or starts.

Arrange for a Cummins Service technician.

---

# Information to Collect Before Dispatch

If a technician will be dispatched, collect as much information as possible from the customer.

Recommended information includes:

- Active fault code
- Alarm description
- Whether the generator started manually
- Whether the reset procedure was attempted
- Any unusual observations

Examples:

- Low Coolant
- High Engine Temperature
- FC1223
- Emergency Stop active

This information assists the Service Coordinator in selecting the appropriate technician and preparing the service call.

---

# Safety Reminders

Advise the customer to stop the procedure immediately if:

- Smoke is present.
- Fire is present.
- Fuel is leaking.
- Electrical hazards are observed.
- The generator appears unsafe to operate.

In these situations:

- Do not continue troubleshooting.
- Arrange for immediate service.

---

# Best Practices

- Record any fault codes before scheduling service.
- Walk through each troubleshooting step in order.
- Keep the customer informed throughout the process.
- Escalate the call if the generator cannot be safely restarted.

---

# Common Mistakes

## Selector Not Left in AUTO

A generator cannot automatically respond to a power outage unless the controller is left in **AUTO** mode.

---

## Alarm Reset Skipped

Always attempt a basic alarm reset before proceeding to manual start when an alarm is present.

---

## Repeated Start Attempts

Repeatedly attempting to start the generator without identifying the underlying fault may worsen the situation.

If the generator does not start after the basic procedure, schedule service.

---

## Missing Fault Information

Whenever possible, record any displayed alarm or fault code before dispatching a technician.

This information greatly improves troubleshooting efficiency.

## ATS Not Set in AUTO

A customer could check whether the ATS is set in **AUTO** or not. Simply setting the ATS correctly could resolve a downed generator situation.

## Breaker Turned off

A customer could check whether the breaker is correctly turned on. Simply turning on the breaker could resolve a downed generator situation.