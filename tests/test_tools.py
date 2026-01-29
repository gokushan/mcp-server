"""Tests for MCP tools."""

from unittest.mock import AsyncMock, patch

import pytest

from glpi_mcp_server.tools.contract_tools import create_glpi_contract
from glpi_mcp_server.tools.ticket_tools import create_ticket


@pytest.mark.asyncio
async def test_create_contract_tool():
    mock_client = AsyncMock()
    mock_client.session_token = "valid-token"
    
    with patch("glpi_mcp_server.tools.utils.get_glpi_client", return_value=mock_client):
        with patch("glpi_mcp_server.glpi.contracts.ContractManager.create") as mock_create:
            mock_create.return_value = AsyncMock(model_dump=lambda: {"id": 1, "name": "Test"})
            
            result = await create_glpi_contract(
                name="Test Contract",
                begin_date="2024-01-01"
            )
            
            assert result["id"] == 1
            assert result["name"] == "Test"
            mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_create_ticket_tool():
    mock_client = AsyncMock()
    mock_client.session_token = "valid-token"
    
    with patch("glpi_mcp_server.tools.utils.get_glpi_client", return_value=mock_client):
        with patch("glpi_mcp_server.glpi.tickets.TicketManager.create") as mock_create:
            mock_create.return_value = AsyncMock(model_dump=lambda: {"id": 100, "name": "Issue"})
            
            result = await create_ticket(
                name="Issue",
                content="Description"
            )
            
            assert result["id"] == 100
            mock_create.assert_called_once()
