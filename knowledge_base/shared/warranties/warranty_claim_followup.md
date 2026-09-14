---
title: Warranty Claim Follow-up
title_fr: Suivi des réclamations de garantie
category: warranty
subcategory: claim_followup
system: BMS
language: bilingual
keywords:
  - warranty follow-up
  - claim status
  - variance
  - resubmit
  - suivi de garantie
---

# Last Updated: 2026-09-14

# Warranty Claim Follow-up

## Purpose

This document describes the shared follow-up process after a warranty claim has been created and the Work Order or invoice has been completed.

## Before Completing the Claim

In BMS, verify the required claim fields, including:

- Routing Code
- Engine Serial Number or unit serial number
- Application Code
- Pay Code
- Claim Type
- Failure Code and transmission status
- Failure date
- Hours or mileage
- Unit information
- All four C sections
- SRT, labor, parts, and charge allocation

Use `MFG: UNL`, `Model: ALL`, and `CONFI: ALL` only when the applicable troubleshooting guidance identifies them as an appropriate resolution for a configuration issue. Do not use them to bypass missing claim information.

## Complete the Claim

1. Open **Total Claim** in BMS.
2. Click **Complete**.
3. If completion fails, read the BMS error message and correct the identified issue.
4. If BMS accepts the claim, record the Sibel claim number.
5. Follow the claim until it is paid, requires a variance decision, or requires resubmission.

## Reopen a Claim

When a completed invoice requires verification or correction:

1. Go to **Claims Management → Manage Claim Process → Create/Update Claim**.
2. Press `F7`.
3. Enter `Z8/AK` followed by the Work Order number.
4. Press `F8`.
5. Select the claim and click **Reopen Claim**.
6. Correct the information and verify the claim again before final submission.

## Regular Monitoring

The training material states that warranty follow-up emails are received on Tuesdays and Thursdays. Use them to review claim status and accept variances when appropriate.

The training material identifies the following timing impacts:

| Claim age | Stated impact |
|---|---|
| 89 days or less | No penalty |
| 90 days or more | 80% labor plus 10% parts markup |
| 120 days or more | 80% labor plus 10% parts markup |
| 180 days or more | 50% labor and no parts markup |
| 365 days or more | No reimbursement |

These thresholds should be confirmed against the current official warranty policy before they are used as an operational rule.

## Variances and Resubmission

When a variance is received:

- Review the reason and affected labor, parts, or charges.
- Accept the variance when the result is correct and authorized.
- Correct the claim and resubmit it when the variance resulted from an error or missing information.
- Record unresolved issues and escalate them through the applicable warranty channel.

## Résumé en français

Après la création de la réclamation, vérifier les champs obligatoires, compléter le **Total Claim**, noter le numéro Sibel et suivre l’état de la réclamation. En cas d’erreur, corriger les données avant de soumettre de nouveau. Les courriels de suivi sont indiqués comme étant reçus les mardis et jeudis. Les pénalités liées à l’âge des réclamations doivent être confirmées dans la politique officielle actuelle.

