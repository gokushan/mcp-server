"""MCP Workflow Prompts."""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP):
    """Register workflow prompts."""

    @mcp.prompt("process-and-create-contract")
    def process_and_create_contract(file_path: str) -> str:
        """Workflow to process a contract and create it in GLPI."""
        return f"""Please follow these steps to process the contract document at '{file_path}':

1. Use the 'process_contract' tool to extract data from the document.
2. Present the extracted data to me for review, including the Contract Name, Number, Duration, Renewal Type, SLA Info, Parties, Dates, Cost, and Summary.
3. Ask me for confirmation to proceed with creation.
4. If I confirm, use the 'create_glpi_contract' tool to create the contract in GLPI using the extracted data.
5. Provide the returned Contract ID and any warnings.
"""

    @mcp.prompt("process-and-create-invoice")
    def process_and_create_invoice(file_path: str) -> str:
        """Workflow to process an invoice and create it in GLPI."""
        return f"""Please follow these steps to process the invoice document at '{file_path}':

1. Use the 'process_invoice' tool to extract data from the document.
2. Present the extracted data for review (Vendor, Invoice Number, Dates, Total Amount, Items).
3. Ask for confirmation.
4. If confirmed, use 'create_glpi_invoice' to create it in GLPI.
5. Confirm the creation with the returned ID.
"""

    @mcp.prompt("update-contract-from-document")
    def update_contract_from_document(contract_id: str, file_path: str) -> str:
        """Workflow to update an existing contract from a new document version."""
        return f"""Please help me update Contract ID {contract_id} using the document at '{file_path}':

1. First, use 'get_contract_status' to fetch the current data for Contract {contract_id}.
2. Then, use 'process_contract' to extract data from the new document.
3. Compare the current data with the new extracted data. List specifically what has changed (e.g., end date extended, cost increased).
4. Ask me if I want to apply these updates.
5. If yes, use 'update_glpi_contract' to apply the changes.
"""

    @mcp.prompt("create-ticket-workflow")
    def create_ticket_workflow(description: str) -> str:
        """Guided ticket creation workflow."""
        return f"""Please help me create a support ticket for this issue: "{description}"

1. Analyze the issue description.
2. Suggest an appropriate Title, Ticket Type (Incident/Request), Priority, and Category based on the description.
3. Ask me if these suggestions look correct or if I want to change them.
4. Once confirmed, use 'create_ticket' to create the ticket in GLPI.
"""
