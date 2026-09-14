---
title: Onan Generator Warranty Claims
title_fr: Réclamations de garantie des génératrices Onan
category: warranty
subcategory: generator_claim
vendor: Onan
system: BMS
language: bilingual
keywords:
  - Onan warranty claim
  - generator warranty claim
  - ONAN
  - ONANFSPG
  - PGBU
  - Routing Indicator
  - Unit Config
  - Appl Code
---

# Last Updated: 2026-09-14

# Onan Generator Warranty Claims

## Purpose

This document records the Onan-specific values and decisions used when creating a generator warranty claim in BMS. Follow the shared claim-creation, failure-code, SRT, documentation, and follow-up procedures for the complete sequence.

## Confirm the Coverage Path

1. Verify the generator serial number and Date in Service in PGBU.
2. Confirm that the failed component is part of the Onan generator assembly.
3. Confirm the covered failure and applicable Failure Code.
4. Confirm whether the work was performed in-shop or in the field.

## Onan Claim Type

Use the Claim Type that matches the repair location:

- `ONAN` for Onan work performed in-shop.
- `ONANFSPG` for Onan field-service work.

The training material states that **Routing Indicator** must be set to `Y` for Onan claims.

## BMS Values Identified in the Training

The step-by-step material identifies these values for the demonstrated Onan claim workflow:

- **Vendor:** `Onan`
- **Account Code:** `67` for a base claim
- **Pay Code:** `X`
- **Unit Config:** `ST`
- **Appl Code:** `0810`
- **Severity:** `B`
- **Routing Indicator:** `Y`

Confirm the values against the current warranty procedure when the claim is a campaign, policy, emissions, BIS, parts-only, reconditioned-parts, or other special claim.

## Create and Verify the Claim

1. Apply the correct Failure Code from PGBU.
2. Complete the **Warranty**, **Claim**, **Unit**, and **Failure** sections in BMS.
3. Add `ONAN` or `ONANFSPG` in the **Failure** section when BMS does not populate it automatically.
4. Enter the Warranty Start Date, failure date, and operating hours.
5. Confirm `Unit Config = ST` and `Appl Code = 0810` for the demonstrated Onan workflow.
6. Set **Routing Indicator** to `Y`.
7. Complete the four C's and SRO or Correction narrative.
8. Add the applicable SRTs and any justified additional labor.
9. Verify parts and labor allocation in **Total WO**.
10. Complete and follow the claim using the shared follow-up procedure.

## Onan Parts Warranty

The presentation documents a parts-only claim using account code `62` for an Onan or CECO part purchased within the applicable period. For an Onan parts claim, confirm the current parts-warranty rules and then verify:

- **Warranty Account Code:** `62` rather than the base-claim code.
- **Warranty Start Date:** part purchase date.
- **Hours on failed part:** hours on the part since installation, calculated from the relevant previous Work Order and current Work Order.
- The four C's include the generator serial number, part purchase date, part failure date, and hours on the failed part.

Do not use these values for a standard claim unless the applicable parts-warranty procedure requires them.

## Related Procedures

- [Generator Warranty Overview](generator_warranty_overview.md)
- [Warranty Failure Codes](../failure_codes.md)
- [Warranty Claim Creation](../claim_creation.md)
- [Warranty SRT and Labor](../srt_and_labor.md)
- [Warranty Claim Documentation: 4 C and SRO](../claim_documentation_4c_and_sro.md)
- [Warranty Claim Follow-up](../warranty_claim_followup.md)

## Source Limitations

This document reflects the supplied internal presentations. It does not replace the current official Onan warranty administration or coverage documentation.

## Résumé en français

Pour une réclamation Onan, utiliser `ONAN` en atelier ou `ONANFSPG` sur le terrain, avec `Onan` comme fournisseur. Le Routing Indicator doit être `Y`. Pour le processus présenté, utiliser Unit Config `ST`, Appl Code `0810`, le code de compte `67`, le Pay Code `X` et Severity `B`. Vérifier les règles actuelles pour les réclamations de pièces, qui peuvent utiliser le code `62` et la date d’achat de la pièce.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the Generator (Onan) Warranty Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQCjP3qz3E4yR7fgXVQTT12SAYsoa3P-FE2WkJVsHn0878o?e=his6R8)

---

## Search Terms / Termes de recherche

**English:** generator warranty, Onan warranty, Onan generator warranty, Onan warranty claim, generator warranty claim in BMS, ONAN, ONANFSPG, PGBU, Warranty Coverage Lookup, Fail Code Inclusion List, Routing Indicator, Unit Config, Appl Code, Date in Service, Warranty Start Date, Account Code 67, Pay Code X, Severity B, parts warranty, account code 62.

**Français:** garantie génératrice, garantie Onan, garantie de génératrice Onan, réclamation de garantie Onan, réclamation garantie génératrice BMS, ONAN, ONANFSPG, PGBU, Warranty Coverage Lookup, Fail Code Inclusion List, Routing Indicator, Unit Config, Appl Code, Date in Service, Warranty Start Date, code de compte 67, Pay Code X, Severity B, garantie de pièce, code de compte 62.


