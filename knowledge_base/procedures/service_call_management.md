# Procedure - Service Call Management

# Last Updated: 2026-09-03

## Purpose

This document provides the high-level workflow for receiving, qualifying, booking, and preparing a service call for dispatch.

Use the linked procedures for detailed system instructions, pricing, technician selection, quotations, payment, and customer-specific workflows.

## Objectif

Ce document présente le processus général de réception, d’évaluation, de planification et de préparation d’un appel de service avant le dispatch.

Consultez les procédures liées pour obtenir les instructions détaillées sur les systèmes, les tarifs, la sélection des techniciens, les soumissions, les paiements et les workflows propres à chaque type de client.

---

## Scope and Handoff

This procedure begins after basic front-desk triage, or when a Service Coordinator receives the call directly.

For basic call screening and routing, use [Front Desk Call Triage](front_desk_call_triage.md).

The Service Coordinator is responsible for ensuring that the job is understood, approved, properly prepared, and ready for the applicable detailed procedure.

## High-Level Workflow

```text
Receive or accept the routed request
        ↓
Gather essential customer, site, equipment, and problem information
        ↓
Determine the job type and customer status
        ↓
Confirm parts, approval, financial, and safety requirements
        ↓
Prepare or update the applicable BMS / FieldAware records
        ↓
Select and confirm the appropriate technician
        ↓
Reserve and confirm the appointment
        ↓
Complete the pre-dispatch review
        ↓
Dispatch and maintain accurate records
```

# 1. Gather Essential Information

Use the following questions during the call. Record the answers in the applicable customer and work-order records.

## Customer and Account

- Customer name and company name.
- Phone number and email address.
- Customer account number, if available.
- Whether the customer has an account, contract, or other customer relationship with Cummins.
- Billing information or customer-number details needed to locate or create the account.

## Site and Contact

- Generator site address.
- On-site contact name and telephone number.
- Site access, parking, gate, security, rooftop, or other restrictions.
- Any known safety concerns.

## Equipment

Collect the available generator information, such as:

- Manufacturer and model.
- Serial number or nameplate information.
- Current operating hours, when available.
- Generator location and access details.

## Problem Description

Ask:

- Is an alarm or fault code displayed? Record the exact code and description.
- What happened, and when did it start?
- Will the generator start or operate?
- Are there visible symptoms such as a coolant leak, smoke, or a battery problem?

Examples include `FC1223` and `Low Coolant`.

For inverter (ATS)-related issues, confirm whether a simulated outage can be performed and what time window is suitable.

For non-Cummins equipment, explain that technician availability and product expertise may be limited and that referral to a specialized provider may be necessary.

# 2. Classify the Request

Determine the primary job type:

- Service call or troubleshooting.
- Preventive maintenance.
- Project work, installation, commissioning, upgrade, or major repair.
- Inspection.
- Parts-only request.

Route parts-only requests according to [Front Desk Call Triage](front_desk_call_triage.md). Use the applicable Service or PM workflow for technician work.

# 3. Confirm Customer and Work Requirements

Before scheduling or dispatching, confirm the requirements that apply to the job.

## Customer Status

- Charge customer: verify the customer account and credit status according to branch practice.
- Cash customer: follow the appropriate cash-customer procedure before dispatch or ordering parts.
- Contract or special customer: verify the applicable agreement and service requirements.

See:

- [Cash Customers - Overview](cash_customers_overview.md)
- [Cash Customers - Service Call](cash_customers_service_call.md)
- [Cash Customers - Accepted Quotation](cash_customers_accepted_quote.md)

## Parts and Materials

Confirm at a high level:

- Whether parts are required.
- Whether parts are available or already ordered.
- Expected delivery timing when parts are missing.
- Whether the appointment should wait for parts.

Do not schedule work that depends on unavailable parts unless the appropriate approval has been obtained.

## Customer Approval

Before dispatch, confirm that the customer has approved the work through the applicable method, such as:

- Signed quotation.
- Written email approval.
- Other documented approval accepted by branch practice.

Use [Preparing and Accepting a Quote](quote_management.md) for the quotation and approval workflow.

# 4. Prepare the Records

Create or update the applicable BMS and FieldAware records with enough information for the technician and the next coordinator to understand the job.

At a minimum, ensure that the records include:

- Customer and on-site contact information.
- Equipment identification and location.
- Clear complaint or symptom description.
- Alarm or fault codes.
- Site access and safety information.
- Coverage or billing status.
- Required reports and supporting documents.

Use [BMS - Work Order Creation](../software/bms_work_order_creation.md) for detailed WOQT, work-order, billing-field, and synchronization instructions.

Use [FieldAware - Work Order Creation](../software/fieldaware_work_order_creation.md) for technician assignment, scheduling, reports, and Scheduler verification.

Use [Preparing and Accepting a Quote](quote_management.md) when the work requires a customer quotation or a technician Request for Quote (RFQ).

# 5. Select and Confirm the Technician

Select a technician based on:

- Technical capability.
- Territory and travel requirements.
- Certifications or security requirements.
- Customer and site requirements.
- Availability and workload.

Confirm the technician’s suitability and availability before finalizing the appointment.

Use [Technician Selection Rules](../technicians/tech_selection_rules.md) for the detailed selection rules.

# 6. Schedule and Confirm the Appointment

Reserve an appropriate time slot after the job requirements, approval, parts, and technician availability have been reviewed.

Confirm with the customer:

- Appointment date and time.
- Site address and access instructions.
- On-site contact details.
- Expected work and applicable cost or approval status.
- Any special testing, safety, or site conditions.

Use the detailed FieldAware instructions in [FieldAware - Work Order Creation](../software/fieldaware_work_order_creation.md).

# 7. Pre-Dispatch Checklist

Before dispatching, verify:

- Customer and billing information are identified.
- Site address and on-site contact are confirmed.
- Equipment, complaint, and alarm information are documented.
- Safety and access requirements are visible to the technician.
- Customer approval is documented.
- Credit, payment, or deposit requirements are satisfied.
- Required parts are available or an exception is approved.
- Technician suitability and availability are confirmed.
- Appointment details are confirmed with the customer.
- BMS and FieldAware records are complete and synchronized.
- Required reports and documents are attached.
- The job appears correctly on the FieldAware schedule.

# Related Procedures

- [Front Desk Call Triage](front_desk_call_triage.md)
- [Preparing and Accepting a Quote](quote_management.md)
- [BMS - Work Order Creation](../software/bms_work_order_creation.md)
- [FieldAware - Work Order Creation](../software/fieldaware_work_order_creation.md)
- [Technician Selection Rules](../technicians/tech_selection_rules.md)
- [Cash Customers - Overview](cash_customers_overview.md)
- [Cash Customers - Service Call](cash_customers_service_call.md)
- [Cash Customers - Accepted Quotation](cash_customers_accepted_quote.md)
- [Customer Deposits Process](cash_customers_deposits.md)
- [Coordinator - Service Billing Rates](../reference/service_hourly_rates.md)

## Golden Rule

A successful service call begins with a complete and accurate booking. The technician should arrive with the correct information, contact, parts, documentation, access instructions, and customer expectations.
