"""[Adapter] Primary Adapter (Driving) for Contract Management.

This module exposes the contract management functionality to the MCP protocol.
It acts as a driving adapter that translates MCP tool calls into domain commands.
"""

from typing import Any

from glpi_mcp_server.glpi.contracts import ContractManager
from glpi_mcp_server.glpi.documents import DocumentManager
from glpi_mcp_server.glpi.models import ContractData
from glpi_mcp_server.tools.utils import get_glpi_client, is_path_allowed
from glpi_mcp_server.config import settings
from pathlib import Path


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
    is_deleted: int = 0,
    # Legacy/Compatibility
    suppliers_id: int | None = None,
    end_date: str | None = None,
    # Document attachment
    file_path: str | None = None,
) -> dict[str, Any]:
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
    
    # Convert dates from string to date objects inside ContractData validation
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
        if not is_path_allowed(file_path):
             response["document_attached"] = False
             response["document_error"] = f"Access to path '{file_path}' is denied. Check allowed roots."
             response["warning"] = (
                 f"Contract created (ID: {result.id}), but document attachment failed: "
                 "Access denied."
             )
        else:
            # Check extension
            ext = Path(file_path).suffix.lower().lstrip(".")
            if ext not in settings.allowed_extensions_list:
                response["document_attached"] = False
                response["document_error"] = f"File extension '{ext}' is not allowed. Allowed: {settings.allowed_extensions_list}"
                response["warning"] = (
                    f"Contract created (ID: {result.id}), but document attachment failed: "
                    f"Extension '{ext}' not allowed."
                )
            else:
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


async def update_glpi_contract(
    id: int,
    name: str | None = None,
    begin_date: str | None = None,
    end_date: str | None = None,
    cost: float | None = None,
    comment: str | None = None,
    states_id: int | None = None
) -> dict[str, Any]:
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


async def get_contract_status_by_id(id: int) -> dict[str, Any]:
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


async def search_contracts(
    name: str | None = None,
    num: str | None = None,
    id: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search for contracts by name, contract number, or ID.
    
    This tool allows flexible searching using one or more criteria. 
    GLPI will return contracts matching the provided 'searchText' filters.

    Args:
        name: Part of the contract name to search for
        num: Part of the contract number to search for
        id: Specific contract ID to find
        limit: Maximum number of results (default 20)

    Returns:
        List of matching contracts
    """
    client = await get_glpi_client()
    manager = ContractManager(client)
    
    results = await manager.search(name=name, num=num, id=id, limit=limit)
    return [r.model_dump() for r in results]


async def attach_document_to_contract(
    contract_id: int,
    file_path: str,
    document_name: str | None = None,
) -> dict[str, Any]:
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
        ValueError: If contract doesn't exist, file is invalid, or access denied
    """
    if not is_path_allowed(file_path):
        raise ValueError(f"Access to path '{file_path}' is denied. Check your configured allowed roots.")

    # Check extension
    ext = Path(file_path).suffix.lower().lstrip(".")
    if ext not in settings.allowed_extensions_list:
        raise ValueError(f"File extension '{ext}' is not allowed. Allowed: {settings.allowed_extensions_list}")

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
