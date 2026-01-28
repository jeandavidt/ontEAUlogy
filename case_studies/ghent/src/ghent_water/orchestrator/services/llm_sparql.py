"""LLM-powered SPARQL translation service using PydanticAI.

This module provides natural language to SPARQL translation using PydanticAI
for type-safe, provider-agnostic LLM interactions with validation and retry logic.
"""

import hashlib
import logging
import re
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

from pydantic_ai.providers.openai import OpenAIProvider

from ghent_water.orchestrator.services.namespace_manager import namespace_manager

logger = logging.getLogger(__name__)

# Debug directory for saving LLM outputs
DEBUG_DIR = Path("/tmp/llm_sparql_debug")
DEBUG_DIR.mkdir(exist_ok=True)

# Maximum retry attempts for invalid SPARQL
MAX_VALIDATION_RETRIES = 3


def get_sparql_prefixes() -> str:
    """Get SPARQL PREFIX declarations from the namespace manager.

    Returns:
        String containing PREFIX declarations for SPARQL queries.
    """
    return namespace_manager.get_sparql_prefixes()


# =============================================================================
# Pydantic Models for Type-Safe Responses
# =============================================================================


class QuerySource(str, Enum):
    """Source of the SPARQL query."""

    LLM = "llm"
    FALLBACK = "fallback"


class SparqlTranslationResult(BaseModel):
    """Result of translating a natural language question to SPARQL.

    This model ensures type safety and validation of the translation result.
    """

    generated_sparql: str = Field(..., description="The generated SPARQL query")
    simulation_required: bool = Field(
        default=False, description="Whether simulation is needed"
    )
    suggested_models: List[str] = Field(
        default_factory=list, description="Relevant model IDs"
    )
    source: QuerySource = Field(default=QuerySource.LLM, description="Query source")
    is_valid: bool = Field(
        default=True, description="Whether the query passed validation"
    )
    validation_error: Optional[str] = Field(
        default=None, description="Validation error message"
    )
    attempt_count: int = Field(default=1, description="Number of LLM attempts made")
    final_attempt: bool = Field(
        default=False, description="Whether this was the final retry attempt"
    )


# =============================================================================
# ONTOLOGY CONTEXT FOR LLM
# =============================================================================


def get_system_prompt() -> str:
    """Get the system prompt with dynamic PREFIX declarations from the ontology."""
    # Use namespace_manager directly to ensure latest prefixes
    from .namespace_manager import namespace_manager

    prefixes = namespace_manager.get_sparql_prefixes()
    return f"""You are a SPARQL expert for the waterFRAME ontology. The ontology models urban water systems.

AVAILABLE PREFIXES (use these exact URIs):
{prefixes}

ENTITY TYPES:
- wf:WaterSource (natural water bodies like rivers)
- wf:DrinkingWaterPlant (DWP - treats source water for consumption)
- wf:WastewaterTreatmentPlant (WWTP - treats wastewater before discharge)
- wf:IndustrialFacility (factories with water demands)
- wf:ResidentialArea (housing districts)
- wf:WaterZone (geographic zones like UpstreamZone, DownstreamZone)
- wf:FlowConnection (links between entities showing water flow)

KEY PROPERTIES:
- wf:hasEffluent, wf:hasInfluent, wf:hasCapacity, wf:hasWaterDemand
- wf:hasTreatmentCapability, wf:locatedInZone, wf:hasComponent
- wf:hasUpstreamSource, wf:hasDownstreamTarget

IMPORTANT URIs:
- ghent:GhentWaterSystem, ghent:UpstreamZone, ghent:DownstreamZone
- ghent:DWP1, ghent:DWP2, ghent:WWTP1, ghent:WWTP2
- ghent:LieveRiver, ghent:LieveSegment1, ghent:LieveSegment2, ghent:LieveSegment3
- ghent:Dampoort, ghent:Muide, ghent:Texfin, ghent:FoodPro
- ghent:ChipTech, ghent:PharmaGen, ghent:BrewCo

SPARQL CONSTRUCTION RULES:
1. Include appropriate PREFIX declarations at the start of your query.
2. Use ghent: prefix for case entities, wf: for ontology classes/properties.
3. Use qudt: for quantity values (numericValue, unit).
4. For SELECT queries, always include a WHERE clause.

JSON OUTPUT REQUIREMENTS:
CRITICAL: You MUST respond with a valid JSON object matching this exact schema:

{{
  "generated_sparql": "string - your SPARQL query here",
  "simulation_required": false,
  "suggested_models": [],
  "source": "llm",
  "is_valid": true,
  "validation_error": null
}}

FIELD CONSTRAINTS:
- "generated_sparql": Must be a valid SPARQL query as a string
- "simulation_required": Boolean, true only for future/prediction/what-if scenarios
- "suggested_models": Array of strings, empty unless specific models are needed
- "source": Always "llm" 
- "is_valid": Always true for your initial response
- "validation_error": Always null for your initial response

IMPORTANT:
- The SPARQL query MUST be in the "generated_sparql" field
- Do NOT use field names like "query", "sparql", or any other variations
- Ensure your JSON is properly formatted and valid
- Double-check all field names match exactly

SIMULATION LOGIC:
Only set simulation_required=true for questions about:
- Future performance or predictions
- "What-if" scenarios  
- Questions asking to "simulate" or "predict"
- Questions about effluent/discharge that require modeling

Otherwise, use the existing static data to answer the query.
"""


# =============================================================================
# SPARQL Validator
# =============================================================================


class SparqlValidator:
    """Validates SPARQL query syntax."""

    @staticmethod
    def validate(query: str) -> tuple[bool, Optional[str]]:
        """Validate a SPARQL query syntax.

        Args:
            query: The SPARQL query to validate.

        Returns:
            Tuple of (is_valid, error_message).
        """
        from rdflib.plugins.sparql import prepareQuery
        from .namespace_manager import namespace_manager

        query = query.strip()
        if not query:
            return False, "Empty query"

        try:
            prepareQuery(query, initNs=namespace_manager.get_all_prefixes())
            return True, None
        except Exception as e:
            return False, str(e)


# =============================================================================
# PydanticAI-based LLM Service
# =============================================================================


class LLMService:
    """LLM service using PydanticAI for type-safe translations.

    Flow:
    1. Try to reach LLM provider
    2. If unreachable, return error
    3. Send question with context
    4. Validate response
    5. If invalid, retry up to MAX_VALIDATION_RETRIES times
    6. If still invalid after retries, return error
    """

    # Provider configurations
    PROVIDER_CONFIGS = {
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "models": [
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "google/gemini-2.0-flash-exp",
                "anthropic/claude-3-haiku",
            ],
            "default_model": "openai/gpt-4o-mini",
        },
        "lmstudio": {
            "base_url": "http://localhost:1234/v1",
            "models": ["local-model"],
            "default_model": "local-model",
        },
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "auto",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = MAX_VALIDATION_RETRIES,
    ):
        """Initialize the LLM service.

        Args:
            api_key: API key for the provider.
            provider: LLM provider - "openrouter", "lmstudio", or "auto".
            model: Specific model to use. If None, uses provider default.
            base_url: Custom base URL for the API.
            max_retries: Maximum retry attempts for invalid SPARQL.
        """
        self._api_key = api_key
        self._provider = provider
        self._model = model
        self._base_url = base_url
        self._max_retries = max_retries
        self._agent = None  # Deprecated: replaced by _provider_instance
        self._provider_instance: Optional[OpenAIProvider] = None
        self._initialized = False
        self._init_attempted = False
        self._provider_type: Optional[str] = None
        self._validator = SparqlValidator()

    async def initialize(self) -> bool:
        """Initialize the LLM client based on available providers.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        import os

        # Avoid repeated slow initialization attempts
        if self._init_attempted and not self._initialized:
            return False

        self._init_attempted = True

        # Try providers in order based on configuration
        if self._provider == "auto":
            if await self._try_initialize_lmstudio():
                return True
            if await self._try_initialize_openrouter():
                return True
            logger.warning("No LLM provider available.")
            return False
        elif self._provider == "lmstudio":
            if await self._try_initialize_lmstudio():
                return True
            logger.warning(
                "LM Studio not available. Install LM Studio and load a model."
            )
            return False
        elif self._provider == "openrouter":
            if await self._try_initialize_openrouter():
                return True
            logger.warning("OpenRouter not available. Set OPENROUTER_API_KEY env var.")
            return False
        else:
            logger.warning(f"Unknown provider: {self._provider}")
            return False

    async def _try_initialize_lmstudio(self) -> bool:
        """Try to initialize LM Studio local model."""
        base_url = self._base_url or "http://localhost:1234/v1"

        try:
            async with __import__("httpx").AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{base_url}/models")
                if response.status_code == 200:
                    self._model = self._model or "local-model"
                    self._provider_type = "lmstudio"
                    self._provider_instance = OpenAIProvider(
                        base_url=base_url, api_key="not-needed"
                    )
                    self._initialized = True
                    logger.info(f"LM Studio initialized at {base_url}")
                    return True
        except Exception:
            pass

        return False

    async def _try_initialize_openrouter(self) -> bool:
        """Try to initialize OpenRouter client."""
        import os

        # Check config first, then environment variable
        settings = __import__(
            "ghent_water.orchestrator.config", fromlist=["get_settings"]
        ).get_settings()
        api_key = (
            self._api_key
            or os.environ.get("OPENROUTER_API_KEY")
            or settings.llm_api_key
        )

        if not api_key:
            logger.warning(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY in .env file."
            )
            return False

        try:
            self._model = (
                self._model or self.PROVIDER_CONFIGS["openrouter"]["default_model"]
            )
            self._provider_type = "openrouter"
            self._provider_instance = OpenAIProvider(
                base_url="https://openrouter.ai/api/v1", api_key=api_key
            )
            self._initialized = True
            logger.info(f"OpenRouter initialized with model: {self._model}")
            return True
        except ImportError:
            logger.warning("pydantic-ai not installed. Run: pip install pydantic-ai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter: {e}")
            # Mask API key for security - never log full key
            if api_key and len(api_key) > 12:
                masked_key = f"{api_key[:8]}...{api_key[-4:]}"
            else:
                masked_key = "***"
            logger.error(
                f"API key status: {'present' if api_key else 'missing'} (masked: {masked_key})"
            )

            # Check if it's a network error
            if "Connection" in str(e) or "Network" in str(e):
                logger.error(
                    "Cannot connect to OpenRouter. Check your network connection."
                )

        return False

    async def _get_llm_response(self, prompt: str) -> str:
        """Send prompt to LLM and get raw text response."""
        if not self._provider_instance:
            raise RuntimeError("LLM provider not initialized.")

        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        # Dynamically get base_url from provider instance, if available
        base_url = getattr(self._provider_instance, "base_url", None)
        if not base_url:
            raise RuntimeError("OpenAIProvider instance does not have a base_url.")

        # Remove trailing slash to prevent double slash when concatenating
        base_url = base_url.rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "messages": messages,
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            # NEVER log the actual API key - log status code only
            logger.error(f"HTTP error during LLM call: {e.response.status_code}")
            raise RuntimeError(
                f"LLM API request failed with status {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error during LLM call: {type(e).__name__}")
            raise RuntimeError("Network error connecting to LLM service") from e
        except Exception as e:
            logger.error(f"Unexpected error during LLM call: {type(e).__name__}")
            raise RuntimeError("Unexpected error during LLM request") from e

    @property
    def provider(self) -> Optional[str]:
        """Get the active provider type."""
        return self._provider_type

    @property
    def current_model(self) -> Optional[str]:
        """Get the current model name."""
        return self._model

    async def translate(self, question: str) -> SparqlTranslationResult:
        """Translate natural language question to SPARQL.

        Flow:
        1. Check if LLM is reachable
        2. Send question to LLM
        3. Validate response
        4. If invalid, retry with error message (max retries)
        5. If still invalid, return error

        Args:
            question: The natural language question.

        Returns:
            SparqlTranslationResult with the generated query and validation status.
        """
        # Check if LLM is available
        if not self._initialized or not self._provider_instance:
            return SparqlTranslationResult(
                generated_sparql="",
                is_valid=False,
                validation_error="LLM provider not available. Please configure OpenRouter or LM Studio.",
                source=QuerySource.LLM,
                final_attempt=True,
            )

        # Attempt translation with retry logic
        attempt = 0
        last_error: str = "Unknown validation error"

        while attempt < self._max_retries:
            attempt += 1
            is_final = attempt >= self._max_retries

            # Build prompt with error context if retrying
            if attempt == 1:
                prompt = self._build_prompt(question)
            else:
                prompt = self._build_retry_prompt(question, last_error)

            try:
                raw_llm_output = await self._get_llm_response(prompt)

                # Save raw output for debugging
                if logger.level <= logging.DEBUG:
                    output_hash = hashlib.md5(raw_llm_output.encode()).hexdigest()[:8]
                    debug_file = DEBUG_DIR / f"llm_output_{output_hash}.json"
                    debug_file.write_text(raw_llm_output)
                    logger.debug(f"Saved LLM output to {debug_file}")

                try:
                    translation = SparqlTranslationResult.model_validate_json(
                        raw_llm_output
                    )
                except Exception as json_e:
                    # Log FULL output, not truncated
                    logger.warning(
                        f"Failed to parse LLM output as JSON: {json_e}\n"
                        f"Question: {question}\n"
                        f"Full output ({len(raw_llm_output)} chars):\n{raw_llm_output}"
                    )

                    # Save to file for post-mortem analysis
                    error_file = (
                        DEBUG_DIR
                        / f"parse_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
                    error_file.write_text(
                        f"Question: {question}\n\n"
                        f"Error: {json_e}\n\n"
                        f"Full LLM Output:\n{raw_llm_output}"
                    )

                    last_error = f"LLM returned invalid JSON: {json_e}. Output saved to {error_file}"
                    if is_final:
                        return SparqlTranslationResult(
                            generated_sparql="",
                            is_valid=False,
                            validation_error=last_error,
                            source=QuerySource.LLM,
                            attempt_count=attempt,
                            final_attempt=True,
                        )
                    continue  # Retry if JSON parsing fails
                sparql = self._clean_sparql(translation.generated_sparql)

                # Validate the generated query
                is_valid, error = self._validator.validate(sparql)

                if is_valid:
                    translation.generated_sparql = sparql
                    translation.attempt_count = attempt
                    translation.final_attempt = is_final
                    translation.is_valid = True
                    return translation
                else:
                    last_error = error or "Validation failed"
                    logger.warning(f"Validation attempt {attempt} failed: {last_error}")

                    if is_final:
                        return SparqlTranslationResult(
                            generated_sparql=sparql,
                            simulation_required=self._check_simulation_required(
                                question
                            ),
                            suggested_models=self._find_suggested_models(question),
                            source=QuerySource.LLM,
                            is_valid=False,
                            validation_error=f"After {attempt} attempts: {error}",
                            attempt_count=attempt,
                            final_attempt=True,
                        )

            except Exception as e:
                logger.error(f"LLM translation attempt {attempt} failed: {e}")

                if is_final:
                    return SparqlTranslationResult(
                        generated_sparql="",
                        is_valid=False,
                        validation_error=f"LLM error after {attempt} attempts: {str(e)}",
                        source=QuerySource.LLM,
                        attempt_count=attempt,
                        final_attempt=True,
                    )

        # Should not reach here, but return error just in case
        return SparqlTranslationResult(
            generated_sparql="",
            is_valid=False,
            validation_error="Unexpected translation error",
            source=QuerySource.LLM,
            final_attempt=True,
        )

    def _build_prompt(self, question: str) -> str:
        """Build the initial prompt for the LLM."""
        return f"""Translate this question into a structured SPARQL context:

"{question}"
"""

    def _build_retry_prompt(self, question: str, error: str) -> str:
        """Build a retry prompt with validation error context."""
        return f"""The previous response had errors:

ERROR: {error}

You MUST fix the issue and respond with a valid JSON object matching this exact schema:

{{
  "generated_sparql": "string - your corrected SPARQL query here",
  "simulation_required": boolean,
  "suggested_models": array of strings,
  "source": "llm",
  "is_valid": true,
  "validation_error": null
}}

CRITICAL REQUIREMENTS:
- Ensure JSON is valid and properly formatted
- Use EXACT field names shown above
- The SPARQL query goes in "generated_sparql" field ONLY
- Double-check quotes, brackets, and commas
- Do not include any text outside the JSON object

Question: "{question}"
"""

    def _clean_sparql(self, output: str) -> str:
        """Clean up LLM output to extract clean SPARQL."""
        sparql = output.strip()

        # Remove markdown code blocks
        sparql = re.sub(r"^```sparql\s*", "", sparql, flags=re.IGNORECASE)
        sparql = re.sub(r"\s*```$", "", sparql)
        sparql = re.sub(r"^```\s*", "", sparql, flags=re.IGNORECASE)

        return sparql.strip()

    def _check_simulation_required(self, question: str) -> bool:
        """Check if the question requires simulation."""
        simulation_keywords = [
            "simulate",
            "predict",
            "future",
            "scenario",
            "what if",
            "effluent",
            "discharge",
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in simulation_keywords)

    def _find_suggested_models(self, question: str) -> List[str]:
        """Find models that might be needed for the question."""
        question_lower = question.lower()
        models = []

        if "wwtp1" in question_lower or ("wwtp" in question_lower and "1" in question):
            models.append("wwtp1")
        elif "wwtp2" in question_lower or (
            "wwtp" in question_lower and "2" in question
        ):
            models.append("wwtp2")
        elif "wwtp" in question_lower:
            models.extend(["wwtp1", "wwtp2"])

        if "dwp1" in question_lower or ("dwp" in question_lower and "1" in question):
            models.append("dwp1")
        elif "dwp2" in question_lower or ("dwp" in question_lower and "2" in question):
            models.append("dwp2")
        elif "dwp" in question_lower:
            models.extend(["dwp1", "dwp2"])

        if "river" in question_lower or "lieve" in question_lower:
            models.append("lieve_river")

        return list(set(models))


# =============================================================================
# Translator Service
# =============================================================================


class LlmSparqlTranslator:
    """Service for translating natural language to SPARQL using PydanticAI.

    Provides NL→SPARQL translation with automatic provider detection,
    validation, and retry logic.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "auto",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = MAX_VALIDATION_RETRIES,
    ):
        """Initialize the translator service.

        Args:
            api_key: API key for the LLM provider.
            provider: LLM provider - "openrouter", "lmstudio", or "auto".
            model: Specific model to use.
            base_url: Custom base URL for the API.
            max_retries: Maximum retry attempts for invalid SPARQL.
        """
        self._llm_service = LLMService(
            api_key=api_key,
            provider=provider,
            model=model,
            base_url=base_url,
            max_retries=max_retries,
        )
        self._initialized = False

    async def initialize(self, api_key: Optional[str] = None) -> bool:
        """Initialize the LLM service.

        Returns:
            True if initialization succeeded.
        """
        self._initialized = await self._llm_service.initialize()
        return self._initialized

    async def translate(self, question: str) -> SparqlTranslationResult:
        """Translate natural language to SPARQL.

        Args:
            question: The natural language question.

        Returns:
            SparqlTranslationResult with the generated and validated query.
        """
        if not self._initialized:
            await self.initialize()

        return await self._llm_service.translate(question)

    async def execute_query(
        self,
        question: str,
        sparql_engine,
    ) -> Dict[str, Any]:
        """Translate and execute a natural language query.

        Args:
            question: The natural language question.
            sparql_engine: SPARQL engine to execute queries.

        Returns:
            Dictionary with translation result and query results.
        """
        translation = await self.translate(question)

        result = translation.model_dump()
        sparql = translation.generated_sparql

        if sparql and translation.is_valid:
            try:
                query_result = sparql_engine.execute_query(sparql)
                raw_results = query_result.get("results", {})
                if isinstance(raw_results, dict) and "bindings" in raw_results:
                    result["results"] = raw_results["bindings"]
                elif isinstance(raw_results, list):
                    result["results"] = raw_results
                else:
                    result["results"] = []
                result["query_time_ms"] = query_result.get("query_time_ms", 0.0)
            except Exception as e:
                logger.error(f"SPARQL execution failed: {e}")
                result["results"] = []
                result["error"] = str(e)
                # Re-raise to let caller handle it if needed
                raise RuntimeError(f"SPARQL execution failed: {e}") from e
        else:
            error_msg = translation.validation_error or "Invalid SPARQL query"
            result["results"] = []
            result["error"] = error_msg
            raise ValueError(f"SPARQL translation failed: {error_msg}")

        return result

    @property
    def provider(self) -> Optional[str]:
        """Get the active LLM provider."""
        return self._llm_service.provider

    @property
    def current_model(self) -> Optional[str]:
        """Get the current model name."""
        return self._llm_service.current_model

    @property
    def is_ready(self) -> bool:
        """Check if the translator is ready for queries."""
        return self._initialized or self._llm_service._initialized


# =============================================================================
# Global translator instance factory
# =============================================================================


def create_llm_sparql_translator(
    api_key: Optional[str] = None,
    provider: str = "auto",
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    max_retries: int = MAX_VALIDATION_RETRIES,
) -> LlmSparqlTranslator:
    """Create and configure an LLM SPARQL translator instance.

    Args:
        api_key: API key for the LLM provider.
        provider: LLM provider - "openrouter", "lmstudio", or "auto".
        model: Specific model to use.
        base_url: Custom base URL for the API.
        max_retries: Maximum retry attempts for invalid SPARQL.

    Returns:
        Configured LlmSparqlTranslator instance.
    """
    return LlmSparqlTranslator(
        api_key=api_key,
        provider=provider,
        model=model,
        base_url=base_url,
        max_retries=max_retries,
    )


# Lazy-loaded global instance (initialized on first use)
_llm_sparql_translator: Optional[LlmSparqlTranslator] = None


def get_llm_sparql_translator() -> LlmSparqlTranslator:
    """Get the global LLM SPARQL translator instance, creating it if needed.

    This function loads configuration from settings and creates a properly
    configured translator instance.

    Returns:
        Configured LlmSparqlTranslator instance.
    """
    global _llm_sparql_translator

    if _llm_sparql_translator is None:
        from ..config import get_settings

        settings = get_settings()

        _llm_sparql_translator = create_llm_sparql_translator(
            api_key=settings.llm_api_key,
            provider=settings.llm_provider,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            max_retries=settings.llm_max_retries,
        )

    return _llm_sparql_translator


# Backwards compatibility: old global instance
llm_sparql_translator = None  # Deprecated, use get_llm_sparql_translator() instead
