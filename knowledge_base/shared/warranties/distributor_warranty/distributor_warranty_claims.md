---
title: Distributor Warranty Claims
title_fr: Réclamations de garantie du distributeur
category: warranty
subcategory: distributor_claim
system: BMS
language: bilingual
keywords:
  - distributor warranty claim
  - dealer warranty claim
  - réclamation de garantie du distributeur
  - DWFSPG
  - DWFE
  - Default Warranty
  - Dist Warranty Investigation
  - Total WO
---

# Last Updated: 2026-09-14

# Distributor Warranty Claims

## Purpose

This procedure documents the Onan distributor-warranty claim workflow shown in the distributor presentation. Use it after confirming that the repair belongs on the distributor warranty path.

## Create the Claim in BMS

1. Open the applicable Work Order.
2. Open the **Warranty** tab.
3. Select the distributor Claim Type:
   - `DWFSPG` for field-service work.
   - `DWFE` for in-shop work.
4. Select `Onan` as the vendor.
5. Press `F10`.
6. Click **OK** when prompted.
7. When **Dist Warranty Investigation** appears, close the page without saving, as shown in the presentation.

## Apply the Coverage

Open:

```text
Default Warranty → Selection Default Warranty
```

Enter the applicable warranty percentage for:

- Parts
- Labor

Use the confirmed distributor warranty coverage. Do not automatically apply 100% unless the applicable warranty terms authorize it.

## Verify Total Work Order

1. Go to **Total WO** at the bottom of the Work Order.
2. Verify that the parts and labor amounts covered by warranty appear in the correct warranty columns.
3. Correct any allocation issue before finalizing the Work Order or claim.

## Final Checks

Confirm that:

- The Claim Type matches the work location.
- `Onan` is the correct vendor for the claim.
- The parts and labor percentages are correct.
- Warranty-covered amounts appear correctly in **Total WO**.
- The technician's diagnosis and repair documentation support the claim.
- Any additional claims on the same Work Order have been allocated correctly.

If the Claim Type, coverage percentage, vendor, or allocation is unclear, stop and confirm the applicable distributor warranty rule before proceeding.

## Source Limitations

This procedure reflects the supplied distributor presentation. It does not establish coverage eligibility, exclusions, approval authority, reimbursement rates, or a complete distributor policy. Confirm those items in the current official source.

## Résumé en français

Dans BMS, ouvrir l’onglet **Warranty**, sélectionner `DWFSPG` pour un travail sur le terrain ou `DWFE` pour un travail en atelier, puis choisir `Onan` comme fournisseur. Fermer **Dist Warranty Investigation** sans sauvegarder. Dans **Default Warranty**, entrer les pourcentages applicables aux pièces et à la main-d’œuvre, puis vérifier les montants dans **Total WO** avant de finaliser le bon de travail.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the Distributor Warranty Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQCpq7KcIB-oToTMPLpckNZNAReu8oDT1Yd7hNoBFdZN1m4?e=9zIKqe)

---

## Search Terms / Termes de recherche

**English:** distributor warranty, dealer warranty, Onan warranty claim, warranty claim in BMS, DWFSPG, DWFE, Default Warranty, Dist Warranty Investigation, Total WO, warranty parts percentage, warranty labor percentage.

**Français:** garantie du distributeur, réclamation de garantie, garantie Onan, réclamation garantie BMS, DWFSPG, DWFE, Default Warranty, Dist Warranty Investigation, Total WO, pourcentage pièces garantie, pourcentage main-d'œuvre garantie.