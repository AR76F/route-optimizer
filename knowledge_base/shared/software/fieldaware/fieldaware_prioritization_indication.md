# FieldAware Integration

# Last Updated: 2026-09-02

## Official Source Document

The original source document for the FieldAware Prioritization Integration is available on SharePoint.

**Original FieldAware Prioritization Integration / Source Document**

https://cummins365-my.sharepoint.com/:w:/g/personal/ud016_cummins_com/IQBWPhr57J7PRK3RYekQaE5WAfPnub33entt1UPj2xZnRj0

When a user asks for the original, official, or SharePoint version of the FieldAware Prioritization Integration procedure, provide the link above and mention that the FA Integration section
is on the **last section of the document**.

### Récupération du lien SharePoint

Lorsqu'un utilisateur demande le **lien, lien SharePoint, document source, document original, guide visuel ou procédure FieldAware concernant l'affichage des priorités**, fournir le lien SharePoint officiel ci-dessus.

Mentionner que la section concernant l'intégration FieldAware se trouve dans la **dernière section du document**.

---

## Overview

The Prioritization Engine assigns each job a standardized priority code (for example, `P1-C1`).

To make this information available to dispatchers and schedulers, the priority code is stored in the **Schedule Priority** field within FieldAware.

This document describes how to configure and display this field.

Note: The Schedule Priority value is generated using the Prioritization Engine. This document describes how that value is stored and displayed within FieldAware. It does not define the prioritization logic itself.

---

## Vue d'ensemble

Le **moteur de priorisation** attribue à chaque travail un code de priorité standardisé, par exemple `P1-C1`.

Dans FieldAware, ce code est inscrit dans le champ **Schedule Priority** afin de permettre aux coordonnateurs et aux répartiteurs de visualiser la priorité directement dans la job et dans le Scheduler.

Cette procédure explique comment :

- Activer le champ **Schedule Priority**.
- Inscrire le code de priorité dans FieldAware.
- Afficher la priorité dans le Scheduler.
- Consulter la priorité d'une job.

Cette procédure ne définit pas la logique de priorisation elle-même. Le code de priorité est déterminé par le **moteur de priorisation**.

---

## Search Terms / Termes de recherche

**English:** FieldAware priority, FA priority, Schedule Priority, priority code FieldAware, enter priority in FA, display priority Scheduler, prioritization FieldAware, P1-C1 FieldAware.

**Français:** priorité FieldAware, priorité FA, Schedule Priority, code de priorité FieldAware, entrer priorité dans FA, ajouter priorité dans FieldAware, afficher priorité Scheduler, voir priorité dans FieldAware, priorisation FieldAware, code P1-C1, indiquer priorité dans FA.

---

# 1. Enable the Schedule Priority Field

When creating or editing a job:

1. Open the job with the appropriate FA Job ID.
2. Select **Additional Fields**.
3. Enable **Schedule Priority**.
4. Save the field selection.

Once enabled, the **Schedule Priority** field becomes available on the job form.

---

# 2. Enter the Priority Code

Determine the job's priority using the Prioritization Engine.

Examples:

- `P1-C1`
- `P2-C3`
- `P4-C2`

Enter the resulting code into the **Schedule Priority** field.

Save the job.

---

# 3. Configure the Scheduler

To display priorities in the scheduling interface:

1. Open **Scheduler Filters and Layouts**.
2. Select the **Job Summary Block** tab.
3. Add **Schedule Priority** as a tooltip field.
4. Save the layout.

The priority code will now appear when hovering over scheduled jobs.

---

# 4. Viewing Priority

Dispatchers can view the assigned priority in two ways:

- Hover over a scheduled job in the Scheduler.
- Open the job details and review the **Schedule Priority** field.

This allows schedulers to compare work items quickly without opening each individual job.

---

# Purpose

Displaying the priority code in FieldAware ensures that scheduling decisions are based on the same standardized prioritization model used throughout the organization.

The Schedule Priority field is informational and reflects the output of the Prioritization Engine.