from __future__ import annotations

import argparse
from datetime import datetime
from html import unescape
from io import BytesIO
from pathlib import Path
import re
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.database import SessionLocal
from backend.app.models import Ticket
from backend.app.schemas import ImportSummary
from backend.app.services.imports import BOOL_COLUMNS, CSV_TO_MODEL_MAP, DATE_COLUMNS


def normalize_header(value: str) -> str:
    cleaned = value.replace("\ufeff", "").strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return re.sub(r"_+", "_", cleaned).strip("_")


def clean_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    return unescape(text)


def parse_date_dayfirst(value: object) -> datetime | None:
    text = clean_text(value)
    if text is None:
        return None

    iso_match = re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?", text)
    if iso_match:
        parsed = pd.to_datetime(text, format="mixed", errors="coerce")
    else:
        parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")

    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def parse_bool(value: object) -> bool | None:
    text = clean_text(value)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in {"yes", "true", "1"}:
        return True
    if lowered in {"no", "false", "0"}:
        return False
    return None


def parse_upload(contents: bytes) -> pd.DataFrame:
    dataframe = pd.read_csv(BytesIO(contents), encoding="utf-8-sig")
    dataframe.columns = [normalize_header(str(column)) for column in dataframe.columns]
    return dataframe


def merge_csv_dayfirst(contents: bytes) -> ImportSummary:
    dataframe = parse_upload(contents)
    created = 0
    updated = 0
    failed = 0
    errors: list[str] = []

    db = SessionLocal()
    try:
        for row_index, row in dataframe.iterrows():
            try:
                payload: dict[str, object] = {}

                for csv_column, model_column in CSV_TO_MODEL_MAP.items():
                    if csv_column not in dataframe.columns:
                        continue

                    raw_value = row[csv_column]
                    if model_column in DATE_COLUMNS:
                        payload[model_column] = parse_date_dayfirst(raw_value)
                    elif model_column in BOOL_COLUMNS:
                        payload[model_column] = parse_bool(raw_value)
                    else:
                        payload[model_column] = clean_text(raw_value)

                ticket_id = payload.get("vendor_ticket_id")
                if not ticket_id:
                    raise ValueError("Missing ticket_number")

                payload["vendor_description"] = payload.get("vendor_subject")

                existing = db.query(Ticket).filter(Ticket.vendor_ticket_id == ticket_id).one_or_none()
                if existing is None:
                    db.add(Ticket(**payload))
                    created += 1
                else:
                    for field, value in payload.items():
                        setattr(existing, field, value)
                    updated += 1
            except Exception as exc:
                failed += 1
                errors.append(f"Row {row_index + 2}: {exc}")

        db.commit()
    finally:
        db.close()

    return ImportSummary(new=created, updated=updated, failed=failed, errors=errors)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reimport a vendor CSV with day-first slash-date parsing for legacy files.")
    parser.add_argument("csv_path", help="Absolute or relative path to the vendor CSV file")
    args = parser.parse_args()

    path = Path(args.csv_path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"CSV file not found: {path}")

    result = merge_csv_dayfirst(path.read_bytes())
    print(f"Imported with day-first parsing: {path}")
    print(result.model_dump())


if __name__ == "__main__":
    main()
