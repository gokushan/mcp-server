"""[Composition Root] Application Entry Point.

This module is the Composition Root where all dependencies are wired together.
It configures the FastMCP server and registers tools, resources, and prompts.
The actual Primary Adapters are the tool functions in the tools/ directory.
"""

from fastmcp import FastMCP

from .config import settings
from .glpi.contracts import ContractManager
from .glpi.documents import DocumentManager
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
    # Identification
    num: str | None = None,
    entities_id: int | None = None,
    is_recursive: int = 0,
    # Classification
    contracttypes_id: int | None = None,
    states_id: int | None = None,
    # Financial
    cost: float | None = None,
    accounting_number: str | None = None,
    # Dates & Duration
    begin_date: str | None = None,
    duration: int | None = None,
    notice: int | None = None,
    periodicity: int | None = None,
    billing: int | None = None,
    renewal: int | None = None,
    # Alerts
    alert: int | None = None,
    # SLA
    week_begin_hour: str | None = None,
    week_end_hour: str | None = None,
    use_saturday: int = 0,
    saturday_begin_hour: str | None = None,
    saturday_end_hour: str | None = None,
    use_sunday: int = 0,
    sunday_begin_hour: str | None = None,
    sunday_end_hour: str | None = None,
    # Limits
    max_links_allowed: int | None = None,
    # Location
    locations_id: int | None = None,
    # Obs
    comment: str | None = None,
    # Templates
    is_template: int = 0,
    template_name: str | None = None,
    # State
    is_deleted: int = 0,
    # Legacy/Compatibility
    suppliers_id: int | None = None,
    end_date: str | None = None,
    # Document attachment
    file_path: str | None = None,
) -> dict:
    """Create a new contract in GLPI.

    Args:
        name: Contract name (Required)
        num: Contract number
        entities_id: Entity ID
        is_recursive: Recursive (0|1)
        contracttypes_id: Contract type ID
        states_id: Contract state ID
        cost: Contract cost
        accounting_number: Accounting number
        begin_date: Start date (YYYY-MM-DD)
        duration: Duration in months
        notice: Notice in months
        periodicity: Periodicity in months
        billing: Billing in months
        renewal: Renewal (1=Tacit, 2=Express)
        alert: Alert in months
        week_begin_hour: Week start hour (HH:MM:SS)
        week_end_hour: Week end hour (HH:MM:SS)
        use_saturday: Use Saturday (0|1)
        saturday_begin_hour: Saturday start hour (HH:MM:SS)
        saturday_end_hour: Saturday end hour (HH:MM:SS)
        use_sunday: Use Sunday (0|1)
        sunday_begin_hour: Sunday start hour (HH:MM:SS)
        sunday_end_hour: Sunday end hour (HH:MM:SS)
        max_links_allowed: Max links
        locations_id: Location ID
        comment: Comments
        is_template: Is template (0|1)
        template_name: Template name
        is_deleted: Is deleted (0|1)
        suppliers_id: Supplier ID
        end_date: End date (YYYY-MM-DD)
        file_path: Optional path to contract document to attach

    Returns:
        Created contract details with document attachment status
    """
    client = await get_glpi_client()
    manager = ContractManager(client)
    
    data = ContractData(
        name=name,
        num=num,
        entities_id=entities_id,
        is_recursive=is_recursive,
        contracttypes_id=contracttypes_id,
        states_id=states_id,
        cost=cost,
        accounting_number=accounting_number,
        begin_date=begin_date,
        duration=duration,
        notice=notice,
        periodicity=periodicity,
        billing=billing,
        renewal=renewal,
        alert=alert,
        week_begin_hour=week_begin_hour,
        week_end_hour=week_end_hour,
        use_saturday=use_saturday,
        saturday_begin_hour=saturday_begin_hour,
        saturday_end_hour=saturday_end_hour,
        use_sunday=use_sunday,
        sunday_begin_hour=sunday_begin_hour,
        sunday_end_hour=sunday_end_hour,
        max_links_allowed=max_links_allowed,
        locations_id=locations_id,
        comment=comment,
        is_template=is_template,
        template_name=template_name,
        is_deleted=is_deleted,
        suppliers_id=suppliers_id,
        end_date=end_date
    )
    
    result = await manager.create(data)
    response = result.model_dump()
    
    # Attach document if file_path provided
    if file_path:
        doc_manager = DocumentManager(client)
        try:
            doc_result = await doc_manager.attach_to_item(
                file_path=file_path,
                item_id=result.id,
                item_type="Contract",
                document_name=name,
            )
            response["document_attached"] = True
            response["document_id"] = doc_result.id
            response["document_name"] = doc_result.name
        except Exception as e:
            # Contract created successfully, but document attachment failed
            response["document_attached"] = False
            response["document_error"] = str(e)
            response["warning"] = (
                f"Contract created successfully (ID: {result.id}), "
                f"but document attachment failed: {str(e)}. "
                "You can retry using the 'attach_document_to_contract' tool."
            )
    
    return response


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


@mcp.tool()
async def attach_document_to_contract(
    contract_id: int,
    file_path: str,
    document_name: str | None = None,
) -> dict:
    """Attach a document to an existing contract in GLPI.
    
    This tool is useful when:
    - Document attachment failed during contract creation
    - You want to add additional documents to a contract
    - You need to update/replace contract documentation
    
    Args:
        contract_id: ID of the contract to attach document to
        file_path: Absolute path to the document file
        document_name: Optional name for the document (defaults to contract name)
    
    Returns:
        Document attachment details
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If contract doesn't exist or file is invalid
    """
    client = await get_glpi_client()
    
    # Get contract name if document_name not provided
    if not document_name:
        contract_manager = ContractManager(client)
        contract = await contract_manager.get(contract_id)
        document_name = contract.name
    
    # Attach document
    doc_manager = DocumentManager(client)
    result = await doc_manager.attach_to_item(
        file_path=file_path,
        item_id=contract_id,
        item_type="Contract",
        document_name=document_name,
    )
    
    return {
        "success": True,
        "contract_id": contract_id,
        "document_id": result.id,
        "document_name": result.name,
        "filename": result.filename,
        "message": f"Document '{result.name}' attached successfully to Contract ID {contract_id}",
    }


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
