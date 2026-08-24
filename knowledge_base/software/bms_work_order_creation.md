# - Work Order Creation (BMS & FieldAware)

# Version 1.0.0

# Last Updated: 2026-07-20

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Creation of initial document.

## Purpose

This document describes the complete process for creating a Mobile Service Work Order (WO) using BMS and FieldAware.

It guides Service  through the entire workflow, beginning with creating a Work Order Quote (WOQT) in BMS and ending with dispatching the work order to FieldAware for technician scheduling.

The objective is to ensure work orders are created consistently, contain all required customer and equipment information, are billed correctly, and are properly dispatched to the assigned technician.

---

# Systems Used

This procedure involves the following systems:

- **BMS** – Work Order creation, customer information, units, job planning, billing and invoicing.
- **FieldAware** – Technician assignment and scheduling.
- **Google Maps** – Mileage calculation for travel charges.

---

# Workflow Overview

```text
Customer Request
        ↓
Create WOQT
        ↓
Complete Work Order Information
        ↓
Select Unit & Site
        ↓
Configure Job Plan (SRTs)
        ↓
Add Miscellaneous Charges
        ↓
Convert WOQT → WO
        ↓
Assign Technician
        ↓
Send to FieldAware
        ↓
Schedule Appointment
```

---

# Part 1 – Creating the Work Order Quote (WOQT)

The first step is to create a **Work Order Quote (WOQT)** in BMS.

Creating the WOQT before converting it into a Work Order ensures the customer is quoted correctly and avoids unnecessary diagnostic charges.

---

## Opening a New Work Order

Open a new **Work Order** window in BMS.

Complete the following fields before saving the record.

---

### Service Location

Select the appropriate service location.

| Branch | Code |
|---------|------|
| Candiac | **Z8** |
| Ottawa | **AK** |

---

### Customer

Enter the customer's **Customer Number**.

If the customer does not yet exist, a customer account must be created before continuing.

---

### Work Order Type

Select:

```text
Mobile
```

This option is used for standard mobile service calls.

---

### Transaction Type

Enter:

```text
WOQT
```

This creates a Work Order Quote.

---

### Subtype

Select the subtype that best represents the service being performed.

Examples include:

- FSPG
- FSONPG
- PMR ASAP
- PMR EMERGENT

Ensure the selected subtype matches the customer's request.

---

### Purchase Order (PO)

If the customer has provided a Purchase Order number, enter it in the **PO** field.

> **Important**
>
> The Purchase Order is the only value that can still be modified after the work order has been invoiced.

---

### Payment Type

Select the appropriate payment method.

Common values include:

- CHARGE
- COD / CASH

Refer to the Cash Customer procedure when processing COD/CASH work orders.

---

# Complaint Section

The **Complaint** section should clearly summarize the customer's issue.

Include:

- Description of the problem
- Alarm or fault codes
- Customer observations
- Contact person's name
- Contact person's phone number

Example:

```text
Generator displays FC1223 Low Coolant alarm.

Customer reports unit shuts down approximately
20 minutes after starting.

On-Site Contact

John Smith
514-555-1234
```

A well-written complaint helps technicians understand the issue before arriving on site.

---

# Cause Section

Before the technician has inspected the equipment, enter:

```text
To be determined.
```

The Cause section will be completed after troubleshooting has been performed.

---

# Coverage Section

For standard customer-billable work, select:

```text
Customer Billable
```

Only select another coverage type if warranty or another billing arrangement applies.

---

# Correction Section

Before dispatching the technician, enter:

```text
To be filled once the work has been performed by the technician.
```

This section documents the repair work completed and is finalized during invoicing.

---

# Remarks Section

Enter the standard customer message:

```text
Thank you for choosing Cummins.

Quote may vary once work has been completed.
```

Additional customer-specific notes may also be added when appropriate.

---

# Saving the WOQT

Once all required fields have been completed:

1. Save the Work Order.
2. BMS will generate the **WOQT Number**.

The generated WOQT will be used throughout the remainder of the process.

> **Best Practice**
>
> Review all customer information before saving. Correcting customer, billing, or complaint information is much easier before additional work is completed.
> Never flip from WO to WOQT if you have already created a WO, it may double the SRT hours as they merge.

---

# Part 2 – Unit & Product Information

Once the WOQT has been created, the next step is to associate the correct generator unit with the work order.

Select the **Unit / Products** tab.

---

## Selecting the Unit

Choose the unit associated with the customer's service request.

1. Select the Unit lookup button.
2. Choose the correct generator from the list.

If no matching unit exists, a new Unit must be created.

(The procedure for creating a new Unit is covered in **Appendix A**.)

---

## Viewing Unit Details

Select **Unit** to review information related to the generator.

Verify:

- Generator information
- Existing comments
- Existing safety concerns

Review any documented safety concerns before dispatching the technician.

---

## Site Information

Select **Site Info**.

Verify that the generator is associated with the correct customer site.

The site is normally selected automatically if the unit has already been created.

If no site exists, a new Site must be created.

(The procedure for creating a Site is covered in **Appendix B**.)

---

## Market Segment

Select the appropriate Market Segment.

| Market Segment | When to Use |
|----------------|-------------|
| **SOLUTIONS** | Customer has a Preventive Maintenance (PM) contract. |
| **STANDBY** | Customer does not have a service contract. |

Selecting the correct Market Segment ensures proper reporting and service classification.

---

## Product Information

After selecting the unit, verify that the following information appears automatically under **Products**:

- Serial Number
- Model Designation

If this information is incorrect, review the selected Unit before continuing.

---

## Primary Failure Measurement

Set:

```text
Primary Failure Measure = HOURS
```

---

## Primary Failure Point

The Primary Failure Point represents the generator's operating hours.

If this is the first recorded service for the unit and no previous history exists:

```text
Enter:

1
```

Otherwise:

- Review the previous work order for the unit.
- Retrieve the latest recorded operating hours.
- Enter the updated hour reading.

> **Note**
>
> Operating hours may be updated before invoicing if a more accurate reading becomes available.

---

At this stage:

- The Work Order Quote has been created.
- Customer information has been entered.
- The correct generator unit has been associated with the work order.
- The correct site has been verified.
- Product information has been confirmed.

The next step is to build the **Job Plan** by adding the required Standard Repair Times (SRTs).

# Part 3 – Building the Job Plan

Once the Unit and Site have been verified, the next step is to build the **Job Plan**.

The Job Plan determines the labor allocation that will be quoted to the customer and later billed on the work order.

Select the **Job Plan** tab.

---

## Standard Repair Times (SRTs)

The Job Plan is built using **Standard Repair Times (SRTs)**.

Every standard mobile service call begins with two mandatory SRTs:

- **99-999 – NON-SRT DETAIL**
- **99-990 – TRAVEL**

These two SRTs form the basis of the initial quotation.

---

## Adding SRT 99-999 (NON-SRT DETAIL)

In the Job Plan window:

| Field | Value |
|--------|-------|
| Load SRTs For Group | **99** |
| Procedure | **999** |
| Of Qty | **1** |

Select:

```text
Retrieve
```

The SRT will automatically populate the Job Plan.

---

## Adding SRT 99-990 (TRAVEL)

Repeat the same process.

| Field | Value |
|--------|-------|
| Load SRTs For Group | **99** |
| Procedure | **990** |
| Of Qty | **1** |

Select:

```text
Retrieve
```

The Travel SRT will now appear in the Job Plan.

---

## Four-Hour Rule

A standard mobile service call is quoted as a minimum of **4 labor hours**.

After retrieving the SRTs:

Adjust the labor allocation so that the total SRT hours equal:

```text
4.0 Hours
```

Typically this is accomplished by adjusting the quantities associated with:

- 99-999
- 99-990

The exact allocation may vary depending on the expected travel time.

---

## Reviewing the Job Plan

Before continuing, verify:

- Required SRTs have been added.
- Labor allocation totals **4 hours**.
- No duplicate SRTs exist.
- Quantities have been adjusted correctly.

Once complete:

Save the Job Plan.

> **Best Practice**
>
> Verify the labor allocation before converting the quotation into a Work Order. Correcting SRTs is significantly easier before technician time has been entered.

---

# Part 4 – Miscellaneous Charges

After completing the Job Plan, travel charges must be added to the work order.

Select:

```text
Total WO
```

The **Total Work Order** window will open.

---

## Miscellaneous Charges

Open the:

```text
Misc Charges
```

tab.

---

## Mileage

Select the arrow beside the **Name** field.

Choose:

```text
KILOMETRES
```

---

## Quantity

Enter the total number of kilometers that will be billed.

Mileage is calculated using **Google Maps**.

---

## Mileage Calculation Rules

### North Shore

Calculate the round-trip distance between:

- Assigned storage unit
- Customer site

---

### Montreal Region

Calculate the round-trip distance between:

- Candiac Branch
- Customer site

---

### National Capital Region

Calculate the round-trip distance between:

- Ottawa Branch
- Customer site

---

## Amount

Enter:

```text
3.25
```

This represents the standard mileage rate.

> **Note**
>
> Verify the current mileage rate against the official Service Hourly Rates document if rates have changed.

---

## Tax District

Enter the appropriate provincial tax code.

Examples:

| Province | Tax District |
|-----------|--------------|
| Quebec | QC |
| Ontario | ON |

---

## Saving Miscellaneous Charges

Once all required information has been entered:

Save the record.

Review the Misc Charges before continuing to ensure:

- Mileage quantity is correct.
- Correct tax district has been selected.
- Mileage amount has been entered.

---

# Part 5 – Converting the Quote into a Work Order

Once the quotation has been completed, it must be converted into a live Work Order.

Select:

```text
Quote => WO
```

located beside the **Transaction Type** field.

---

## Accept Quote

When prompted with:

```text
Accept / Reject Quote
```

Select:

```text
Accept
```

---

## Tax District Warning

You may receive the following message:

```text
Tax District Not Selected for Mobile Work Order.

Do you want to proceed?
```

Select:

```text
Yes
```

to continue.

---

## Why Create a WOQT First?

The quotation should always be created before converting it into a Work Order.

This process:

- Allows the customer to approve pricing.
- Ensures labor is quoted correctly.
- Prevents unnecessary diagnostic charges from being billed.

---

# Part 6 – Updating the Work Order Status

After selecting the technician and reserving a time slot, update the Work Order Status.

In the **STATUS** section, record:

- Assigned technician
- Scheduled service date

Example:

```text
Assigned Technician:

François Racine

Scheduled:

2026-07-22
```

Keeping the Status section up to date allows  and technicians to quickly identify the current assignment.

---

# Part 7 – Sending the Work Order to FieldAware

After saving the Work Order:

Select:

```text
Send to FA
```

located in the lower-left portion of the Work Order window.

This action synchronizes the Work Order with FieldAware.

> **Important**
>
> Every time changes are made to the Work Order in BMS, select **Send to FA** again.
>
> Failure to synchronize the Work Order may result in changes being overwritten when technicians enter labor or update the work order in FieldAware.

At this stage, the Work Order has been successfully created in BMS and synchronized with FieldAware.

The next step is to complete the technician assignment and scheduling directly in FieldAware.

# Part 8 – Completing the Work Order in FieldAware

Once the Work Order has been successfully synchronized from BMS, the remaining scheduling activities are completed in **FieldAware**.

FieldAware is used to assign technicians, schedule appointments, assign reports, and publish the work order to the technician's Scheduler.

---

## Opening the Work Order

Open any existing job in FieldAware.

This provides access to the search window.

Using the **FA Job ID** generated by BMS:

1. Locate the **FA Job ID** on the Work Order in BMS.
2. Enter the Job Number into the FieldAware search bar.
3. Open the corresponding job.

---

## Verify the Job Description

Once the work order has been opened:

Verify that the **Job Description** accurately reflects the Complaint section entered in BMS.

Examples:

```text
FC1223 Low Coolant Alarm

Generator shuts down approximately
20 minutes after starting.
```

If the description is incorrect:

- Update the Complaint section in BMS.
- Select **Send to FA** again.
- Refresh the job in FieldAware.

---

## Assigning the Technician

Navigate to the:

```text
Crew
```

section.

Add the selected technician.

Once added:

Assign that technician as the:

```text
Job Lead
```

> **Important**
>
> A technician **must** be assigned as the **Job Lead**.
>
> Without a Job Lead, the work order will not appear under that technician's schedule.

---

## Scheduling the Appointment

Navigate to the:

```text
Time Slot
```

section.

Enter:

- Appointment Date
- Appointment Start Time
- Appointment End Time

Verify that the scheduled appointment matches the agreed customer appointment.

---

## Assigning Reports

Assign the reports required for the work order.

### Standard Reports

Assign:

- Field Service Basic
- RFQ (Request for Quotation)

---

### Additional Reports

Assign additional reports when required.

Examples include:

- Fire Pump Inspection
- Monthly Inspection
- Quinquennial Inspection
- Customer-specific inspection forms
- Other branch-specific reports

Only assign reports required for the work being performed.

---

## Saving the Work Order

Once all scheduling information has been entered:

Select:

```text
Save
```

The work order should now appear on the Scheduler.

---

## Scheduler Verification

Open the Scheduler.

Verify:

- Correct technician
- Correct date
- Correct start time
- Correct duration

Confirm the work order appears under the assigned technician.

---

## Save Failures

Occasionally, FieldAware may fail to save the record.

If this occurs:

1. Refresh FieldAware.
2. Re-open the work order.
3. Save again.

Repeat until the save is successful.

Never assume the work order has been scheduled until it appears correctly on the Scheduler.

---

# Appendix A – Creating a New Unit

A new Unit should only be created when no existing generator can be associated with the customer's work order.

Open:

```text
Units
```

Ensure all editable fields appear in **yellow** before entering information.

---

## Customer Information

Enter:

- Customer Number

---

## Unit Information

Complete the following fields:

| Field | Information |
|--------|-------------|
| Unit | Usually the generator Serial Number |
| VIN / GSN | Generator Serial Number |
| Manufacturer | Usually **Onan** |
| Model # | Generator Model (or **GENSET** if unavailable) |
| Unit Type | **ST** |
| Labor Multiplier | Automatically assigned |
| Sales Segment | STANDBY or SOLUTIONS |
| WO Site Info | Existing customer site |

---

## Product Information

Under Products:

Enter:

- Serial Number
- Model Number

Use the **Serial Number Lookup Tool** on the **PGBU Warranty System** to identify the correct generator model.

Verify:

| Field | Value |
|--------|------|
| Family | 99 |
| Application Code | 0810 |

Application Code is entered under:

```text
Engine Detail
```

---

## Overhaul Question

If prompted:

```text
Is this product being added due to an overhaul,
major rebuild or repower?
```

Select:

```text
No
```

---

## Saving the Unit

Save the record.

Then immediately select:

```text
Send to FA
```

This creates the Unit in FieldAware.

---

# Appendix B – Creating a New Site

Create a Site only when the generator location does not already exist.

Open:

```text
Site Info
```

Open any existing site.

Select:

- Binoculars
- Setup
- F6

to create a new Site.

---

## Site Information

Complete:

| Field | Information |
|--------|-------------|
| Site Name | Customer site name |
| Site Address | Street address |
| City | City |
| State | Province Code (QC / ON) |
| Postal Code | Postal Code |
| Country | CA |
| Site Phone Number | Customer phone number |
| Primary Service Location | Z8 or AK |
| Tax District | Province Code |

---

### Primary Service Location

| Branch | Code |
|---------|------|
| Candiac | Z8 |
| Ottawa | AK |

---

## Saving the Site

Save the Site.

Immediately select:

```text
Send to FA
```

to synchronize it with FieldAware.

---

# Appendix C – Adding Safety Concerns

Safety concerns should be documented whenever they are known before dispatching the technician.

Examples include:

- Roof access
- Confined space
- High voltage
- Restricted access
- LOTO requirements
- Security escorts
- Environmental hazards

---

## Entering Safety Concerns

Open:

```text
Units
```

Select:

```text
Misc. Info
```

Open the:

```text
Safety Concerns
```

tab.

Enter:

- Concern
- Detailed description

Example:

```text
Roof access only.

Permanent ladder damaged.

Fall arrest required.
```

Save the record.

---

# Best Practices

- Verify customer information before creating the WOQT.
- Confirm the correct Unit and Site have been selected.
- Review all safety concerns before dispatching a technician.
- Ensure Job Plan SRTs total the correct labor allocation.
- Verify mileage calculations using Google Maps.
- Always create a WOQT before converting to a Work Order.
- Assign a Job Lead in FieldAware.
- Verify the work order appears on the Scheduler before considering the dispatch complete.
- Select **Send to FA** every time changes are made in BMS.

---

# Common Mistakes

## Wrong Unit Selected

Always verify:

- Serial Number
- Model
- Site

before saving.

---

## Incorrect SRT Allocation

Confirm the Job Plan reflects the correct labor allocation before converting the quotation.

---

## Mileage Calculated Incorrectly

Remember:

- North Shore uses Storage Unit → Customer.
- Montreal uses Candiac Branch → Customer.
- Ottawa uses Ottawa Branch → Customer.

Always calculate round-trip distance.

---

## Technician Not Assigned as Job Lead

Without a Job Lead:

- The work order will not appear correctly on the Scheduler.

---

## Forgot to Send to FA

Every modification made in BMS must be synchronized by selecting:

```text
Send to FA
```

Failure to synchronize may result in data loss or outdated information in FieldAware.

---

# Related Documents

- service_call_management.md
- quote_management.md
- invoicing.md
- overtime_entry.md
- service_billing_rates.md
- cash_customers_service_call.md
- clover_training.md
- technician_selection_rules.md
- technician_profiles.md