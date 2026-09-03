# BMS - Site Creation

# Last Updated: 2026-09-03

## Purpose

This procedure explains how to create a new customer Site in BMS when the required generator location does not already exist.

Use [BMS - Work Order Creation](bms_work_order_creation.md) for selecting an existing Site and completing the Work Order.

## Objectif

Cette procédure explique comment créer un nouveau site client dans BMS lorsque l’emplacement requis de la génératrice n’existe pas déjà.

Consultez [BMS - Work Order Creation](bms_work_order_creation.md) pour sélectionner un site existant et compléter le bon de travail.

## Quick Reference / Référence rapide

```text
Confirm no existing Site is available
        ↓
Open Site Info and create a new record
        ↓
Enter site, address, branch, and tax information
        ↓
Verify the customer and location
        ↓
Save and Send to FA
```

### French Retrieval Metadata

**Création site BMS / nouveau site / Site Info / adresse / ville / province / code postal / emplacement de service principal / district fiscal / Send to FA**

## SharePoint Visual Reference

The visual BMS Site Creation guide is maintained on SharePoint.

**SharePoint Link:** `[https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQACOQw4keJPTYBOVTlP-0SkAZAo7AOR5Tb9XsCla_KZufk?e=dmLd0C]`

The Markdown procedure is the detailed text reference; the visual guide is supplemental.

# 1. Confirm That a New Site Is Required

Search the Site lookup before creating a record. Create a new Site only when the generator location does not already exist for the customer.

Confirm the customer, street address, city, province, postal code, and branch before proceeding.

# 2. Open a New Site

1. Open **Site Info** from the applicable Work Order or Unit record.
2. Open the Site lookup using the **binoculars** button.
3. Select **Setup**.
4. Use **F6** to create a new Site.

## Site Information

Complete the applicable fields:

| Field | Information |
|---|---|
| Site Name | Customer site name |
| Site Address | Street address |
| City | City where the generator is located |
| Province | **QC** or **ON**, as applicable |
| Postal Code | Site postal code |
| Country | **CA** |
| Site Phone Number | Customer or site contact number |
| Primary Service Location | **Z8** for Candiac or **AK** for Ottawa |
| Tax District | Applicable provincial tax district |

## Primary Service Location

| Branch | Code |
|---|---|
| Candiac | **Z8** |
| Ottawa | **AK** |

## Tax District

Select the tax district that applies to the site and branch. Confirm the selection before saving.

# 3. Resolve Site Selection Errors

When selecting or saving a Site, BMS may display an error indicating that the city and postal-code combination is invalid or unavailable in the cross-reference database.

If this occurs:

1. Select the City from the available BMS values.
2. Select the applicable Postal Code from the available BMS values.
3. Confirm the corrected information.
4. Select **OK** again.

Do not substitute an approximate city or postal code. If the correct values are unavailable, escalate the issue before continuing.

# 4. Verify and Save the Site

Before saving, verify:

- Site name and address.
- City, province, postal code, and country.
- Site contact telephone number.
- Primary Service Location.
- Tax District.
- Customer association.

1. Save the Site using **F10** or the BMS save command.
2. Select **Send to FA** to synchronize the new Site with FieldAware.
3. Return to the Unit or Work Order and confirm that the Site is selected.

## Common Mistakes

- Creating a duplicate Site instead of searching first.
- Selecting the wrong customer site.
- Entering an invalid city/postal-code combination.
- Omitting the Primary Service Location or Tax District.
- Saving the Site without selecting **Send to FA**.

## Related Documents

- [BMS - Work Order Creation](bms_work_order_creation.md)
- [BMS - Unit Creation](bms_unit_creation.md)
- [FieldAware - Work Order Creation](fieldaware_work_order_creation.md)
- [BMS - Searching Records](bms_searching_records.md)
- [Service Department Resources](../reference/service_department_resources.md)

## Search Terms / Termes de recherche

**English:** BMS site creation, create Site, new customer site, Site Info, site address, city postal code error, primary service location, tax district, Candiac Z8, Ottawa AK, Send to FA.

**Français:** création site BMS, créer un site, nouveau site client, informations du site, adresse du site, erreur ville code postal, emplacement de service principal, district fiscal, Candiac Z8, Ottawa AK, Send to FA.
