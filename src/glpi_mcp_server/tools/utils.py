from pathlib import Path
from typing import Mapping
from ..glpi.api_client import GLPIAPIClient


async def get_glpi_client() -> GLPIAPIClient:
    """Get authenticated GLPI client."""
    client = GLPIAPIClient()
    # Ensure session is initialized
    try:
        if not client.session_token:
            await client.init_session()
    except Exception:
        # If initialization fails, new calls will try to re-init
        pass
    return client


def to_host_path(internal_path: str | Path) -> str:
    """Translate an internal container path to a host path.
    
    Args:
        internal_path: The path inside the container.
        
    Returns:
        The corresponding host path, or the original path if no match.
    """
    from ..config import settings
    
    p = str(Path(internal_path).resolve())
    
    # 1. Check success/error folders
    int_success = str(settings.folder_success_path) if settings.folder_success_path else None
    int_errores = str(settings.folder_errores_path) if settings.folder_errores_path else None
    
    if int_success and p.startswith(int_success):
        return p.replace(int_success, settings.host_folder_success or int_success, 1)
    
    if int_errores and p.startswith(int_errores):
        return p.replace(int_errores, settings.host_folder_errores or int_errores, 1)
    
    # 2. Check roots
    int_roots = [str(r) for r in settings.allowed_roots_list]
    host_roots = settings.host_allowed_roots_list
    
    # Use zip to map 1:1 by order
    for int_root, host_root in zip(int_roots, host_roots):
        if p.startswith(int_root):
            return p.replace(int_root, host_root, 1)
            
    return p


def to_internal_path(host_path: str | Path) -> str:
    """Translate a host path to an internal container path.
    
    Args:
        host_path: The path on the host.
        
    Returns:
        The corresponding internal path, or the original path if no match.
    """
    from ..config import settings
    
    h = str(host_path)
    
    # 1. Check success/error folders
    host_success = settings.host_folder_success
    host_errores = settings.host_folder_errores
    
    if host_success and h.startswith(host_success):
        int_path = str(settings.folder_success_path) if settings.folder_success_path else host_success
        return h.replace(host_success, int_path, 1)
        
    if host_errores and h.startswith(host_errores):
        int_path = str(settings.folder_errores_path) if settings.folder_errores_path else host_errores
        return h.replace(host_errores, int_path, 1)
        
    # 2. Check roots
    int_roots = [str(r) for r in settings.allowed_roots_list]
    host_roots = settings.host_allowed_roots_list
    
    for host_root, int_root in zip(host_roots, int_roots):
        if h.startswith(host_root):
            return h.replace(host_root, int_root, 1)
            
    return h


def is_path_allowed(path_str: str) -> bool:
    """Check if the path is allowed based on configured roots.
    
    Args:
        path_str: Absolute path to check
        
    Returns:
        True if allowed, False otherwise
    """
    from ..config import settings
    
    # 1. Path Traversal Check (Prevention)
    if ".." in path_str:
        raise ValueError(f"Security error: Path traversal attempt detected in '{path_str}'")

    allowed_roots = settings.allowed_roots_list
    if not allowed_roots:
        raise ValueError("Security error: No allowed roots configured on server")
        
    try:
        path_obj = Path(path_str)
        
        # 2. Symlink Check (on the file itself)
        if path_obj.exists() and path_obj.is_symlink():
            raise ValueError(f"Security error: Path '{path_str}' is a symbolic link, which is not allowed")

        # 3. Resolution and Root Verification
        target_path = path_obj.resolve()
        
        for root in allowed_roots:
            if target_path.is_relative_to(root):
                return True
                
        raise ValueError(f"Security error: Path '{path_str}' is outside of all allowed root directories")
    except (ValueError, RuntimeError) as e:
        if isinstance(e, ValueError) and "Security error" in str(e):
            raise
        return False


def filter_kwargs(func, kwargs: dict) -> dict:
    """Filter kwargs to ONLY include those that the function accepts.
    
    This is useful for passing dictionary data to functions that don't
    support **kwargs (like FastMCP tools).
    """
    import inspect
    sig = inspect.signature(func)
    return {
        k: v for k, v in kwargs.items() 
        if k in sig.parameters
    }


def move_file_safely(source_path: str | Path, target_dir: str | Path) -> Path:
    """Move a file to a target directory with a unique name to avoid collisions.
    
    The new filename will have the format: YYYYMMDD_HHMMSS_RANDOM_original_name
    
    Args:
        source_path: Path to the source file
        target_dir: Path to the destination directory
        
    Returns:
        The new Path of the moved file
    """
    import shutil
    import datetime
    import secrets
    import string

    src = Path(source_path)
    dst_dir = Path(target_dir).resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    
    new_filename = f"{timestamp}_{random_suffix}_{src.name}"
    target_path = dst_dir / new_filename
    
    shutil.move(str(src), str(target_path))
    return target_path
