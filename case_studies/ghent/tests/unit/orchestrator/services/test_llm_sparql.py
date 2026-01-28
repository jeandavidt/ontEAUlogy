"""Unit tests for the LLM SPARQL translation service."""

import pytest
from unittest.mock import MagicMock, patch
from ghent_water.orchestrator.services.llm_sparql import LLMService, SparqlValidator

def test_sparql_validator_valid():
    """Test validator with valid SPARQL."""
    validator = SparqlValidator()
    query = "SELECT ?s WHERE { ?s ?p ?o }"
    # We need to mock namespace_manager because the validator uses it
    with patch("ghent_water.orchestrator.services.llm_sparql.namespace_manager") as mock_ns:
        mock_ns.get_all_prefixes.return_value = {}
        is_valid, error = validator.validate(query)
        if not is_valid:
            print(f"Validation error: {error}")
        assert is_valid is True
        assert error is None

def test_sparql_validator_invalid():
    """Test validator with invalid SPARQL."""
    validator = SparqlValidator()
    query = "INVALID QUERY"
    with patch("ghent_water.orchestrator.services.llm_sparql.namespace_manager") as mock_ns:
        mock_ns.get_all_prefixes.return_value = {}
        is_valid, error = validator.validate(query)
        assert is_valid is False
        assert error is not None

@pytest.mark.asyncio
async def test_llm_service_initialization_auto():
    """Test LLM service initialization detects providers."""
    service = LLMService(provider="auto")
    
    with patch.object(service, "_try_initialize_lmstudio", return_value=True):
        success = await service.initialize()
        assert success is True
        
    with patch.object(service, "_try_initialize_lmstudio", return_value=False):
        with patch.object(service, "_try_initialize_openrouter", return_value=True):
            success = await service.initialize()
            assert success is True

@pytest.mark.asyncio
async def test_llm_service_translate_not_initialized():
    """Test translation fails when not initialized."""
    service = LLMService()
    result = await service.translate("What are the DWPs?")
    assert result.is_valid is False
    assert "not available" in result.validation_error
