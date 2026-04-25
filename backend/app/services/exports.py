from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy.orm import Session

from ..models import Ticket


EXPORT_COLUMNS = [
    ("Ticket ID", "vendor_ticket_id"),
    ("Subject", "vendor_subject"),
    ("Vendor Status", "vendor_status"),
    ("Internal Status", "internal_status"),
    ("Internal Owner", "internal_owner"),
    ("Vendor Issue Category", "vendor_issue_category"),
    ("Issue Category", "issue_category"),
    ("Root Cause", "root_cause"),
    ("From", "vendor_from_name"),
    ("From Email", "vendor_from_email"),
    ("Help Topic", "vendor_help_topic"),
    ("Priority", "vendor_priority"),
    ("Created Date", "vendor_created_date"),
    ("Closed Date", "vendor_closed_date"),
    ("Comments", "comments"),
]


def is_open_ticket(ticket: Ticket) -> bool:
    return (ticket.vendor_status or "").strip().lower() != "closed"


def is_training_related(ticket: Ticket) -> bool:
    values = [ticket.issue_category, ticket.vendor_issue_category]
    normalized = " ".join(value.lower() for value in values if value)
    return "training" in normalized


def write_sheet(workbook: Workbook, title: str, tickets: list[Ticket]) -> None:
    sheet = workbook.create_sheet(title)
    headers = [column_title for column_title, _ in EXPORT_COLUMNS]
    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for ticket in tickets:
        sheet.append([getattr(ticket, field_name) for _, field_name in EXPORT_COLUMNS])

    for column_cells in sheet.columns:
        values = [str(cell.value or "") for cell in column_cells]
        max_length = min(max(len(value) for value in values) + 2, 40)
        sheet.column_dimensions[column_cells[0].column_letter].width = max_length


def build_excel_report(db: Session) -> bytes:
    tickets = db.query(Ticket).order_by(Ticket.vendor_created_date.desc()).all()

    workbook = Workbook()
    workbook.remove(workbook.active)

    write_sheet(workbook, "All Tickets", tickets)
    write_sheet(workbook, "Open Tickets", [ticket for ticket in tickets if is_open_ticket(ticket)])
    write_sheet(workbook, "Training Related", [ticket for ticket in tickets if is_training_related(ticket)])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.read()
