# Software - System Overview

# Last Updated: 2026-09-03

## Purpose

This document provides a high-level overview of the primary software applications used by the Power Generation Service Department and explains how information flows between them.

Understanding the role of each system helps Service Coordinators know where information originates, how it is synchronized, and where specific tasks should be completed.

## Objectif

Ce document fournit un aperçu général des principales applications logicielles utilisées par le département de service Power Generation et explique comment l’information circule entre celles-ci.

Comprendre le rôle de chaque système permet aux coordonnateurs de service de savoir d’où provient l’information, comment elle est synchronisée et dans quel système les différentes tâches doivent être effectuées.

---

# Software Ecosystem

The Power Generation Service Department primarily uses four software platforms:

1. **Business Management System (BMS)**
2. **FieldAware (FA)**
3. **Clover**
4. **Power BI**

Each system serves a different purpose while supporting the overall service workflow.

---

# Software Architecture

```text
                    +----------------------+
                    |       Clover         |
                    | Payment Processing   |
                    +----------+-----------+
                               |
                 Authorization ID (Manual)
                               |
                               v
+------------------+     Send to FA      +------------------+
|       BMS        | <-----------------> |    FieldAware    |
| ERP / Work Order |                     | Field Operations |
+---------+--------+                     +---------+--------+
          |
          | Nightly Data Refresh
          v
+--------------------------+
|         Power BI         |
| Reporting & Analytics    |
+--------------------------+
```

---

# Business Management System (BMS)

## Overview

Business Management System (BMS) is the Enterprise Resource Planning (ERP) system used by the Power Generation Service Department.

BMS is considered the **primary system of record** for service operations.

## Primary Functions

BMS is used to manage:

- Customer accounts
- Work Orders
- Work Order Quotes (WOQT)
- Units
- Sites
- Job Planning
- Standard Repair Times (SRTs)
- Billing
- Invoicing
- Purchase Orders
- Miscellaneous Charges

Most operational procedures begin in BMS.

---

# FieldAware (FA)

## Overview

FieldAware is the field service management platform used by technicians and Service Coordinators.

It is primarily responsible for technician scheduling and field execution.

## Primary Functions

FieldAware is used to manage:

- Technician scheduling
- Job assignments
- Job Lead assignments
- Appointment scheduling
- Technician reports
- Field Service Basic reports
- Request for Quotation (RFQ) reports

FieldAware receives work orders created in BMS.

---

# Clover

## Overview

Clover is the payment processing platform used for handling customer credit card transactions.

It is primarily used for cash customers and credit card payments.

## Primary Functions

Clover is used to process:

- Credit card pre-authorizations
- Customer payments
- Refunds
- Payment receipts
- Customer payment profiles

Unlike FieldAware, Clover does **not** automatically synchronize with BMS.

After a payment or pre-authorization has been processed:

- Retrieve the **Authorization ID**
- Record the Authorization ID as the **Purchase Order (PO)** number on the corresponding BMS Work Order

Clover serves as the system of record for payment transactions, while BMS remains the system of record for work orders and billing.

---

# Power BI

## Overview

Power BI is the reporting and analytics platform used by management and administration.

Power BI is intended for reporting purposes only.

No operational information is entered directly into Power BI.

## Primary Functions

Power BI provides:

- Operational dashboards
- KPI reporting
- Financial reporting
- Productivity tracking
- Administrative reports
- Branch performance metrics

---

# Data Flow

## BMS ⇄ FieldAware

BMS and FieldAware communicate through synchronization.

Changes made in BMS can be transmitted to FieldAware using:

```text
Send to FA
```

Likewise, technician activity completed in FieldAware is reflected back into BMS.

This enables two-way communication between both systems.

> **Important**
>
> Whenever changes are made to a Work Order in BMS, Service Coordinators should select **Send to FA** to ensure FieldAware reflects the latest information.

Failure to synchronize may result in outdated information appearing in FieldAware or coordinator changes being overwritten after technician updates.

---

## BMS → Power BI

Power BI receives operational data from BMS once every night.

Information entered into BMS during the day will generally not appear in Power BI until the next scheduled refresh.

Power BI reporting is therefore based on the previous overnight synchronization.

---

## Clover → BMS

There is **no automatic synchronization** between Clover and BMS.

After processing a payment or pre-authorization in Clover:

1. Retrieve the payment details.
2. Open the payment receipt.
3. Record the Authorization ID.
4. Enter the Authorization ID as the Purchase Order (PO) number on the BMS Work Order.

This manual process links the payment transaction to the corresponding work order.

---

# System Responsibilities

| System | Primary Responsibility |
|----------|------------------------|
| **BMS** | Enterprise Resource Planning (ERP), customer management, work orders, billing, invoicing, units and sites |
| **FieldAware** | Technician scheduling, dispatching, field reporting and appointment management |
| **Clover** | Credit card processing, pre-authorizations, payments, refunds and customer payment profiles |
| **Power BI** | Business reporting, dashboards, analytics and performance monitoring |

---

# Key Concepts

## BMS is the Source of Truth

Customer information, work orders, billing information, units, and service history originate in BMS.

Operational changes should always begin in BMS unless another procedure specifically states otherwise.

---

## FieldAware Synchronization

FieldAware relies on BMS synchronization.

Always use **Send to FA** after modifying a Work Order.

---

## Clover Integration

Clover does not automatically communicate with BMS.

Service Coordinators are responsible for manually transferring the Clover Authorization ID into the Purchase Order field on the corresponding BMS Work Order.

---

## Power BI Reporting

Power BI is a reporting platform.

It is updated once daily through a scheduled overnight synchronization from BMS.

Recent operational changes may not appear until the following business day.

---

# Common Questions

## Which system creates Work Orders?

**BMS**

---

## Which system schedules technicians?

**FieldAware**

---

## Which system processes customer payments?

**Clover**

---

## Which system produces management reports?

**Power BI**

---

## Which system is considered the source of truth?

**BMS**

---

