# Prioritization Engine

## Overview

The **Prioritization Engine** defines a single, shared prioritization logic used by both the **Service** and **Project Management (PM)** organizations.

Every work item—whether it is a service call, equipment failure, commissioning activity, or preventive maintenance task—is assigned a standardized priority code. This code enables consistent comparison of all work across the organization and ensures that scheduling decisions are based on a common set of rules.

The engine is designed to be deterministic: given the same inputs, it will always produce the same priority.

---

## Objective

The goal of the Prioritization Engine is to:

- Establish a unified prioritization model across the Service and PM departments.
- Assign every job a standardized priority code.
- Allow any two jobs to be compared instantly.
- Remove ambiguity from scheduling decisions.
- Provide the foundation for an interactive tool that determines job urgency automatically.

---

## Priority Code

Each job receives a priority code using the following structure:

```
P#-C#
```

Where:

- **P#** = Priority level (highest importance first)
- **C#** = Client class (used when priorities are equal)

The code is evaluated from **left to right**, meaning:

1. Priority level is compared first.
2. If priorities are identical, client class is compared.
3. Additional criteria may be introduced in future versions if required.

Example:

```
P1-C2
P2-C1
```

`P1-C2` has higher priority because the priority level takes precedence over the client class.

---

## Decision Principle

The prioritization code allows planners and dispatchers to compare any two jobs immediately and determine:

- Which job should be executed first.
- Which job can remain in the schedule.
- Whether a new incoming job should replace an existing scheduled job.

This creates a transparent and repeatable decision-making process.

---

## Future Interactive Tool

This prioritization logic will serve as the core of an interactive application.

The application will:

1. Ask the user a series of business questions.
2. Evaluate the responses according to the prioritization rules.
3. Automatically generate the appropriate priority code.
4. Explain why the assigned priority was selected.

---

## Repository Purpose

This repository contains the documentation, business rules, and supporting artifacts required to define and maintain the Prioritization Engine.

It is intended to be the single source of truth for:

- Prioritization rules
- Priority code definitions
- Decision logic
- Documentation
- Future implementation guidance