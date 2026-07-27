# Coordinator - Clover Training

# Version 1.0.0

# Last Updated: 2026-07-20

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Creation of initial document.

## Purpose

This document provides Service Coordinators with the standard procedure for using the Clover Virtual Terminal to process cash customer payments, pre-authorizations, purchases, and refunds.

It also explains how Clover transactions integrate with BMS work orders and outlines best practices for managing cash customer profiles.

---

# Systems Used

- Clover Virtual Terminal
- BMS

---

# Accessing Clover

Access to Clover requires an account registration.

If you do not already have access:

- Request a registration link from the Service Department Manager.
- Complete the registration process.
- Log in using your Cummins email address (WWID@cummins.com).

Clover can be accessed at:

https://www.clover.com/login

---

# Clover Workflow

```text
Customer Requires Payment
            ↓
Log into Clover
            ↓
Open Virtual Terminal
            ↓
Select Transaction Type
            ↓
Process Payment or Pre-Authorization
            ↓
Retrieve Payment Receipt
            ↓
Record Authorization ID
            ↓
Enter Authorization ID as the PO Number in BMS
            ↓
Send Receipt to Customer
```

---

# Opening the Virtual Terminal

After logging into Clover:

1. Open the appropriate branch dashboard.
2. Select **Virtual Terminal**.
3. Choose the appropriate **Transaction Type**.

Available transaction types include:

- Pre-Authorization
- Purchase
- Refund

---

# Processing a Pre-Authorization

## Standard Service Calls

For a standard cash service call:

- Obtain a **$750 pre-authorization** before dispatching the technician.

The technician should **not** be dispatched until the pre-authorization has been successfully completed.

---

## Creating the Pre-Authorization

1. Select **Pre-Authorization** from the Transaction Type drop-down list.
2. Enter the pre-authorization amount.
3. Add a reasonable amount for potential additional charges if appropriate.
4. Enter the customer's payment information.
5. Complete the transaction.

Only fields marked with an asterisk (*) are mandatory.

---

# Processing a Customer Payment

When collecting a payment:

1. Select the appropriate Transaction Type.
2. Enter the sales amount.
3. Enter the customer's payment information.
4. Process the payment.

---

# Cash Quotations

When a **cash customer accepts a quotation**:

**Do not perform a pre-authorization.**

Instead:

- Collect payment for the **entire quoted amount**.

After payment:

1. Create an Order Entry (OE) in BMS.
2. Reserve the payment against the work order.
3. Enter the payment in the Charges tab.
4. Add the payment reference in the Comments section.
5. Apply the OE to the Misc Charges section of the work order.
6. File the OE and payment receipt according to branch procedures.

Refer to:

- cash_customers_service_call.md
- cash_customer_accepted_quote.md

for the complete cash customer payment workflow.

Refer to:

- cash_customers_order_entry.md

for the complete order entry workflow.

---

# Retrieving the Payment Receipt

After processing the transaction:

1. Locate the completed payment.
2. Select **Details**.
3. Select **View Payment Receipt**.

> Do **not** use **Send Receipt**, as this function is currently unavailable.

Save the receipt as a PDF.

Send the receipt to the customer.

---

# Authorization ID

After opening the payment receipt:

Record the **Authorization ID**.

The Authorization ID must be entered as the:

**Purchase Order (PO) Number**

on the corresponding BMS Work Order.

Failure to record the Authorization ID may prevent payment tracking.

---

# Creating Customer Profiles

It is recommended to create a Clover customer profile for every new cash customer.

Benefits include:

- Faster future transactions.
- Secure storage of payment information.

Customer payment information is only available within the branch where it was originally saved.

---

## Naming Convention

When creating a new customer profile:

Append the customer's BMS account number to the end of their last name.

Example:

```text
Brisson123456
```

---

# Pre-Authorization Expiration

If customer payment information is **not saved**:

- Pre-authorizations expire after **2 weeks**.

If parts are not expected to arrive within that period:

Add a reminder such as:

```text
Contact the customer for payment once the order is ready.
```

---

# Coordinator Responsibilities

Before dispatching a technician:

- Confirm the appropriate transaction type.
- Obtain the required payment or pre-authorization.
- Verify that the Authorization ID has been recorded.
- Enter the Authorization ID as the PO Number in BMS.
- Save and send the payment receipt.
- Create a customer profile whenever possible.
- Follow the cash quotation process for accepted quotations.

---

# Common Mistakes

## Technician Dispatched Before Payment

Always obtain the required payment or pre-authorization before dispatching a technician.

---

## Wrong Transaction Type

Do not use a pre-authorization when collecting payment for an accepted cash quotation.

---

## Authorization ID Not Recorded

Always enter the Authorization ID as the PO Number on the BMS Work Order.

---

## Customer Profile Not Created

Whenever possible, create a Clover customer profile to simplify future transactions.

---

## Expired Pre-Authorization

Remember that pre-authorizations expire after two weeks if the customer's payment information is not saved.

---

# Best Practices

- Create a customer profile for every new cash customer.
- Explain the benefits of securely saving payment information.
- Save every payment receipt as a PDF.
- Verify that the Authorization ID has been entered into BMS before closing the transaction.
- Review pre-authorizations regularly to ensure they do not expire before parts become available.

---
