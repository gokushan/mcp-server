"""Tests for authentication module."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from authlib.integrations.httpx_client import OAuth2Client

from glpi_mcp_server.auth.oauth_client import OAuthClient, TokenStorage
from glpi_mcp_server.config import settings


@pytest.fixture
def mock_token_storage(tmp_path):
    storage_path = tmp_path / "tokens.json"
    return TokenStorage(storage_path)


@pytest.fixture
def oauth_client(mock_token_storage):
    return OAuthClient(
        client_id="test-id",
        client_secret="test-secret",
        token_storage_path=mock_token_storage.storage_path,
    )


def test_token_storage_save_load(mock_token_storage):
    token = {"access_token": "test-token", "token_type": "Bearer"}
    mock_token_storage.save_token(token)
    
    loaded = mock_token_storage.load_token()
    assert loaded["access_token"] == "test-token"
    assert "stored_at" in loaded


def test_oauth_client_generate_pkce(oauth_client):
    verifier, challenge = oauth_client._generate_pkce_pair()
    assert len(verifier) >= 43
    assert len(challenge) > 0
    assert verifier != challenge


def test_get_valid_token_returns_none_if_missing(oauth_client):
    assert oauth_client.get_valid_token() is None


def test_get_valid_token_returns_token_if_valid(oauth_client, mock_token_storage):
    future = datetime.now() + timedelta(hours=1)
    token = {
        "access_token": "valid",
        "expires_at": future.timestamp()
    }
    mock_token_storage.save_token(token)
    
    assert oauth_client.get_valid_token()["access_token"] == "valid"


def test_get_valid_token_returns_none_if_expired(oauth_client, mock_token_storage):
    past = datetime.now() - timedelta(hours=1)
    token = {
        "access_token": "expired",
        "expires_at": past.timestamp()
    }
    mock_token_storage.save_token(token)
    
    assert oauth_client.get_valid_token() is None
