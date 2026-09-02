# Power BI - WIP Management

# Last Updated: 2026-09-02

## Purpose

This document explains how Service Coordinators use Power BI to retrieve and manage the Work In Progress (WIP) report.

The WIP report is used to monitor open Work Orders, prioritize follow-up actions, and maintain an acceptable Days Sales Outstanding (DSO).

---

## Objectif

Ce document explique comment les coordonnateurs de service utilisent **Power BI** pour consulter, exporter et gérer le rapport **WIP (Work In Progress)**.

Le rapport WIP permet notamment de :

- Consulter les bons de travail ouverts.
- Identifier les travaux en attente ou vieillissants.
- Suivre les jours sans main-d'œuvre (**DNL - Days No Labor**).
- Prioriser les suivis et la facturation.
- Maintenir un niveau acceptable de **DSO (Days Sales Outstanding)**.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official SharePoint document for the **Power BI WIP Management** procedure contains the original visual guide and screenshots for accessing, filtering, and exporting the WIP report.

Le document SharePoint officiel de la procédure **Power BI WIP Management** contient le guide visuel original et les captures d'écran pour consulter, filtrer et exporter le rapport WIP.

**Official SharePoint Link:**

[Open the Power BI WIP Visual Guide / Ouvrir le guide visuel Power BI WIP](https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQDsqKdqWoJKR6_Ns-wmptWTAbp8RzaPAdPacwu-VSLZvPg?e=gqgBwA)

### Link Retrieval Rule / Règle de récupération du lien

When a user asks for the **WIP procedure, WIP source document, SharePoint link, original document, official guide, visual guide, screenshots, or WIP training material**, provide the **Official SharePoint Link above**.

Lorsqu'un utilisateur demande la **procédure WIP, le document source WIP, le lien SharePoint, le document original, le guide officiel, le guide visuel, les captures d'écran ou le matériel de formation WIP**, fournir le **lien SharePoint officiel ci-dessus**.

Examples of requests that should return this link:

**English**
- Give me the WIP procedure.
- Do you have the WIP SharePoint link?
- Show me the WIP source document.
- Where is the visual WIP guide?
- Give me the original Power BI WIP procedure.

**Français**
- Donne-moi la procédure WIP.
- As-tu le lien SharePoint du WIP?
- Donne-moi le document source du WIP.
- Où est le guide visuel du WIP?
- As-tu un lien pour cette procédure?

---

## Quick Reference / Référence rapide

**Power BI WIP / WIP Detail / Work In Progress**

Use this resource when looking for:

- WIP
- WIP management
- WIP report
- Open Work Orders
- WIP Detail
- Work Order aging
- Days No Labor (DNL)
- Days Sales Outstanding (DSO)
- WIP Excel export

Termes de recherche en français :

- WIP
- Gestion du WIP
- Rapport WIP
- WIP Power BI
- WIP Detail
- Travaux en cours
- Bons de travail ouverts
- BT ouverts
- Exporter le WIP
- Exporter WIP en Excel
- Jours sans main-d'œuvre
- DNL
- DSO
- Suivi des bons de travail
- Vieillissement des bons de travail

---

## Power BI WIP Link / Lien Power BI WIP

The **WIP Detail** report can be accessed directly using the Power BI link below.

Le rapport **WIP Detail** peut être consulté directement à partir du lien Power BI ci-dessous.

**Power BI WIP:**

[Open WIP Detail in Power BI / Ouvrir WIP Detail dans Power BI](https://app.powerbi.com/groups/me/apps/ed3dd510-050a-47ed-9455-477e60121d5d/reports/22237f46-ec09-4610-94f3-865fe6b5eb39/ReportSection7a177c83064b2c714917?experience=power-bi)

### Link Retrieval Rule / Règle de récupération du lien

When a user asks for the **WIP link, Power BI WIP link, WIP dashboard, WIP Detail report, or direct access to the WIP**, provide the Power BI link above.

Lorsqu'un utilisateur demande le **lien WIP, lien Power BI du WIP, tableau de bord WIP, rapport WIP Detail ou accès direct au WIP**, fournir le lien Power BI ci-dessus.

---

# Systems Used

- Power BI
- Microsoft Excel

---

# Opening Power BI

It is recommended to use **Google Chrome** when accessing Power BI.

Open the Power BI dashboard.

On the left navigation panel:

1. Select **Most Used**.
2. Open **WIP**.
3. Select **WIP Detail**.

This report displays all open Work Orders.

---

# Recommended Filters

Apply the following filters before reviewing the report.

| Filter | Recommended Value |
|----------|-------------------|
| GEO / AREA VP | All |
| BRANCH | Candiac or Ottawa |
| SUPERVISOR | Your Name |
| WIP Category | All |

All remaining filters may remain on **All** unless a more specific search is required.

---

# Exporting the WIP Report

To export the report:

1. Select the **three-dot menu** (⋯).
2. Choose:

```text
Export Data
```

3. Select:

```text
Data with current layout
```

4. Select:

```text
Export
```

The report will be downloaded as a Microsoft Excel file.

---

# Opening the Export

Locate the downloaded file.

Depending on your browser settings, it may be found in:

- Browser Downloads
- Windows Downloads folder
- Another user-defined download location

Open the Excel file.

---

# Preparing the Spreadsheet

The exported spreadsheet contains numerous columns.

Hide columns that are not required for daily WIP management.

To hide a column:

1. Right-click the column header.
2. Select:

```text
Hide
```

This allows the report to focus on the information most relevant to the Service Coordinator.

---

# Key Columns

The following columns are typically the most useful.

| Column | Description |
|----------|-------------|
| ORDER # | Work Order Number |
| SUBTYPE | Work Order subtype |
| WO SUP. NAME | Assigned supervisor |
| AGE | Age of the Work Order |
| DNL | Days No Labor |
| TOTAL | Total Work Order value |
| CUST. NAME | Customer name |
| BMS STATUS COMMENT | Current status and coordinator notes |

---

# Using the WIP Report

The WIP report should be reviewed regularly to:

- Monitor open Work Orders.
- Identify aging work orders.
- Follow up on jobs with no recent labor activity.
- Identify invoices requiring attention.
- Prioritize coordinator workload.

Regular review of the report helps reduce delays in billing and work order completion.

---

# Performance Objective

The objective is to maintain the WIP report as accurately as possible.

Particular attention should be given to:

- Aging Work Orders
- Days No Labor (DNL)
- Days Sales Outstanding (DSO)

Target:

```text
DSO < 13 Days
```

Maintaining a low DSO improves branch cash flow and overall operational performance.

---

# Best Practices

- Review the WIP report daily.
- Apply filters before exporting.
- Hide unnecessary columns to simplify analysis.
- Prioritize Work Orders with high AGE or DNL values.
- Keep BMS Status Comments up to date to reflect current progress.

---

# Common Mistakes

## Incorrect Branch Selected

Verify that the correct branch has been selected before exporting the report.

---

## Reviewing All Supervisors

Filter by your own supervisor name unless reviewing branch-wide performance.

---

## Ignoring Aging Work Orders

High AGE and DNL values often indicate Work Orders requiring immediate follow-up.

---

## Outdated Status Comments

Keep BMS Status Comments current to ensure the WIP accurately reflects the latest progress.

---

# Coordinator Tip

The WIP report is one of the most valuable tools for managing daily workload.

Reviewing it at the beginning and end of each day helps identify overdue Work Orders, prioritize invoicing activities, and maintain the branch's DSO target.