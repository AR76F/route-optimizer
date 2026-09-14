---
title: Warranty SRT and Labor
title_fr: Temps de réparation standard et main-d'œuvre sous garantie
category: warranty
subcategory: srt_labor
system: BMS
language: bilingual
keywords:
  - SRT
  - Standard Repair Time
  - labor
  - main-d'œuvre
  - 99-999
  - 99-990
---

# Last Updated: 2026-09-14

# Warranty SRT and Labor

## Purpose

This document describes the shared process for finding Standard Repair Times (SRTs), entering them in BMS, and allocating warranty labor. Product-specific search locations and exceptions belong in the applicable warranty folder.

## Find the SRT

Select SRTs based on the actions documented in the technician's report.

- **Onan:** PGBU → **Tools & Resources** → **SRT Lookup** → enter the generator serial number and search using keywords from the report.
- **CECO:** QuickServe Online → enter the serial number → **Warranty** → **Standard Repair Time** → select **Default / Out of Chassis** under Manufacturer → **Quick Search**.

When searching, use meaningful keywords from the actual repair action. If the first search fails, try equivalent terms used in the technical documentation.

## Enter SRTs in BMS

1. Open the **Job Plan** tab.
2. Add each applicable SRT.
3. Enter the quantity and required alternate or rate values.
4. Retrieve or confirm the SRT.
5. Select **Build Correction Narrative**.
6. In **Correction**, explain in English what the technician did for each SRT.
7. Compare the SRT time with the technician's actual time.

## Additional Labor

Use `99-999` only for time that cannot be represented by an available SRT and that is supported by the technician's report. The report must clearly explain the additional time and the action performed. The training material recommends entering the additional time in clear blocks, such as four-hour blocks, when appropriate.

Use `99-990` for travel time when the applicable warranty permits it.

Do not use additional labor codes to conceal missing documentation or unsupported time.

## Apply Warranty Allocation

After the SRTs and additional labor are entered:

1. In **Job Plan**, select **Default SRT Warranty** when available.
2. Set the applicable labor allocation to `100%` only when the warranty covers the full labor amount.
3. Return to **Total WO** and compare technician actual hours with allocated SRT hours.
4. Confirm the warranty labor amount and the remaining customer amount are correct.
5. Remove or uncheck non-warranty administrative items when required so the Work Order reflects the correct warranty allocation.

The presentations also identify `88 ADM` as an item to uncheck in the demonstrated workflow. Confirm this rule for the specific claim before applying it.

## Verification

The SRT and labor entry must agree with the technician's report. Every `99-999` entry must have a clear explanation in the SRO or correction documentation. If no applicable SRT exists, document the reason and follow the applicable approval or exception process.

## Résumé en français

Les SRT doivent être choisis selon les actions réellement effectuées par le technicien. Les rechercher dans PGBU pour Onan ou QuickServe Online pour CECO, puis les entrer dans **Job Plan**. Utiliser `99-999` seulement pour le temps supplémentaire justifié et `99-990` pour le déplacement lorsque la garantie le permet. Vérifier ensuite l’allocation dans **Total WO**.

