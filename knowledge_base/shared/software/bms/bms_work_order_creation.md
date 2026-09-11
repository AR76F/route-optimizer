# BMS - Work Order Creation

# Last Updated: 2026-09-03

## Purpose

This procedure explains how to create and prepare a service Work Order Quote (WOQT) and Work Order in BMS before synchronizing it to FieldAware.

Use the linked procedures for creating new units or sites and for completing technician assignment, scheduling, and report assignment in FieldAware.

## Objectif

Cette procédure explique comment créer et préparer une soumission de bon de travail (WOQT) et un bon de travail (WO) de service dans BMS avant de les synchroniser avec FieldAware.

Consultez les procédures liées pour créer une nouvelle unité ou un nouveau site et pour effectuer l’assignation du technicien, la planification et l’assignation des rapports dans FieldAware.

## Quick Reference / Référence rapide

```text
Create WOQT in BMS
        ↓
Complete customer and work-order information
        ↓
Select existing Unit and Site, or create them if required
        ↓
Complete Job Plan and Misc Charges
        ↓
Convert WOQT to WO after approval
        ↓
Verify customer credit, parts, technician, and appointment
        ↓
Send to FA
        ↓
Complete FieldAware scheduling and reports
```

### French Retrieval Metadata

**Création bon de travail BMS / WOQT / WO / bon de travail / Work Order / soumission / plan de travail / SRT / frais divers / FieldAware / Send to FA**

## Systems Used

- **BMS** - Customer, unit, site, Work Order, WOQT, Job Plan, billing, and invoicing records.
- **FieldAware** - Technician assignment, scheduling, reports, and Scheduler verification.
- **Google Maps** - Mileage calculation for travel charges.

## SharePoint Visual Reference

The visual BMS Work Order creation guide is maintained on SharePoint.

**SharePoint Link:** `[https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQACOQw4keJPTYBOVTlP-0SkAZAo7AOR5Tb9XsCla_KZufk?e=dmLd0C]`

The Markdown procedure is the detailed text reference; the visual guide is supplemental.

# Part 1 - Create the WOQT

Always create the quotation as a **WOQT** before converting it to a live Work Order. This ensures that pricing can be approved and helps avoid unnecessary diagnostic charges.

## Open a New Work Order

Open a new **Work Order** window in BMS and complete the following fields before saving.

### Service Location

| Branch | Code |
|---|---|
| Candiac | **Z8** |
| Ottawa | **AK** |

### Customer

Enter the customer’s **Customer Number**. If the customer does not exist, create the customer account before continuing.

### Work Order Type

For a standard mobile service call, select:

```text
Mobile
```

### Transaction Type

Enter:

```text
WOQT
```

### Subtype

Select the subtype that best represents the work, such as:

- FSPG
- FSONPG
- PMR ASAP
- PMR EMERGENT

### Contact

Enter the person who communicated the service request. Confirm the on-site contact name and phone number are also documented in the Complaint or applicable work-order fields.

### Purchase Order (PO)

Enter the customer’s PO when available or required. The PO is the only value that can still be modified after invoicing.

### Payment Type

Select the applicable payment type, such as:

- **CHARGE** - Customer has an approved credit account.
- **COD / CASH** - Payment is required according to the cash-customer procedure.

For cash customers, follow [Cash Customers - Service Call](../procedures/cash_customers_service_call.md) or [Cash Customers - Accepted Quotation](../procedures/cash_customers_accepted_quote.md).

## Complete the Work-Order Sections

### Complaint

Summarize the customer’s issue and include:

- Problem description and customer observations.
- Alarm or fault codes.
- On-site contact name and phone number.
- Relevant access, safety, or site information.

Example:

```text
Generator displays FC1223 Low Coolant alarm.
Customer reports unit shuts down approximately 20 minutes after starting.
On-Site Contact: John Smith, 514-555-1234
```

### Cause

Before inspection, enter:

```text
To be determined.
```

The technician or coordinator completes the Cause after troubleshooting.

### Coverage

For standard customer-billable work, select:

```text
Customer Billable
```

Select warranty or another coverage only when supported by the applicable documentation.

### Correction

Before work is completed, enter:

```text
To be filled once the work has been performed by the technician.
```

### Remarks

Use the standard customer message when applicable:

```text
Thank you for choosing Cummins.
Quote may vary once work has been completed.
```

### Supervisor

Enter the responsible coordinator or supervisor according to branch practice.

## Save the WOQT

After the required fields are complete:

1. Press **F10** or use the BMS save command.
2. Confirm that BMS generates the WOQT number.
3. Use the WOQT number on related documents and Parts Department requests.

Do not switch an existing WO back to WOQT. This may merge or duplicate SRT hours.

# Part 2 - Associate the Unit and Site

Select the **Unit / Products** tab and associate the correct existing generator unit.

1. Open the Unit lookup.
2. Verify the serial number, model, and existing unit details.
3. Select the correct unit.
4. Open **Site Info** and verify the associated customer site.

If the unit does not exist, use [BMS - Unit Creation](bms_unit_creation.md).

If the site does not exist, use [BMS - Site Creation](bms_site_creation.md).

## Market Segment

| Market Segment | Use when |
|---|---|
| **SOLUTIONS** | Customer has a Preventive Maintenance contract. |
| **STANDBY** | Customer does not have a service contract. |

## Product Information

Confirm that the selected unit supplies the correct:

- Serial Number.
- Model Designation.
- Product and family information.

## Primary Failure Measurement

Set:

```text
Primary Failure Measure = HOURS
```

The Primary Failure Point represents the generator’s operating hours. Use the latest available reading; enter `1` only when no previous service history exists and the process requires an initial value.

# Part 3 - Build the Job Plan

Select the **Job Plan** tab. The Job Plan determines the labor allocation quoted and later billed.

## Required SRTs

Every standard mobile service call begins with:

- **99-999 - NON-SRT DETAIL**
- **99-990 - TRAVEL**

To retrieve an SRT:

| Field | Value |
|---|---|
| Load SRTs For Group | **99** |
| Procedure | **999** or **990** |
| Of Qty | **1** |

Select **Retrieve** for each required SRT.

## Four-Hour Rule

A standard mobile service call is quoted as a minimum of **4.0 labor hours**. Adjust the SRT quantities so the total allocation meets the applicable minimum and reflects the expected travel and work.

Review the Job Plan before converting the WOQT:

- Required SRTs are present.
- Labor allocation is correct.
- No duplicate SRTs exist.
- The total is consistent with the quotation and approval.

Save the Job Plan.

# Part 4 - Add Miscellaneous Charges

Open **Total WO**, then select **Misc Charges**.

## Mileage

Select `KILOMETRES` in the **Name** field and enter the round-trip distance calculated with Google Maps.

Use the applicable starting point:

- North Shore: assigned storage unit to customer site.
- Montreal region: Candiac Branch to customer site.
- National Capital Region: Ottawa Branch to customer site.

The standard mileage rate is currently **$3.25/km**. Verify current rates in [Service Billing Rates](../reference/service_hourly_rates.md).

Enter the appropriate tax district and save the Misc Charges record.

Confirm:

- Mileage quantity is correct.
- Round-trip distance was used.
- Rate and tax district are correct.
- Other applicable charges, such as load-bank fees, are included.

# Part 5 - Convert the WOQT to a WO

After the quotation is complete and approval requirements are satisfied:

1. Select **Quote => WO** beside Transaction Type.
2. At **Accept / Reject Quote**, select **Accept**.
3. If BMS displays a tax-district warning, select **Yes** only after confirming the correct tax district and billing arrangement.

Creating the WOQT first:

- Allows customer approval of pricing.
- Ensures labor and travel are quoted correctly.
- Prevents unnecessary diagnostic charges.

# Part 6 - Pre-Scheduling Verification

Before finalizing the technician assignment and appointment:

- Confirm the Complaint contains enough information about the work or generator issue.
- Confirm the Work Order contact is the person who communicated the request.
- Confirm the on-site contact name and phone number are included.
- Verify that customer credit is sufficient for the job.
- If credit is insufficient, obtain the required approval before proceeding.
- Verify that required parts are available or confirm an approved alternative.
- Select an appropriate tentative time slot in FieldAware.
- Contact the selected technician when required to review the issue and confirm suitability.
- Confirm the proposed appointment with the customer.

For quotation preparation and approval, use [Preparing and Accepting a Quote](../procedures/quote_management.md).

# Part 7 - Update Status and Synchronize

In the **STATUS** section, record the assigned technician and scheduled service date. Add a status entry whenever a significant intervention or follow-up occurs.

After saving the BMS Work Order, select:

```text
Send to FA
```

Select **Send to FA** again after every BMS modification. Otherwise, later FieldAware updates may overwrite the change.

Continue with [FieldAware - Work Order Creation](fieldaware_work_order_creation.md) for the FA Job ID, technician, scheduling, reports, and Scheduler verification.

# Safety Concerns

Document known safety concerns before dispatching, such as:

- Roof access or fall hazards.
- Confined space or high voltage.
- Restricted access or security escort.
- LOTO requirements.
- Environmental hazards.

Use the Unit record’s **Misc. Info > Safety Concerns** area when applicable. Enter the concern and a clear description, then save the record.

# Best Practices

- Always create a WOQT before converting to a WO.
- Verify customer, Unit, Site, and contact information before saving.
- Confirm SRT allocation and mileage before conversion.
- Verify customer approval, credit, parts, and technician suitability before scheduling.
- Select **Send to FA** after every BMS change.
- Do not consider dispatch complete until the job appears under the correct technician and date in the FieldAware Scheduler.

# Common Mistakes

- Creating a WO instead of a WOQT at the start.
- Selecting the wrong Unit or Site.
- Omitting the on-site contact from the Complaint.
- Scheduling before parts or customer credit are confirmed.
- Forgetting the 4-hour minimum or required SRTs.
- Calculating mileage as one-way instead of round-trip.
- Forgetting to synchronize BMS changes with **Send to FA**.
- Assigning or scheduling the job without completing the Field Service Basic and RFQ report framework in FieldAware.

# Related Documents

- [BMS - Unit Creation](bms_unit_creation.md)
- [BMS - Site Creation](bms_site_creation.md)
- [FieldAware - Work Order Creation](fieldaware_work_order_creation.md)
- [Preparing and Accepting a Quote](../procedures/quote_management.md)
- [Service Call Management](../procedures/service_call_management.md)
- [Service Billing Rates](../reference/service_hourly_rates.md)
- [BMS Overtime Entry](bms_overtime_entry.md)
- [BMS - Searching Records](bms_searching_records.md)
- [Cash Customers - Service Call](../procedures/cash_customers_service_call.md)

## Search Terms / Termes de recherche

**English:** BMS work order creation, WOQT, WO, Work Order, create quotation, convert quote to work order, Complaint, Cause, Coverage, Correction, Remarks, Unit, Site, Job Plan, SRT, 99-999, 99-990, Misc Charges, mileage, Send to FA, customer credit, parts availability.

**Français:** création bon de travail BMS, WOQT, WO, bon de travail, créer une soumission, convertir une soumission, plainte, cause, couverture, correction, remarque, unité, site, plan de travail, SRT, frais divers, kilométrage, Send to FA, crédit client, disponibilité des pièces.
