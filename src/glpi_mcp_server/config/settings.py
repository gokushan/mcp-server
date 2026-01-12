"""Configuration management using Pydantic Settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OAuth 2.1 Configuration
    oauth_client_id: str = Field(..., description="OAuth 2.1 Client ID")
    oauth_client_secret: str = Field(..., description="OAuth 2.1 Client Secret")
    oauth_authorization_url: str = Field(
        ..., description="OAuth 2.1 Authorization endpoint"
    )
    oauth_token_url: str = Field(..., description="OAuth 2.1 Token endpoint")
    oauth_redirect_uri: str = Field(
        default="http://localhost:8080/callback",
        description="OAuth 2.1 Redirect URI",
    )

    # GLPI API Configuration
    glpi_api_url: str = Field(..., description="GLPI API base URL")
    glpi_app_token: str = Field(..., description="GLPI Application Token")

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai", description="LLM provider for document processing"
    )

    # OpenAI Configuration
    openai_api_key: str | None = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(
        default="gpt-4-turbo-preview", description="OpenAI model to use"
    )

    # Anthropic Configuration
    anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API Key"
    )
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", description="Anthropic model to use"
    )

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama base URL"
    )
    ollama_model: str = Field(default="llama2", description="Ollama model to use")

    # Server Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    token_storage_path: Path = Field(
        default=Path.home() / ".glpi-mcp" / "tokens.json",
        description="Path to store OAuth tokens",
    )

    def validate_llm_config(self) -> None:
        """Validate LLM configuration based on provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Anthropic provider"
            )


# Global settings instance
settings = Settings()
