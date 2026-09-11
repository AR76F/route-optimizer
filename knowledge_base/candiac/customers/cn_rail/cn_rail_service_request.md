---
title: CN Rail Service Request
title_fr: Demande de service CN Rail
category: customer
subcategory: service_request
customer: CN Rail
customer_fr: CN Rail
region: Candiac
language: bilingual
keywords:
  - CN Rail
  - Olivier Gendron
  - EY
  - service request
  - demande de service
  - PRJPM
  - eRailSafe
  - G1
  - G2
  - 750h maintenance
  - 3000h maintenance
---

# Last Updated: 2026-09-11

# CN Rail Service Request

## Purpose

This procedure guides Service Coordinators when Olivier Gendron sends a CN Rail service request.

## Objectif

Cette procédure guide les coordonnateurs de service lorsqu'Olivier Gendron transmet une demande de service pour CN Rail.

---

## Response Time

Respond to the request within 24 hours.

Confirm the following information:

- CN Rail terminal, such as Taschereau or Old Port
- Unit number
- Scope of Work
- Affected generator, G1 or G2, when possible

Technicians assigned to the work must hold valid eRailSafe accreditation.

The applicable project number changes once per year. Confirm the current project number before creating the Work Order.

---

## Create the Work Order in BMS

1. Open the **Project** tab.
2. Press `F7`.
3. Enter the current CN Rail project number.
4. Press `F8`.
5. Open the **Work Order** tab.
6. Select **Create Work Order**.

Enter:

```text
Customer: EY
Work Type: Mobile
Contact: Olivier Gendron
Subtype: PRJPM
Complaint: Unit number, terminal, and Scope of Work
```

Select the correct unit, either `G1` or `G2`.

Because CN Rail units are frequently moved, open the **Unit** tab and verify the current site address before creating the Work Order or scheduling the intervention.

---

## Labor and Travel

Enter the labor time under:

```text
99 999
```

Do not add travel charges or kilometer charges.

---

## Scheduled Maintenance

### 750-Hour Maintenance

For 750-hour maintenance:

- The work may require one or two technicians.
- Send the parts list to Jean-François.
- Confirm that the generator and load-bank requirements match the site conditions.

The load bank is multivoltage. The documented generator voltage is 480 V.

### 3,000-Hour Maintenance

For 3,000-hour maintenance:

- Send the 750-hour maintenance parts list to Jean-François.
- Plan approximately two technicians for two days.
- A technician may perform the load-bank test alone, but the work will take longer.
- Confirm the required 750-hour maintenance parts.

---

## Important Notes

- Confirm the current project number because it changes annually.
- Verify whether the request concerns generator G1 or G2.
- Confirm the site address because the units are frequently moved.
- Assign only technicians with eRailSafe accreditation.
- Do not add travel or kilometer charges.
- Confirm current maintenance parts and site requirements before scheduling.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official visual guide for this procedure is available here:

[Open the CN Rail Service Request Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQAo53TnX2lrT449agZ11lPPATM1JKW3HEKsSbIhL9goms8?e=V9uGdR)

