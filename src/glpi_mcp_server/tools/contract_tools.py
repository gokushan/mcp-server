"""Contract management tools."""

from typing import Any

from ..glpi.contracts import ContractManager
from ..glpi.models import ContractData
from .utils import get_glpi_client


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
) -> dict[str, Any]:
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
    
    # Convert dates from string to date objects inside ContractData validation
    data = ContractData(
        name=name,
        begin_date=begin_date, # Pydantic will parse YYYY-MM-DD string
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
