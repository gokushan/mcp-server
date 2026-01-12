"""Pydantic models for GLPI entities."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class ContractData(BaseModel):
    """Contract data model."""

    name: str = Field(..., description="Contract name")
    num: str | None = Field(None, description="Contract number/reference")
    begin_date: date | None = Field(None, description="Contract start date")
    end_date: date | None = Field(None, description="Contract end date")
    renewal_type: int = Field(0, description="Renewal type (0=none, 1=auto, 2=manual)")
    cost: float | None = Field(None, description="Contract cost")
    comment: str | None = Field(None, description="Additional comments")
    suppliers_id: int | None = Field(None, description="Supplier ID")
    contracttypes_id: int | None = Field(None, description="Contract type ID")
    states_id: int | None = Field(None, description="Contract state ID")


class ContractResponse(BaseModel):
    """Contract response from GLPI API."""

    id: int = Field(..., description="Contract ID")
    name: str
    num: str | None = None
    begin_date: str | None = None
    end_date: str | None = None
    cost: float | None = None
    state: str | None = None
    supplier: str | None = None
    last_update: datetime | None = None


class InvoiceData(BaseModel):
    """Invoice/Budget data model."""

    name: str = Field(..., description="Invoice name/description")
    number: str | None = Field(None, description="Invoice number")
    begin_date: date | None = Field(None, description="Invoice date")
    end_date: date | None = Field(None, description="Due date")
    value: float = Field(..., description="Invoice total amount")
    suppliers_id: int | None = Field(None, description="Supplier ID")
    comment: str | None = Field(None, description="Additional notes")


class InvoiceResponse(BaseModel):
    """Invoice response from GLPI API."""

    id: int = Field(..., description="Invoice ID")
    name: str
    number: str | None = None
    date: str | None = None
    due_date: str | None = None
    amount: float | None = None
    status: str | None = None
    supplier: str | None = None


class TicketData(BaseModel):
    """Ticket data model."""

    name: str = Field(..., description="Ticket title")
    content: str = Field(..., description="Ticket description")
    type: int = Field(1, description="Ticket type (1=incident, 2=request)")
    priority: int = Field(3, description="Priority (1-5)")
    category: int | None = Field(None, description="Category ID")
    urgency: int = Field(3, description="Urgency (1-5)")
    impact: int = Field(3, description="Impact (1-5)")
    requesttypes_id: int | None = Field(None, description="Request source ID")


class TicketResponse(BaseModel):
    """Ticket response from GLPI API."""

    id: int = Field(..., description="Ticket ID")
    name: str
    status: str
    priority: int
    created: datetime
    updated: datetime | None = None
    assigned_to: str | None = None
    category: str | None = None


class ProcessedContract(BaseModel):
    """Processed contract data from document."""

    contract_name: str
    parties: dict[str, str] = Field(
        default_factory=dict, description="Contract parties (client, provider)"
    )
    start_date: str | None = None
    end_date: str | None = None
    renewal_type: str | None = None
    amount: float | None = None
    currency: str = "EUR"
    payment_terms: str | None = None
    key_terms: list[str] = Field(default_factory=list)
    summary: str


class ProcessedInvoice(BaseModel):
    """Processed invoice data from document."""

    invoice_number: str
    vendor: str
    client: str
    invoice_date: str
    due_date: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)
    subtotal: float
    tax: float = 0.0
    total: float
    currency: str = "EUR"
    payment_method: str | None = None
    bank_account: str | None = None


class APIResponse(BaseModel):
    """Generic API response."""

    success: bool
    message: str | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    error: str | None = None
