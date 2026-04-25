# Deployment And Data Migration

## 1. Purpose

This document explains how application code and application data should be handled during deployment.

## 2. Key Principle

Code deployment and data deployment are separate activities.

The application code can be deployed without the current local ticket data unless a separate data migration step is carried out.

## 3. Current Local Data Location

Current local database:

- `backend/plm_tickets.db`

This SQLite database currently contains:

- imported vendor ticket data
- internal status updates
- internal ownership assignments
- issue categories
- root cause entries
- comments

## 4. What Happens If Nothing Is Migrated

If the application is deployed with a fresh empty database:

- the deployed application will not contain the locally enriched tickets
- user-entered classifications and comments will not appear
- the system will behave like a new environment

## 5. Recommended Deployment Approach

### 5.1 Initial MVP Deployment

For a first deployment, one of these approaches should be used:

- move the current SQLite database into the deployed environment
- export the ticket data and import it into the deployment database

### 5.2 Preferred Production Direction

For production use, the preferred direction is:

- PostgreSQL as the deployment database
- a one-time migration of the current SQLite ticket data

## 6. Migration Requirements

Any migration approach must preserve:

- `vendor_ticket_id`
- vendor ticket fields
- internal fields entered by users
- record timestamps where possible

Special requirement:

- internal enrichment fields must remain linked to the correct `vendor_ticket_id`

## 7. Suggested Deployment Sequence

1. Freeze local updates during the final migration window.
2. Back up the local SQLite database.
3. Prepare the target deployment database.
4. Load the current ticket data into the target environment.
5. Deploy the application code.
6. Validate that a sample of enriched tickets is present.
7. Resume normal use in the deployed environment.

## 8. Minimum Validation After Migration

Check:

- total ticket count
- known sample ticket IDs
- known internal status values
- known issue categories
- known comments on selected tickets
- Excel export from the deployed environment

## 9. Risks

- deploying code without data migration
- overwriting newer ticket data with an older backup
- losing internal comments or classifications during migration
- moving to production without validation of sample records

## 10. Recommended Immediate Actions

- keep using the local database as the working system of record during MVP
- create a backup routine for `backend/plm_tickets.db`
- decide whether first deployment will use SQLite or PostgreSQL
- define a simple promotion checklist before go-live
