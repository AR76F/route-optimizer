# Job Booking

# Version 1.1.0

# Last Updated: 2026-07-15

# Updated By: Jipeng Li

# Change Log:

v1.1.0
- Merged a significant portion of the file "Taking a customer call" into the current job booking file.

v1.0.1
- Added minor details

v1.0.0
- Creation of initial document.

## Purpose

The Job Booking process ensures that customer requests are documented accurately, assigned to the appropriate technician, properly scheduled, and fully prepared before dispatch.

A properly booked job reduces delays, avoids scheduling conflicts, improves first-time fix rates, and ensures technicians arrive on site with the correct information and parts. [1](https://cummins365-my.sharepoint.com/personal/ud016_cummins_com/_layouts/15/Doc.aspx?sourcedoc=%7B56DB06D2-14A7-4522-95D1-DF8D7E8930AC%7D&file=CapaciteTechs_CandiacEtOttawa%20%281%29.xlsx&action=default&mobileredirect=true)

---

# Overview

## Job Booking Workflow

```text
Receive customer call
        ↓
Gather information
        ↓
Determine job type
        ↓
Verify credit
        ↓
Verify parts
        ↓
Select technician
        ↓
Reserve time slot
        ↓
Customer approval
        ↓
Create work order
        ↓
Assign technician
        ↓
Dispatch
```

---

# Receiving the Customer Call

## Greeting

Begin every customer interaction professionally.

Suggested greeting:

> "Cummins Service, my name is [your name], how may I help you today?"

Before gathering information, have a notebook, paper, or digital document ready to record customer details and technical information.

# Step 1 - Gather Customer Information

## Customer Information

Collect the following:

- Customer name
- Company name
- Phone number
- Email address
- Customer account number (if available)

If the customer does not already exist in BMS:

- Create a new customer account.
- Verify billing information.

---

## Site Information

Always obtain:

- Site address
- Site contact name
- Site contact phone number

Technicians must know who to contact upon arrival.

---

## Generator Information

Collect as much information as possible.

Examples:

- Serial number
- Model
- Data plate information
- Current operating hours
- Generator location

Examples of locations:

- Roof
- Basement
- Mechanical room
- Boat
- Remote site
- Restricted-access site

Also document any known safety concerns reported by the customer.

---

## Technical Information

Record all symptoms reported by the customer.

Examples:

- Alarm code
- Fault code
- Won't start
- Leaking coolant
- Battery problem
- ATS issue
- Excessive smoke

Examples of useful descriptions:

- FC1223
- Low Coolant
- Generator trips after 20 minutes
- ATS remains in utility position

The more information collected, the easier technician selection becomes.

### Automatic Transfer Switch (ATS) Calls

For ATS-related issues, confirm:

- Whether a simulated power outage can be performed.
- The preferred testing window.

### Non-Cummins Generators

If the equipment is not manufactured by Cummins:

- Inform the customer that a technician can still be dispatched.
- Explain that the technician may not be certified on that specific equipment.
- Advise that the customer may be referred to a specialized provider if required.

---

# Step 2 - Determine Job Type

## Service Call

Use when:

- Customer reports a fault.
- Equipment requires troubleshooting.
- Customer requests urgent support.

Examples:

- Generator will not start.
- Cooling system leak.
- Battery charger failure.

---

## Preventive Maintenance

Use when:

- Scheduled maintenance is required.
- PM contract work is due.
- Service interval has been reached.

---

## Project Work

Use when:

- Generator installation
- Commissioning
- Load bank testing
- Upgrades
- Major repairs

---

## Inspection

Use when:

- Site inspection
- Monthly inspection
- Annual inspection
- Fire pump inspection
- Quinquennial inspection

---

# Step 3 - Verify Customer Status

## Charge Customers

Verify:

- Credit account exists.
- Credit limit is sufficient.

If credit is insufficient:

- Contact Elena DiBernardo.
- Request a credit increase.

Do not proceed until credit concerns are resolved.

---

## Cash Customers

Before dispatch:

- Collect payment information.
- Process payment according to branch policy.
- Verify deposit requirements.

Minimum service-call billing generally includes:

- Four hours labor
- Kilometrage charges

Refer to the Cash Customer Procedure document for complete details.

---

# Step 4 - Verify Parts Availability

## Parts Required

Determine:

- Are parts required immediately?
- Are parts already ordered?
- Are parts in stock?

---

## If Parts Are Missing

Contact:

- Parts Department

Determine:

- Availability
- Expected delivery date
- Alternative options

Never schedule work requiring unavailable parts unless management or the technician approves proceeding.

---

# Step 5 - Select the Appropriate Technician

## Selection Criteria

Choose the technician based on:

1. Technical capability
2. Territory coverage
3. Customer requirements
4. Certifications
5. Security clearances
6. Availability
7. Current workload

---

## Examples

### Engine Issue

Preferred Technicians

- Pier-Luc Côté
- Alain Duguay
- François Racine

---

### Electrical Issue

Preferred Technicians

- Michael Sulte
- Christian Dubreuil
- François Racine

---

### ATS Issue

Preferred Technicians

- François Racine
- Christian Dubreuil
- Alain Duguay

---

### Government or High-Security Site

Preferred Technicians

- François Racine
- Alain Duguay
- Ali Reza-Sabour

---

## Technician Confirmation

Before booking:

- Call the selected technician.
- Review customer complaint.
- Discuss job details.
- Confirm suitability.

If needed:

- Request technician recommendations.

---

# Step 6 - Reserve a Time Slot

## FieldAware Scheduling

Select a tentative time slot.

Consider:

- Customer availability
- Travel time
- Parts availability
- Technician workload
- Priority level

---

## Placeholder Creation

If scheduling is not finalized:

- Create a placeholder in FieldAware.
- Create an Outlook reminder.

Purpose:

- Prevent double-booking.
- Protect the selected time slot.

---

# Step 7 - Confirm Appointment

## Customer Confirmation

Before dispatching:

Confirm with the customer:

- Appointment date
- Appointment time
- Site accessibility
- Contact information
- Cost of the service

---

## Confirm Special Site Conditions

Ask:

- Is parking available?
- Are there gate restrictions?
- Is rooftop access required?
- Are there snow removal concerns?
- Which entrance should be used?
- Are there safety concerns?

---

# Step 8 - Create and Update Work Order

## Complaint Section

The complaint section should contain:

### Customer Complaint

Examples:

- FC1223 alarm active
- Unit does not start in Auto
- Excessive coolant leak

### On-Site Contact

Include:

```text
On-Site Contact:
John Smith
514-555-1234
```

### Site Notes

Examples:

```text
Generator located on roof.

Access through loading dock.

Parking available behind building.
```

### Site Access Information

Document any site-specific access requirements.

Examples:

- Roof access
- Restricted access
- Marine application
- Mechanical room
- Security escort required

---

## Coverage Section

Select:

```text
Customer Billable
```

unless another coverage type applies.

---

## Cause Section

Before troubleshooting:

```text
To Be Determined.
```

---

## Correction Section

Before work begins:

```text
To be completed by technician.
```

---

## Remarks Section

Use:

```text
Thank you for choosing Cummins.

Quote may vary once work has been completed.
```

---

# Step 9 - Assign in FieldAware

After customer approval:

- Remove any temporary placeholder or customer hold created during scheduling.
- Remove unnecessary reports before dispatching the work order.

## Technician Assignment

Assign:

- Correct technician
- Job lead status
- Reports

---

## Required Reports

Standard assignments:

- Field Service Basic
- RFQ (Request for Quotation)

Additional reports as required:

- Fire Pump Report
- Monthly Inspection
- Quinquennial Inspection
- Customer-specific documentation

---

## Scheduling Details

Verify:

- Date
- Start time
- End time
- Technician assignment

Save the job.

Confirm that the job appears correctly on the scheduler.

## Priority Code

Assign and display the appropriate priority code in the Schedule Priority field.

---

# Step 10 - Final Pre-Dispatch Review

Before dispatching the job, verify:

## Customer Information

- Customer verified
- Contact information verified
- Site information verified

## Technical Information

- Serial number obtained
- Complaint documented
- Alarm codes documented

## Financial Review

- Credit approved
- Deposit collected if required

## Parts Review

- Parts available
- Delivery dates confirmed

## Scheduling Review

- Technician confirmed
- Time slot confirmed
- FieldAware assignment completed

## Documentation Review

- Reports attached
- Notes complete
- Safety concerns documented

---

# Customer Approval

Before dispatching the technician, ensure that the customer has approved the work.

Approval may be received through:

- A signed quotation.
- Written email confirmation.

Once approval is received:

- Finalize the work order.
- Dispatch the technician.
- Update FieldAware accordingly.

---

# Common Booking Mistakes

## Missing On-Site Contact

Always provide:

- Name
- Phone number

Technicians should never arrive on site without a contact person.

---

## Insufficient Complaint Information

Avoid:

```text
Generator not working.
```

Use:

```text
Generator displaying FC1223 alarm, low coolant warning active, unit shuts down after approximately 15 minutes.
```

---

## Incorrect Technician Assignment

Always validate:

- Territory
- Skillset
- Availability

before scheduling.

---

## Scheduling Before Parts Are Available

Confirm parts delivery timelines before booking work that requires parts.

---

## Failure to Document Safety Concerns

Examples:

- Roof access
- Confined space
- Restricted access
- High-voltage area
- Security clearance requirements

All safety concerns must be visible to technicians before arrival.

---

# Job Booking Golden Rule

A successful service call begins with a successful booking.

The coordinator's objective is to ensure the technician arrives on site with:

- The correct information
- The correct customer contact
- The correct parts
- The correct documentation
- The correct expectations

The quality of the booking directly impacts the quality of the service experience.

# Best Practices

- Gather as much technical information as possible during the initial call.
- Verify customer information before creating a work order.
- Confirm technician suitability before assigning the job.
- Verify parts availability before scheduling.
- Clearly document site access requirements.
- Maintain accurate FieldAware scheduling to avoid double-booking.