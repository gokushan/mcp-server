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
    oauth_client_id: str | None = Field(default=None, description="OAuth 2.1 Client ID")
    oauth_client_secret: str | None = Field(default=None, description="OAuth 2.1 Client Secret")
    oauth_authorization_url: str | None = Field(
        default=None, description="OAuth 2.1 Authorization endpoint"
    )
    oauth_token_url: str | None = Field(default=None, description="OAuth 2.1 Token endpoint")
    oauth_redirect_uri: str = Field(
        default="http://localhost:8080/callback",
        description="OAuth 2.1 Redirect URI",
    )

    # GLPI API Configuration
    glpi_api_url: str = Field(..., description="GLPI API base URL")
    glpi_app_token: str = Field(..., description="GLPI Application Token")
    glpi_user_token: str | None = Field(default=None, description="GLPI User Token (API Token)")

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai", description="LLM provider for document processing"
    )

    # OpenAI Configuration
    openai_api_key: str | None = Field(default=None, description="OpenAI API Key")
    openai_url: str = Field(
        default="https://api.openai.com/v1/chat/completions", description="OpenAI API Endpoint URL"
    )
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
    anthropic_base_url: str = Field(
        default="https://api.anthropic.com/v1", description="Anthropic base URL"
    )

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama base URL"
    )
    ollama_model: str = Field(default="llama2", description="Ollama model to use")
    llm_max_chars: int = Field(
        default=20000, description="Maximum characters to send to LLM from document content"
    )
    timeout_llm: float = Field(
        default=300.0, description="Default timeout for LLM requests in seconds"
    )
    llm_mock: bool = Field(
        default=False, description="Enable LLM mocking for faster development"
    )

    # Server Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    token_storage_path: Path = Field(
        default=Path.home() / ".glpi-mcp" / "tokens.json",
        description="Path to store OAuth tokens",
    )

    # Security Configuration
    glpi_allowed_roots: str = Field(
        default="", 
        description="Comma-separated list of allowed root directories for file access"
    )
    
    # Processed files destination folders
    glpi_folder_success: str | None = Field(
        default=None, 
        description="Folder path where successfully processed files are moved"
    )
    glpi_folder_errores: str | None = Field(
        default=None, 
        description="Folder path where failed processed files are moved"
    )

    # Host paths for translation (used when running in Docker)
    glpi_host_allowed_roots: str = Field(
        default="", 
        description="Comma-separated list of host root directories (for reporting to client)"
    )
    glpi_host_folder_success: str | None = Field(
        default=None, 
        description="Host path for success folder"
    )
    glpi_host_folder_errores: str | None = Field(
        default=None, 
        description="Host path for error folder"
    )

    # MCP Transport Configuration
    mcp_transport: str = Field(
        default="streamable-http", description="MCP Transport method (stdio, sse, streamable-http)"
    )
    mcp_host: str = Field(
        default="0.0.0.0", description="Host for the MCP Server"
    )
    mcp_port: int = Field(
        default=8081, description="Port for the MCP Server"
    )

    @property
    def allowed_roots_list(self) -> list[Path]:
        """Parse allowed roots into a list of Path objects.
        
        Raises:
            ValueError: If any root path is relative or contains '..'
        """
        if not self.glpi_allowed_roots:
            return []
        
        paths = []
        for path_str in self.glpi_allowed_roots.split(","):
            clean_path = path_str.strip()
            if not clean_path:
                continue
                
            if ".." in clean_path:
                raise ValueError(f"Security error: Allowed root path '{clean_path}' cannot contain '..'")
            
            p = Path(clean_path)
            # We want to be strict with global allowed roots, they must be absolute
            if not p.is_absolute():
                 raise ValueError(f"Security error: Allowed root path '{clean_path}' must be an absolute path")
                
            paths.append(p.resolve())
        return paths

    glpi_allowed_extensions: str = Field(
        default="pdf,txt,doc,docx",
        description="Comma-separated list of allowed file extensions"
    )

    @property
    def folder_success_path(self) -> Path | None:
        """Get the absolute Path object for the success folder."""
        if not self.glpi_folder_success:
            return None
        # Ensure we strip whitespace that might come from .env
        clean_path = self.glpi_folder_success.strip()
        if not clean_path:
            return None
        p = Path(clean_path)
        return p.resolve() if p.is_absolute() else None

    @property
    def folder_errores_path(self) -> Path | None:
        """Get the absolute Path object for the error folder."""
        if not self.glpi_folder_errores:
            return None
        # Ensure we strip whitespace that might come from .env
        clean_path = self.glpi_folder_errores.strip()
        if not clean_path:
            return None
        p = Path(clean_path)
        return p.resolve() if p.is_absolute() else None

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Parse allowed extensions into a list of strings."""
        if not self.glpi_allowed_extensions:
            return ["pdf", "txt", "doc", "docx"]
        
        return [
            ext.strip().lower().lstrip(".") 
            for ext in self.glpi_allowed_extensions.split(",") 
            if ext.strip()
        ]

    @property
    def host_allowed_roots_list(self) -> list[str]:
        """Parse host allowed roots into a list of strings."""
        if not self.glpi_host_allowed_roots:
            return [str(p) for p in self.allowed_roots_list]
        
        return [
            path.strip() 
            for path in self.glpi_host_allowed_roots.split(",") 
            if path.strip()
        ]

    @property
    def host_folder_success(self) -> str | None:
        """Get host success folder path."""
        if self.glpi_host_folder_success:
            return self.glpi_host_folder_success.strip()
        return str(self.folder_success_path) if self.folder_success_path else None

    @property
    def host_folder_errores(self) -> str | None:
        """Get host error folder path."""
        if self.glpi_host_folder_errores:
            return self.glpi_host_folder_errores.strip()
        return str(self.folder_errores_path) if self.folder_errores_path else None

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
