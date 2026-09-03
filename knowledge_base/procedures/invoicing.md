# Procedure - Invoicing

# Last Updated: 2026-09-03

## Purpose

This procedure explains how to review and complete a service work order in FieldAware and BMS after the technician has finished the work, then close and deliver the invoice.

Use the linked procedures for detailed work-order creation, billing rates, overtime, customer-specific requirements, cash-customer payment, and invoice credits.

## Objectif

Cette procédure explique comment réviser et compléter un bon de travail de service dans FieldAware et BMS après la fin des travaux du technicien, puis fermer et transmettre la facture.

Consultez les procédures liées pour les détails sur la création des bons de travail, les taux de facturation, les heures supplémentaires, les exigences propres aux clients, les paiements des clients comptant et les crédits de facture.

---

## General Invoicing Visual Guide - SharePoint

For the **general Service invoicing procedure using BMS and FieldAware**, use the following SharePoint visual guide:

**Resource:** [General BMS / FieldAware Invoicing - Visual Guide](https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQCJiCrEfbZ6QY6d2gosj1POAXw8D-DQpcUdq95F_Scs6vI)

This visual guide supports the standard invoicing workflow described in this document, including reviewing the completed FieldAware job, verifying the required information in BMS, completing the work order, and preparing the invoice.

This resource is for **general Service invoicing**. It is separate from the **Clover Invoice to Pay** procedure used for applicable cash-customer payment workflows.

### Visual Guide Retrieval Terms

**English:** general invoicing visual guide, general invoicing link, invoicing SharePoint link, BMS invoicing visual guide, FieldAware invoicing visual guide, BMS FieldAware invoicing link, standard invoicing guide, service invoicing visual, general invoice procedure link

**Français:** guide visuel facturation générale, lien facturation générale, lien SharePoint facturation, guide facturation BMS, guide facturation FieldAware, procédure visuelle de facturation, lien procédure facturation, guide visuel facturation service

> **Note**
>
> The SharePoint guide is intended as a supplementary visual reference. This Markdown document remains the primary detailed procedure for general BMS/FieldAware invoicing.

---

## Quick Reference / Référence rapide

```text
Retrieve FA Job ID
        ↓
Review FieldAware reports
        ↓
Complete work-order information
        ↓
Verify unit hours, SRTs, Job Plan, and Misc Charges
        ↓
Confirm PO and customer-specific requirements
        ↓
Close the work order
        ↓
Save, send, and file the invoice
```

---

### French Retrieval Metadata

**Facturation service / Invoicing / Invoice / Facture / FieldAware / BMS / FA Job ID / Field Service Report / SRT / Job Plan / Misc Charges / fermeture de facture**

## Before Invoicing

Confirm that:

- The technician has completed the work and submitted the required report.
- The FA Job ID is available from the BMS Work Order.
- The customer and work order are correctly identified.
- Any required quotation has been prepared, approved, and processed.
- Customer-specific invoice requirements have been reviewed.

If the customer is Hydro-Québec, use [Hydro-Québec Invoicing Requirements](../customers/hydro_quebec_invoicing.md) before sending the invoice.

---

## RFQ Rule

If the technician submitted a **Request for Quotation (RFQ)** report, confirm that the quotation was prepared and sent to the customer for approval before invoicing.

Use [Preparing and Accepting a Quote](quote_management.md) for the quotation workflow.

# 1. Open the FieldAware Job

1. Locate the **FA Job ID** on the BMS Work Order.
2. Open [FieldAware](https://app.fieldaware.com/).
3. Search for the FA Job ID.
4. Open the applicable job.

Review the **Field Service Basic** report and any **Request for Quotation (RFQ)** report attached to the job.

# 2. Review and Clean the Field Service Report

Open the Field Service Report and review the technician’s entries before invoicing.

## Correction

Rewrite the technician’s comments in the third person so the invoice and work-order record read consistently.

Instead of:

> I performed a visual inspection.

Use:

> The technician performed a visual inspection.

Save the report after editing. In the FieldAware workflow, use **F10** to save when applicable.

> **Warning:** Apostrophes may change to question marks after saving. Reopen or reread the Correction section and correct any changed characters before continuing.

## Cause

Enter the cause identified in the technician’s report.

If the cause is missing or unclear, contact the technician before completing the invoice. Do not guess the cause.

## Coverage

Select the coverage that applies:

- **Chargeable to Customer**
- **Distributor Warranty**
- **Warranty**

Confirm the selected coverage against the work order, quotation, warranty information, and branch practice.

## Remarks

Enter a concise, professional comment that supports the invoice and explains any necessary customer-facing context.

A simple "**Merci d'avoir choisi Cummins**" works also.

## Unit Information

Update the generator’s operating hours using the reading provided in the technician’s report.

# 3. Verify Labor and SRTs

Open **Total WO** and compare the SRT values:

- **Actual**
- **Allocated**
- **Billable**

For a normal completed job, these values should agree where applicable.

> **Billing control:** Do not increase customer billing solely because actual hours exceed the hours quoted or allocated. Review the quotation and applicable approval before making any billing change.

If the values do not reconcile, open the **Job Plan** and correct or complete the SRT allocation before closing the invoice.

## Job Plan Check

Confirm that the Job Plan contains all required SRTs, including:

- The applicable base SRTs.
- `99-999` where required.
- `99-990` for travel/movement where required.

The total billable amount must be distributed across the applicable SRTs. Verify the result in **Total WO** after making changes.

For detailed SRT, labor, and Job Plan rules, use [BMS - Work Order Creation](../software/bms_work_order_creation.md) and [Service Billing Rates](../reference/service_hourly_rates.md).

# 4. Verify Miscellaneous Charges

In **Total WO**, open **Misc Charges** and confirm that applicable travel or mileage charges have been added.

Verify the quantity, rate, tax treatment, and customer applicability against [Service Billing Rates](../reference/service_hourly_rates.md) and the work-order details.

# 5. Final Invoice Review

Before closing, verify:

- Customer and billing information.
- Work description and technician report.
- Cause, Correction, Coverage, and Remarks.
- Generator operating hours.
- Actual, Allocated, and Billable SRT values.
- Job Plan and required SRTs.
- Travel or mileage Misc Charges.
- Purchase Order (PO), when required.
- Customer-specific invoice requirements.
- Any required quotation approval or RFQ processing.

# 6. Close the Work Order

When all information is complete and the billing values are reconciled:

1. Confirm that a PO has been entered when required.
2. Select the **Close** checkbox.
3. Enter the required security code.
4. Save the invoice/work order.

Do not close the work order while required reports, cause information, coverage, SRTs, charges, approval, or customer information are incomplete.

# 7. Deliver the Invoice

Follow the applicable delivery method.

## HighRadius-Generated Invoice

If HighRadius generates and delivers the invoice, no additional manual email is required unless branch or customer requirements specify otherwise.

## Manual Email Delivery

If the invoice must be sent manually:

1. Open the customer lookup/contact setup in BMS.
2. Select the customer and choose **Setup**.
3. Confirm that the customer’s email address is present and correct.
4. If it is missing, obtain the address from the customer and add it to the contact record.
5. Save the contact record with **F10**, when applicable.
6. Use **Send to FA** when required to synchronize the updated contact information.
7. Save and send the invoice by email.

### Email Format

Subject:

```text
[Invoice Number]
```

Include:

- A brief description or summary of the work.
- The invoice or required attachment.
- A professional thank-you to the customer.

Example structure:

```text
Subject: Invoice 123456

Hello [Customer],

Please find attached the invoice for [brief description of work].

Thank you for choosing Cummins.
```

Confirm that the invoice was sent to the correct customer email address.

# 8. Filing and Follow-Up

After delivery:

- Confirm that the invoice is closed in BMS.
- Confirm that the work order and FieldAware records are synchronized where required.
- File or retain supporting reports and approval documentation according to branch practice.
- If payment remains outstanding, follow the applicable customer or cash-customer process.

For cash customers, use [Cash Customers - Service Call](cash_customers_service_call.md) or [Cash Customers - Accepted Quotation](cash_customers_accepted_quote.md).

For a credit against an already invoiced work order, use [Customer Invoice Credit](customer_invoice_credit.md).

## Common Mistakes

- Invoicing before an RFQ quotation has been approved.
- Leaving technician comments in the first person.
- Failing to reread the Correction section after saving because apostrophes changed.
- Leaving Cause or Coverage incomplete.
- Forgetting to update unit hours.
- Closing with mismatched SRT values.
- Omitting `99-999`, `99-990`, or applicable travel charges.
- Closing without a required PO or security code.
- Sending the invoice to a missing or outdated email address.
- Increasing billing only because actual hours exceeded the quoted amount.

## Related Documents

- [Preparing and Accepting a Quote](quote_management.md)
- [BMS - Work Order Creation](../software/bms_work_order_creation.md)
- [FieldAware - Work Order Creation](../software/fieldaware_work_order_creation.md)
- [Service Billing Rates](../reference/service_hourly_rates.md)
- [BMS Overtime Entry](../software/bms_overtime_entry.md)
- [Hydro-Québec Invoicing Requirements](../customers/hydro_quebec_invoicing.md)
- [Customer Invoice Credit](customer_invoice_credit.md)
- [Cash Customers - Service Call](cash_customers_service_call.md)
- [Cash Customers - Accepted Quotation](cash_customers_accepted_quote.md)

## Search Terms / Termes de recherche

**English:** service invoicing, invoice work order, FieldAware invoice, FA Job ID, Field Service Basic, Request for Quotation, RFQ invoice, Correction section, Cause, Coverage, Remarks, unit hours, SRT, Actual Allocated Billable, Job Plan, Misc Charges, mileage charges, close invoice, PO number, security code, HighRadius invoice, send invoice to customer.

**Français:** facturation service, facturer un bon de travail, facture FieldAware, numéro FA Job ID, rapport Field Service, demande de soumission RFQ, section Correction, cause, couverture, remarque, heures de la génératrice, SRT, heures réelles allouées facturables, plan de travail, frais divers, frais de déplacement, fermer la facture, numéro de PO, code de sécurité, facture HighRadius, envoyer la facture au client.
