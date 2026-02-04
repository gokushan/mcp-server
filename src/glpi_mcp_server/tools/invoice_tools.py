"""[Adapter] Primary Adapter (Driving) for Invoice Management.

This module exposes the invoice management functionality to the MCP protocol.
It acts as a driving adapter that translates MCP tool calls into domain commands.
"""

from typing import Any

from glpi_mcp_server.glpi.invoices import InvoiceManager
from glpi_mcp_server.glpi.models import InvoiceData
from glpi_mcp_server.tools.utils import get_glpi_client


async def create_glpi_invoice(
    name: str,
    begin_date: str,
    value: float,
    number: str | None = None,
    end_date: str | None = None,
    suppliers_id: int | None = None,
    comment: str | None = None,
) -> dict[str, Any]:
    """Create a new invoice/budget in GLPI.

    Args:
        name: Invoice name/description
        begin_date: Invoice date (YYYY-MM-DD)
        value: Total amount
        number: Invoice number
        end_date: Due date (YYYY-MM-DD)
        suppliers_id: Supplier ID
        comment: Additional notes

    Returns:
        Created invoice details
    """
    client = await get_glpi_client()
    manager = InvoiceManager(client)
    
    data = InvoiceData(
        name=name,
        begin_date=begin_date,
        value=value,
        number=number,
        end_date=end_date,
        suppliers_id=suppliers_id,
        comment=comment
    )
    
    result = await manager.create(data)
    return result.model_dump()


async def update_glpi_invoice(
    id: int,
    name: str | None = None,
    value: float | None = None,
    number: str | None = None,
    end_date: str | None = None,
    comment: str | None = None
) -> dict[str, Any]:
    """Update an existing invoice in GLPI.

    Args:
        id: Invoice ID
        name: Updated name
        value: Updated amount
        number: Updated number
        end_date: Updated due date
        comment: Updated comments

    Returns:
        Updated invoice details
    """
    client = await get_glpi_client()
    manager = InvoiceManager(client)
    
    update_data = {}
    if name is not None: update_data["name"] = name
    if value is not None: update_data["value"] = value
    if number is not None: update_data["number"] = number
    if end_date is not None: update_data["end_date"] = end_date
    if comment is not None: update_data["comment"] = comment
    
    result = await manager.update(id, update_data)
    return result.model_dump()


async def get_invoice_status(id: int) -> dict[str, Any]:
    """Get invoice details.

    Args:
        id: Invoice ID

    Returns:
        Invoice details
    """
    client = await get_glpi_client()
    manager = InvoiceManager(client)
    
    result = await manager.get(id)
    return result.model_dump()
