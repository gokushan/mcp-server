import asyncio
from pathlib import Path
import sys
import json
sys.path.append(str(Path.cwd() / "src"))
from glpi_mcp_server.tools.utils import get_glpi_client

async def fetch_contract(contract_id):
    async with await get_glpi_client() as client:
        data = await client.get(f"Contract/{contract_id}")
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(fetch_contract(36))
