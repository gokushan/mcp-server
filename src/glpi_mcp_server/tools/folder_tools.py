"""[Adapter] Folder Management Tools.
"""

from typing import Any
from ..config import settings


async def list_folders() -> list[str]:
    """List allowed folders for file access.
    
    This tool returns the list of root directories that the MCP server
    is allowed to access.
    
    Returns:
        List of absolute paths.
    """
    return [str(path) for path in settings.allowed_roots_list]


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
                    files.append(str(child.resolve()))
                    
    return files
