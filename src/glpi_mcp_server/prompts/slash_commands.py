"""Slash Commands for GLPI MCP Server."""

from fastmcp import FastMCP


def register_slash_commands(mcp: FastMCP):
    """Register all slash commands."""

    # ===== CONTRACTS =====
    
    @mcp.prompt("contract-create")
    def contract_create(
        name: str,
        begin_date: str,
        end_date: str = "",
        cost: str = "",
        renewal: str = "manual"
    ) -> str:
        """Create a new contract.
        
        Usage: /contract-create name="Name" begin_date="2026-01-01"
        """
        renewal_map = {"none": "0", "auto": "1", "manual": "2"}
        renewal_type = renewal_map.get(renewal.lower(), "2")
        
        return f"""Create a new contract in GLPI:

**Data:**
- Name: {name}
- Start: {begin_date}
- End: {end_date or "Not specified"}
- Cost: {cost or "Not specified"}
- Renewal: {renewal} (type {renewal_type})

**Steps:**
1. Use 'create_glpi_contract' tool
2. Show created contract ID
"""

    @mcp.prompt("contract-process")
    def contract_process(file_path: str, auto_create: str = "false") -> str:
        """Process contract document.
        
        Usage: /contract-process file_path="/path/file.pdf" auto_create="true"
        """
        auto = auto_create.lower() == "true"
        
        prompt = f"""Process contract document: {file_path}

**Steps:**
1. Use 'process_contract' to extract data
2. Display extracted information
"""
        
        if auto:
            prompt += "3. Auto-create in GLPI using 'create_glpi_contract'\n"
        else:
            prompt += "3. Ask for confirmation\n4. If confirmed, create in GLPI\n"
        
        return prompt

    @mcp.prompt("contract-status")
    def contract_status(id: str) -> str:
        """Get contract status.
        
        Usage: /contract-status id="123"
        """
        return f"""Get details for Contract ID {id}:

Use 'get_contract_status' tool and display:
- Name, number, dates
- Financial info
- Current state
- Supplier details
"""