from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_ticket_id: str
    vendor_subject: str | None = None
    vendor_description: str | None = None
    vendor_from_name: str | None = None
    vendor_from_email: str | None = None
    vendor_priority: str | None = None
    vendor_department: str | None = None
    vendor_help_topic: str | None = None
    vendor_source: str | None = None
    vendor_status: str | None = None
    vendor_last_updated: datetime | None = None
    vendor_created_date: datetime | None = None
    vendor_sla_due_date: datetime | None = None
    vendor_sla_plan: str | None = None
    vendor_due_date: datetime | None = None
    vendor_closed_date: datetime | None = None
    vendor_overdue: bool | None = None
    vendor_agent_assigned: str | None = None
    vendor_issue_category: str | None = None
    internal_status: str | None = None
    internal_owner: str | None = None
    issue_category: str | None = None
    root_cause: str | None = None
    comments: str | None = None


class TicketRead(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TicketUpdate(BaseModel):
    internal_status: str | None = None
    internal_owner: str | None = None
    issue_category: str | None = None
    root_cause: str | None = None
    comments: str | None = None


class ImportSummary(BaseModel):
    new: int
    updated: int
    failed: int
    errors: list[str]
