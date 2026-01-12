"""OAuth 2.1 client implementation with PKCE support."""

import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from authlib.integrations.httpx_client import OAuth2Client

from ..config import settings


class TokenStorage:
    """Secure token storage with encryption."""

    def __init__(self, storage_path: Path):
        """Initialize token storage.

        Args:
            storage_path: Path to store tokens
        """
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_token(self, token: dict[str, Any]) -> None:
        """Save token to storage.

        Args:
            token: OAuth token dictionary
        """
        # Add timestamp for expiration tracking
        token["stored_at"] = datetime.now().isoformat()

        # In production, encrypt the token before storing
        # For now, we'll store as JSON (TODO: Add encryption)
        with open(self.storage_path, "w") as f:
            json.dump(token, f, indent=2)

    def load_token(self) -> dict[str, Any] | None:
        """Load token from storage.

        Returns:
            Token dictionary or None if not found
        """
        if not self.storage_path.exists():
            return None

        try:
            with open(self.storage_path, "r") as f:
                token = json.load(f)
            return token
        except (json.JSONDecodeError, IOError):
            return None

    def clear_token(self) -> None:
        """Clear stored token."""
        if self.storage_path.exists():
            self.storage_path.unlink()


class OAuthClient:
    """OAuth 2.1 client with PKCE support for GLPI authentication.

    This class implements the OAuth 2.1 authorization code flow with PKCE
    (Proof Key for Code Exchange) for enhanced security.

    Attributes:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        authorization_url: OAuth authorization endpoint
        token_url: OAuth token endpoint
        redirect_uri: OAuth redirect URI
        token_storage: Token storage instance
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        authorization_url: str | None = None,
        token_url: str | None = None,
        redirect_uri: str | None = None,
        token_storage_path: Path | None = None,
    ):
        """Initialize OAuth client.

        Args:
            client_id: OAuth client ID (defaults to settings)
            client_secret: OAuth client secret (defaults to settings)
            authorization_url: Authorization endpoint (defaults to settings)
            token_url: Token endpoint (defaults to settings)
            redirect_uri: Redirect URI (defaults to settings)
            token_storage_path: Path to store tokens (defaults to settings)
        """
        self.client_id = client_id or settings.oauth_client_id
        self.client_secret = client_secret or settings.oauth_client_secret
        self.authorization_url = authorization_url or settings.oauth_authorization_url
        self.token_url = token_url or settings.oauth_token_url
        self.redirect_uri = redirect_uri or settings.oauth_redirect_uri

        storage_path = token_storage_path or settings.token_storage_path
        self.token_storage = TokenStorage(storage_path)

        self._client: OAuth2Client | None = None
        self._code_verifier: str | None = None

    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(
            "utf-8"
        )
        code_verifier = code_verifier.rstrip("=")

        # Generate code challenge (SHA256 hash of verifier)
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.rstrip("=")

        return code_verifier, code_challenge

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """Get authorization URL for user to visit.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Tuple of (authorization_url, state)
        """
        # Generate PKCE pair
        self._code_verifier, code_challenge = self._generate_pkce_pair()

        # Generate state if not provided
        if state is None:
            state = secrets.token_urlsafe(32)

        # Create OAuth client
        self._client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
        )

        # Generate authorization URL with PKCE
        auth_url, _ = self._client.create_authorization_url(
            self.authorization_url,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )

        return auth_url, state

    async def exchange_code_for_token(
        self, authorization_response: str
    ) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            authorization_response: Full callback URL with code

        Returns:
            Token dictionary

        Raises:
            ValueError: If code verifier is missing or token exchange fails
        """
        if not self._code_verifier:
            raise ValueError("Authorization flow not initiated")

        if not self._client:
            self._client = OAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
            )

        # Exchange code for token with PKCE verifier
        token = await self._client.fetch_token(
            self.token_url,
            authorization_response=authorization_response,
            code_verifier=self._code_verifier,
        )

        # Save token
        self.token_storage.save_token(token)

        return token

    async def refresh_token(self, refresh_token: str | None = None) -> dict[str, Any]:
        """Refresh access token.

        Args:
            refresh_token: Refresh token (loads from storage if not provided)

        Returns:
            New token dictionary

        Raises:
            ValueError: If refresh token is not available
        """
        if refresh_token is None:
            stored_token = self.token_storage.load_token()
            if not stored_token or "refresh_token" not in stored_token:
                raise ValueError("No refresh token available")
            refresh_token = stored_token["refresh_token"]

        if not self._client:
            self._client = OAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
            )

        # Refresh token
        token = await self._client.refresh_token(
            self.token_url, refresh_token=refresh_token
        )

        # Save new token
        self.token_storage.save_token(token)

        return token

    def get_valid_token(self) -> dict[str, Any] | None:
        """Get valid access token from storage.

        Returns:
            Token dictionary if valid, None otherwise
        """
        token = self.token_storage.load_token()
        if not token:
            return None

        # Check if token is expired
        if "expires_at" in token:
            expires_at = datetime.fromtimestamp(token["expires_at"])
            if expires_at <= datetime.now() + timedelta(minutes=5):
                # Token expired or expiring soon
                return None

        return token

    async def ensure_valid_token(self) -> str:
        """Ensure we have a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            ValueError: If no token available and authentication required
        """
        token = self.get_valid_token()

        if token:
            return token["access_token"]

        # Try to refresh token
        stored_token = self.token_storage.load_token()
        if stored_token and "refresh_token" in stored_token:
            new_token = await self.refresh_token()
            return new_token["access_token"]

        raise ValueError(
            "No valid token available. Please authenticate using get_authorization_url()"
        )

    def clear_tokens(self) -> None:
        """Clear all stored tokens."""
        self.token_storage.clear_token()
