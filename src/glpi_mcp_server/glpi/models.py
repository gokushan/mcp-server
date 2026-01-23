"""[Domain] Entities and Data Models.

This module defines the core domain entities used throughout the application.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class ContractData(BaseModel):
    """Contract data model."""

    # === IDENTIFICACIÓN ===
    name: str = Field(..., description="Nombre del contrato (REQUERIDO)")
    num: str | None = Field(None, description="Número de contrato")
    entities_id: int | None = Field(None, description="ID de entidad")
    is_recursive: int = Field(0, description="Recursivo (0|1)")

    # === CLASIFICACIÓN ===
    contracttypes_id: int | None = Field(None, description="Tipo de contrato")
    states_id: int | None = Field(None, description="Estado del contrato")

    # === FINANCIERO ===
    cost: float | None = Field(None, description="Coste (formato: '1234.56')")
    accounting_number: str | None = Field(None, description="Número de contabilidad")

    # === FECHAS Y DURACIÓN ===
    begin_date: date | None = Field(None, description="Fecha de inicio")
    duration: int | None = Field(None, description="Duración en meses")
    notice: int | None = Field(None, description="Preaviso en meses")
    periodicity: int | None = Field(None, description="Periodicidad en meses")
    billing: int | None = Field(None, description="Facturación en meses")
    renewal: int | None = Field(None, description="1=Tácita, 2=Expresa")

    # === ALERTAS ===
    alert: int | None = Field(None, description="Alerta previa en meses")

    # === HORARIOS SOPORTE (SLA) ===
    week_begin_hour: str | None = Field(None, description="Inicio semana (HH:MM:SS)")
    week_end_hour: str | None = Field(None, description="Fin semana (HH:MM:SS)")

    use_monday: int = Field(0, description="Usar lunes (0|1)")
    monday_begin_hour: str | None = Field(None, description="Inicio lunes (HH:MM:SS)")
    monday_end_hour: str | None = Field(None, description="Fin lunes (HH:MM:SS)")

    use_saturday: int = Field(0, description="Usar sábado (0|1)")
    saturday_begin_hour: str | None = Field(None, description="Inicio sábado (HH:MM:SS)")
    saturday_end_hour: str | None = Field(None, description="Fin sábado (HH:MM:SS)")

    # === LÍMITES ===
    max_links_allowed: int | None = Field(None, description="Máx. elementos vinculables")

    # === UBICACIÓN ===
    locations_id: int | None = Field(None, description="ID de ubicación")

    # === OBSERVACIONES ===
    comment: str | None = Field(None, description="Comentarios")

    # === PLANTILLAS ===
    is_template: int = Field(0, description="Es plantilla (0|1)")
    template_name: str | None = Field(None, description="Nombre plantilla")

    # === ESTADO ===
    is_deleted: int = Field(0, description="Borrado lógico (0|1)")

    # Legacy/Compatibility fields (optional)
    suppliers_id: int | None = Field(None, description="Supplier ID")
    end_date: date | None = Field(None, description="Contract end date")


class ContractResponse(BaseModel):
    """Contract response from GLPI API."""

    id: int = Field(..., description="Contract ID")
    name: str
    num: str | None = None
    begin_date: str | None = None
    end_date: str | None = None
    cost: float | None = None
    state: int | str | None = None
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
    status: int |str | None = None
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
    contract_num: str | None = None
    accounting_number: str | None = None
    
    parties: dict[str, Any] = Field(
        default_factory=dict, description="Contract parties (client, provider)"
    )
    
    start_date: str | None = None
    end_date: str | None = None
    duration_months: int | None = None
    
    # 1=Tacit, 2=Express (LLM should try to map or return None)
    renewal_type: str | None = None 
    renewal_enum: int | None = Field(None, description="Mapped renewal type: 1=Tacit/Auto, 2=Express/Manual")
    
    notice_months: int | None = None
    billing_frequency_months: int | None = None
    
    amount: float | None = None
    currency: str = "EUR"
    payment_terms: str | dict[str, Any] | None = None
    
    # SLA Info
    sla_support_hours: dict[str, Any] | None = Field(None, description="Extracted support hours details")
    
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
