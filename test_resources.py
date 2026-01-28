"""Test script to verify MCP resources are registered."""

from glpi_mcp_server.server import mcp

def main():
    print("=== MCP Server Resources ===\n")
    
    # Get all registered resources
    if hasattr(mcp, '_resource_manager') and hasattr(mcp._resource_manager, '_resources'):
        resources = mcp._resource_manager._resources
        print(f"Total resources registered: {len(resources)}\n")
        
        for uri_template, handler in resources.items():
            print(f"✓ Resource: {uri_template}")
            if hasattr(handler, '__doc__') and handler.__doc__:
                print(f"  Description: {handler.__doc__.strip()}")
            print()
    else:
        print("Could not access resource manager")
        print(f"MCP object attributes: {dir(mcp)}")

if __name__ == "__main__":
    main()
