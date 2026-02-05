import httpx
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
        payload = {k: v for k, v in data.model_dump(mode='json').items() if v is not None}
        
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
        try:
            data = await self.client.get(f"{self.endpoint}/{contract_id}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Contract with ID {contract_id} not found in GLPI.") from e
            raise

        if not data:
            raise ValueError(f"Contract with ID {contract_id} returned no data from GLPI.")

        if data.get("is_deleted") == 1:
            raise ValueError(f"Contract with ID {contract_id} is deleted or does not exist.")

        # Map GLPI response to our model
        # Note: Actual mapping depends on GLPI API response structure
        return ContractResponse(
            id=data.get("id"),
            name=data.get("name"),
            num=data.get("num"),
            begin_date=data.get("begin_date"),
            end_date=data.get("end_date"),
            comment=data.get("comment"),
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
            criteria: Search criteria (passed as params to GET /Contract)
            limit: Max results (range parameter)
            offset: Pagination offset
            
        Returns:
            List of contracts
        """
        params = criteria or {}
        params["range"] = f"{offset}-{offset + limit - 1}"
        
        raw_list = await self.client.get(self.endpoint, params=params)
        
        if not isinstance(raw_list, list):
            raw_list = [raw_list] if raw_list else []
            
        contracts = []
        for item in raw_list:
            contracts.append(ContractResponse(
                id=item.get("id"),
                name=item.get("name"),
                num=item.get("num"),
                begin_date=item.get("begin_date"),
                end_date=item.get("end_date"),
                comment=item.get("comment"),
                state=item.get("states_id"),
                last_update=item.get("date_mod")
            ))
            
        return contracts

    async def search(
        self,
        name: str | None = None,
        num: str | None = None,
        id: int | None = None,
        limit: int = 50,
    ) -> list[ContractResponse]:
        """Search contracts by name, number or ID using GLPI's searchText.

        Args:
            name: Contract name search string
            num: Contract number search string
            id: Contract ID
            limit: Maximum results to return

        Returns:
            List of matching contracts
        """
        params: dict[str, Any] = {"expand_dropdowns": "true"}
        
        if name:
            params["searchText[name]"] = name
        if num:
            params["searchText[num]"] = num
        if id:
            params["searchText[id]"] = str(id)

        # The API returns a list of results
        results = await self.client.get(self.endpoint, params=params)
        
        if not isinstance(results, list):
            # Sometimes GLPI returns a single dict if there's only one result? 
            # Usually it's a list for search queries.
            results = [results] if results else []

        contracts = []
        for item in results[:limit]:
            contracts.append(ContractResponse(
                id=item.get("id"),
                name=item.get("name"),
                num=item.get("num"),
                begin_date=item.get("begin_date"),
                end_date=item.get("end_date"),
                comment=item.get("comment"),
                state=item.get("states_id"),
                last_update=item.get("date_mod")
            ))
            
        return contracts

    async def delete(self, contract_id: int, force_purge: bool = False) -> bool:
        """Delete a contract.

        Args:
            contract_id: Contract ID
            force_purge: If True, delete from database. If False, move to trash (is_deleted=1).

        Returns:
            True if successful
        """
        params = {"force_purge": "true" if force_purge else "false"}
        endpoint = f"{self.endpoint}/{contract_id}"
        return await self.client.delete(endpoint, params=params)
