"""Configuration management for the orchestrator."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    app_name: str = "ontEAUlogy Ghent Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Ontology paths
    ontology_path: str = "data/ontology/waterframe.ttl"
    instances_path: str = "data/ontology/instances/"
    
    # SPARQL endpoint (if using external endpoint)
    sparql_endpoint: Optional[str] = None
    
    # LLM settings (for natural language query)
    llm_provider: str = "anthropic"
    llm_api_key: Optional[str] = None
    llm_model: str = "claude-sonnet-4-20250514"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "GHENT_WATER_"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
