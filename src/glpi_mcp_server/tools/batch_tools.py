"""[Adapter] Batch Processing Tools.
"""

from typing import Any
from glpi_mcp_server.tools.folder_tools import read_path_allowed
from glpi_mcp_server.tools.document_tools import process_contract
from glpi_mcp_server.tools.contract_tools import create_glpi_contract


async def tool_batch_contracts(path: str | None = None) -> list[dict[str, Any]]:
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
        A list of results for each file processed, including success/failure status
        and details about the created contract/document.
    """
    results = []
    
    # 1. Get list of files
    try:
        files = await read_path_allowed(path)
    except Exception as e:
        return [{
            "file": path or "ALL_ROOTS",
            "status": "error",
            "error": f"Failed to list files: {str(e)}"
        }]

    if not files:
        return []

    # 2. Process each file
    for file_path in files:
        result_entry = {
            "file": file_path,
            "status": "pending",
            "contract_id": None,
            "document_attached": False,
            "error": None
        }
        
        try:
            # A. Extract Data
            extraction_result = await process_contract(file_path)
            
            # Prepare data for creation
            # We filter out None values to let create_glpi_contract use defaults
            contract_data = {k: v for k, v in extraction_result.items() if v is not None}
            
            # B. Create Contract (this tool also handles document attachment)
            creation_result = await create_glpi_contract(
                file_path=file_path,
                **contract_data
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
            
        results.append(result_entry)
        
    return results
