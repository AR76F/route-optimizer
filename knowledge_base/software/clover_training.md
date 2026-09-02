# Clover Training

# Last Updated: 2026-09-02

## Purpose

This document provides a concise overview of using the **Clover Virtual Terminal** to process cash customer pre-authorizations and payments.

It also explains how the Clover Authorization ID is associated with the corresponding BMS Work Order.

## Objectif

Ce document fournit un aperçu de l'utilisation du **Clover Virtual Terminal** pour traiter les préautorisations et les paiements des clients Cash.

Il explique également comment le numéro d'autorisation Clover doit être associé au bon de travail correspondant dans BMS.

---

## Quick Reference / Référence rapide

**Clover / Virtual Terminal / Cash Customer Payments / Paiements clients Cash**

Clover is used to process:

- Pre-authorizations
- Purchases / payments
- Refunds

For a standard cash customer service call:

```text
$750 Pre-Authorization
```

must be obtained before sending the technician to site.

For an accepted cash customer quotation:

```text
Full quoted amount = Payment
```

Do **not** use a pre-authorization for an accepted cash quotation.

After processing a pre-authorization or payment:

1. Retrieve the transaction.
2. Open **Details**.
3. Select **View Payment Receipt**.
4. Record the **Authorization ID**.
5. Enter the Authorization ID as the **PO number on the BMS Work Order**.
6. Save the receipt as a PDF and send it to the customer.

### French Retrieval Concepts

- Clover
- Terminal virtuel Clover
- Paiement client Cash
- Préautorisation
- Préautorisation de 750 $
- Paiement carte de crédit
- Paiement d'une soumission
- Numéro d'autorisation
- ID d'autorisation
- Reçu de paiement
- PO dans BMS

---

# Accessing Clover

Go to:

```text
www.clover.com
```

Log in using your Cummins email address:

```text
WWID@cummins.com
```

and your Clover password.

---

# Virtual Terminal

From the Clover dashboard:

1. Open the appropriate branch.
2. Select **Virtual Terminal**.
3. Select the appropriate **Transaction Type**.

The Virtual Terminal is used to process:

- Pre-Authorizations
- Purchases
- Refunds

---

# Pre-Authorization

For a standard cash customer service call, obtain a:

```text
$750 Pre-Authorization
```

before sending the technician to the customer site.

To process the pre-authorization:

1. Select **Pre-Authorization** from the Transaction Type drop-down.
2. Enter the pre-authorization amount.
3. Add additional allowance for potential applicable fees when required.
4. Enter the customer's payment information.
5. Select **Pre-Authorize Payment**.

---

# Accepted Cash Quotation

When a cash customer accepts a quotation:

**Do not perform a pre-authorization.**

Collect payment for the:

```text
Full Quotation Amount
```

The payment must be received before proceeding with the accepted cash quotation workflow.

The payment must then be reserved against the Work Order using the applicable **Customer Deposit / Order Entry (OE) process**.

---

# Retrieving the Transaction Receipt

After processing a pre-authorization or payment:

1. Retrieve the transaction.
2. Select **Details**.
3. Select **View Payment Receipt**.

Do not use:

```text
Send Receipt
```

as this function is not working according to the original Clover training procedure.

Save the receipt as a PDF and send it to the customer.

---

# Authorization ID

Retrieve the **Authorization ID** from the payment receipt.

Enter the Authorization ID as the:

```text
PO Number
```

on the corresponding BMS Work Order.

For a service call, the pre-authorization must be completed before the technician is sent to site.

---

# Customer Profiles

It is recommended to create a Clover profile for new cash customers so their credit card information can be saved for future transactions.

Saved payment information is available only within the branch where the transaction/profile was created.

When creating a customer profile, append the customer's **BMS account number** to their last name.

Example:

```text
Brisson12345
```

---

# Pre-Authorization Expiration

When the customer's payment information is not saved, pre-authorizations expire after:

```text
2 Weeks
```

If a required part will take longer than two weeks to arrive, add a note such as:

```text
Contact the customer for payment once the order is ready.
```

---

## Official SharePoint Guide / Guide SharePoint officiel

The official SharePoint document for **Clover Training** contains the complete visual procedure, including screenshots of the Clover login, Virtual Terminal, transaction processing, payment receipt, Authorization ID, and cash quotation workflow.

Le document SharePoint officiel de **formation Clover** contient la procédure visuelle complète avec les captures d'écran nécessaires.

**Official SharePoint Link:**

[Open the Clover Training Guide](https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQAXG1oUf57mSpIvTuqMf0TkAcmgDeixwFPSC-v8kCWVnNI?e=FfK8F2)

### Link Retrieval Rule / Règle de récupération du lien

When a user asks for the **Clover procedure link, SharePoint link, source document, original training document, official document, visual guide, screenshots, or Clover training material**, provide the **Official SharePoint Link above**.

Lorsqu'un utilisateur demande le **lien Clover, lien SharePoint, document source, document original, document de formation, guide visuel, captures d'écran ou procédure Clover**, fournir le **lien SharePoint officiel ci-dessus**.

Examples of requests that should return this link:

**English**
- Give me the Clover procedure.
- Do you have the Clover SharePoint link?
- Show me the Clover training document.
- Where is the visual Clover guide?
- Give me the original Clover procedure.

**Français**
- Donne-moi la procédure Clover.
- As-tu le lien SharePoint pour Clover?
- Donne-moi le document de formation Clover.
- Où est le guide visuel Clover?
- As-tu un lien pour cette procédure?

---

## Search Terms / Termes de recherche

**English:** Clover, Clover training, Virtual Terminal, cash customer payment, credit card payment, pre-authorization, $750 pre-authorization, accepted cash quotation, payment receipt, Authorization ID, Clover PO, Clover customer profile.

**Français:** Clover, formation Clover, terminal virtuel, client Cash, paiement client Cash, paiement carte de crédit, préautorisation, préautorisation 750 $, soumission Cash acceptée, reçu Clover, numéro d'autorisation, ID d'autorisation, PO Clover, profil client Clover.