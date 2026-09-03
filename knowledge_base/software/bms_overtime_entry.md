# BMS - Overtime Entry 

# Last Updated: 2026-09-03

## Purpose

This document explains how Service Coordinators must enter **overtime (OT)** in BMS when preparing quotations or completing invoicing.

Correctly charging overtime ensures that customer quotations and invoices accurately reflect labor costs and comply with branch billing practices.

## Objectif

Ce document explique comment les coordonnateurs de service doivent entrer les **heures supplémentaires (OT)** dans BMS lors de la préparation des soumissions ou de la facturation.

La saisie correcte des heures supplémentaires permet de s’assurer que les soumissions et les factures reflètent fidèlement les coûts de main-d’œuvre et respectent les pratiques de facturation de la succursale.

---

# When to Apply Overtime

Overtime must be entered whenever a technician works **more than 8 regular hours in a single day**.

Hours exceeding the first 8 regular hours must be charged using the appropriate overtime rate.

## Example

A technician works **10 hours**.

The labor should be entered as:

- 8 hours → Regular Time (RT)
- 2 hours → Overtime (OT)

Do **not** enter all 10 hours as regular time.

---

# Where to Perform This Step

This procedure is completed in the **Job Plan** tab within **BMS**.

It applies to:

- Customer quotations
- Customer invoicing

Whenever overtime is applicable, the coordinator must update the Job Plan accordingly.

---

# Entering Overtime in BMS

## Step 1

Enter the first **8 hours** using the normal labor operation lines.

Typical examples include:

- 88 ADM 00 902
- 88 JSA
- 99 999
- 99 990

These represent the technician's regular labor.

---

## Step 2

After the first 8 hours have been entered, create an **additional Job Plan line**.

This additional line is used exclusively for overtime hours.

Do not modify the regular labor line.

---

## Step 3

For the overtime entry:

Access:

```text
99 999
```

Access Type:

```text
R
```

Rate Type:

```text
FSOT
```

Enter only the hours worked beyond the initial 8 regular hours.

---

# Overtime Rate

The **Rate** field is **not populated automatically**.

Coordinators must manually enter the correct hourly rate.

Use the current service rate sheets available on the departmental Teams site.

Examples include:

- Candiac Mobile Service Rates
- Ottawa Mobile Service Rates
- Candiac In-Shop Rates
- Ottawa In-Shop Rates

Always verify that the rate corresponds to the branch and service type before saving.

---

# Example

Technician works:

**10 hours**

The Job Plan should contain:

| Labor Type | Hours |
|------------|------:|
| Regular Time | 8.0 |
| FSOT | 2.0 |

---

# Coordinator Responsibilities

Before saving the quotation or invoice:

- Verify whether total labor exceeds 8 hours.
- Split regular and overtime hours correctly.
- Create a separate Job Plan line for overtime.
- Select **FSOT** as the overtime rate type.
- Manually enter the correct overtime rate using the current rate sheet.
- Verify the final labor totals before completing the quotation or invoice.

---

# Common Mistakes

## Charging All Hours as Regular Time

Incorrect:

```text
10 hours RT
```

Correct:

```text
8 hours RT
2 hours FSOT
```

---

## Forgetting to Add a Separate Job Plan Line

Overtime must always be entered on its own Job Plan line.

---

## Incorrect Rate Type

Always use:

```text
FSOT
```

for overtime entries.

---

## Incorrect Hourly Rate

Do not rely on BMS to populate the overtime rate.

The coordinator must manually enter the appropriate rate using the current branch rate sheet.

---

# Best Practices

- Review technician labor hours before completing every quotation or invoice.
- Apply overtime consistently whenever labor exceeds 8 hours.
- Confirm the correct overtime rate before saving the Job Plan.
- Double-check the quotation or invoice after entering overtime.

---
