from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
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

BRAND_PRIMARY = "002A3A"
BRAND_HEADER_BG = "EAF2F4"
LOGO_PATH = Path(__file__).resolve().parents[3] / "frontend" / "public" / "blatchford-mark.jpeg"


def is_open_ticket(ticket: Ticket) -> bool:
    return (ticket.vendor_status or "").strip().lower() != "closed"


def is_workshop_required(ticket: Ticket) -> bool:
    return (ticket.issue_category or "").strip().lower() == "workshop required"


def format_cell_value(value: object) -> object:
    if hasattr(value, "strftime"):
        return value
    return value


def add_sheet_branding(sheet, title: str) -> None:
    last_column = sheet.cell(row=1, column=len(EXPORT_COLUMNS)).column_letter
    sheet.row_dimensions[1].height = 48
    sheet.row_dimensions[2].height = 48
    sheet.merge_cells(f"C1:{last_column}2")

    title_cell = sheet["C1"]
    title_cell.value = f"Blatchford PLM Ticket Manager\n{title}"
    title_cell.font = Font(bold=True, size=16, color="FFFFFF")
    title_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    title_cell.fill = PatternFill(fill_type="solid", fgColor=BRAND_PRIMARY)

    accent_cell = sheet["A1"]
    accent_cell.fill = PatternFill(fill_type="solid", fgColor=BRAND_PRIMARY)
    sheet["A2"].fill = PatternFill(fill_type="solid", fgColor=BRAND_PRIMARY)
    sheet["B1"].fill = PatternFill(fill_type="solid", fgColor=BRAND_PRIMARY)
    sheet["B2"].fill = PatternFill(fill_type="solid", fgColor=BRAND_PRIMARY)
    sheet.column_dimensions["A"].width = 4
    sheet.column_dimensions["B"].width = 16

    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH))
        logo.width = 76
        logo.height = 76
        logo.anchor = OneCellAnchor(
            _from=AnchorMarker(
                col=1,
                colOff=pixels_to_EMU(14),
                row=0,
                rowOff=pixels_to_EMU(26),
            ),
            ext=XDRPositiveSize2D(
                cx=pixels_to_EMU(logo.width),
                cy=pixels_to_EMU(logo.height),
            ),
        )
        sheet.add_image(logo)


def write_sheet(workbook: Workbook, title: str, tickets: list[Ticket]) -> None:
    sheet = workbook.create_sheet(title)
    add_sheet_branding(sheet, title)

    headers = [column_title for column_title, _ in EXPORT_COLUMNS]
    sheet.append([])
    sheet.append(headers)

    for cell in sheet[4]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(fill_type="solid", fgColor=BRAND_HEADER_BG)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for ticket in tickets:
        sheet.append([format_cell_value(getattr(ticket, field_name)) for _, field_name in EXPORT_COLUMNS])

    sheet.freeze_panes = "A5"
    sheet.auto_filter.ref = f"A4:{sheet.cell(row=4, column=len(EXPORT_COLUMNS)).column_letter}{sheet.max_row}"

    for index, column_cells in enumerate(sheet.columns, start=1):
        if index == 1:
            continue
        if index == 2:
            continue
        values = [str(cell.value or "") for cell in column_cells]
        max_length = min(max(len(value) for value in values) + 2, 40)
        sheet.column_dimensions[get_column_letter(index)].width = max_length

    for row in sheet.iter_rows(min_row=5, max_row=sheet.max_row):
        for cell in row:
            if hasattr(cell.value, "strftime"):
                cell.number_format = "DD/MM/YYYY HH:MM"


def build_excel_report(db: Session) -> bytes:
    tickets = db.query(Ticket).order_by(Ticket.vendor_created_date.desc()).all()

    workbook = Workbook()
    workbook.remove(workbook.active)

    write_sheet(workbook, "All Tickets", tickets)
    write_sheet(workbook, "Open Tickets", [ticket for ticket in tickets if is_open_ticket(ticket)])
    write_sheet(workbook, "Workshop Required", [ticket for ticket in tickets if is_workshop_required(ticket)])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.read()
