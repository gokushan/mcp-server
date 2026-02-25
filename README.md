# GLPI MCP Server

MCP Server for GLPI integration with OAuth 2.1 authentication and document processing capabilities.

## Features

- 🔐 **OAuth 2.1 Authentication** with PKCE for secure API access
- 📄 **Document Processing** for contracts and invoices (PDF/Word)
- 🔧 **GLPI Integration** for contracts, invoices, and tickets
- 🤖 **AI-Powered Extraction** using LLMs to parse documents
- 📊 **MCP Resources** for querying GLPI data
- 🔄 **Workflow Prompts** for guided operations

## Installation

### Prerequisites

- Python 3.10 or higher
- GLPI instance
- API access to an LLM (OpenAI, Anthropic, or local Ollama)

### Setup

1. Clone the repository:
```bash
cd /home/gokushan/proyectos-mcp/glpi-mcp/server
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Configure OAuth 2.1 in GLPI:
   - Go to Setup > General > API
   - Enable OAuth 2.1
   - Create a new OAuth client
   - Copy Client ID and Client Secret to .env

## Configuration

Edit `.env` file with your settings:

```env
# GLPI OAuth 2.1
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://your-glpi.example.com/oauth/authorize
OAUTH_TOKEN_URL=https://your-glpi.example.com/oauth/token

# GLPI API
GLPI_API_URL=https://your-glpi.example.com/apirest.php
GLPI_APP_TOKEN=your-app-token

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
```

## Usage

### Running the Server

```bash
glpi-mcp-server
```

Or with Python:
```bash
python -m glpi_mcp_server.server
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "glpi": {
      "command": "python",
      "args": ["-m", "glpi_mcp_server.server"],
      "env": {
        "GLPI_API_URL": "https://your-glpi.example.com/apirest.php",
        "OAUTH_CLIENT_ID": "your-client-id"
      }
    }
  }
}
```

## Available Tools

### Document Processing
- `process_contract` - Extract data from contract documents
- `process_invoice` - Extract data from invoice documents

### Contract Management
- `create_glpi_contract` - Create new contract in GLPI
- `update_glpi_contract` - Update existing contract
- `get_contract_status_by_id` - Query contract details by ID
- `search_contracts` - Search for contracts by name or number
- `delete_glpi_contract` - Delete a contract and its documents
- `attach_document_to_contract` - Attach a file to an existing contract

### Invoice Management
- `create_glpi_invoice` - Create new invoice in GLPI
- `update_glpi_invoice` - Update existing invoice
- `get_invoice_status` - Query invoice details

### Ticket Management
- `create_ticket` - Create support ticket
- `update_ticket` - Update ticket or add followup
- `get_ticket_status` - Query ticket details

### Folder & Batch Operations
- `list_folders` - List directories within allowed roots (supports path translation)
- `read_path_allowed` - List files in an allowed path (supports path translation)
- `tool_batch_contracts` - Process multiple contracts in batch

## Available Resources

- `glpi://contracts/{id}` - Contract details (JSON)
- `glpi://contracts/list` - List of all active contracts
- `glpi://invoices/{id}` - Invoice details
- `glpi://invoices/list` - List of invoices
- `glpi://tickets/{id}` - Ticket details
- `glpi://tickets/list` - List of tickets

## Available Prompts

- `process-and-create-contract` - Workflow to extract and create a contract
- `process-and-create-invoice` - Workflow to extract and create an invoice
- `update-contract-from-document` - Guided update of an existing contract
- `find-contract` - Search and retrieve contract info
- `create-ticket-workflow` - Guided support ticket creation
- `process-batch-contracts` - Orchestrate batch processing of folders
- `delete-contract` - Safe deletion flow (with confirmation)

## Documentation

For more detailed information, please refer to the following guides:

- [Startup Guide](docs/STARTUP_GUIDE.md) - How to run the server in different modes
- [Deployment Guide](docs/DEPLOYMENT.md) - Remote deployment and production setup
- [Git Workflow](docs/WORKFLOW_GIT.md) - Internal development processes

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Architecture

The server follows SOLID principles with clear separation of concerns:

- **auth/** - OAuth 2.1 authentication
- **processors/** - Document parsing and AI extraction
- **glpi/** - GLPI API client and models
- **tools/** - MCP tool implementations
- **resources/** - MCP resource implementations
- **prompts/** - MCP prompt implementations
- **config/** - Configuration management

## Security

- OAuth 2.1 with PKCE for authorization
- Secure token storage with encryption
- Automatic token refresh
- API request validation
- Input sanitization

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
