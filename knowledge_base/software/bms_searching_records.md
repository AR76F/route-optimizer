# BMS - Searching Records

# Last Updated: 2026-09-03

## Purpose

This document explains the different methods available for **searching customers, work orders, work order history, and other records within BMS**.

Searching efficiently allows Service Coordinators to quickly retrieve customer information, previous service history, invoices, and work orders.

## Objectif

Ce document explique les différentes méthodes disponibles dans BMS pour rechercher des clients, des bons de travail, l’historique des travaux et d’autres dossiers.

Une recherche efficace permet aux coordonnateurs de service de retrouver rapidement les renseignements sur les clients, l’historique des travaux, les factures et les bons de travail.

---

## French Retrieval Metadata

**French Title:** BMS - Recherche de dossiers

**French Keywords:** recherche BMS, rechercher dans BMS, recherche client BMS, trouver client BMS, numéro client BMS, rechercher bon de travail, rechercher work order, recherche WO, historique client BMS, historique travaux client, Service Lookup, Work Order Query, recherche facture BMS, numéro de facture, numéro de bon de commande, purchase order, recherche par superviseur, recherche F7 F8, mode Query BMS, recherche avec pourcentage BMS, wildcard BMS, recherche avec %, trouver ancien bon de travail

**French Retrieval Phrases:**
- Comment faire une recherche dans BMS?
- Comment rechercher un client dans BMS?
- Comment trouver un numéro de client dans BMS?
- Comment trouver un bon de travail dans BMS?
- Comment rechercher un ancien work order?
- Comment voir l'historique d'un client dans BMS?
- Comment voir les anciens travaux d'un client?
- Comment utiliser Service Lookup dans BMS?
- Comment utiliser Work Order Query dans BMS?
- Comment rechercher avec F7 et F8 dans BMS?
- Comment rechercher une facture dans BMS?
- Comment rechercher avec un numéro de facture?
- Comment rechercher avec un numéro de bon de commande?
- Comment rechercher par numéro de téléphone dans BMS?
- Comment utiliser le symbole % pour une recherche dans BMS?
- Comment retrouver les anciens travaux effectués pour un client?

---

# Search Methods

BMS provides two primary methods for searching information:

1. **Service Lookup**
2. **Work Order Query**

Each method serves a different purpose.

---

# Service Lookup

The **Service Lookup** tool is used to locate:

- Customer Numbers
- Work Orders
- Work Order Quotes (WOQT)
- Invoices
- Customer Work History

---

## Finding a Customer Number

Open:

```text
Service Lookup
```

Under the **Work Orders** section:

1. Select the **binoculars** beside **Customer**.
2. Open **Customer Lookup**.
3. Search using one of the following:

- Customer Name
- Phone Number
- Site Address

### Wildcard Searches

Use the **%** symbol before and after the search value.

Examples:

```text
%CUMMINS%

%6836863%
```

Once the customer has been located:

- Record the Customer Number for future reference.

> **Best Practice**
>
> Whenever possible, search using the customer's phone number to reduce duplicate results.

---

## Viewing Customer Work History

To retrieve a customer's service history:

Open:

```text
Service Lookup
```

Configure the search:

| Field | Value |
|--------|-------|
| Query | All Work Orders |
| Order By | Create Date |

Next:

1. Select the **binoculars** beside **Customer**.
2. Open **Customer Lookup**.
3. Enter the Customer Number in the **Identifier** field.
4. Select the customer.

BMS will display all available work orders associated with every unit owned by that customer.

This information can be used to:

- Review previous repairs.
- Check historical operating hours.
- Review technician notes.
- Verify previous invoices.
- Confirm recurring issues.

---

# Work Order Search

The Work Order window provides another method of searching records.

Open a:

```text
Work Order
```

window.

---

## Enter Query Mode

Press:

```text
F7
```

All searchable fields will become **white**, indicating that BMS has entered Query Mode.

---

## Search Criteria

You may search using any of the following:

- Work Order Number
- Invoice Number
- Customer Number
- Phone Number
- Purchase Order Number
- Supervisor Name
- Market Segment

Enter the appropriate value into the corresponding field.

---

## Execute the Search

Press:

```text
F8
```

to execute the query.

BMS will retrieve all matching records.

---

# SharePoint Resource

A visual reference for BMS record searching is available on SharePoint.

**Resource:** [BMS Searching Records - Visual Guide](https://cummins365.sharepoint.com/:p:/s/GRP_CC40846-AdministrationFSPG/IQCH9dgGQAjHS4al0EBw844xAewQEJ4ObAt0rLJJxMAMpcw?e=zxZ94e)

> **Note**
>
> The SharePoint slides are intended as a visual reference only. This document contains the more detailed procedure and should be used as the primary reference for BMS record searching.

---

# Choosing the Right Search Method

| If you need to... | Use |
|-------------------|-----|
| Find a Customer Number | Service Lookup |
| Review customer service history | Service Lookup |
| Find an existing Work Order | Work Order Query |
| Search by Invoice Number | Work Order Query |
| Search by Customer Number | Work Order Query |
| Search by Purchase Order | Work Order Query |
| Search by Supervisor | Work Order Query |

---

# Best Practices

- Use **Service Lookup** whenever customer history is required.
- Use **Work Order Query** when searching for a specific work order or invoice.
- Use wildcard (%) searches whenever the full customer name is unknown.
- Record the Customer Number before beginning other procedures.
- Sort customer history by **Create Date** when reviewing recent service activity.

---

# Common Mistakes

## Forgetting Wildcards

Searching for:

```text
CUMMINS
```

may return no results.

Instead use:

```text
%CUMMINS%
```

---

## Searching the Wrong Window

Use **Service Lookup** for customer history.

Use **Work Order Query** for work order-specific searches.

---

## Not Entering Query Mode

Always press:

```text
F7
```

before entering search criteria in the Work Order window.

---

## Forgetting to Execute the Query

After entering search criteria:

Press:

```text
F8
```

to retrieve matching records.

---