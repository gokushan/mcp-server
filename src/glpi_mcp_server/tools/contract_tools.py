"""[Adapter] Primary Adapter (Driving) for Contract Management.

This module exposes the contract management functionality to the MCP protocol.
It acts as a driving adapter that translates MCP tool calls into domain commands.
"""

from typing import Any

from ..glpi.contracts import ContractManager
from ..glpi.models import ContractData
from .utils import get_glpi_client


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
        use_sunday: Use Sunday (0|1)
        sunday_begin_hour: Sunday start hour (HH:MM:SS)
        sunday_end_hour: Sunday end hour (HH:MM:SS)
        use_saturday: Use Saturday (0|1)
        saturday_begin_hour: Saturday start hour (HH:MM:SS)
        saturday_end_hour: Saturday end hour (HH:MM:SS)
        max_links_allowed: Max links
        locations_id: Location ID
        comment: Comments
        is_template: Is template (0|1)
        template_name: Template name
        is_deleted: Is deleted (0|1)
        suppliers_id: Supplier ID
        end_date: End date (YYYY-MM-DD)

    Returns:
        Created contract details
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
    return result.model_dump()


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


async def get_contract_status(id: int) -> dict[str, Any]:
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
