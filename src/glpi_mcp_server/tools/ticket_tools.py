"""[Adapter] Primary Adapter (Driving) for Ticket Management.

This module exposes the ticket management functionality to the MCP protocol.
It acts as a driving adapter that translates MCP tool calls into domain commands.
"""

from typing import Any

from ..glpi.models import TicketData
from ..glpi.tickets import TicketManager
from .utils import get_glpi_client


async def create_ticket(
    name: str,
    content: str,
    type: int = 1,
    priority: int = 3,
    category: int | None = None,
    urgency: int = 3,
    impact: int = 3,
    requesttypes_id: int | None = None
) -> dict[str, Any]:
    """Create a support ticket in GLPI.

    Args:
        name: Ticket title
        content: Ticket description
        type: Ticket type (1=incident, 2=request)
        priority: Priority (1-5)
        category: Category ID
        urgency: Urgency (1-5)
        impact: Impact (1-5)
        requesttypes_id: Request source ID

    Returns:
        Created ticket details
    """
    client = await get_glpi_client()
    manager = TicketManager(client)
    
    data = TicketData(
        name=name,
        content=content,
        type=type,
        priority=priority,
        category=category,
        urgency=urgency,
        impact=impact,
        requesttypes_id=requesttypes_id
    )
    
    result = await manager.create(data)
    return result.model_dump()


async def update_ticket(
    id: int,
    status: int | None = None,
    content: str | None = None,
    solution: str | None = None,
    priority: int | None = None
) -> dict[str, Any]:
    """Update an existing ticket or add followup.

    Args:
        id: Ticket ID
        status: New status
        content: Followup content to add
        solution: Solution description (when closing)
        priority: Updated priority

    Returns:
        Updated ticket details
    """
    client = await get_glpi_client()
    manager = TicketManager(client)
    
    # Logic for update vs followup vs solution
    # Simplified here to just update fields
    # In real implementation, would use different endpoints for followup/solution
    
    update_data = {}
    if status is not None: update_data["status"] = status
    if priority is not None: update_data["priority"] = priority
    
    # TODO: Implement add_followup and add_solution methods in TicketManager
    # and call them if content/solution provided
    
    result = await manager.update(id, update_data)
    return result.model_dump()


async def get_ticket_status(id: int) -> dict[str, Any]:
    """Get ticket details.

    Args:
        id: Ticket ID

    Returns:
        Ticket details
    """
    client = await get_glpi_client()
    manager = TicketManager(client)
    
    result = await manager.get(id)
    return result.model_dump()
