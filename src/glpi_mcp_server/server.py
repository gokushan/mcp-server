"""[Composition Root] Application Entry Point.

This module is the Composition Root where all dependencies are wired together.
It configures the FastMCP server and registers tools, resources, and prompts.
The actual Primary Adapters are the tool functions in the tools/ directory.
"""

from fastmcp import FastMCP

from .config import settings
from .glpi.contracts import ContractManager
from .glpi.invoices import InvoiceManager
from .glpi.models import ContractData, InvoiceData, TicketData
from .glpi.tickets import TicketManager
from .processors.contract_processor import ContractProcessor
from .processors.invoice_processor import InvoiceProcessor
from .prompts.workflow_prompts import register_prompts
from .resources.glpi_resources import register_resources
from .prompts.slash_commands import register_slash_commands
from .tools.utils import get_glpi_client

# Initialize MCP Server
mcp = FastMCP("GLPI MCP Server")


# --- Document Processing Tools ---

@mcp.tool()
async def process_contract(file_path: str) -> dict:
    """Process a contract document and extract structured data.
    
    Args:
        file_path: Absolute path to the contract document
        
    Returns:
        Extracted contract data
    """
    processor = ContractProcessor()
    result = await processor.process(file_path)
    return result.model_dump()


@mcp.tool()
async def process_invoice(file_path: str) -> dict:
    """Process an invoice document and extract structured data.
    
    Args:
        file_path: Absolute path to the invoice document
        
    Returns:
        Extracted invoice data
    """
    processor = InvoiceProcessor()
    result = await processor.process(file_path)
    return result.model_dump()


# --- Contract Management Tools ---

@mcp.tool()
async def create_glpi_contract(
    name: str,
    begin_date: str,
    num: str | None = None,
    end_date: str | None = None,
    renewal_type: int = 0,
    cost: float | None = None,
    comment: str | None = None,
    suppliers_id: int | None = None,
    contracttypes_id: int | None = None,
    states_id: int | None = None,
) -> dict:
    """Create a new contract in GLPI.

    Args:
        name: Contract name
        begin_date: Start date (YYYY-MM-DD)
        num: Contract number/reference
        end_date: End date (YYYY-MM-DD)
        renewal_type: Renewal type (0=none, 1=auto, 2=manual)
        cost: Contract cost
        comment: Additional comments
        suppliers_id: Supplier ID
        contracttypes_id: Contract type ID
        states_id: Contract state ID

    Returns:
        Created contract details
    """
    client = await get_glpi_client()
    manager = ContractManager(client)
    
    data = ContractData(
        name=name,
        begin_date=begin_date,
        num=num,
        end_date=end_date,
        renewal_type=renewal_type,
        cost=cost,
        comment=comment,
        suppliers_id=suppliers_id,
        contracttypes_id=contracttypes_id,
        states_id=states_id
    )
    
    result = await manager.create(data)
    return result.model_dump()


@mcp.tool()
async def update_glpi_contract(
    id: int,
    name: str | None = None,
    begin_date: str | None = None,
    end_date: str | None = None,
    cost: float | None = None,
    comment: str | None = None,
    states_id: int | None = None
) -> dict:
    """Update an existing contract in GLPI.

    Args:
        id: Contract ID
        name: Updated name
        begin_date: Updated start date
        end_date: Updated end date
        cost: Updated cost
        comment: Updated comments
        states_id: Updated state ID

    Returns:
        Updated contract details
    """
    client = await get_glpi_client()
    manager = ContractManager(client)
    
    update_data = {}
    if name is not None: update_data["name"] = name
    if begin_date is not None: update_data["begin_date"] = begin_date
    if end_date is not None: update_data["end_date"] = end_date
    if cost is not None: update_data["cost"] = cost
    if comment is not None: update_data["comment"] = comment
    if states_id is not None: update_data["states_id"] = states_id
    
    result = await manager.update(id, update_data)
    return result.model_dump()


@mcp.tool()
async def get_contract_status(id: int) -> dict:
    """Get contract details and status.

    Args:
        id: Contract ID

    Returns:
        Contract details
    """
    client = await get_glpi_client()
    manager = ContractManager(client)
    
    result = await manager.get(id)
    return result.model_dump()


# --- Invoice Management Tools ---

@mcp.tool()
async def create_glpi_invoice(
    name: str,
    begin_date: str,
    value: float,
    number: str | None = None,
    end_date: str | None = None,
    suppliers_id: int | None = None,
    comment: str | None = None,
) -> dict:
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


@mcp.tool()
async def update_glpi_invoice(
    id: int,
    name: str | None = None,
    value: float | None = None,
    number: str | None = None,
    end_date: str | None = None,
    comment: str | None = None
) -> dict:
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


@mcp.tool()
async def get_invoice_status(id: int) -> dict:
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


# --- Ticket Management Tools ---

@mcp.tool()
async def create_ticket(
    name: str,
    content: str,
    type: int = 1,
    priority: int = 3,
    category: int | None = None,
    urgency: int = 3,
    impact: int = 3,
    requesttypes_id: int | None = None
) -> dict:
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


@mcp.tool()
async def update_ticket(
    id: int,
    status: int | None = None,
    content: str | None = None,
    solution: str | None = None,
    priority: int | None = None
) -> dict:
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
    
    update_data = {}
    if status is not None: update_data["status"] = status
    if priority is not None: update_data["priority"] = priority
    
    result = await manager.update(id, update_data)
    return result.model_dump()


@mcp.tool()
async def get_ticket_status(id: int) -> dict:
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


# --- Register Resources and Prompts ---
register_resources(mcp)
register_prompts(mcp)
register_slash_commands(mcp)


def main():
    """Run server."""
    # Validate configuration
    try:
        settings.validate_llm_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Note: LLM configuration is only required for document processing tools.")
        print("Other tools will work without LLM configuration.")
    
    mcp.run()


if __name__ == "__main__":
    main()
