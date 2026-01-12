"""Main MCP Server entry point."""

from fastmcp import FastMCP

from .config import settings
from .prompts.workflow_prompts import register_prompts
from .resources.glpi_resources import register_resources
from .tools.contract_tools import (
    create_glpi_contract,
    get_contract_status,
    update_glpi_contract,
)
from .tools.document_tools import process_contract, process_invoice
from .tools.invoice_tools import (
    create_glpi_invoice,
    get_invoice_status,
    update_glpi_invoice,
)
from .tools.ticket_tools import create_ticket, get_ticket_status, update_ticket

# Initialize MCP Server
mcp = FastMCP(
    "GLPI MCP Server",
    dependencies=["httpx", "pydantic", "pdfplumber", "python-docx", "authlib"],
)

# --- Register Tools ---

# Document Processing Tools
mcp.add_tool(process_contract)
mcp.add_tool(process_invoice)

# Contract Management Tools
mcp.add_tool(create_glpi_contract)
mcp.add_tool(update_glpi_contract)
mcp.add_tool(get_contract_status)

# Invoice Management Tools
mcp.add_tool(create_glpi_invoice)
mcp.add_tool(update_glpi_invoice)
mcp.add_tool(get_invoice_status)

# Ticket Management Tools
mcp.add_tool(create_ticket)
mcp.add_tool(update_ticket)
mcp.add_tool(get_ticket_status)

# --- Register Resources ---
register_resources(mcp)

# --- Register Prompts ---
register_prompts(mcp)


def main():
    """Run server."""
    # Validate configuration
    try:
        settings.validate_llm_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    mcp.run()


if __name__ == "__main__":
    main()
