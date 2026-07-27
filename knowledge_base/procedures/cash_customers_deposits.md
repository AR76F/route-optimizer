# Customer Deposits Process

# Version 1.0.0

# Last Updated: 2026-07-20

# Updated By: Jipeng Li

# Change Log:

v1.0.0
- Initial transcription from the Customer Deposits Process OneBMS presentation.

## Receiving a Customer Deposit

Create an **Order Entry (OE)** to receive a customer deposit for:

- Engine sale
- Service event
- Parts order

Within the **Charges** tab:

- Name: **DEPOSIT**
- Apply the appropriate **Tax District**
- Apply the applicable sales taxes

### Purchase Order

```text
DEP
```

### Comments

Add any references required.

Examples:

- Serial Number
- Work Order Number

Example:

```text
WO #123456
```

> **Note**
>
> The presentation uses the **BC Tax District** as an example.
>
> Each branch must apply the correct Tax District applicable to its own location.

---

# Down Payments / Advance Payments

Once a deposit becomes a **down payment** or **partial payment** toward:

- Engine sales
- Parts sales
- Service work

the applicable sales taxes must be charged.

Examples include:

- GST
- HST
- Provincial Sales Tax (where applicable)

Source:

- Canada Revenue Agency (CRA)
- Excise Tax Act, subsection 168(1)
- CRA Memorandum GST 300-6-8 – Deposits

---

# Applying the Deposit on the Final Invoice

## Order Entry (OE / XENG)

When producing the final invoice:

Within the **Charges** tab:

- Name: **DEPOSIT**
- Use the same Tax District used on the original OE.
- Enter the deposit amount as a **negative value**.

---

## Work Order (WO)

Within the **Misc Charges** tab:

- Name: **DEPOSIT**
- Use the same Tax District used on the original OE.
- Enter the deposit amount as a **negative value**.

---

# Original OE – Customer Deposit

When applying the deposit:

- The original deposit information should match the amount and Tax District used on the final invoice.
- The deposit is applied as a negative value to reduce the customer's remaining balance.

---

# Sales Tax on Deposits

Sales tax treatment depends on whether the deposit is **refundable** or **non-refundable**.

## Refundable Deposit

If the customer agreement specifies that the deposit is refundable:

- Do **not** charge sales tax when the deposit is initially received.
- Taxes will be calculated on the final sale.
- Apply the deposit as a negative value on the final invoice.
- No sales tax is applied to the original deposit.

---

## Non-Refundable Deposit

If the deposit is non-refundable:

- Sales tax must be charged when the deposit is received.

This also applies to:

- Down payments
- Advance payments
- Service work proceeding after payment

Applicable taxes include:

- GST
- HST
- Provincial Sales Tax (where applicable)

Source:

- Canada Revenue Agency (CRA)
- Excise Tax Act, subsection 168(1)
- CRA Memorandum GST 300-6-8 – Deposits