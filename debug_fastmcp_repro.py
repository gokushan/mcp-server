from fastmcp import FastMCP

mcp = FastMCP("Debug Server")

@mcp.resource("test://static")
def static_resource() -> str:
    return "static"

@mcp.resource("test://param/{id}")
def param_resource(id: str) -> str:
    return f"id is {id}"

@mcp.resource("test://int_param/{id}")
def int_param_resource(id: int) -> str:
    return f"id is {id}"

def main():
    print("Resources registered:")
    # Access internal resource manager if possible, or use Context if available
    if hasattr(mcp, '_resource_manager') and hasattr(mcp._resource_manager, '_resources'):
        for uri in mcp._resource_manager._resources:
            print(f"- {uri}")
            
    # Also verify if list_resources works
    try:
        print("\nListing resources via method:")
        # mcp.list_resources might be async or return a list
        # But FastMCP object might not expose it directly in the same way as the runtime
        pass 
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
