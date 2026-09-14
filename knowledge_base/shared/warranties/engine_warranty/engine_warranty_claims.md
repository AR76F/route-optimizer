---
title: Generator Engine Warranty Claims
title_fr: Réclamations de garantie du moteur de génératrice
category: warranty
subcategory: engine_claim
vendor: CECO
system: BMS
language: bilingual
keywords:
  - engine warranty claim
  - CECO claim
  - FACT
  - FACTFSE
  - QuickServe
  - QSOL
  - réclamation garantie moteur
---

# Last Updated: 2026-09-14

# Generator Engine Warranty Claims

## Purpose

This document records the CECO-specific values and decisions used when creating a generator-engine warranty claim in BMS. Follow the shared claim-creation procedure for the complete sequence.

## Confirm the Coverage Path

1. Verify the engine or ESN and Date in Service in QuickServe Online.
2. Confirm that the failed component and documented root cause are covered.
3. Confirm whether the work was performed in-shop or in the field.
4. Confirm the correct CECO Claim Type before entering the claim.

## CECO Claim Type

Use the Claim Type that matches the repair location:

- `FACT` for CECO work performed in-shop.
- `FACTFSE` for CECO field-service work.

The training material states that **Routing Indicator** is not required for CECO claims. Leave it blank unless the current official procedure requires otherwise.

## BMS Values Identified in the Training

The step-by-step material identifies these values for the demonstrated CECO claim workflow:

- **Vendor:** `CECO`
- **Account Code:** `67` for a base claim
- **Pay Code:** `X`
- **Severity:** `B`

Confirm the values against the current warranty procedure when the claim is a campaign, policy, emissions, BIS, parts-only, or reconditioned-parts claim. Those claim categories may use different account codes.

## Create and Verify the Claim

Use the shared documents to complete the claim:

1. Apply the correct Failure Code from QuickServe Online.
2. Complete the **Warranty**, **Claim**, **Unit**, and **Failure** sections in BMS.
3. Add `FACT` or `FACTFSE` in the **Failure** section when BMS does not populate it automatically.
4. Enter the Warranty Start Date, failure date, and operating hours.
5. Complete the four C's and the SRO or Correction narrative.
6. Add the applicable SRTs and any justified additional labor.
7. Verify parts and labor allocation in **Total WO**.
8. Complete and follow the claim using the shared follow-up procedure.

## Troubleshooting Missing Configuration Data

If the engine or application information is missing, consult QuickServe Online and the applicable warranty documentation. Do not replace missing configuration data with generic values unless the current approved procedure explicitly authorizes it.

## Related Procedures

- [Generator Engine Warranty Overview](engine_warranty_overview.md)
- [Warranty Failure Codes](../failure_codes.md)
- [Warranty Claim Creation](../claim_creation.md)
- [Warranty SRT and Labor](../srt_and_labor.md)
- [Warranty Claim Documentation: 4 C and SRO](../claim_documentation_4c_and_sro.md)
- [Warranty Claim Follow-up](../warranty_claim_followup.md)

## Source Limitations

This document reflects the supplied internal presentations. It does not replace the current official CECO warranty administration or coverage documentation.

## Résumé en français

Pour une réclamation moteur CECO dans BMS, utiliser `FACT` pour un travail en atelier et `FACTFSE` pour un travail sur le terrain. Le fournisseur est `CECO`, le code de compte indiqué pour une réclamation de base est `67`, le Pay Code est `X` et la gravité est `B`. Le Routing Indicator n’est pas requis selon la présentation. Vérifier toujours les valeurs propres aux campagnes, politiques, émissions, pièces ou autres catégories.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the Engine Warranty Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQAAOrtHVj1SQILdihxqEyXoAVmMCBEz3RJb5bX0ZMicpaM?e=FZn4qs)

---

## Search Terms / Termes de recherche

**English:** engine warranty, generator engine warranty, CECO engine warranty, CECO warranty claim, engine warranty claim in BMS, FACT, FACTFSE, QuickServe, QSOL, Warranty Failure Code Manual, Warranty Start Date, Date in Service, Engine Serial Number, ESN, Account Code 67, Pay Code X, Severity B.

**Français:** garantie moteur, garantie du moteur de génératrice, garantie moteur CECO, réclamation de garantie CECO, réclamation garantie moteur BMS, FACT, FACTFSE, QuickServe, QSOL, Warranty Failure Code Manual, Warranty Start Date, Date in Service, numéro de série du moteur, ESN, code de compte 67, Pay Code X, Severity B.


