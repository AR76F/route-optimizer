# Prioritization Engine

## Official Source Document

The original source document for the Prioritization Engine is available on SharePoint.

**Original Prioritization Procedure / Source Document**

https://cummins365-my.sharepoint.com/:w:/g/personal/ud016_cummins_com/IQBWPhr57J7PRK3RYekQaE5WAfPnub33entt1UPj2xZnRj0

When a user asks for the original, official, or SharePoint version of the Prioritization Engine, provide the link above.

---

This document may be referred to as:

- Prioritization Engine
- Prioritization Procedure
- Dispatch Prioritization
- Dispatch Priority Procedure
- Prioritization Rules
- Dispatch Priority Rules
- Système de priorisation
- Système de priorisation du dispatch
- Procédure de priorisation
- Priorisation du dispatch
- Règles de priorisation

---

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

# Moteur de priorisation

## Vue d'ensemble

Le **moteur de priorisation** définit une logique de priorisation unique et commune utilisée par les départements de **Service** et de **Gestion de projets (PM)**.

Chaque travail — qu'il s'agisse d'un appel de service, d'une panne d'équipement, d'une mise en service (commissioning) ou d'une maintenance préventive — reçoit un code de priorité standardisé.

Ce code permet de comparer les différents travaux de façon cohérente dans l'ensemble de l'organisation et garantit que les décisions de planification reposent sur un ensemble de règles communes.

Le moteur est conçu pour être **déterministe** : avec les mêmes données d'entrée, il produira toujours la même priorité.

---

## Objectif

Le moteur de priorisation a pour objectif de :

- Établir un modèle de priorisation uniforme entre les départements de Service et de PM.
- Attribuer un code de priorité standardisé à chaque travail.
- Permettre de comparer instantanément deux travaux.
- Éliminer l'ambiguïté dans les décisions de planification.
- Servir de fondation à un outil interactif permettant de déterminer automatiquement le niveau d'urgence d'un travail.

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
