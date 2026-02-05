"""Tests for document processors."""

from unittest.mock import MagicMock, patch

import pytest

from glpi_mcp_server.processors.contract_processor import ContractProcessor
from glpi_mcp_server.processors.document_parser import DocumentParser
from glpi_mcp_server.processors.invoice_processor import InvoiceProcessor


@pytest.fixture
def mock_parser():
    with patch("glpi_mcp_server.processors.base_processor.DocumentParser") as mock:
        yield mock


@pytest.mark.asyncio
async def test_contract_processor_flow(mock_parser):
    # Mock LLM response
    mock_data = {
        "contract_name": "Test Contract",
        "parties": {"client": "A", "provider": "B"},
        "summary": "Summary"
    }
    
    # Mock llm_provider to openai to match the response mock
    with patch("glpi_mcp_server.processors.contract_processor.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_api_key = "key"
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": str(mock_data).replace("'", '"')}}]
            }
            mock_post.return_value = mock_response
            
            processor = ContractProcessor()
            # Mock extract_text
            processor.parser.extract_text = MagicMock(return_value="Contract content")
            
            result = await processor.process("dummy.pdf")
            
            assert result.name == "Test Contract"
            assert result.summary == "Summary"


@pytest.mark.asyncio
async def test_invoice_processor_flow():
    mock_data = {
        "invoice_number": "INV-001",
        "name": "Test Invoice",
        "vendor": "Vendor",
        "client": "Client",
        "invoice_date": "2024-01-01",
        "subtotal": 100.0,
        "total": 121.0
    }
    
    # Mock llm_provider to openai
    with patch("glpi_mcp_server.processors.invoice_processor.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_api_key = "key"

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": str(mock_data).replace("'", '"')}}]
            }
            mock_post.return_value = mock_response
            
            processor = InvoiceProcessor()
            processor.parser.extract_text = MagicMock(return_value="Invoice content")
            
            result = await processor.process("dummy.pdf")
            
            assert result.number == "INV-001"
            assert result.total == 121.0
