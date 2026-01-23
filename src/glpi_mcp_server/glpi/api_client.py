"""[Adapter] Secondary Adapter (Driven) for GLPI API.

This module implements the driven adapter that communicates with the external
GLPI API, handling authentication (via OAuth) and HTTP requests.
"""

import logging
from typing import Any

import httpx

from ..auth import OAuthClient
from ..config import settings

logger = logging.getLogger(__name__)


class GLPIAPIClient:
    """Base GLPI API client with OAuth 2.1 authentication.

    This class provides the foundation for all GLPI API interactions,
    handling authentication, session management, and common HTTP operations.

    Attributes:
        api_url: GLPI API base URL
        app_token: GLPI application token
        oauth_client: OAuth client for authentication
        session_token: Current GLPI session token
    """

    def __init__(
        self,
        api_url: str | None = None,
        app_token: str | None = None,
        user_token: str | None = None,
        oauth_client: OAuthClient | None = None,
    ):
        """Initialize GLPI API client.

        Args:
            api_url: GLPI API base URL (defaults to settings)
            app_token: GLPI application token (defaults to settings)
            user_token: GLPI user token for simple auth (defaults to settings)
            oauth_client: OAuth client instance (creates new if not provided)
        """
        self.api_url = (api_url or settings.glpi_api_url).rstrip("/")
        self.app_token = app_token or settings.glpi_app_token
        self.user_token = user_token or settings.glpi_user_token
        self.oauth_client = oauth_client or OAuthClient()
        self.session_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "GLPIAPIClient":
        """Async context manager entry."""
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.kill_session()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            Async HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _get_headers(self, include_session: bool = True) -> dict[str, str]:
        """Get request headers with authentication.

        Args:
            include_session: Whether to include session token

        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}"
        }

        if include_session and self.session_token:
            headers["Session-Token"] = self.session_token

        return headers

    async def init_session(self) -> str:
        """Initialize GLPI session.

        Uses either User Token (if configured) or OAuth 2.1.

        Returns:
            Session token

        Raises:
            ValueError: If authentication fails
        """
        client = await self._get_client()
        headers = await self._get_headers(include_session=False)

        if self.user_token:
            # Use User Token Auth
            # Method provided by user: Authorization: user_token <token>
            headers["Authorization"] = f"user_token {self.user_token}"
            logger.debug("Using User Token authentication")
        else:
            # Use OAuth 2.1 Auth
            # Get valid OAuth access token
            logger.debug("Using OAuth authentication")
            access_token = await self.oauth_client.ensure_valid_token()
            headers["Authorization"] = f"Bearer {access_token}"

        response = await client.get(
            f"{self.api_url}/initSession",
            headers=headers,
        )

        if response.status_code != 200:
            logger.error(f"Failed to initialize session: {response.text}")
            raise ValueError(f"Session initialization failed: {response.text}")

        data = response.json()
        self.session_token = data.get("session_token")

        if not self.session_token:
            raise ValueError("No session token received from GLPI")

        logger.info("GLPI session initialized successfully")
        return self.session_token

    async def kill_session(self) -> None:
        """Kill current GLPI session."""
        if not self.session_token:
            return

        try:
            client = await self._get_client()
            headers = await self._get_headers()

            await client.get(
                f"{self.api_url}/killSession",
                headers=headers,
            )

            logger.info("GLPI session terminated")
        except Exception as e:
            logger.warning(f"Failed to kill session: {e}")
        finally:
            self.session_token = None
            if self._client:
                await self._client.aclose()
                self._client = None

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Perform GET request to GLPI API.

        Args:
            endpoint: API endpoint (e.g., "Contract/42")
            params: Query parameters

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.session_token:
            await self.init_session()

        client = await self._get_client()
        headers = await self._get_headers()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = await client.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()

    async def post(
        self, endpoint: str, data: dict[str, Any]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Perform POST request to GLPI API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.session_token:
            await self.init_session()

        client = await self._get_client()
        headers = await self._get_headers()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = await client.post(url, headers=headers, json={"input": data})

        response.raise_for_status()
        return response.json()

    async def put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Perform PUT request to GLPI API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.session_token:
            await self.init_session()

        client = await self._get_client()
        headers = await self._get_headers()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = await client.put(url, headers=headers, json={"input": data})

        response.raise_for_status()
        return response.json()

    async def delete(self, endpoint: str) -> bool:
        """Perform DELETE request to GLPI API.

        Args:
            endpoint: API endpoint

        Returns:
            True if successful

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.session_token:
            await self.init_session()

        client = await self._get_client()
        headers = await self._get_headers()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = await client.delete(url, headers=headers)

        response.raise_for_status()
        return True

    async def search(
        self, itemtype: str, criteria: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Search for items in GLPI.

        Args:
            itemtype: Item type (e.g., "Contract", "Ticket")
            criteria: Search criteria

        Returns:
            List of matching items
        """
        params = {"criteria": criteria} if criteria else {}
        result = await self.get(f"search/{itemtype}", params=params)
        return result.get("data", [])
