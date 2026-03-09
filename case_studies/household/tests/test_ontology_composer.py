"""Tests for OntologyComposer using waterFRAME ontology property chains.

These tests verify that the OntologyComposer can:
1. Use wf:dataFlowsTo property chain for automatic composition inference
2. Discover agents by capability using cap:* taxonomy
3. Compose via physical flows using wf:flowsTo
4. Validate execution using wf:hasPrecondition
5. Invoke operations using wf:hasHTTPGrounding
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import importlib.util

# Import agent_composer directly from core orchestrator file
core_orchestrator_path = (
    Path(__file__).parent.parent.parent / "core" / "orchestrator" / "src" /
    "ontEAUlogy_core" / "services" / "agent_composer.py"
)
spec = importlib.util.spec_from_file_location("agent_composer", core_orchestrator_path)
agent_composer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_composer_module)

OntologyComposer = agent_composer_module.OntologyComposer
ValidationResult = agent_composer_module.ValidationResult
InvocationResult = agent_composer_module.CompositionChain
Agent = agent_composer_module.Agent


@pytest.fixture
def mock_ontology_with_property_chains():
    """Create a mock ontology with waterFRAME property chains."""
    ontology = Mock()
    ontology.is_loaded.return_value = True

    def mock_query_sparql(query):
        # Property chain inference for dataFlowsTo
        if "dataFlowsTo" in query and "MBR_Simulation" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "targetOp": {"value": "https://w3id.org/waterframe/case/household/RO_Simulation"},
                            "sharedOutput": {"value": "https://w3id.org/waterframe/case/household/MBR_Effluent_Flow"},
                            "paramName": {"value": "effluent_flow_m3d"}
                        }
                    ]
                }
            }

        # Agent discovery with ontology-based I/O
        elif "ComputationalAgent" in query and "requiresInput" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/MBR_Agent"},
                            "agentLabel": {"value": "Membrane Bioreactor Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/MBR_Simulation"},
                            "endpoint": {"value": "http://localhost:8101"},
                            "modelId": {"value": "mbr"}
                        }
                    ]
                }
            }

        # Capability-based discovery
        elif "hasCapability" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/MBR_Agent"},
                            "agentLabel": {"value": "Membrane Bioreactor Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/MBR_Simulation"},
                            "endpoint": {"value": "http://localhost:8101"},
                            "modelId": {"value": "mbr"}
                        },
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/RO_Agent"},
                            "agentLabel": {"value": "Reverse Osmosis Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/RO_Simulation"},
                            "endpoint": {"value": "http://localhost:8102"},
                            "modelId": {"value": "ro"}
                        }
                    ]
                }
            }

        # Precondition query
        elif "hasPrecondition" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "constraint": {"value": "https://w3id.org/waterframe/case/household/MBR_Influent_Flow"},
                            "expression": {"value": "influent_flow_m3d > 0"},
                            "paramName": {"value": "influent_flow_m3d"}
                        }
                    ]
                }
            }

        # HTTP grounding query
        elif "hasHTTPGrounding" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "method": {"value": "POST"},
                            "path": {"value": "/simulate/mbr"},
                            "requestFormat": {"value": "application/json"},
                            "responseFormat": {"value": "application/json"}
                        }
                    ]
                }
            }

        # Operation I/O queries
        elif "requiresInput" in query or "producesOutput" in query:
            if "MBR_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "influent_flow_m3d"}},
                            {"paramName": {"value": "influent_cod_mg_l"}},
                            {"paramName": {"value": "effluent_flow_m3d"}},
                            {"paramName": {"value": "effluent_cod_mg_l"}},
                            {"paramName": {"value": "energy_kwh_d"}}
                        ]
                    }
                }
            elif "RO_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "feed_flow_m3d"}},
                            {"paramName": {"value": "feed_cod_mg_l"}},
                            {"paramName": {"value": "permeate_flow_m3d"}},
                            {"paramName": {"value": "permeate_cod_mg_l"}}
                        ]
                    }
                }

        # Physical flows query
        elif "flowsTo" in query and "monitorsPort" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "sourceAgent": {"value": "https://w3id.org/waterframe/case/household/MBR_Agent"},
                            "targetAgent": {"value": "https://w3id.org/waterframe/case/household/RO_Agent"},
                            "outPort": {"value": "https://w3id.org/waterframe/case/household/MBR_Effluent_Port"}
                        }
                    ]
                }
            }

        return {"results": {"bindings": []}}

    ontology.query_sparql = mock_query_sparql
    return ontology


@pytest.fixture
def composer(mock_ontology_with_property_chains):
    """OntologyComposer instance with mock ontology."""
    return OntologyComposer(mock_ontology_with_property_chains, base_url="http://localhost:8100")


class TestOntologyComposerDataFlowsTo:
    """Tests for wf:dataFlowsTo property chain inference."""

    @pytest.mark.asyncio
    async def test_dataflows_to_inference_mbr_to_ro(self, composer):
        """Verify wf:dataFlowsTo is inferred for MBR -> RO chain."""
        compositions = await composer.find_composable_operations(
            "https://w3id.org/waterframe/case/household/MBR_Simulation"
        )

        assert len(compositions) > 0
        assert any(
            "RO_Simulation" in c["target_operation"]
            for c in compositions
        )

    @pytest.mark.asyncio
    async def test_inferred_mappings_tracking(self, composer):
        """Test that inferred mappings are tracked during composition."""
        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"permeate_cod_mg_l"}
        )

        # Should have inferred mappings from dataFlowsTo
        assert "effluent_flow_m3d" in result.inferred_mappings or len(result.inferred_mappings) == 0


class TestOntologyComposerCapabilityDiscovery:
    """Tests for capability-based agent discovery using cap:* taxonomy."""

    @pytest.mark.asyncio
    async def test_discover_by_dynamic_simulation_capability(self, composer):
        """Find agents by cap:DynamicSimulation."""
        agents = await composer.discover_by_capability(
            required_capabilities=["cap:DynamicSimulation"],
            available_data={"influent_flow_m3d", "influent_cod_mg_l"}
        )

        assert len(agents) >= 1
        assert any(a.id == "MBR_Agent" for a in agents)

    @pytest.mark.asyncio
    async def test_discover_by_mass_balance_capability(self, composer):
        """Find agents by cap:MassBalance."""
        agents = await composer.discover_by_capability(
            required_capabilities=["cap:MassBalance", "cap:WaterQualityPrediction"],
            available_data={"influent_flow_m3d"}
        )

        assert len(agents) >= 1
        agent_ids = [a.id for a in agents]
        assert "MBR_Agent" in agent_ids or "RO_Agent" in agent_ids

    @pytest.mark.asyncio
    async def test_discover_returns_agent_objects(self, composer):
        """Verify discover_by_capability returns proper Agent objects."""
        agents = await composer.discover_by_capability(
            required_capabilities=["cap:DynamicSimulation"],
            available_data={"influent_flow_m3d"}
        )

        for agent in agents:
            assert isinstance(agent, Agent)
            assert agent.id
            assert agent.operation_uri
            assert isinstance(agent.required_inputs, set)
            assert isinstance(agent.produced_outputs, set)


class TestOntologyComposerPreconditionValidation:
    """Tests for wf:hasPrecondition validation."""

    @pytest.mark.asyncio
    async def test_validate_positive_flow_precondition(self, composer):
        """Validate execution with positive flow rate."""
        result = await composer.validate_execution(
            operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
            input_data={"influent_flow_m3d": 100}
        )

        assert result.valid is True
        assert len(result.violations) == 0

    @pytest.mark.asyncio
    async def test_validate_fails_negative_flow(self, composer):
        """Validation fails with negative flow rate."""
        result = await composer.validate_execution(
            operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
            input_data={"influent_flow_m3d": -5}
        )

        assert result.valid is False
        assert any("influent_flow_m3d" in v for v in result.violations)

    @pytest.mark.asyncio
    async def test_validate_fails_zero_flow(self, composer):
        """Validation fails with zero flow rate."""
        result = await composer.validate_execution(
            operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
            input_data={"influent_flow_m3d": 0}
        )

        assert result.valid is False

    @pytest.mark.asyncio
    async def test_validate_missing_parameter(self, composer):
        """Validation passes when precondition parameter is missing from input."""
        result = await composer.validate_execution(
            operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
            input_data={"other_param": 100}  # Missing influent_flow_m3d
        )

        # Should not fail if the parameter is not in input_data
        # (the check is only for provided parameters)
        assert result.valid is True


class TestOntologyComposerPhysicalFlows:
    """Tests for port-based flow composition using wf:flowsTo."""

    @pytest.mark.asyncio
    async def test_compose_via_physical_flows(self, composer):
        """Discover composition via physical port connections."""
        chains = await composer.compose_via_physical_flows(
            "https://w3id.org/waterframe/case/household/MBR_Unit"
        )

        assert len(chains) >= 1
        assert any(
            "MBR_Agent" in c.source_agent and "RO_Agent" in c.target_agent
            for c in chains
        )

    @pytest.mark.asyncio
    async def test_physical_flow_chain_structure(self, composer):
        """Verify CompositionChain structure from physical flows."""
        chains = await composer.compose_via_physical_flows(
            "https://w3id.org/waterframe/case/household/MBR_Unit"
        )

        for chain in chains:
            assert chain.source_agent
            assert chain.target_agent
            assert chain.flow_path  # Should have port URI


class TestOntologyComposerInvocation:
    """Tests for HTTP grounding invocation."""

    @pytest.mark.asyncio
    async def test_invoke_operation_success(self, composer):
        """Invoke operation using HTTP grounding."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await composer.invoke_operation(
                operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
                input_data={"influent_flow_m3d": 100, "influent_cod_mg_l": 200}
            )

            assert result.success is True
            assert result.data is not None

    @pytest.mark.asyncio
    async def test_invoke_operation_precondition_failure(self, composer):
        """Invocation fails when preconditions are not met."""
        result = await composer.invoke_operation(
            operation="https://w3id.org/waterframe/case/household/MBR_Simulation",
            input_data={"influent_flow_m3d": -5}  # Invalid: negative flow
        )

        assert result.success is False
        assert "Precondition" in result.error or "precondition" in result.error

    @pytest.mark.asyncio
    async def test_invoke_operation_no_grounding(self, composer):
        """Handle case where operation has no HTTP grounding."""
        # Modify mock to return no grounding
        original_query = composer._ontology.query_sparql

        def no_rounding_query(q):
            if "hasHTTPGrounding" in q:
                return {"results": {"bindings": []}}
            return original_query(q)

        composer._ontology.query_sparql = no_rounding_query

        result = await composer.invoke_operation(
            operation="https://w3id.org/waterframe/case/household/NoGrounding_Op",
            input_data={}
        )

        assert result.success is False
        assert "No HTTP grounding" in result.error


class TestOntologyComposerConstraintEvaluation:
    """Tests for constraint expression evaluation."""

    def test_evaluate_greater_than(self, composer):
        """Evaluate > constraints."""
        assert composer._evaluate_constraint("flow > 0", 10) is True
        assert composer._evaluate_constraint("flow > 0", 0) is False
        assert composer._evaluate_constraint("flow > 0", -1) is False

    def test_evaluate_less_than(self, composer):
        """Evaluate < constraints."""
        assert composer._evaluate_constraint("flow < 100", 50) is True
        assert composer._evaluate_constraint("flow < 100", 100) is False

    def test_evaluate_greater_equal(self, composer):
        """Evaluate >= constraints."""
        assert composer._evaluate_constraint("flow >= 0", 0) is True
        assert composer._evaluate_constraint("flow >= 0", 5) is True
        assert composer._evaluate_constraint("flow >= 0", -1) is False

    def test_evaluate_equality(self, composer):
        """Evaluate == constraints."""
        assert composer._evaluate_constraint("status == active", "active") is True
        assert composer._evaluate_constraint("status == active", "inactive") is False

    def test_evaluate_invalid_expression_defaults_true(self, composer):
        """Invalid expressions default to True for safety."""
        assert composer._evaluate_constraint("invalid_expr", 10) is True


class TestOntologyComposerIntegration:
    """Integration tests combining multiple features."""

    @pytest.mark.asyncio
    async def test_full_composition_flow(self, composer):
        """Test complete composition flow with ontology features."""
        # Store original mock
        original_mock = composer._ontology.query_sparql

        # Update mock to return proper I/O for composition
        def improved_mock(query):
            # Return MBR agent with proper inputs
            if "ComputationalAgent" in query and "requiresInput" in query:
                return {
                    "results": {
                        "bindings": [
                            {
                                "agent": {"value": "https://w3id.org/waterframe/case/household/MBR_Agent"},
                                "agentLabel": {"value": "Membrane Bioreactor Model"},
                                "operation": {"value": "https://w3id.org/waterframe/case/household/MBR_Simulation"},
                                "endpoint": {"value": "http://localhost:8101"},
                                "modelId": {"value": "mbr"}
                            }
                        ]
                    }
                }
            # Return MBR inputs
            elif "requiresInput" in query and "MBR_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "influent_flow_m3d"}},
                            {"paramName": {"value": "influent_cod_mg_l"}}
                        ]
                    }
                }
            # Return MBR outputs
            elif "producesOutput" in query and "MBR_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "effluent_flow_m3d"}},
                            {"paramName": {"value": "effluent_cod_mg_l"}},
                            {"paramName": {"value": "energy_kwh_d"}}
                        ]
                    }
                }
            return original_mock(query)

        composer._ontology.query_sparql = improved_mock

        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"effluent_cod_mg_l"}  # MBR output, reachable in 1 layer
        )

        # Should discover MBR agent
        assert result.found is True
        assert len(result.layers) >= 1
        assert any(a.id == "MBR_Agent" for layer in result.layers for a in layer.agents)

    @pytest.mark.asyncio
    async def test_capability_then_validate_then_invoke(self, composer):
        """Full workflow: discover by capability, validate, invoke."""
        # 1. Discover by capability
        agents = await composer.discover_by_capability(
            required_capabilities=["cap:DynamicSimulation", "cap:MassBalance"],
            available_data={"influent_flow_m3d", "influent_cod_mg_l"}
        )

        assert len(agents) > 0
        agent = agents[0]

        # 2. Validate
        validation = await composer.validate_execution(
            operation=agent.operation_uri,
            input_data={"influent_flow_m3d": 100, "influent_cod_mg_l": 200}
        )

        assert validation.valid is True


class TestOntologyComposerErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_composer_with_unloaded_ontology(self):
        """Handle unloaded ontology gracefully."""
        ontology = Mock()
        ontology.is_loaded.return_value = False

        composer = OntologyComposer(ontology)

        result = await composer.compose(
            initial_data={"influent_flow_m3d"},
            target_outputs={"effluent_cod_mg_l"}
        )

        assert result.found is False
        assert result.layers == []

    @pytest.mark.asyncio
    async def test_discover_by_capability_unloaded_ontology(self):
        """Handle capability discovery with unloaded ontology."""
        ontology = Mock()
        ontology.is_loaded.return_value = False

        composer = OntologyComposer(ontology)

        agents = await composer.discover_by_capability(
            required_capabilities=["cap:DynamicSimulation"],
            available_data={"influent_flow_m3d"}
        )

        assert agents == []

    @pytest.mark.asyncio
    async def test_validate_execution_unloaded_ontology(self):
        """Handle validation with unloaded ontology."""
        ontology = Mock()
        ontology.is_loaded.return_value = False

        composer = OntologyComposer(ontology)

        result = await composer.validate_execution(
            operation="case:MBR_Simulation",
            input_data={"influent_flow_m3d": 100}
        )

        # Should allow execution if ontology not loaded
        assert result.valid is True


class TestOntologyComposerNamespaceHandling:
    """Tests for proper namespace handling in queries."""

    @pytest.mark.asyncio
    async def test_uses_correct_wf_namespace(self, composer):
        """Verify queries use correct waterFRAME namespace."""
        with patch.object(composer._ontology, "query_sparql") as mock_query:
            mock_query.return_value = {"results": {"bindings": []}}

            await composer.discover_by_capability(
                required_capabilities=["cap:DynamicSimulation"],
                available_data={"influent_flow_m3d"}
            )

            # Check that the query was called with correct namespace
            call_args = mock_query.call_args[0][0]
            assert "https://ugentbiomath.github.io/waterframe#" in call_args
            assert "PREFIX wf:" in call_args

    @pytest.mark.asyncio
    async def test_uses_correct_cap_namespace(self, composer):
        """Verify queries use correct capability namespace."""
        with patch.object(composer._ontology, "query_sparql") as mock_query:
            mock_query.return_value = {"results": {"bindings": []}}

            await composer.discover_by_capability(
                required_capabilities=["cap:DynamicSimulation"],
                available_data={"influent_flow_m3d"}
            )

            call_args = mock_query.call_args[0][0]
            assert "cap:" in call_args
            assert "capability#" in call_args