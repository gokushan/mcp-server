"""[Adapter] Folder Management Tools.
"""

from typing import Any
from ..config import settings
from .utils import to_host_path, to_internal_path


async def list_folders() -> dict[str, Any]:
    """List allowed folders for file access categorized by purpose.
    
    This tool returns a dictionary of directories the MCP server
    is allowed to access, categorized by their use:
    - to_process: Source directories where files are picked up.
    - processed: Directory where successfully processed files are moved.
    - errors: Directory where failed files are moved.
    - success: Boolean indicating if all defined paths are accessible.
    
    Returns:
        Dictionary with categories of absolute paths and overall status.
    """
    result = {
        "to_process": [],
        "processed": [],
        "errors": [],
        "success": True
    }
    
    all_ok = True
    
    # 1. Source folders (to process)
    for p in settings.allowed_roots_list:
        try:
            if p.exists() and p.is_dir():
                result["to_process"].append(to_host_path(p))
            else:
                all_ok = False
        except Exception:
            all_ok = False
            continue
            
    # 2. Processed folder
    if settings.folder_success_path:
        p = settings.folder_success_path
        try:
            if p.exists() and p.is_dir():
                result["processed"].append(to_host_path(p))
            else:
                all_ok = False
        except Exception:
            all_ok = False
            
    # 3. Errors folder
    if settings.folder_errores_path:
        p = settings.folder_errores_path
        try:
            if p.exists() and p.is_dir():
                result["errors"].append(to_host_path(p))
            else:
                all_ok = False
        except Exception:
            all_ok = False
            
    result["success"] = all_ok
    return result


async def read_path_allowed(path: str | None = None) -> list[str]:
    """List allowed files in a directory or all allowed roots.
    
    This tool lists files with allowed extensions (PDF, TXT, DOC, DOCX) 
    in the specified path (must be an allowed root or subfolder) or, 
    if no path is provided, in all configured allowed root directories.
    
    Args:
        path: Optional absolute path to scan. If None, scans all allowed roots.
    
    Returns:
        List of absolute paths to allowed files.
    """
    from ..tools.utils import is_path_allowed
    from pathlib import Path
    
    # Translate host path to internal path if provided
    if path:
        path = to_internal_path(path)
    
    files = []
    allowed_exts = set(settings.allowed_extensions_list)
    
    paths_to_scan = []
    
    if path:
        if not is_path_allowed(path):
             raise ValueError(f"Access to path '{path}' is denied. Check allowed roots.")
        paths_to_scan.append(Path(path))
    else:
        paths_to_scan = settings.allowed_roots_list
        
    for p in paths_to_scan:
        if not p.exists() or not p.is_dir():
            continue
            
        for child in p.iterdir():
            if child.is_file():
                # Check extension (case insensitive)
                ext = child.suffix.lower().lstrip(".")
                if ext in allowed_exts:
                    files.append(to_host_path(child))
                    
    return files
