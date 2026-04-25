from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    vendor_ticket_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    vendor_subject: Mapped[str | None] = mapped_column(String(500))
    vendor_description: Mapped[str | None] = mapped_column(Text)
    vendor_from_name: Mapped[str | None] = mapped_column(String(255))
    vendor_from_email: Mapped[str | None] = mapped_column(String(255))
    vendor_priority: Mapped[str | None] = mapped_column(String(100))
    vendor_department: Mapped[str | None] = mapped_column(String(100))
    vendor_help_topic: Mapped[str | None] = mapped_column(String(255))
    vendor_source: Mapped[str | None] = mapped_column(String(100))
    vendor_status: Mapped[str | None] = mapped_column(String(100))
    vendor_last_updated: Mapped[datetime | None] = mapped_column(DateTime)
    vendor_created_date: Mapped[datetime | None] = mapped_column(DateTime)
    vendor_sla_due_date: Mapped[datetime | None] = mapped_column(DateTime)
    vendor_sla_plan: Mapped[str | None] = mapped_column(String(255))
    vendor_due_date: Mapped[datetime | None] = mapped_column(DateTime)
    vendor_closed_date: Mapped[datetime | None] = mapped_column(DateTime)
    vendor_overdue: Mapped[bool | None] = mapped_column(Boolean)
    vendor_agent_assigned: Mapped[str | None] = mapped_column(String(255))
    vendor_issue_category: Mapped[str | None] = mapped_column(String(255))

    internal_status: Mapped[str | None] = mapped_column(String(100))
    internal_owner: Mapped[str | None] = mapped_column(String(255))
    issue_category: Mapped[str | None] = mapped_column(String(255))
    root_cause: Mapped[str | None] = mapped_column(String(255))
    comments: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
