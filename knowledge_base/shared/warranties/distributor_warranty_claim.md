---
title: Distributor Warranty Claim
title_fr: Réclamation de garantie du distributeur
category: warranty
subcategory: distributor_claim
system: BMS
language: bilingual
keywords:
  - distributor warranty
  - dealer warranty
  - warranty claim
  - réclamation de garantie
  - garantie du distributeur
  - Onan
  - DWFSPG
  - DWFE
  - Default Warranty
  - Dist Warranty Investigation
  - Total WO
---

# Last Updated: 2026-09-11

# Distributor Warranty Claim

## Purpose

This procedure provides a concise guide for creating an Onan distributor warranty claim in BMS and verifying the warranty amounts on the Work Order.

## Objectif

Cette procédure fournit un guide sommaire pour créer une réclamation de garantie du distributeur Onan dans BMS et vérifier les montants sous garantie dans le bon de travail.

---

## Before Starting

Confirm that the required warranty information is available, including:

- Customer and Work Order information
- Unit or generator information
- Technician diagnosis and repair details
- Warranty coverage information
- Warranty percentage for parts and labor

---

## Create the Distributor Warranty Claim

In BMS:

1. Open the applicable Work Order.
2. Open the **Warranty** tab.
3. Select the applicable **Claim Type**:
   - `DWFSPG` for field service work.
   - `DWFE` for in-shop work.
4. Select `Onan` as the **Vendor**.
5. Press `F10` to continue.
6. Click **OK** when prompted.
7. When **Dist Warranty Investigation** appears, close the window without saving.

---

## Enter the Warranty Coverage

Open:

```text
Default Warranty → Selection Default Warranty
```

Enter the applicable percentage covered by warranty for:

- Parts
- Labor

Use the warranty coverage information for the specific claim. Do not assume that the entire Work Order is covered.

---

## Verify the Work Order Amounts

At the bottom of the Work Order, open **Total WO**.

Verify that the warranty-covered parts and labor amounts appear in the correct warranty columns. Correct any allocation issue before finalizing the Work Order or claim.

---

## Important Notes

- Use `DWFSPG` for field service and `DWFE` for in-shop work.
- Select `Onan` as the vendor for the distributor warranty claim.
- Close **Dist Warranty Investigation** without saving when the procedure requires it.
- Verify the warranty allocation in **Total WO** before completing the claim.
- If the coverage, claim type, or warranty allocation is unclear, confirm it with an experienced warranty resource before proceeding.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the Distributor Warranty Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQCpq7KcIB-oToTMPLpckNZNAReu8oDT1Yd7hNoBFdZN1m4?e=9zIKqe)

---

## Search Terms / Termes de recherche

**English:** distributor warranty, dealer warranty, Onan warranty claim, warranty claim in BMS, DWFSPG, DWFE, Default Warranty, Dist Warranty Investigation, Total WO, warranty parts percentage, warranty labor percentage.

**Français:** garantie du distributeur, réclamation de garantie, garantie Onan, réclamation garantie BMS, DWFSPG, DWFE, Default Warranty, Dist Warranty Investigation, Total WO, pourcentage pièces garantie, pourcentage main-d'œuvre garantie.
