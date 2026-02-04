import asyncio
import sys
from fastmcp import Client

async def main():
    print("Starting diagnostic client...")
    server_url = "http://localhost:8000/mcp"
    
    try:
        # Connect to the server using Streamable HTTP
        async with Client(server_url) as client:
            print(f"--- Connected to {server_url} ---")
            
            # List tools to verify discovery
            print("Fetching tools...")
            tools = await client.list_tools()
            print(f"Discovered {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool.name}")
            
            if any(t.name == "get_contract_status_by_id" for t in tools):
                print("\nTesting 'get_contract_status_by_id' tool call...")
                # Using a dummy ID for testing
                result = await client.call_tool("get_contract_status_by_id", {"id": 1})
                print(f"Tool Result received successfully.")
            
            if any(t.name == "search_contracts" for t in tools):
                print("\nTesting 'search_contracts' tool call...")
                result = await client.call_tool("search_contracts", {"name": "Tecno", "limit": 5})
                print(f"Tool Result received successfully. Results found.")
            else:
                print("\n'search_contracts' tool not found, skipping search test.")
                
            print("\n--- Diagnostic SUCCESS ---")
            
    except Exception as e:
        print(f"\n--- Diagnostic FAILED ---")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
