"""Configuration management for the orchestrator."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """Application metadata."""

    name: str = "ontEAUlogy Orchestrator"
    version: str = "0.1.0"
    description: str = "Generic orchestrator for water system ontologies"


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = "0.0.0.0"
    port: int = 8080
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class OntologyConfig(BaseModel):
    """Ontology file configuration."""

    base_path: str = "../../data"
    case_study_path: str = "data"
    files: List[str] = Field(default_factory=list)


class ModelDiscoveryConfig(BaseModel):
    """Model service discovery configuration."""

    id: str
    endpoint: str
    entity: str
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)


class ModelsConfig(BaseModel):
    """Models configuration."""

    discovery: List[ModelDiscoveryConfig] = Field(default_factory=list)


class NamespaceConfig(BaseModel):
    """Namespace prefix configuration."""

    prefix: str
    uri: str


class NamespacesConfig(BaseModel):
    """Namespace configuration."""

    namespaces: List[NamespaceConfig] = Field(default_factory=list)


class LLMConfig(BaseModel):
    """LLM configuration for natural language queries."""

    provider: str = "auto"  # auto, openrouter, lmstudio
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    max_retries: int = 3


class OrchestratorConfig(BaseSettings):
    """Complete orchestrator configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application info
    app: AppConfig = Field(default_factory=AppConfig)

    # Server settings
    server: ServerConfig = Field(default_factory=ServerConfig)

    # Ontology configuration
    ontology: OntologyConfig = Field(default_factory=OntologyConfig)

    # Models configuration
    models: ModelsConfig = Field(default_factory=ModelsConfig)

    # Namespaces configuration
    namespaces: NamespacesConfig = Field(default_factory=NamespacesConfig)

    # LLM configuration
    llm: LLMConfig = Field(default_factory=LLMConfig)

    # Logging
    log_level: str = "INFO"

    # Backwards compatibility properties for llm_sparql.py
    @property
    def llm_provider(self) -> str:
        return self.llm.provider
    
    @property
    def llm_api_key(self) -> Optional[str]:
        return self.llm.api_key
    
    @property
    def llm_model(self) -> Optional[str]:
        return self.llm.model
    
    @property
    def llm_base_url(self) -> Optional[str]:
        return self.llm.base_url
    
    @property
    def llm_max_retries(self) -> int:
        return self.llm.max_retries


def load_config(config_path: Optional[Path] = None) -> OrchestratorConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML config file. If None, uses env vars only.

    Returns:
        OrchestratorConfig instance
    """
    config = OrchestratorConfig()

    if config_path and config_path.exists():
        logger.info(f"Loading config from {config_path}")
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        if yaml_data:
            # Update config with YAML values
            if "app" in yaml_data:
                config.app = AppConfig(**yaml_data["app"])
            if "server" in yaml_data:
                config.server = ServerConfig(**yaml_data["server"])
            if "ontology" in yaml_data:
                config.ontology = OntologyConfig(**yaml_data["ontology"])
            if "models" in yaml_data:
                models_data = yaml_data["models"]
                if "discovery" in models_data:
                    discovery = [ModelDiscoveryConfig(**m) for m in models_data["discovery"]]
                    config.models = ModelsConfig(discovery=discovery)
            if "namespaces" in yaml_data:
                ns_data = yaml_data["namespaces"]
                if "namespaces" in ns_data:
                    namespaces = [NamespaceConfig(**n) for n in ns_data["namespaces"]]
                    config.namespaces = NamespacesConfig(namespaces=namespaces)
            if "llm" in yaml_data:
                config.llm = LLMConfig(**yaml_data["llm"])
            if "log_level" in yaml_data:
                config.log_level = yaml_data["log_level"]
    else:
        if config_path:
            logger.warning(f"Config file not found: {config_path}")

    return config


# Global config instance (lazy loaded)
_config: Optional[OrchestratorConfig] = None


def get_config(config_path: Optional[Path] = None) -> OrchestratorConfig:
    """Get the global config instance."""
    global _config
    if _config is None or config_path:
        _config = load_config(config_path)
    return _config


# Alias for backwards compatibility with llm_sparql.py
def get_settings() -> OrchestratorConfig:
    """Get settings (alias for get_config for backwards compatibility)."""
    return get_config()
