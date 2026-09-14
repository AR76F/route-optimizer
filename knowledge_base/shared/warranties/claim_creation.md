---
title: Warranty Claim Creation
title_fr: Création d'une réclamation de garantie
category: warranty
subcategory: claim_creation
system: BMS
language: bilingual
keywords:
  - warranty claim
  - claim type
  - création de réclamation
  - BMS
  - account code
  - pay code
---

# Last Updated: 2026-09-14

# Warranty Claim Creation

## Purpose

This document describes the shared BMS workflow for creating a warranty claim after coverage, the failed component, and the Failure Code have been verified. Vendor, Claim Type, and other values vary by warranty and must be confirmed in the applicable product-specific document.

## Before Creating the Claim

Confirm that the Work Order contains:

- The correct unit and serial number
- The Date in Service or Warranty Start Date
- Current hours or mileage
- The failed component and root cause
- The Failure Code
- The technician's repair documentation
- The repair location: in-shop or field service
- The applicable warranty vendor and coverage path

## Warranty Tab

1. Open the **Warranty** tab in BMS.
2. Complete the applicable warranty fields.
3. Enter the **Warranty Start Date**. For a parts-only warranty, use the part purchase date when required by the applicable procedure.
4. Enter the operating hours or mileage.
5. Set **Severity** to `B` when required by the warranty workflow.

## Claim Tab

Complete the **Claim** section using the values applicable to the warranty:

- **Claim Type:** select the in-shop or field-service value specified for the warranty.
- **Account Code:** the training material identifies `67` for base Onan and CECO claims. Other codes include `62` for new parts, `65` for campaigns, `68` for policy, `70` for emissions, `96` for BIS, and `97` for reconditioned parts. Confirm the correct code before submission.
- **Pay Code:** the training material identifies `X` for the distributor workflow.
- **Serial Number:** select or enter the unit serial number using **LOV**.
- **Routing Indicator:** complete it only when required by the applicable warranty.

## Unit and Failure Tabs

1. Complete the product-specific unit information.
2. Confirm the application and configuration values.
3. Return to the **Failure** tab.
4. Add the applicable Claim Type if BMS did not populate it automatically.
5. Use **Build Cause Narrative** when available to generate the Cause text.
6. Confirm that the narrative accurately reflects the technician's report.

## Multiple Claims on One Work Order

When multiple claims are recorded on the same Work Order, additional allocation and claim-management steps may apply. Follow the applicable multi-claim procedure before completing the invoice.

## Final Pre-Submission Check

Verify the Routing Code, Engine Serial Number or unit serial number, Application Code, Pay Code, Claim Type, Failure Code, failure date, hours or mileage, and the required 4 C documentation. Then continue with the SRT, labor, parts, and charge-allocation procedures.

## Résumé en français

Avant de créer la réclamation, vérifier l’unité, le numéro de série, la date de début de garantie, les heures ou le kilométrage, la pièce défectueuse, la cause, le code de défaillance et le type de travail. Dans BMS, remplir les onglets **Warranty**, **Claim**, **Unit** et **Failure** avec les valeurs propres à la garantie concernée. Les codes de compte et les indicateurs de routage doivent être confirmés avant l’envoi.

