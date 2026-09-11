# Customer Invoice Credit Procedure

# Last Updated: 2026-09-02

## Purpose

This procedure explains how to create a **credit against an already invoiced customer Work Order in BMS**.

The credit is created through **Order Entry** using transaction type `WOCM`.

## Objectif

Cette procédure explique comment effectuer un **crédit sur une facture client déjà facturée dans BMS**.

Le crédit est créé dans **Order Entry** en utilisant le type de transaction `WOCM`.

---

## Quick Reference / Référence rapide

**Customer Invoice Credit / BMS Credit / Crédit de facture client**

For a Service Work Order credit:

- Open **Order Entry**.
- Use transaction type `WOCM`.
- Set **Pick Up** to `Y`.
- Set **Ship Via** to `EM`.
- Enter the applicable customer and unit information.
- Add parts through the Parts Department when required.
- Enter labor, mileage, and applicable parts credits under **Charges**.
- Credit amounts must be entered as **negative values before taxes**.
- Document the invoice reference and reason for the credit under **Comments**.
- Complete the credit through **Total Order**.

### French Retrieval Concepts

- Crédit client
- Crédit facture
- Crédit de facture client
- Faire un crédit dans BMS
- Crédit BMS
- Crédit sur bon de travail
- Crédit sur Work Order
- Facture déjà facturée
- WOCM
- Order Entry
- Labor Rebill
- Crédit kilométrage
- Crédit pièces
- Montant négatif
- Annuler montant facture
- Corriger facture client

---

# Open Order Entry

In BMS, open:

```text
Parts - Customer Care
→ Maintain Customer Orders
→ Order Entry
```

If **Order Entry** is already available in Favorites, it can be opened directly.

---

# Complete the Order Information

Enter the applicable customer and credit information.

Use:

| Field | Value |
|---|---|
| Bill To | Customer account |
| Transaction Type | `WOCM` |
| Pick Up | `Y` |
| Contact | Contact for the credit |
| Ship Via | `EM` |
| Unit | Customer unit number |

Press **F10** after entering the unit information.

---

# Parts

Open the **Items** tab.

If parts must be included in the credit:

- Contact the **Parts Department**.
- Provide the **Order Reference Number** displayed in the Order Entry.
- The Parts Department must add the applicable parts to the credit.

---

# Enter the Credit Amounts

Open the:

```text
Charges
```

tab.

Enter the applicable credit lines, including:

- **Labor Rebill**
- Mileage
- Parts, when applicable

Travel time is included under **Labor Rebill**.

> **Important**
>
> All credit amounts must be entered as **negative values**.
>
> Enter the amounts **before taxes**. Applicable taxes are added/calculated afterward.

Press **F10** to save.

---

# Document the Credit

Open the:

```text
Comments
```

tab.

Use:

```text
Comment Type: Standard
```

Document:

- The invoice being credited.
- The reason for the credit.
- Your WWID for reference.

Example:

```text
IN REFERENCE TO INVOICE XXXXXXX

Credit issued for [reason].

WWID: XXXXX
```

---

# Distributor Comment

Add another comment using:

```text
Comment Type: Distributor
Reason: Other
```

Enter:

```text
.
```

as the comment.

---

# Complete the Credit

Select:

```text
Total Order
```

Enter or verify:

- Original invoice reference number.
- Invoice total.
- Purchase Order number, when applicable.
- Invoice Security Code.

Confirm that the credit amounts are correct.

Then select:

```text
Invoice
```

to complete the credit.

---

## Official SharePoint Guide / Guide SharePoint officiel

The official SharePoint document for the **Customer Invoice Credit Procedure** contains the complete visual BMS procedure, including screenshots showing Order Entry, customer information, Items, Charges, Comments, and Total Order.

Le document SharePoint officiel de la **procédure de crédit de facture client** contient la procédure visuelle complète dans BMS avec les captures d'écran nécessaires.

**Official SharePoint Link:**

[Open the Customer Invoice Credit Guide](https://cummins365-my.sharepoint.com/:w:/g/personal/ud016_cummins_com/IQCjUcGkP6qdQol5qSFmscP2ATiaaYAbSjtXoLPb98bHZY8?e=kuvK1l)

### Link Retrieval Rule / Règle de récupération du lien

When a user asks for the **customer invoice credit procedure, BMS credit procedure, WOCM procedure, SharePoint link, source document, original document, official guide, visual guide, or screenshots**, provide the **Official SharePoint Link above**.

Lorsqu'un utilisateur demande la **procédure de crédit client, procédure de crédit de facture, procédure WOCM, lien SharePoint, document source, document original, guide officiel, guide visuel ou captures d'écran**, fournir le **lien SharePoint officiel ci-dessus**.

Examples of requests that should return this link:

**English**
- How do I credit a customer invoice?
- Give me the BMS credit procedure.
- How do I create a WOCM?
- Do you have the SharePoint link?
- Show me the visual credit procedure.

**Français**
- Comment faire un crédit sur une facture?
- Comment faire un crédit dans BMS?
- Donne-moi la procédure WOCM.
- As-tu le lien SharePoint?
- Où est le guide visuel pour les crédits?
- Donne-moi la procédure de crédit client.

---

## Search Terms / Termes de recherche

**English:** customer credit, invoice credit, customer invoice credit, credit invoice BMS, BMS credit, WOCM, Order Entry credit, Labor Rebill, mileage credit, parts credit, negative amount, credit Work Order.

**Français:** crédit client, crédit facture, crédit de facture client, faire crédit BMS, crédit BMS, WOCM, Order Entry, crédit bon de travail, crédit WO, Labor Rebill, crédit kilométrage, crédit pièces, montant négatif.