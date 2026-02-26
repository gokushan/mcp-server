import asyncio
import sys
from glpi_mcp_server.tools.folder_tools import list_folders
from glpi_mcp_server.config import settings
import json

async def main():
    print("Allowed roots:")
    for p in settings.allowed_roots_list:
        print(f" - {p}")
        print(f"   exists: {p.exists()}")
        print(f"   is_dir: {p.is_dir()}")
        import os
        print(f"   access R_OK|X_OK: {os.access(p, os.R_OK | os.X_OK)}")
        print()
    res = await list_folders()
    print("list_folders() result:")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
