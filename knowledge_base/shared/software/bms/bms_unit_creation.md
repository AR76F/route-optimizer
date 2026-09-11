# BMS - Unit Creation

# Last Updated: 2026-09-03

## Purpose

This procedure explains how to create a new generator Unit in BMS when no existing Unit can be associated with the Work Order.

Use [BMS - Work Order Creation](bms_work_order_creation.md) for selecting an existing Unit and completing the Work Order.

## Objectif

Cette procédure explique comment créer une nouvelle unité de génératrice dans BMS lorsqu’aucune unité existante ne peut être associée au bon de travail.

Consultez [BMS - Work Order Creation](bms_work_order_creation.md) pour sélectionner une unité existante et compléter le bon de travail.

## Quick Reference / Référence rapide

```text
Confirm no existing Unit is available
        ↓
Open Units and create a new record
        ↓
Enter customer, serial-number, product, and site information
        ↓
Set family 99 and application code 0810
        ↓
Answer the overhaul question
        ↓
Save and Send to FA
```

### French Retrieval Metadata

**Création unité BMS / nouvelle unité / génératrice / Unit / Unit-Products / numéro de série / VIN / GSN / moteur / Engine Detail / code application 0810 / Send to FA**

## SharePoint Visual Reference

The visual BMS Unit Creation guide is maintained on SharePoint.

**SharePoint Link:** `[https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQACOQw4keJPTYBOVTlP-0SkAZAo7AOR5Tb9XsCla_KZufk?e=dmLd0C]`

The Markdown procedure is the detailed text reference; the visual guide is supplemental.

# 1. Confirm That a New Unit Is Required

Create a new Unit only when the customer’s generator cannot be found in the existing Unit lookup.

Before creating it, check the serial number, model, customer, and site information carefully to avoid duplicate Units.

# 2. Open a New Unit

1. Open **Units** in BMS.
2. Use **F6** to create a new Unit record.
3. Confirm that editable fields are available before entering information.

## Customer Information

Enter the customer’s **Customer Number**.

## Unit Information

Complete the applicable fields:

| Field | Value or guidance |
|---|---|
| Unit | Usually the generator serial number |
| VIN / GSN | Generator serial number |
| Manufacturer | Usually **Onan**, or the actual manufacturer |
| Model | Generator model; use **GENSET** only when the model is unavailable |
| Unit Type | **ST** |
| Labor Multiplier | Select A, B, or C according to equipment size when not assigned automatically |
| Site | Existing customer site, when available |
| Segment | **STANDBY** unless the applicable contract requires **SOLUTIONS** |

## Product Information

Under **Products**, enter or verify:

- Serial Number.
- Model Number or model designation.
- Product family.

Use the Serial Number Lookup Tool in the PGBU Warranty System when needed to identify the correct model.

Set:

| Field | Value |
|---|---|
| Family | **99** |
| Application Code | **0810** |

Enter the application code under **Engine Detail**.

## Overhaul Question

If BMS asks whether the product is being added because of an overhaul, major rebuild, or repower, select:

```text
No
```

# 3. Verify the Unit and Site

Before saving, verify:

- Customer number.
- Serial number and VIN/GSN.
- Manufacturer and model.
- Unit type and segment.
- Product family and application code.
- Associated customer site.

If the site does not exist, use [BMS - Site Creation](bms_site_creation.md).

# 4. Save and Synchronize

1. Save the Unit using **F10** or the BMS save command.
2. Select **Send to FA** to synchronize the new Unit with FieldAware.
3. Return to the Work Order and select the new Unit.

## Safety Concerns

Safety concerns are not part of the creation fields, but they must be recorded when known. Use **Misc. Info > Safety Concerns** to enter the concern and detailed description, then save the record.

## Common Mistakes

- Creating a duplicate Unit instead of searching first.
- Entering the wrong serial number or model.
- Omitting Family `99` or Application Code `0810`.
- Selecting the wrong Unit Type or Segment.
- Forgetting to associate the correct Site.
- Saving the Unit without selecting **Send to FA**.

## Related Documents

- [BMS - Work Order Creation](bms_work_order_creation.md)
- [BMS - Site Creation](bms_site_creation.md)
- [FieldAware - Work Order Creation](fieldaware_work_order_creation.md)
- [BMS - Searching Records](bms_searching_records.md)

## Search Terms / Termes de recherche

**English:** BMS unit creation, create Unit, new generator Unit, Unit Products, serial number, VIN, GSN, manufacturer, model, unit type ST, family 99, application code 0810, Engine Detail, Send to FA.

**Français:** création unité BMS, créer une unité, nouvelle unité de génératrice, unité-produits, numéro de série, VIN, GSN, fabricant, modèle, type unité ST, famille 99, code application 0810, détails moteur, Send to FA.
