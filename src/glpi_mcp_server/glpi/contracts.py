"""Contract management operations."""

from typing import Any

from .api_client import GLPIAPIClient
from .models import ContractData, ContractResponse


class ContractManager:
    """Manager for GLPI contracts."""

    def __init__(self, client: GLPIAPIClient):
        self.client = client
        self.endpoint = "Contract"

    async def create(self, data: ContractData) -> ContractResponse:
        """Create a new contract.

        Args:
            data: Contract data

        Returns:
            Created contract details
        """
        # Convert Pydantic model to dict, filtering None values
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        
        response = await self.client.post(self.endpoint, payload)
        
        # Determine ID from response (can be list or dict)
        if isinstance(response, list):
            contract_id = response[0].get("id")
        else:
            contract_id = response.get("id")
            
        return await self.get(contract_id)

    async def update(self, contract_id: int, data: dict[str, Any]) -> ContractResponse:
        """Update an existing contract.

        Args:
            contract_id: Contract ID
            data: Fields to update

        Returns:
            Updated contract details
        """
        payload = {"id": contract_id, **data}
        await self.client.put(self.endpoint, payload)
        return await self.get(contract_id)

    async def get(self, contract_id: int) -> ContractResponse:
        """Get contract details.

        Args:
            contract_id: Contract ID

        Returns:
            Contract details
        """
        data = await self.client.get(f"{self.endpoint}/{contract_id}")
        
        # Map GLPI response to our model
        # Note: Actual mapping depends on GLPI API response structure
        return ContractResponse(
            id=data.get("id"),
            name=data.get("name"),
            num=data.get("num"),
            begin_date=data.get("begin_date"),
            end_date=data.get("end_date"),
            cost=float(data.get("cost", 0) or 0),
            state=data.get("states_id"),  # Need to resolve state name separately
            last_update=data.get("date_mod")
        )

    async def list_contracts(
        self, 
        criteria: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[ContractResponse]:
        """List contracts with filtering.
        
        Args:
            criteria: Search criteria
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of contracts
        """
        # TODO: Implement full search logic with criteria mapping
        raw_list = await self.client.search(self.endpoint, criteria)
        
        contracts = []
        for item in raw_list[:limit]:
            contracts.append(ContractResponse(
                id=item.get("id"),
                name=item.get("name"),
                num=item.get("num"),
                begin_date=item.get("begin_date"),
                end_date=item.get("end_date")
            ))
            
        return contracts
