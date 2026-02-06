"""[Composition Root] Application Entry Point.

This module is the Composition Root where all dependencies are wired together.
It configures the FastMCP server and registers tools, resources, and prompts.
The actual Primary Adapters are the tool functions in the tools/ directory.
"""

from fastmcp import FastMCP

from glpi_mcp_server.config import settings
from glpi_mcp_server.processors.contract_processor import ContractProcessor
from glpi_mcp_server.processors.invoice_processor import InvoiceProcessor
from glpi_mcp_server.prompts.workflow_prompts import register_prompts
from glpi_mcp_server.resources.glpi_resources import register_resources


# Import Tools
from glpi_mcp_server.tools.contract_tools import (
    create_glpi_contract,
    update_glpi_contract,
    get_contract_status_by_id,
    search_contracts,
    attach_document_to_contract,
    delete_glpi_contract
)
from glpi_mcp_server.tools.invoice_tools import (
    create_glpi_invoice,
    update_glpi_invoice,
    get_invoice_status
)
from glpi_mcp_server.tools.ticket_tools import (
    create_ticket,
    update_ticket,
    get_ticket_status
)
from glpi_mcp_server.tools.document_tools import (
    process_contract,
    process_invoice
)
from glpi_mcp_server.tools.folder_tools import list_folders, read_path_allowed
from glpi_mcp_server.tools.batch_tools import tool_batch_contracts
from glpi_mcp_server.tools.utils import is_path_allowed

# Initialize MCP Server
mcp = FastMCP("GLPI MCP Server")


# --- Register Tools ---
# Registering imported tools explicitly
mcp.tool()(process_contract)
mcp.tool()(process_invoice)

mcp.tool()(create_glpi_contract)
mcp.tool()(update_glpi_contract)
mcp.tool()(get_contract_status_by_id)
mcp.tool()(search_contracts)
mcp.tool()(attach_document_to_contract)
mcp.tool()(delete_glpi_contract)

mcp.tool()(create_glpi_invoice)
mcp.tool()(update_glpi_invoice)
mcp.tool()(get_invoice_status)

mcp.tool()(create_ticket)
mcp.tool()(update_ticket)
mcp.tool()(get_ticket_status)

mcp.tool(name="list_folders")(list_folders)
mcp.tool(name="read_path_allowed")(read_path_allowed)
mcp.tool(name="tool_batch_contracts")(tool_batch_contracts)


# --- Register Resources and Prompts ---
register_resources(mcp)
register_prompts(mcp)


def main():
    """Run server."""
    # Validate configuration
    try:
        settings.validate_llm_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Note: LLM configuration is only required for document processing tools.")
        print("Other tools will work without LLM configuration.")
    
    # If I am in docker, I need to use 0.0.0.0. to accept all external connections    
    mcp.run(
        transport=settings.mcp_transport, 
        host=settings.mcp_host, 
        port=settings.mcp_port
    )



if __name__ == "__main__":
    main()
