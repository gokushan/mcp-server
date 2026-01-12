"""Invoice management operations."""

from typing import Any

from .api_client import GLPIAPIClient
from .models import InvoiceData, InvoiceResponse


class InvoiceManager:
    """Manager for GLPI invoices (Budgets)."""

    def __init__(self, client: GLPIAPIClient):
        self.client = client
        # Note: GLPI uses 'Budget' for financial tracking or custom objects
        # We'll use Budget for this implementation
        self.endpoint = "Budget"

    async def create(self, data: InvoiceData) -> InvoiceResponse:
        """Create a new invoice/budget.

        Args:
            data: Invoice data

        Returns:
            Created invoice details
        """
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        
        response = await self.client.post(self.endpoint, payload)
        
        if isinstance(response, list):
            invoice_id = response[0].get("id")
        else:
            invoice_id = response.get("id")
            
        return await self.get(invoice_id)

    async def update(self, invoice_id: int, data: dict[str, Any]) -> InvoiceResponse:
        """Update an existing invoice.

        Args:
            invoice_id: Invoice ID
            data: Fields to update

        Returns:
            Updated invoice details
        """
        payload = {"id": invoice_id, **data}
        await self.client.put(self.endpoint, payload)
        return await self.get(invoice_id)

    async def get(self, invoice_id: int) -> InvoiceResponse:
        """Get invoice details.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice details
        """
        data = await self.client.get(f"{self.endpoint}/{invoice_id}")
        
        return InvoiceResponse(
            id=data.get("id"),
            name=data.get("name"),
            number=data.get("template_name"), # Using template_name as number for example
            date=data.get("begin_date"),
            due_date=data.get("end_date"),
            amount=float(data.get("value", 0) or 0),
            status="active" # TODO: Map from GLPI status
        )

    async def list_invoices(
        self, 
        criteria: dict[str, Any] | None = None,
        limit: int = 50
    ) -> list[InvoiceResponse]:
        """List invoices.
        
        Args:
            criteria: Search criteria
            limit: Max results
            
        Returns:
            List of invoices
        """
        raw_list = await self.client.search(self.endpoint, criteria)
        
        invoices = []
        for item in raw_list[:limit]:
            invoices.append(InvoiceResponse(
                id=item.get("id"),
                name=item.get("name"),
                amount=float(item.get("value", 0) or 0)
            ))
            
        return invoices
