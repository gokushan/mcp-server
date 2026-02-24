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
from glpi_mcp_server.tools.utils import filter_kwargs, move_file_safely
from glpi_mcp_server.config import settings



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
        files = await read_path_allowed(path)
    except Exception as e:
        return {
            "results": [{
                "file": path or "ALL_ROOTS",
                "status": "error",
                "error": f"Failed to list files: {str(e)}"
            }],
            "summary_text": f"Error crítico al intentar listar los archivos: {str(e)}"
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
            "error": None
        }
        
        try:
            # A. Extract Data
            extraction_result = await process_contract(file_path)
            
            # Check for prompt injection
            if extraction_result.get("prompt_injection_detected", False):
                result_entry["status"] = "error"
                result_entry["error"] = "Abortado: Se ha detectado un posible intento de inyección de código (Prompt Injection) en el contenido del archivo."
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
                 
        except Exception as e:
            # Record Failure
            result_entry["status"] = "error"
            result_entry["error"] = str(e)
            
        # >> Mover el archivo a la carpeta correspondiente con nombre seguro <<
        try:
            source_path = Path(file_path)
            if result_entry["status"] == "success" and settings.glpi_folder_success:
                target_dir = Path(settings.glpi_folder_success).resolve()
                new_path = move_file_safely(source_path, target_dir)
                result_entry["processed_path"] = str(new_path)
            elif result_entry["status"] == "error" and settings.glpi_folder_errores:
                target_dir = Path(settings.glpi_folder_errores).resolve()
                new_path = move_file_safely(source_path, target_dir)
                result_entry["processed_path"] = str(new_path)
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
