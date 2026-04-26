# PLM Ticket Manager

MVP scaffold for importing PLM vendor tickets from CSV, preserving internal enrichment fields, and exporting an Excel workbook.

## Python Version

This project is pinned to `Python 3.11.11` via `.python-version`.

## Environment Variables

Backend:

- `PLM_DATABASE_URL`
- `PLM_CORS_ALLOWED_ORIGINS`

Frontend:

- `VITE_API_BASE_URL`

Defaults:

- local backend database: `sqlite:///./plm_tickets.db`
- local frontend API base URL: `http://localhost:8000`

## Backend

```bash
cd backend
../.venv/bin/pip install -r requirements.txt
../.venv/bin/uvicorn app.main:app --reload
```

API base URL: `http://localhost:8000`

Example backend environment:

```bash
PLM_DATABASE_URL=sqlite:///./plm_tickets.db
PLM_CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Endpoints:

- `POST /imports/csv`
- `GET /tickets`
- `GET /tickets/{id}`
- `PATCH /tickets/{id}`
- `GET /exports/excel`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Example frontend environment:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## CSV Notes

- Headers are normalized to snake_case during import.
- CSVs are read using `utf-8-sig` to handle BOM-prefixed files.
- Vendor fields are re-imported on each upload.
- Internal fields are preserved across imports.
