from pathlib import Path
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
