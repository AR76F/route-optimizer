---
title: Electric Bus Warranty Claims
title_fr: Réclamations de garantie des autobus électriques
category: warranty
subcategory: electric_bus_claim
vendor: CECO
system: BMS
language: bilingual
keywords:
  - electric bus warranty claim
  - EV bus claim
  - CECO
  - FACT
  - QuickServe
  - QSOL
  - Warranty Failure Code Manual
  - MR
---

# Last Updated: 2026-09-14

# Electric Bus Warranty Claims

## Purpose

This document records the electric-bus-specific decisions shown in the training presentation. Follow the shared BMS claim, Failure Code, SRT, documentation, and follow-up procedures for the complete workflow.

## Example Claim Path

For a suspected electric-bus warranty repair:

1. Obtain the unit mileage and confirm the unit is correctly entered in the Work Order.
2. Identify the electric-bus model and ESN.
3. Confirm the failed component and root cause from the technician's diagnosis.
4. Check coverage using the approved Cummins warranty resources.
5. Use QuickServe Online document `5579915`, **Warranty Failure Code Manual for All Electrifications**, to identify the exact Failure Code.
6. Enter the Failure Code in BMS.
7. Create and document the CECO claim using the shared procedures.

## BMS Values Identified in the Training

The electric-bus example identifies these values:

- **Vendor:** `CECO`
- **Product Group:** `MR`
- **Location:** `AA`
- **Claim Type:** `FACT` for factory in-shop work
- **Account Code:** `67` for a base claim
- **Pay Code:** `X`
- **Severity:** `B`

The presentation does not establish that every electric-bus claim has the same work location, Claim Type, account code, or severity. Confirm the correct values for each claim.

## Electric-Bus Failure Code Entry

1. Open the **Failure** tab in BMS.
2. Enter the Failure Code identified from the electrification manual.
3. Confirm **Vendor = CECO**.
4. Confirm **Product Group = MR** and **Location = AA** for the demonstrated workflow.
5. Press `F10`.
6. If BMS finds the warranty automatically, confirm the Claim Type and accept the result.
7. If BMS does not find the warranty automatically, select the appropriate Claim Type manually, using `FACT` for the demonstrated factory in-shop example.

## Documentation Requirements

Complete the four C's in English and ensure that the technician's report supports the Complaint, Cause, Coverage, and Correction. Document progressive damage when an initial electrical failure damages another covered component. The SRO must clearly explain any `99-999` time.

## Common Electric-Bus Claim Examples

The presentation discusses failures involving components such as:

- High-voltage sensors
- Pack management unit
- Power steering pump
- Charge control unit
- Electronic water pump
- Thermal management system heater

These examples do not establish coverage by themselves. Confirm the component, root cause, model, and warranty status before claiming the repair.

## Related Procedures

- [Electric Bus Warranty Overview](electric_bus_warranty_overview.md)
- [Warranty Failure Codes](../failure_codes.md)
- [Warranty Claim Creation](../claim_creation.md)
- [Warranty SRT and Labor](../srt_and_labor.md)
- [Warranty Claim Documentation: 4 C and SRO](../claim_documentation_4c_and_sro.md)
- [Warranty Claim Follow-up](../warranty_claim_followup.md)

## Source Limitations

This document reflects the supplied electric-bus training presentation. It does not replace current CECO warranty administration, coverage, or safety requirements for high-voltage systems.

## Résumé en français

Pour l’exemple d’autobus électrique présenté, utiliser CECO comme fournisseur, le groupe de produits `MR`, la location `AA`, le Claim Type `FACT`, le code de compte `67`, le Pay Code `X` et Severity `B`. Vérifier la pièce et le code dans le manuel QuickServe Online `5579915`. Ces valeurs doivent être confirmées pour chaque réclamation.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the Electric Bus Warranty Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQCjP3qz3E4yR7fgXVQTT12SAYsoa3P-FE2WkJVsHn0878o)

---

## Search Terms / Termes de recherche

**English:** electric bus warranty, EV bus warranty, electric bus warranty claim, CECO electric bus claim, Accelera warranty, BES, EV___B, high-voltage battery warranty, energy storage warranty, power distribution warranty, power electronics warranty, propulsion system warranty, thermal management warranty, QuickServe, QSOL, Warranty Failure Code Manual for All Electrifications, FACT, MR, Product Group, Location AA, Account Code 67, Pay Code X, Severity B, 4 C, SRO, 99-999.

**Français:** garantie autobus électrique, garantie autobus EV, réclamation de garantie autobus électrique, réclamation CECO autobus électrique, garantie Accelera, BES, EV___B, garantie batterie haute tension, garantie stockage d’énergie, garantie distribution électrique, garantie électronique de puissance, garantie système de propulsion, garantie gestion thermique, QuickServe, QSOL, Warranty Failure Code Manual for All Electrifications, FACT, MR, Product Group, Location AA, code de compte 67, Pay Code X, Severity B, les 4 C, SRO, 99-999.


