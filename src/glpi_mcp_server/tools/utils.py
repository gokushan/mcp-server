"""Utilities for tools."""

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
