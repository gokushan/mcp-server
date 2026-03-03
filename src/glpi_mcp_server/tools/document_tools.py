"""[Adapter] Primary Adapter (Driving) for Document Processing.

This module exposes the document processing functionality to the MCP protocol.
It acts as a driving adapter, orchestrating the processing workflow.
"""

import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..glpi.models import ProcessedContract, ProcessedInvoice
from ..processors.contract_processor import ContractProcessor
from ..processors.invoice_processor import InvoiceProcessor
from ..tools.utils import is_path_allowed, to_internal_path
from ..tools.error_codes import get_error_response, FileReadError, FileExtensionError

logger = logging.getLogger(__name__)


async def process_contract(file_path: str) -> dict[str, Any]:
    """Process a contract document and extract structured data.
    
    Args:
        file_path: Absolute path to the contract document
        
    Returns:
        Extracted contract data
    """
    file_path = to_internal_path(file_path)
    try:
        if not is_path_allowed(file_path):
            return {
                "success": False,
                "error": f"Access to path '{file_path}' is denied. Check allowed roots.",
                **get_error_response(103)
            }
        
        if not Path(file_path).exists():
             return {
                 "success": False,
                 "error": f"Path not found: {file_path}",
                 **get_error_response(104)
             }

        processor = ContractProcessor()
        result = await processor.process(file_path)
        return result.model_dump()

    except FileNotFoundError as e:
        logger.warning("[process_contract] File not found: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(104)
        }
    except FileExtensionError as e:
        logger.warning("[process_contract] Extension not allowed: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(102)
        }
    except FileReadError as e:
        logger.error("[process_contract] File read/malformed error: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(100)
        }
    except ValidationError as e:
        # Pydantic validation failed: the LLM could not extract a valid contract structure
        # (e.g. the file does not contain a contract, required fields like 'name' are null)
        logger.warning("[process_contract] Pydantic ValidationError — file may not contain a valid contract: %s", e)
        return {
            "success": False,
            "error": f"The document does not contain a valid contract structure: {e.error_count()} field(s) failed validation.",
            **get_error_response(100)
        }
    except ValueError as e:
        # Catches security errors raised by is_path_allowed
        err_str = str(e)
        logger.error("[process_contract] ValueError: %s", err_str)
        if "Security error" in err_str or "denied" in err_str.lower():
            return {
                "success": False,
                "error": err_str,
                **get_error_response(103)
            }
        return {
            "success": False,
            "error": err_str,
            **get_error_response(100)
        }
    except Exception as e:
        logger.error("[process_contract] Unexpected error: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(100)
        }


async def process_invoice(file_path: str) -> dict[str, Any]:
    """Process an invoice document and extract structured data.
    
    Args:
        file_path: Absolute path to the invoice document
        
    Returns:
        Extracted invoice data
    """
    file_path = to_internal_path(file_path)
    try:
        if not is_path_allowed(file_path):
            return {
                "success": False,
                "error": f"Access to path '{file_path}' is denied. Check allowed roots.",
                **get_error_response(103)
            }
        
        if not Path(file_path).exists():
             return {
                 "success": False,
                 "error": f"Path not found: {file_path}",
                 **get_error_response(104)
             }

        processor = InvoiceProcessor()
        result = await processor.process(file_path)
        return result.model_dump()

    except FileNotFoundError as e:
        logger.warning("[process_invoice] File not found: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(104)
        }
    except FileExtensionError as e:
        logger.warning("[process_invoice] Extension not allowed: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(102)
        }
    except FileReadError as e:
        logger.error("[process_invoice] File read/malformed error: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(100)
        }
    except ValidationError as e:
        logger.warning("[process_invoice] Pydantic ValidationError — file may not contain a valid invoice: %s", e)
        return {
            "success": False,
            "error": f"The document does not contain a valid invoice structure: {e.error_count()} field(s) failed validation.",
            **get_error_response(100)
        }
    except ValueError as e:
        err_str = str(e)
        logger.error("[process_invoice] ValueError: %s", err_str)
        if "Security error" in err_str or "denied" in err_str.lower():
            return {
                "success": False,
                "error": err_str,
                **get_error_response(103)
            }
        return {
            "success": False,
            "error": err_str,
            **get_error_response(100)
        }
    except Exception as e:
        logger.error("[process_invoice] Unexpected error: %s", e)
        return {
            "success": False,
            "error": str(e),
            **get_error_response(100)
        }
