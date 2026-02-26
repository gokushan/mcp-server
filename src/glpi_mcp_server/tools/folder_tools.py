"""[Adapter] Folder Management Tools.
"""

from typing import Any
from ..config import settings
from .utils import to_host_path, to_internal_path
import os
from pathlib import Path
from .error_codes import get_error_response


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
    
    def is_dir_accessible(p: Path) -> bool:
        """Check if a path is an existing, searchable, and readable directory."""
        try:
            return p.exists() and p.is_dir() and os.access(p, os.R_OK | os.X_OK)
        except Exception:
            return False

    # 1. Source folders (to process)
    for p in settings.allowed_roots_list:
        if is_dir_accessible(p):
            result["to_process"].append(to_host_path(p))
        else:
            all_ok = False
            
    # 2. Processed folder
    if settings.folder_success_path:
        p = settings.folder_success_path
        if is_dir_accessible(p):
            result["processed"].append(to_host_path(p))
        else:
            all_ok = False
            
    # 3. Errors folder
    if settings.folder_errores_path:
        p = settings.folder_errores_path
        if is_dir_accessible(p):
            result["errors"].append(to_host_path(p))
        else:
            all_ok = False
            
    result["success"] = all_ok
    return result


async def read_path_allowed(path: str | None = None) -> dict[str, Any]:
    """List allowed files in a directory or all allowed roots.
    
    This tool lists files with allowed extensions (PDF, TXT, DOC, DOCX) 
    in the specified path (must be an allowed root or subfolder) or, 
    if no path is provided, in all configured allowed root directories.
    
    Args:
        path: Optional absolute path to scan. If None, scans all allowed roots.
    
    Returns:
        Dictionary with 'files' (list) and optionally 'error', 'error_code', 'error_description'.
    """
    from ..tools.utils import is_path_allowed
    from pathlib import Path
    
    # Translate host path to internal path if provided
    if path:
        path = to_internal_path(path)
    
    files = []
    allowed_exts = set(settings.allowed_extensions_list)
    
    paths_to_scan = []
    
    try:
        if path:
            if not is_path_allowed(path):
                 return {
                     "files": [],
                     "error": f"Access to path '{path}' is denied. Check allowed roots.",
                     **get_error_response(103)
                 }
            
            p_obj = Path(path)
            if not p_obj.exists():
                 return {
                     "files": [],
                     "error": f"Path not found: {path}",
                     **get_error_response(104)
                 }
            if not p_obj.is_dir():
                 return {
                     "files": [],
                     "error": f"Path is not a directory: {path}",
                     **get_error_response(100) # Malformed/Unreadable context
                 }
            paths_to_scan.append(p_obj)
        else:
            paths_to_scan = settings.allowed_roots_list
            
        for p in paths_to_scan:
            try:
                # Use a safer check for directory existence/accessibility
                try:
                    is_dir = p.is_dir()
                except (PermissionError, OSError):
                    if path:
                        return {
                            "files": [],
                            "error": f"Permission denied accessing root path: {p}",
                            **get_error_response(103)
                        }
                    continue

                if not is_dir:
                    continue
                    
                # Iterate directory
                try:
                    for child in p.iterdir():
                        try:
                            if child.is_file():
                                # Check extension (case insensitive)
                                ext = child.suffix.lower().lstrip(".")
                                if ext in allowed_exts:
                                    # Translate to host path
                                    files.append(to_host_path(child))
                        except (PermissionError, OSError):
                            # Skip individual files we can't access
                            continue
                except (PermissionError, OSError) as e:
                     # This happens if p.iterdir() fails immediately
                     if path:
                          return {
                              "files": [],
                              "error": f"Permission denied listing items in: {p}",
                              **get_error_response(103)
                          }
                     continue

            except Exception as e:
                 if path:
                      return {
                          "files": [],
                          "error": f"Unexpected error scanning path {p}: {str(e)}",
                          **get_error_response(100)
                      }
                 continue
                 
        return {"files": files, "success": True}
        
    except Exception as e:
        err_str = str(e).lower()
        code = 100
        if "denied" in err_str or "not allowed" in err_str:
            code = 103
        elif "not found" in err_str:
            code = 104
            
        return {
            "files": [],
            "error": str(e),
            **get_error_response(code)
        }
