# Cash Customers - Customer Deposits / Order Entry (OE)

# Last Updated: 2026-09-02

## Purpose

This procedure explains how to **receive, record, and apply a customer deposit using an Order Entry (OE) in OneBMS**.

It applies to customer deposits associated with:

- Service work
- Parts orders
- Engine sales

## Objectif

Cette procédure explique comment **réceptionner, enregistrer et appliquer un dépôt client à l'aide d'un Order Entry (OE) dans OneBMS**.

Elle s'applique notamment aux dépôts associés aux travaux de service, aux commandes de pièces et aux ventes de moteurs.

---

## Quick Reference / Référence rapide

**Customer Deposit / Order Entry / OE / Dépôt client**

To receive a customer deposit:

- Create an **OE** with the customer's information.
- Use the **Charges** tab.
- Select `DEPOSIT`.
- Enter the amount received.
- Apply the appropriate **Tax District**.
- Use `DEP` as the PO number when applicable.
- Add the applicable Work Order or Serial Number reference in **Comments**.
- Apply the deposit to the corresponding Work Order through **Misc Charges**.
- When applying the deposit, use the **same amount and Tax District** as the original OE and enter the deposit as a **negative value**.

### French Retrieval Concepts

- Dépôt client
- Dépôt dans BMS
- Dépôt dans OneBMS
- Order Entry
- OE
- Créer un OE
- Réceptionner paiement
- Réceptionner montant
- Paiement client cash
- Appliquer dépôt
- Misc Charges
- Charges
- DEPOSIT
- Paiement sur bon de travail
- Paiement sur WO
- Dépôt négatif
- Tax District

---

# Creating the Order Entry (OE)

Create an **Order Entry (OE)** using the customer's information.

For a customer deposit, use:

```text
Transaction Type: OE
```

Enter the applicable customer and order information.

When applicable, use:

```text
PO: DEP
```

---

# Recording the Deposit

Open the:

```text
Charges
```

tab.

Enter:

```text
Name: DEPOSIT
Amount: Amount received
Tax District: Applicable Tax District
```

The Tax District must reflect the correct tax treatment for the applicable branch/location.

---

# Adding the Payment Reference

Open the:

```text
Comments
```

tab.

Add a reference identifying the payment.

The reference may include:

- Work Order number
- Serial Number
- Other relevant payment reference

Example:

```text
PAYMENT FOR WOQT 123456
```

The purpose is to clearly identify which Work Order or transaction the deposit belongs to.

---

# Applying the Deposit to the Work Order

Open the corresponding Work Order.

Navigate to:

```text
Misc Charges
```

Add:

```text
Name: DEPOSIT
```

Use the:

- Same deposit amount.
- Same Tax District.

The deposit must be entered as a:

```text
Negative Value
```

This applies the previously received deposit against the Work Order balance.

---

# Deposit Application Rule

The original OE and the Work Order deposit application must correspond.

```text
Original OE
DEPOSIT
+ Amount Received
+ Applicable Tax District

        ↓

Work Order - Misc Charges
DEPOSIT
- Same Amount
+ Same Tax District
```

The negative deposit reduces the amount remaining on the final invoice.

---

# Sales Tax on Deposits

Sales tax treatment depends on whether the deposit is **refundable or non-refundable**.

## Refundable Deposit

If a contract specifically states that the deposit is refundable:

- Do **not** charge sales tax when the deposit is initially received.
- Taxes are calculated on the final sale.
- Apply the deposit as a negative value on the final invoice without sales tax on the original deposit.

## Non-Refundable Deposit / Down Payment

If the deposit is non-refundable, or becomes a down payment or advance payment toward work that is proceeding:

- Applicable sales taxes must be charged.

This may include:

- GST
- HST
- Applicable provincial sales taxes

The appropriate Tax District must be used.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official **Customer Deposits Process OneBMS** SharePoint document contains the complete visual procedure, including screenshots showing the Order Entry, Charges, Comments, deposit application, and sales-tax treatment.

Le document SharePoint officiel **Customer Deposits Process OneBMS** contient la procédure visuelle complète avec les captures d'écran nécessaires pour créer et appliquer un dépôt client dans OneBMS.

**Official SharePoint Link:**

[Open the Customer Deposits Process OneBMS Guide](https://cummins365-my.sharepoint.com/:p:/g/personal/ud016_cummins_com/IQCxLYmalriDS5ZqeNavhIjKAYTk2S-yFOjMsHFaz1Tfm9I?e=nK3sae)

### Link Retrieval Rule / Règle de récupération du lien

When a user asks for the **Customer Deposit procedure, Order Entry procedure, OE deposit procedure, SharePoint link, source document, original document, official guide, visual guide, screenshots, or OneBMS deposit training material**, provide the **Official SharePoint Link above**.

Lorsqu'un utilisateur demande la **procédure de dépôt client, procédure OE, création d'un OE, application d'un dépôt, lien SharePoint, document source, document original, guide officiel, guide visuel ou captures d'écran**, fournir le **lien SharePoint officiel ci-dessus**.

Examples of requests that should return this link:

**English**
- How do I create an OE for a customer deposit?
- Give me the customer deposit procedure.
- How do I apply a deposit to a Work Order?
- Do you have the SharePoint link?
- Show me the visual OE procedure.

**Français**
- Comment créer un OE pour un dépôt client?
- Comment réceptionner un montant dans BMS?
- Comment appliquer un dépôt sur un bon de travail?
- Donne-moi la procédure OE.
- As-tu le lien SharePoint?
- Où est le guide visuel pour les dépôts?

---

## Search Terms / Termes de recherche

**English:** customer deposit, Order Entry, OE, create OE, customer payment, receive deposit, DEPOSIT charge, Misc Charges, apply deposit, negative deposit, deposit Work Order, Tax District, OneBMS deposit.

**Français:** dépôt client, Order Entry, OE, créer OE, réceptionner paiement, réceptionner montant, paiement client, DEPOSIT, Misc Charges, appliquer dépôt, dépôt négatif, dépôt bon de travail, dépôt WO, Tax District, dépôt OneBMS.