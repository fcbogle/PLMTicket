# AGENTS.md

## Project Name

PLM Ticket Manager

---

## Project Purpose

Build a web application to manage PLM support tickets received from an external PLM support provider.

The application will:

- allow upload of CSV files from a local machine
- import and persist vendor ticket data
- support a small, configurable set of internal enrichment fields
- generate a clean, formatted Excel workbook for review

The system is intentionally designed to **start simple and evolve over time**.

---

## Core Design Principles

1. **Start small, scale safely**
   - Begin with a minimal dataset and expand as needed

2. **Separate vendor vs internal data**
   - Vendor data = imported from CSV
   - Internal data = user-managed, never overwritten

3. **Excel is output, not storage**
   - Database is the system of record

4. **Local-first simplicity**
   - CSV upload from user machine
   - No dependency on external integrations initially

---

## MVP Scope (Critical)

The first version of the system should ONLY include:

- CSV upload from local machine
- Ticket import and merge logic
- Small number of internal enrichment fields
- Basic ticket list UI
- Excel export

Avoid overengineering early.

---

## Key Use Cases

### 1. Upload CSV from Local Machine

User uploads a CSV file via the UI.

Backend should:

- accept file upload
- validate structure
- parse CSV
- process ticket records
- return summary (new / updated / failed)

---

### 2. Import and Merge Tickets

System behaviour:

- Identify tickets using a unique key (vendor_ticket_id)
- Insert new tickets
- Update vendor fields for existing tickets (if needed)
- Preserve ALL internal fields

---

### 3. Maintain Minimal Enrichment Fields (MVP)

Start with a small set of fields:

- issue_category
- root_cause
- training_required (boolean)
- user_error (boolean)
- internal_status
- internal_owner
- comments

These fields should be:

- editable in UI
- stored in database
- preserved across imports

⚠️ Important:
Design must allow easy addition of new fields later without breaking structure.

---

### 4. View and Filter Tickets

UI should support:

- basic table view
- search by ticket ID or text
- filtering by:
  - status
  - category
  - training_required
  - user_error

---

### 5. Generate Excel Output

User triggers export.

Output:

- clean formatted workbook
- suitable for management review

MVP sheets:

1. All Tickets
2. Open Tickets
3. Training Required

---

## Architecture

### Frontend

- React + TypeScript
- Simple UI (no heavy frameworks required initially)
- File upload component
- Table view for tickets
- Basic edit form

---

### Backend

- FastAPI
- Pandas (CSV parsing)
- SQLAlchemy
- OpenPyXL (Excel export)

Responsibilities:

- file upload handling
- CSV parsing
- merge logic
- database operations
- Excel generation

---

### Database

Use:

- SQLite (MVP)

Future:

- PostgreSQL (Azure deployment)

---

## Data Model (MVP)

### Ticket Table

#### Vendor Fields (from CSV)

- vendor_ticket_id
- title
- description
- created_by
- created_date
- resolved_date
- vendor_status
- resolution_notes

#### Internal Fields (MVP only)

- internal_status
- internal_owner
- issue_category
- root_cause
- training_required
- user_error
- comments

#### Metadata

- created_at
- updated_at

---

## CSV Import Rules

- CSV is uploaded manually from local machine
- File is processed immediately
- No automatic scheduling required
- No external system integration required

Matching logic:

- Use vendor_ticket_id as unique key

Behaviour:

- new ticket → insert
- existing ticket → update vendor fields only
- NEVER overwrite internal fields

---

## API Endpoints (MVP)

```text
POST   /imports/csv        # upload CSV file
GET    /tickets            # list tickets
GET    /tickets/{id}       # ticket detail
PATCH  /tickets/{id}       # update enrichment fields
GET    /exports/excel      # generate Excel report
