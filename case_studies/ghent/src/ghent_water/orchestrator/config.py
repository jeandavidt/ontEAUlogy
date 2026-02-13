"""Configuration management for the orchestrator."""

from functools import lru_cache
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = "ontEAUlogy Ghent Backend"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080

    # Ontology paths
    # Base path to the ontEAUlogy/data directory (relative to case study root)
    ontology_base_path: str = "../../data"
    # Case study specific data
    case_study_data_path: str = "data"
    # Household case study data path (relative to case_studies/)
    household_data_path: str = "../household/data"
    # Legacy paths (kept for compatibility but not used by new code)
    ontology_path: str = "data/ontology/waterframe.ttl"
    instances_path: str = "data/ontology/instances/"

    # SPARQL endpoint (if using external endpoint)
    sparql_endpoint: Optional[str] = None

    # LLM settings (for natural language query)
    # Provider: "auto", "openrouter", or "lmstudio"
    llm_provider: str = "auto"

    # OpenRouter API key
    openrouter_api_key: Optional[str] = None

    @property
    def llm_api_key(self) -> Optional[str]:
        """Get API key from openrouter_api_key for compatibility."""
        return self.openrouter_api_key

    # Model to use (provider-dependent)
    # OpenRouter: "anthropic/claude-3.5-sonnet", "openai/gpt-4o", etc.
    # LM Studio: any loaded model name
    llm_model: Optional[str] = None

    # Custom base URL (for local LM Studio or custom endpoints)
    llm_base_url: Optional[str] = None

    # Maximum retry attempts for invalid SPARQL
    llm_max_retries: int = 3

    # Logging
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
