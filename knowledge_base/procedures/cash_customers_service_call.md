# Cash Customers - Service Call Procedure

# Version 2.1.0

# Last Updated: 2026-07-23

# Updated By: Jipeng Li

# Change Log:

v2.1.0
- Removed duplicated Order Entry (OE) instructions.
- Added Customer Deposit processing section.
- Referenced the Customer Deposits Process as the authoritative procedure.
- Updated coordinator responsibilities, checklist, best practices, and common mistakes.

v2.0.0
- Completely redesigned procedure.
- Added pre-authorization workflow.
- Added supervisor follow-up.
- Added customer follow-up process.
- Added same-week invoicing requirements.
- Added final payment workflow.
- Added coordinator checklist.
- Added best practices and common mistakes.

v1.0.0
- Creation of initial document.

## Purpose

This procedure describes the complete workflow for managing **cash customers requiring a mobile service call**.

Unlike charge customers, cash customers present a higher financial risk because payment is not protected by an approved credit account. Proper payment handling, follow-up, and timely invoicing are essential to minimize financial exposure.

---

# Workflow Overview

```text
Customer Calls
        ↓
Collect Credit Card Information
        ↓
Complete Clover Pre-Authorization ($750)
        ↓
Dispatch Technician
        ↓
Technician Completes Work
        ↓
Supervisor Follow-Up
        ↓
Contact Customer
        ↓
Confirm Final Charges
        ↓
Convert Pre-Authorization to Payment
        ↓
Process Customer Deposit (OE)
        ↓
Generate Invoice
        ↓
Send Invoice & Receipt
        ↓
File Documentation
```

---

# Before Dispatch

Before dispatching a technician, complete the following steps.

## Collect Customer Payment Information

Obtain:

- Credit card information
- Cardholder name
- Customer authorization to process payment

Determine whether the payment method is:

- Personal credit card
- Commercial credit card

Customer payment information must be stored securely according to branch procedures until payment has been completed.

---

## Standard Pre-Authorization

For standard service calls:

Obtain a **$750 pre-authorization** using Clover.

This pre-authorization must be completed **before dispatching the technician**.

> **Important**
>
> A pre-authorization is **not** a payment.
>
> It only reserves funds on the customer's credit card.

---

# Processing the Pre-Authorization

Using Clover:

1. Open the Virtual Terminal.
2. Select **Pre-Authorization**.
3. Enter the pre-authorization amount.
4. Complete the transaction.
5. Retrieve the payment receipt.
6. Record the Authorization ID.
7. Enter the Authorization ID as the Purchase Order (PO) number on the BMS Work Order.
8. Save the payment receipt.

Refer to the **Clover Training** procedure for detailed instructions.

---

# Technician Dispatch

Once the pre-authorization has been successfully completed:

- Dispatch the technician.
- Complete the Work Order following the standard dispatch procedure.

---

# Post-Service Supervisor Review

The day after the service call, or as soon as practical:

Follow up with the assigned supervisor.

Confirm:

- Technician labor has been entered.
- Technician punch has been completed.
- Work Order information is complete.
- The Work Order is identified as a **Cash Customer**.

---

# Customer Follow-Up

Contact the customer once the technician has completed the work.

During the call:

- Confirm the service has been completed.
- Explain the work performed.
- Answer any customer questions.
- Review the final invoice amount.
- Confirm customer approval to complete the payment.

Whenever possible, send a preview of the invoice before requesting final payment.

---

# Final Payment

Once customer approval has been received:

1. Convert the Clover pre-authorization into the final payment.
2. Verify that the payment has been successfully processed.
3. Generate the payment receipt.
4. Record the Authorization ID if required.
5. Save a copy of the payment receipt.

---

# Processing the Customer Deposit

After the final payment has been completed:

Process the customer's payment by creating an **Order Entry (OE)** in BMS.

The Customer Deposit process includes:

- Creating the Order Entry.
- Recording the customer deposit.
- Applying the correct Tax District.
- Linking the payment to the Work Order.
- Applying the deposit to the final invoice.
- Following the appropriate sales tax rules.

> **Important**
>
> Follow the **Customer Deposits Process** procedure for the complete Order Entry workflow.
>
> The customer deposit should be completed as soon as the payment has been successfully processed.

---

# Invoice Completion

The final invoice should be:

- Prepared during the same week the work was completed.
- Sent during the same week.

Prompt invoicing reduces payment delays and minimizes financial risk.

---

# Sending Documents

After payment has been completed:

Email the customer:

- Final invoice.
- Payment receipt.

Verify that both documents have been successfully delivered.

---

# Filing Documentation

Print or save copies of:

- Final invoice.
- Payment receipt.
- Order Entry documentation.

File the documents in the designated payment drawer located at the front of the Parts Department.

---

# Special Situations

## Parts Delay

If required parts will not arrive before the Clover pre-authorization expires:

- Contact the customer before expiration.
- Obtain payment again when the order is ready.
- Add a reminder in the Work Order.

Example:

```text
Contact customer for payment once the order is ready.
```

---

## Customer Questions

If the customer questions the invoice:

- Explain the completed work.
- Review technician findings.
- Answer all billing questions before completing payment.

---

# Coordinator Responsibilities

Service Coordinators are responsible for:

- Obtaining the customer's payment information.
- Processing the $750 pre-authorization before dispatch.
- Recording the Clover Authorization ID on the Work Order.
- Following up with the supervisor after service completion.
- Contacting the customer to review the completed work.
- Converting the pre-authorization into the final payment.
- Processing the customer deposit following the Customer Deposits Process.
- Producing and sending the invoice during the same week.
- Sending the payment receipt.
- Filing all required documentation.

---

# Coordinator Checklist

## Before Dispatch

- [ ] Credit card information collected.
- [ ] $750 pre-authorization completed.
- [ ] Authorization ID entered on the BMS Work Order.
- [ ] Technician dispatched.

## After Service

- [ ] Technician punch verified.
- [ ] Supervisor follow-up completed.
- [ ] Customer contacted.
- [ ] Final amount confirmed.
- [ ] Pre-authorization converted to payment.
- [ ] Customer deposit processed.
- [ ] Invoice produced.
- [ ] Invoice emailed.
- [ ] Payment receipt emailed.
- [ ] Documentation filed.

---

# Best Practices

- Obtain the pre-authorization before dispatching the technician.
- Follow up with the customer promptly after service completion.
- Complete the Customer Deposits Process immediately after converting the pre-authorization into the final payment.
- Produce invoices during the same week the work was completed.
- Keep all payment documentation organized.
- Create a Clover customer profile whenever possible to simplify future transactions.

---

# Common Mistakes

## Technician Dispatched Before Payment

Always complete the required pre-authorization before dispatching a technician.

---

## Treating a Pre-Authorization as Final Payment

Remember that a pre-authorization only reserves funds.

It must later be converted into the final payment.

---

## Customer Deposit Not Processed

Converting the pre-authorization into a payment does **not** complete the accounting process.

Always complete the **Customer Deposits Process** to correctly record and apply the customer's payment in BMS.

---

## Delayed Customer Follow-Up

Delaying customer contact increases the likelihood of payment issues or disputes.

---

## Delayed Invoicing

Invoices should always be produced and sent during the same week that the work was completed.

---

## Expired Pre-Authorization

If parts or repairs extend beyond the authorization period, contact the customer before the authorization expires to arrange payment again.