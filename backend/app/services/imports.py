from __future__ import annotations

from datetime import datetime
from html import unescape
from io import BytesIO
import re

import pandas as pd
from sqlalchemy.orm import Session

from ..models import Ticket
from ..schemas import ImportSummary


CSV_TO_MODEL_MAP = {
    "ticket_number": "vendor_ticket_id",
    "date_created": "vendor_created_date",
    "subject": "vendor_subject",
    "from": "vendor_from_name",
    "from_email": "vendor_from_email",
    "priority": "vendor_priority",
    "department": "vendor_department",
    "help_topic": "vendor_help_topic",
    "source": "vendor_source",
    "current_status": "vendor_status",
    "last_updated": "vendor_last_updated",
    "sla_due_date": "vendor_sla_due_date",
    "sla_plan": "vendor_sla_plan",
    "due_date": "vendor_due_date",
    "closed_date": "vendor_closed_date",
    "overdue": "vendor_overdue",
    "agent_assigned": "vendor_agent_assigned",
    "issue_category": "vendor_issue_category",
}

DATE_COLUMNS = {
    "vendor_created_date",
    "vendor_last_updated",
    "vendor_sla_due_date",
    "vendor_due_date",
    "vendor_closed_date",
}

BOOL_COLUMNS = {"vendor_overdue"}
REQUIRED_COLUMNS = {"ticket_number", "date_created", "subject", "current_status"}


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


def parse_date(value: object) -> datetime | None:
    text = clean_text(value)
    if text is None:
        return None
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


def merge_csv(db: Session, contents: bytes) -> ImportSummary:
    dataframe = parse_upload(contents)
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        missing_display = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV is missing required columns: {missing_display}")

    created = 0
    updated = 0
    failed = 0
    errors: list[str] = []

    for row_index, row in dataframe.iterrows():
        try:
            payload: dict[str, object] = {}

            for csv_column, model_column in CSV_TO_MODEL_MAP.items():
                if csv_column not in dataframe.columns:
                    continue

                raw_value = row[csv_column]
                if model_column in DATE_COLUMNS:
                    payload[model_column] = parse_date(raw_value)
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
        except Exception as exc:  # pragma: no cover - defensive error collection
            failed += 1
            errors.append(f"Row {row_index + 2}: {exc}")

    db.commit()
    return ImportSummary(new=created, updated=updated, failed=failed, errors=errors)
