# FieldAware - Work Order Creation and Scheduling

# Last Updated: 2026-09-03

## Purpose

This procedure explains how to open a BMS-synchronized job in FieldAware, assign the technician, schedule the appointment, assign the required reports, and verify the Scheduler.

Use [BMS - Work Order Creation](bms_work_order_creation.md) for creating and updating the BMS Work Order and synchronizing it with FieldAware.

## Objectif

Cette procédure explique comment ouvrir dans FieldAware un bon de travail synchronisé à partir de BMS, assigner le technicien, planifier le rendez-vous, assigner les rapports requis et vérifier l’horaire.

Consultez [BMS - Work Order Creation](bms_work_order_creation.md) pour créer et modifier le bon de travail dans BMS et le synchroniser avec FieldAware.

## Quick Reference / Référence rapide

```text
Send to FA from BMS
        ↓
Search the FA Job ID
        ↓
Assign technician as Job Lead
        ↓
Enter date, time, and duration
        ↓
Assign Field Service Basic + RFQ
        ↓
Remove unnecessary reports
        ↓
Assign the technician to every report
        ↓
Save and verify the Scheduler
```

### French Retrieval Metadata

**Création bon de travail FieldAware / assignation technicien / FA Job ID / équipage / Crew / Job Lead / plage horaire / durée / Field Service Basic / Request for Quote / RFQ / horaire / Scheduler / Send to FA**

## SharePoint Visual Reference

The visual FieldAware Work Order and scheduling guide is maintained on SharePoint.

**SharePoint Link:** `[https://cummins365.sharepoint.com/:w:/s/GRP_CC40846-AdministrationFSPG/IQCcmEd76zjeR7XR3WNcjws4AadxFMUGVutzWuWtpsWUfCk?e=7gMrna]`

The Markdown procedure is the detailed text reference; the visual guide is supplemental.

# 1. Synchronize the BMS Work Order

Before opening FieldAware, confirm that the BMS Work Order is complete and saved.

Select:

```text
Send to FA
```

Use **Send to FA** again after every material BMS change. Unsynchronized changes may be overwritten when the technician updates the job.

The **FA Job ID** is generated or displayed after synchronization. Record it for the FieldAware search and related paperwork.

# 2. Open the FieldAware Job

1. Open [FieldAware](https://auth.fieldaware.com/).
2. Sign in with the Cummins email address and WWID when prompted.
3. Open the search tool, represented by the magnifying-glass icon.
4. Enter the FA Job ID from BMS.
5. When required, you may omit the leading `J` from the numeric search value. For example, search `189853` for `J189853`.
6. Select **Search**.
7. Open the corresponding job and confirm the customer and job number.

## Job Description Check

Confirm that the FieldAware job description matches the BMS Complaint and clearly describes the customer’s issue.

If it is incorrect:

1. Correct the Complaint in BMS.
2. Select **Send to FA**.
3. Refresh or reopen the FieldAware job.

# 3. Assign the Technician

1. Scroll to **Crew**.
2. Select the appropriate technician.
3. Select **Add Member**.
4. Confirm that the technician is assigned as **Job Lead**.

The technician must be the appropriate person for the work and site. Use [Technician Selection Rules](../technicians/tech_selection_rules.md) when choosing the technician.

If multiple technicians are assigned, confirm which technician is the Job Lead and manually assign each required report as described below.

# 4. Schedule the Appointment

Enter:

- Appointment date.
- Start time.
- End time.
- Duration.

For a standard service-call example, confirm that **Duration** is **4 hours**. Do not assume the automatically populated duration is correct without checking it.

The proposed appointment must match the customer-approved time slot and account for travel, parts availability, technician workload, and any site restrictions.

# 5. Assign the Reports

The current standard report framework is:

- **Field Service Basic**
- **Request for Quote (RFQ)**

Assign additional reports only when the work requires them.

Remove unnecessary reports from the job.

## Report Assignment Rule

Every required report must have the appropriate technician assigned.

When only one technician is assigned, FieldAware may assign reports automatically. When more than one technician is assigned, verify each report manually and ensure that no required report remains unassigned.

# 6. Save and Verify the Scheduler

1. Select **Save** after the technician, schedule, and reports are complete.
2. Open the **Scheduler**.
3. Confirm the job appears under the correct technician.
4. Verify the date, start time, end time, and duration.
5. Confirm that the Job Lead and required reports are correct.

Never assume that a job is scheduled until it appears correctly in the Scheduler.

## Save Failure

If FieldAware does not save the job:

1. Refresh FieldAware.
2. Reopen the work order.
3. Re-enter or verify the changed information.
4. Select **Save** again.
5. Recheck the Scheduler.

# 7. Completion Checklist

- BMS Work Order was synchronized with **Send to FA**.
- Correct FA Job ID was located.
- Customer and job description were verified.
- Appropriate technician was added to Crew.
- Technician was assigned as Job Lead.
- Date, start time, end time, and duration were verified.
- **Field Service Basic** was assigned.
- **Request for Quote (RFQ)** was assigned when required.
- Unnecessary reports were removed.
- Every required report was assigned to the appropriate technician.
- Job was saved successfully.
- Job appeared correctly in the Scheduler.

## Common Mistakes

- Searching with the wrong FA Job ID or including the `J` prefix when it must be omitted.
- Forgetting to assign a Job Lead.
- Leaving a required report without an assigned technician.
- Forgetting to verify the four-hour duration for a standard service call.
- Failing to remove unnecessary reports.
- Forgetting to select **Send to FA** after a BMS change.
- Assuming a save succeeded without checking the Scheduler.

## Related Documents

- [BMS - Work Order Creation](bms_work_order_creation.md)
- [BMS - Unit Creation](bms_unit_creation.md)
- [BMS - Site Creation](bms_site_creation.md)
- [Service Call Management](../procedures/service_call_management.md)
- [Technician Selection Rules](../technicians/tech_selection_rules.md)
- [FieldAware Prioritization Indication](fieldaware_prioritization_indication.md)

## Search Terms / Termes de recherche

**English:** FieldAware work order, assign technician, FA Job ID, Job Lead, Crew, scheduler, time slot, duration, Field Service Basic, Request for Quote, RFQ, assign report, Send to FA, FieldAware save failure.

**Français:** bon de travail FieldAware, assigner un technicien, numéro FA Job ID, chef d’équipe, Crew, horaire, plage horaire, durée, Field Service Basic, demande de soumission, RFQ, assigner un rapport, Send to FA, échec de sauvegarde FieldAware.
