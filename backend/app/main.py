from io import BytesIO

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Ticket
from .schemas import ImportSummary, TicketRead, TicketUpdate
from .services.exports import build_excel_report
from .services.imports import merge_csv


Base.metadata.create_all(bind=engine)

app = FastAPI(title="PLM Ticket Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/imports/csv", response_model=ImportSummary)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()
        return merge_csv(db, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/tickets", response_model=list[TicketRead])
def list_tickets(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Ticket.vendor_ticket_id.ilike(pattern),
                Ticket.vendor_subject.ilike(pattern),
                Ticket.vendor_from_name.ilike(pattern),
                Ticket.comments.ilike(pattern),
            )
        )

    if status:
        pattern = f"%{status.strip()}%"
        query = query.filter(or_(Ticket.vendor_status.ilike(pattern), Ticket.internal_status.ilike(pattern)))

    if category:
        pattern = f"%{category.strip()}%"
        query = query.filter(or_(Ticket.vendor_issue_category.ilike(pattern), Ticket.issue_category.ilike(pattern)))

    return query.order_by(Ticket.vendor_created_date.desc(), Ticket.id.desc()).all()


@app.get("/tickets/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for field, value in payload.model_dump().items():
        setattr(ticket, field, value)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/exports/excel")
def export_excel(db: Session = Depends(get_db)):
    content = build_excel_report(db)
    filename = "plm_ticket_report.xlsx"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
