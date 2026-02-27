"""[Adapter] Batch Processing Tools.
"""

from typing import Any
import os
import shutil
from pathlib import Path
from glpi_mcp_server.tools.folder_tools import read_path_allowed
from glpi_mcp_server.tools.document_tools import process_contract
from glpi_mcp_server.tools.contract_tools import create_glpi_contract
from glpi_mcp_server.processors.contract_processor import ContractProcessor
from glpi_mcp_server.tools.utils import filter_kwargs, move_file_safely, to_internal_path, to_host_path
from glpi_mcp_server.config import settings
from glpi_mcp_server.tools.error_codes import get_error_response
from glpi_mcp_server.llm.strategies import LLMCancelledError



async def tool_batch_contracts(path: str | None = None) -> dict[str, Any]:
    """Process multiple contracts in batch from allowed folders.
    
    This tool iterates through files in proper directories:
    1. Reads allowed files using 'read_path_allowed'.
    2. Extracts contract data using 'process_contract'.
    3. Creates the contract in GLPI using 'create_glpi_contract'.
    4. Attaches the source document to the created contract.
    
    Args:
        path: Optional specific allowed path to scan. 
              If None, scans all configured allowed roots.
              
    Returns:
        A dictionary containing the individual 'results' list and a global 'summary_text'.
    """
    results = []
    
    # 1. Get list of files
    try:
        read_result = await read_path_allowed(path)
        if "error_code" in read_result:
             # If read_path_allowed returned a structured error, we return it
             return {
                 "results": [{
                     "file": path or "ALL_ROOTS",
                     "status": "error",
                     "error": read_result.get("error"),
                     "error_code": read_result.get("error_code"),
                     "error_description": read_result.get("error_description")
                 }],
                 "summary_text": f"Error al listar archivos: {read_result.get('error')}"
             }
        files = read_result.get("files", [])
    except Exception as e:
        return {
            "results": [{
                "file": path or "ALL_ROOTS",
                "status": "error",
                "error": f"Unexpected error listing files: {str(e)}",
                **get_error_response(104 if "not found" in str(e).lower() else 103)
            }],
            "summary_text": f"Error crítico inesperado al listar archivos: {str(e)}"
        }

    if not files:
        return {
            "results": [],
            "summary_text": "No se encontraron archivos para procesar."
        }

    # 2. Process each file
    for file_path in files:
        result_entry = {
            "file": Path(file_path).name,
            "processed_path": None,
            "status": "pending",
            "contract_id": None,
            "document_attached": False,
            "error": None,
            "error_code": None,
            "error_description": None
        }
        
        try:
            # A. Extract Data
            extraction_result = await process_contract(file_path)
            
            # Check for prompt injection
            if extraction_result.get("prompt_injection_detected", False):
                result_entry["status"] = "error"
                result_entry["error"] = "Abortado: Se ha detectado un posible intento de inyección de código (Prompt Injection) en el contenido del archivo."
                result_entry.update(get_error_response(101))
            else:
                # Prepare data for creation
                # We filter out None values to let create_glpi_contract use defaults
                contract_data = {k: v for k, v in extraction_result.items() if v is not None}
                
                valid_data = filter_kwargs(create_glpi_contract, contract_data)
                
                creation_result = await create_glpi_contract(
                    file_path=file_path,
                    **valid_data
                )
                
                # C. Record Success
                result_entry["status"] = "success"
                result_entry["contract_id"] = creation_result.get("id")
                result_entry["contract_name"] = creation_result.get("name")
                result_entry["document_attached"] = creation_result.get("document_attached", False)
                
                if not result_entry["document_attached"]:
                     result_entry["document_error"] = creation_result.get("document_error")
                 
        except LLMCancelledError as llm_err:
            # LLM timed out or was cancelled by the MCP session
            result_entry["status"] = "error"
            result_entry["error"] = str(llm_err)
            result_entry.update(get_error_response(105))
        except Exception as e:
            # Record Failure
            result_entry["status"] = "error"
            result_entry["error"] = str(e)
            
            # Map error codes
            err_str = str(e).lower()
            if "not found" in err_str or "no exist" in err_str or "not exist" in err_str:
                result_entry.update(get_error_response(104))
            elif "not allowed" in err_str and "extension" in err_str:
                result_entry.update(get_error_response(102))
            elif "not allowed" in err_str or "denied" in err_str:
                result_entry.update(get_error_response(103))
            else:
                result_entry.update(get_error_response(100))
            
        # >> Mover el archivo a la carpeta correspondiente con nombre seguro <<
        try:
            source_path = Path(to_internal_path(file_path))
            if result_entry["status"] == "success" and settings.glpi_folder_success:
                target_dir = Path(settings.glpi_folder_success).resolve()
                new_path = move_file_safely(source_path, target_dir)
                result_entry["processed_path"] = to_host_path(new_path)
            elif result_entry["status"] == "error" and settings.glpi_folder_errores:
                target_dir = Path(settings.glpi_folder_errores).resolve()
                new_path = move_file_safely(source_path, target_dir)
                result_entry["processed_path"] = to_host_path(new_path)
        except Exception as move_error:
             result_entry["status"] = "error"
             existing_error = f"{result_entry.get('error', '')} | ".lstrip(' | ')
             result_entry["error"] = f"{existing_error}Fallo al mover archivo a carpeta destino: {str(move_error)}"
             
        results.append(result_entry)
        
   
    
    processor = ContractProcessor()
    summary_text = await processor.generate_batch_summary(results)
            
    return {
        "results": results,
        "summary_text": summary_text
    }
