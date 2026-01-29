"""Test script to verify MCP resources are registered with detailed info."""

from glpi_mcp_server.server import mcp
import inspect

def main():
    print("=== MCP Server Resources (Detailed) ===\n")
    
    # Get all registered resources
    if hasattr(mcp, '_resource_manager') and hasattr(mcp._resource_manager, '_resources'):
        resources = mcp._resource_manager._resources
        print(f"Total resources registered: {len(resources)}\n")
        
        for uri_template, handler in resources.items():
            print(f"✓ Resource URI: {uri_template}")
            print(f"  Handler: {handler}")
            
            # Try to get the actual function
            if hasattr(handler, '_func'):
                func = handler._func
                print(f"  Function: {func.__name__}")
                sig = inspect.signature(func)
                print(f"  Signature: {sig}")
            
            print()
    else:
        print("Could not access resource manager")
        print(f"\nMCP object type: {type(mcp)}")
        print(f"MCP object attributes: {[attr for attr in dir(mcp) if not attr.startswith('_')]}")
        
    # Try to list resources using MCP's list_resources method
    print("\n=== Trying mcp.list_resources() ===")
    try:
        if hasattr(mcp, 'list_resources'):
            resources_list = mcp.list_resources()
            print(f"Resources from list_resources(): {resources_list}")
    except Exception as e:
        print(f"Error calling list_resources(): {e}")

if __name__ == "__main__":
    main()
