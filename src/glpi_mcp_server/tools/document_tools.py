"""[Adapter] Primary Adapter (Driving) for Document Processing.

This module exposes the document processing functionality to the MCP protocol.
It acts as a driving adapter, orchestrating the processing workflow.
"""

from pathlib import Path
from typing import Any

from ..glpi.models import ProcessedContract, ProcessedInvoice
from ..processors.contract_processor import ContractProcessor
from ..processors.invoice_processor import InvoiceProcessor


async def process_contract(file_path: str) -> dict[str, Any]:
    """Process a contract document and extract structured data.
    
    Args:
        file_path: Absolute path to the contract document
        
    Returns:
        Extracted contract data
    """
    processor = ContractProcessor()
    result = await processor.process(file_path)
    return result.model_dump()


async def process_invoice(file_path: str) -> dict[str, Any]:
    """Process an invoice document and extract structured data.
    
    Args:
        file_path: Absolute path to the invoice document
        
    Returns:
        Extracted invoice data
    """
    processor = InvoiceProcessor()
    result = await processor.process(file_path)
    return result.model_dump()
