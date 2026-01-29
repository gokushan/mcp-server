"""Tests for GLPI API client."""

from unittest.mock import AsyncMock, patch

import pytest

from glpi_mcp_server.glpi.api_client import GLPIAPIClient


@pytest.fixture
def api_client():
    mock_oauth = AsyncMock()
    mock_oauth.ensure_valid_token.return_value = "token"
    return GLPIAPIClient(
        api_url="http://test.com",
        app_token="app-token",
        oauth_client=mock_oauth
    )


@pytest.mark.asyncio
async def test_init_session(api_client):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"session_token": "sess-token"}
        mock_get.return_value = mock_response
        
        token = await api_client.init_session()
        
        assert token == "sess-token"
        assert api_client.session_token == "sess-token"


@pytest.mark.asyncio
async def test_get_request(api_client):
    api_client.session_token = "sess-token"
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        mock_get.return_value = mock_response
        
        result = await api_client.get("item/1")
        
        assert result["id"] == 1
        mock_get.assert_called_with(
            "http://test.com/item/1",
            headers={
                "Content-Type": "application/json",
                "App-Token": "app-token",
                "Session-Token": "sess-token"
            },
            params=None
        )
