"""MCP Resources for GLPI."""

from typing import Any

from fastmcp import FastMCP

from ..glpi.contracts import ContractManager
from ..glpi.invoices import InvoiceManager
from ..glpi.tickets import TicketManager
from ..tools.utils import get_glpi_client


def register_resources(mcp: FastMCP):
    """Register GLPI resources."""
    
    @mcp.resource("glpi://contracts/{id}")
    async def get_contract_resource(id: int) -> str:
        """Get contract details."""
        client = await get_glpi_client()
        manager = ContractManager(client)
        result = await manager.get(id)
        return result.model_dump_json(indent=2)

    @mcp.resource("glpi://contracts/list")
    async def list_contracts_resource() -> str:
        """List contracts."""
        client = await get_glpi_client()
        manager = ContractManager(client)
        results = await manager.list_contracts()
        return str([r.model_dump() for r in results])

    @mcp.resource("glpi://invoices/{id}")
    async def get_invoice_resource(id: int) -> str:
        """Get invoice details."""
        client = await get_glpi_client()
        manager = InvoiceManager(client)
        result = await manager.get(id)
        return result.model_dump_json(indent=2)
        
    @mcp.resource("glpi://invoices/list")
    async def list_invoices_resource() -> str:
        """List invoices."""
        client = await get_glpi_client()
        manager = InvoiceManager(client)
        results = await manager.list_invoices()
        return str([r.model_dump() for r in results])

    @mcp.resource("glpi://tickets/{id}")
    async def get_ticket_resource(id: int) -> str:
        """Get ticket details."""
        client = await get_glpi_client()
        manager = TicketManager(client)
        result = await manager.get(id)
        return result.model_dump_json(indent=2)

    @mcp.resource("glpi://tickets/list")
    async def list_tickets_resource() -> str:
        """List tickets."""
        client = await get_glpi_client()
        manager = TicketManager(client)
        results = await manager.list_tickets()
        return str([r.model_dump() for r in results])
