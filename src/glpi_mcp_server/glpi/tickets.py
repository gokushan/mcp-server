"""Ticket management operations."""

from datetime import datetime
from typing import Any

from .api_client import GLPIAPIClient
from .models import TicketData, TicketResponse


class TicketManager:
    """Manager for GLPI tickets."""

    def __init__(self, client: GLPIAPIClient):
        self.client = client
        self.endpoint = "Ticket"

    async def create(self, data: TicketData) -> TicketResponse:
        """Create a new ticket.

        Args:
            data: Ticket data

        Returns:
            Created ticket details
        """
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        
        response = await self.client.post(self.endpoint, payload)
        
        if isinstance(response, list):
            ticket_id = response[0].get("id")
        else:
            ticket_id = response.get("id")
            
        return await self.get(ticket_id)

    async def update(self, ticket_id: int, data: dict[str, Any]) -> TicketResponse:
        """Update an existing ticket.

        Args:
            ticket_id: Ticket ID
            data: Fields to update

        Returns:
            Updated ticket details
        """
        payload = {"id": ticket_id, **data}
        await self.client.put(self.endpoint, payload)
        return await self.get(ticket_id)

    async def get(self, ticket_id: int) -> TicketResponse:
        """Get ticket details.

        Args:
            ticket_id: Ticket ID

        Returns:
            Ticket details
        """
        data = await self.client.get(f"{self.endpoint}/{ticket_id}")
        
        return TicketResponse(
            id=data.get("id"),
            name=data.get("name"),
            status=str(data.get("status")), # Status is int in GLPI, mapping needed
            priority=int(data.get("priority")),
            created=datetime.fromisoformat(data.get("date").replace(" ", "T")),
            updated=datetime.fromisoformat(data.get("date_mod").replace(" ", "T")) if data.get("date_mod") else None
        )

    async def list_tickets(
        self, 
        criteria: dict[str, Any] | None = None,
        limit: int = 50
    ) -> list[TicketResponse]:
        """List tickets.
        
        Args:
            criteria: Search criteria
            limit: Max results
            
        Returns:
            List of tickets
        """
        raw_list = await self.client.search(self.endpoint, criteria)
        
        tickets = []
        for item in raw_list[:limit]:
            # Basic info available in search results
            tickets.append(TicketResponse(
                id=item.get("id"),
                name=item.get("name"),
                status=str(item.get("status", 1)),
                priority=int(item.get("priority", 3)),
                created=datetime.now() # Date field might differ in search results
            ))
            
        return tickets
