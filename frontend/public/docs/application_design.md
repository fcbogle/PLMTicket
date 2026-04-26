# PLM Ticket Manager Application Design

## 1. Purpose

PLM Ticket Manager is a web application for importing external PLM support tickets, preserving internal enrichment data, and exporting management-ready Excel output.

The system is intentionally designed to start small and evolve safely.

## 2. Application Creator

Application creator:

- Frank C Bogle
- Head of Enterprise Solutions
- Blatchford

## 3. Design Goals

- start with a minimal, usable workflow
- separate vendor-managed data from internal user-managed data
- use the database as the system of record
- keep Excel as an output format only
- support repeated vendor CSV imports without losing internal enrichment

## 4. Current MVP Scope

Implemented scope:

- manual CSV upload
- ticket import and merge logic
- internal enrichment fields
- ticket list and detail/edit UI
- Excel export
- local SQLite persistence

Not yet implemented:

- authentication
- audit history
- background jobs or scheduled imports
- production database migration
- configurable enrichment dictionaries from the backend

## 5. High-Level Workflow

1. User uploads a vendor CSV file.
2. Backend parses and normalizes the CSV.
3. Records are matched using `vendor_ticket_id`.
4. Vendor fields are inserted or updated.
5. Internal fields are preserved.
6. User reviews tickets in the UI and enters internal classifications and notes.
7. User exports an Excel workbook from the current database state.

## 6. Architecture

### 6.1 Frontend

Technology:

- React
- TypeScript
- Vite

Responsibilities:

- upload vendor CSV files
- display ticket list and filters
- display selected ticket detail
- edit internal enrichment fields
- provide save feedback
- trigger Excel export

### 6.2 Backend

Technology:

- FastAPI
- SQLAlchemy
- Pandas
- OpenPyXL

Responsibilities:

- accept CSV uploads
- validate and normalize input
- merge vendor data into the database
- preserve internal fields across imports
- expose ticket list and update APIs
- generate Excel workbooks

### 6.3 Database

Current database:

- SQLite

Current local path:

- `backend/plm_tickets.db`

Role:

- authoritative storage for imported vendor data and internal enrichment data

## 7. Data Model

### 7.1 Vendor Fields

- `vendor_ticket_id`
- `vendor_subject`
- `vendor_description`
- `vendor_from_name`
- `vendor_from_email`
- `vendor_priority`
- `vendor_department`
- `vendor_help_topic`
- `vendor_source`
- `vendor_status`
- `vendor_last_updated`
- `vendor_created_date`
- `vendor_sla_due_date`
- `vendor_sla_plan`
- `vendor_due_date`
- `vendor_closed_date`
- `vendor_overdue`
- `vendor_agent_assigned`
- `vendor_issue_category`

### 7.2 Internal Fields

- `internal_status`
- `internal_owner`
- `issue_category`
- `root_cause`
- `comments`

### 7.3 Metadata

- `created_at`
- `updated_at`

## 8. CSV Import Design

### 8.1 CSV Normalization

The importer currently:

- reads BOM-prefixed CSV files
- normalizes headers to snake_case
- parses day-first dates
- handles blank values
- unescapes HTML-encoded text where present

### 8.2 Merge Rules

Match key:

- `vendor_ticket_id`

Behavior:

- insert new tickets
- update vendor-managed fields on existing tickets
- never overwrite internal fields from the CSV

### 8.3 Import Feedback

The import endpoint returns:

- number of new records
- number of updated records
- number of failed records
- row-level error messages

## 9. User Interface Design

### 9.1 Main Layout

The interface is composed of:

- branded header and export action
- import and filter panel
- ticket list panel
- ticket detail and internal entry panel

### 9.2 Current UX Characteristics

- ticket list and detail panel scroll independently
- save operations show in-page success or error feedback
- internal status uses a controlled dropdown
- issue category uses a controlled dropdown
- vendor data remains read-only

## 10. API Design

Current endpoints:

- `POST /imports/csv`
- `GET /tickets`
- `GET /tickets/{id}`
- `PATCH /tickets/{id}`
- `GET /exports/excel`
- `GET /health`

## 11. Persistence Model

All imported and user-entered data is stored in the local database.

Important consequence:

- user changes are persistent locally
- user changes are not automatically carried into deployment unless the database contents are migrated

## 12. Deployment Considerations

The current system is suitable for local development and MVP operation.

For deployment:

- environment configuration must be separated from local development
- data promotion must be planned explicitly
- the long-term target should be PostgreSQL rather than SQLite

Further deployment detail is documented in:

- [deployment_and_data_migration.md](/Users/frankbogle/PycharmProjects/PLM_Tickets/docs/deployment_and_data_migration.md:1)

## 13. Excel Export Position

The exporter is implemented and usable, but its business rules and formatting are not final.

Further export detail is documented in:

- [export_specification.md](/Users/frankbogle/PycharmProjects/PLM_Tickets/docs/export_specification.md:1)

## 14. Current Risks

- SQLite is not the long-term production database
- the export workbook needs further business definition
- controlled dropdown values are currently frontend-defined
- there is no authentication or audit history yet

## 15. Next Logical Enhancements

- move dropdown values into backend-managed configuration
- refine Excel workbook layout and business rules
- add deployment migration tooling
- add authentication and audit trail
- migrate to PostgreSQL for production use
