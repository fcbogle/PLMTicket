# PLM Ticket Manager

MVP scaffold for importing PLM vendor tickets from CSV, preserving internal enrichment fields, and exporting an Excel workbook.

## Python Version

This project is pinned to `Python 3.11.11` via `.python-version`.

## Backend

```bash
cd backend
../.venv/bin/pip install -r requirements.txt
../.venv/bin/uvicorn app.main:app --reload
```

API base URL: `http://localhost:8000`

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

## CSV Notes

- Headers are normalized to snake_case during import.
- CSVs are read using `utf-8-sig` to handle BOM-prefixed files.
- Vendor fields are re-imported on each upload.
- Internal fields are preserved across imports.
