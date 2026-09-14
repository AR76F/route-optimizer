---
title: Warranty Failure Codes
title_fr: Codes de défaillance de garantie
category: warranty
subcategory: failure_codes
system: BMS
language: bilingual
keywords:
  - failure code
  - fail code
  - code de défaillance
  - BMS
  - QuickServe
  - PGBU
---

# Last Updated: 2026-09-14

# Warranty Failure Codes

## Purpose

This document describes the shared process for identifying and entering a warranty Failure Code in BMS. The correct source and code depend on the product and failed component. Product-specific rules belong in the applicable warranty folder.

## Required Information

Before selecting a code, review:

- The technician's diagnosis and report
- The failed component and root cause
- The unit or engine serial number
- The applicable product and vendor
- Any progressive damage caused by the original failure

Do not select a code from the symptom alone when the technician's report identifies a more specific failed component or cause.

## Find the Failure Code

Use the applicable warranty reference:

- **Onan:** PGBU → **Tools & Resources** → **Warranty Coverage Lookup** → enter the serial number and Fail Date → **Fail Code Inclusion List**. Search the list for the failed part.
- **CECO engine:** QuickServe Online → **Warranty** → **Warranty Failure Code Manual**. Search using a relevant component or failure keyword.
- **CECO electric bus:** QuickServe Online → **Warranty Failure Code Manual for All Electrifications**. Select the code that matches the electric-bus component and failure.

If the Date in Service does not populate in PGBU, the unit may not be registered. Follow the applicable product-specific registration procedure before relying on the coverage result.

## Enter the Code in BMS

1. Open the **Failures** tab in BMS.
2. Place the cursor in **Product Group** and open the lookup using the search icon.
3. Enter the identified **Major** and **Minor** codes.
4. Press `F8` to display the results.
5. Select the failure mode that matches the technician's diagnosis, such as `BR` for broken or `SR` for shorted.
6. Click **Selected** to confirm the code.
7. Enter the applicable location. The training material identifies `AA` for the relevant electric-bus CECO workflow, but product-specific location rules must be followed.

## Verification

Before submitting the claim, verify that:

- The code describes the failed component and documented cause.
- The code belongs to the correct product group and vendor.
- The failure date, hours, or mileage are present.
- Progressive damage is documented when applicable.
- The code has been transmitted or accepted in BMS.

If the code is unclear or unavailable, confirm the diagnosis with the technician and consult the applicable warranty system or manual. Do not invent or guess a code.

## Résumé en français

Le code de défaillance doit correspondre à la pièce défectueuse et à la cause documentée par le technicien. Utiliser PGBU pour Onan et QuickServe Online pour CECO, y compris le manuel des codes de défaillance pour les systèmes d’électrification. Entrer ensuite les codes Major et Minor dans l’onglet **Failures** de BMS et vérifier le produit, le fournisseur, la date de défaillance ainsi que les heures ou le kilométrage.

