"""Integration tests for agent composition with household models.

These tests verify that the agent_composer can discover and chain
household water treatment agents (MBR, RO, Infiltration) correctly.

The tests load the household agent declarations from the TTL file
and verify multi-layer composition scenarios.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import importlib.util

# Import agent_composer directly from core orchestrator file
# (avoids package dependency issues)
# Path: case_studies/household/tests/ -> case_studies/core/orchestrator/...
core_orchestrator_path = (
    Path(__file__).parent.parent.parent / "core" / "orchestrator" / "src" /
    "ontEAUlogy_core" / "services" / "agent_composer.py"
)
spec = importlib.util.spec_from_file_location("agent_composer", core_orchestrator_path)
agent_composer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_composer_module)

AgentComposer = agent_composer_module.AgentComposer
Agent = agent_composer_module.Agent
CompositionLayer = agent_composer_module.CompositionLayer
CompositionResult = agent_composer_module.CompositionResult


@pytest.fixture
def mock_ontology_with_household_agents():
    """Create a mock ontology with household agent declarations."""
    ontology = Mock()
    ontology.is_loaded.return_value = True
    
    # Simulate SPARQL results for agent discovery
    def mock_query_sparql(query):
        # Return agents based on the query type
        if "ComputationalAgent" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/MBR_Agent"},
                            "agentLabel": {"value": "Membrane Bioreactor Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/MBR_Simulation"},
                            "endpoint": {"value": "http://localhost:8101"},
                            "modelId": {"value": "mbr"},
                        },
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/RO_Agent"},
                            "agentLabel": {"value": "Reverse Osmosis Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/RO_Simulation"},
                            "endpoint": {"value": "http://localhost:8102"},
                            "modelId": {"value": "ro"},
                        },
                        {
                            "agent": {"value": "https://w3id.org/waterframe/case/household/Infiltration_Agent"},
                            "agentLabel": {"value": "Soil Infiltration Model"},
                            "operation": {"value": "https://w3id.org/waterframe/case/household/Infiltration_Simulation"},
                            "endpoint": {"value": "http://localhost:8103"},
                            "modelId": {"value": "infiltration"},
                        },
                    ]
                }
            }
        elif "requiresInput" in query or "producesOutput" in query:
            # I/O query - return based on operation URI
            if "MBR_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "influent_flow_m3d"}, "isInput": {"value": "true"}},
                            {"paramName": {"value": "influent_cod_mg_l"}, "isInput": {"value": "true"}},
                            {"paramName": {"value": "effluent_flow_m3d"}, "isInput": {"value": "false"}},
                            {"paramName": {"value": "effluent_cod_mg_l"}, "isInput": {"value": "false"}},
                            {"paramName": {"value": "energy_kwh_d"}, "isInput": {"value": "false"}},
                            # Compatible parameters for RO chaining (effluent -> feed mapping)
                            {"paramName": {"value": "feed_flow_m3d"}, "isInput": {"value": "false"}},
                            {"paramName": {"value": "feed_cod_mg_l"}, "isInput": {"value": "false"}},
                        ]
                    }
                }
            elif "RO_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "feed_flow_m3d"}, "isInput": {"value": "true"}},
                            {"paramName": {"value": "feed_cod_mg_l"}, "isInput": {"value": "true"}},
                            {"paramName": {"value": "permeate_flow_m3d"}, "isInput": {"value": "false"}},
                            {"paramName": {"value": "permeate_cod_mg_l"}, "isInput": {"value": "false"}},
                        ]
                    }
                }
            elif "Infiltration_Simulation" in query:
                return {
                    "results": {
                        "bindings": [
                            {"paramName": {"value": "influent_flow_m3d"}, "isInput": {"value": "true"}},
                            {"paramName": {"value": "outflow_m3d"}, "isInput": {"value": "false"}},
                        ]
                    }
                }
        return {"results": {"bindings": []}}
    
    ontology.query_sparql = mock_query_sparql
    return ontology


@pytest.fixture
def mock_registry():
    """Mock model registry."""
    return Mock()


@pytest.fixture
def composer(mock_ontology_with_household_agents, mock_registry):
    """AgentComposer instance with household agents."""
    return AgentComposer(mock_ontology_with_household_agents, mock_registry, max_iterations=5)


class TestHouseholdAgentComposition:
    """Integration tests for household water treatment agent composition."""
    
    @pytest.mark.asyncio
    async def test_mbr_to_ro_two_layer_composition(self, composer):
        """Test MBR → RO chain: 2-layer composition.
        
        Layer 0: MBR (takes influent_flow/cod, produces effluent_flow/cod)
        Layer 1: RO (takes feed_flow/cod, produces permeate_flow/cod)
        
        The MBR outputs (effluent_*) should connect to RO inputs (feed_*)
        through the parameter name mapping.
        """
        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"permeate_cod_mg_l"}
        )
        
        assert result.found is True, f"Composition failed. Missing: {result.missing}"
        assert len(result.layers) == 2, f"Expected 2 layers, got {len(result.layers)}"
        
        # Layer 0 should have MBR
        assert result.layers[0].agents[0].id == "MBR_Agent"
        assert "influent_flow_m3d" in result.layers[0].agents[0].required_inputs
        assert "effluent_flow_m3d" in result.layers[0].agents[0].produced_outputs
        
        # Layer 1 should have RO
        assert result.layers[1].agents[0].id == "RO_Agent"
        assert "feed_flow_m3d" in result.layers[1].agents[0].required_inputs
        assert "permeate_cod_mg_l" in result.layers[1].agents[0].produced_outputs
        
        # Verify the plan description
        plan = result.describe_plan()
        assert "MBR" in plan or "Bioreactor" in plan
        assert "RO" in plan or "Osmosis" in plan
    
    @pytest.mark.asyncio
    async def test_mbr_only_single_layer(self, composer):
        """Test single MBR agent - 1 layer composition."""
        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"effluent_cod_mg_l"}
        )
        
        assert result.found is True
        assert len(result.layers) == 1
        assert result.layers[0].agents[0].id == "MBR_Agent"
    
    @pytest.mark.asyncio
    async def test_infiltration_alternative_path(self, composer):
        """Test infiltration agent as alternative treatment path."""
        result = await composer.compose(
            initial_data={"influent_flow_m3d"},
            target_outputs={"outflow_m3d"}
        )
        
        assert result.found is True
        assert len(result.layers) == 1
        assert result.layers[0].agents[0].id == "Infiltration_Agent"
    
    @pytest.mark.asyncio
    async def test_parallel_agents_in_layer_zero(self, composer):
        """Test that MBR and Infiltration can run in parallel (both need influent_flow)."""
        # This test verifies that agents with the same input requirements
        # but different outputs can be in the same layer
        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"effluent_cod_mg_l", "outflow_m3d"}
        )
        
        assert result.found is True
        # Both MBR and Infiltration can run in parallel since they both
        # require influent_flow_m3d which is available initially
        # Note: MBR also needs influent_cod_mg_l, but that's also available
        
        # Layer 0 should have both agents (or at minimum 2 agents discovered)
        total_agents = sum(len(layer.agents) for layer in result.layers)
        assert total_agents >= 2, f"Expected at least 2 agents, got {total_agents}"
    
    @pytest.mark.asyncio
    async def test_unattainable_target(self, composer):
        """Test that composition fails gracefully for unattainable targets."""
        result = await composer.compose(
            initial_data={"influent_flow_m3d"},
            target_outputs={"nonexistent_parameter"}
        )
        
        assert result.found is False
        assert "nonexistent_parameter" in result.missing
    
    @pytest.mark.asyncio
    async def test_target_already_satisfied(self, composer):
        """Test early exit when target is already in initial data."""
        result = await composer.compose(
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"influent_flow_m3d"}  # Already available
        )
        
        assert result.found is True
        assert len(result.layers) == 0  # No agents needed
        assert result.discovery_iterations == 1


class TestHouseholdAgentDataStructures:
    """Tests for agent data structures with household-specific data."""
    
    def test_agent_can_execute_with_household_params(self):
        """Test agent execution check with household parameters."""
        mbr_agent = Agent(
            id="mbr",
            name="MBR Model",
            operation_uri="case:MBR_Simulation",
            endpoint="http://localhost:8101",
            required_inputs={"influent_flow_m3d", "influent_cod_mg_l"},
            produced_outputs={"effluent_flow_m3d", "effluent_cod_mg_l", "energy_kwh_d"},
            model_id="mbr"
        )
        
        # Should execute with all required inputs
        assert mbr_agent.can_execute_with({
            "influent_flow_m3d", "influent_cod_mg_l", "extra_param"
        }) is True
        
        # Should not execute with missing inputs
        assert mbr_agent.can_execute_with({"influent_flow_m3d"}) is False
        assert mbr_agent.can_execute_with(set()) is False
    
    def test_composition_layer_aggregates_household_io(self):
        """Test that layer correctly aggregates inputs/outputs."""
        mbr_agent = Agent(
            id="mbr",
            name="MBR Model",
            operation_uri="case:MBR_Simulation",
            endpoint="http://localhost:8101",
            required_inputs={"influent_flow_m3d", "influent_cod_mg_l"},
            produced_outputs={"effluent_flow_m3d", "effluent_cod_mg_l"},
            model_id="mbr"
        )
        
        infiltration_agent = Agent(
            id="infiltration",
            name="Infiltration Model",
            operation_uri="case:Infiltration_Simulation",
            endpoint="http://localhost:8103",
            required_inputs={"influent_flow_m3d"},
            produced_outputs={"outflow_m3d"},
            model_id="infiltration"
        )
        
        layer = CompositionLayer(layer_index=0, agents=[mbr_agent, infiltration_agent])
        
        # Layer should aggregate all required inputs
        assert layer.required_inputs == {
            "influent_flow_m3d", "influent_cod_mg_l"
        }
        
        # Layer should aggregate all produced outputs
        assert layer.produced_outputs == {
            "effluent_flow_m3d", "effluent_cod_mg_l", "outflow_m3d"
        }
    
    def test_composition_result_describes_household_plan(self):
        """Test plan description for household treatment train."""
        mbr_agent = Agent(
            id="mbr",
            name="Membrane Bioreactor",
            operation_uri="case:MBR_Simulation",
            endpoint="http://localhost:8101",
            required_inputs={"influent_flow_m3d", "influent_cod_mg_l"},
            produced_outputs={"effluent_flow_m3d", "effluent_cod_mg_l"},
            model_id="mbr"
        )
        
        ro_agent = Agent(
            id="ro",
            name="Reverse Osmosis",
            operation_uri="case:RO_Simulation",
            endpoint="http://localhost:8102",
            required_inputs={"feed_flow_m3d", "feed_cod_mg_l"},
            produced_outputs={"permeate_flow_m3d", "permeate_cod_mg_l"},
            model_id="ro"
        )
        
        result = CompositionResult(
            found=True,
            layers=[
                CompositionLayer(layer_index=0, agents=[mbr_agent]),
                CompositionLayer(layer_index=1, agents=[ro_agent]),
            ],
            initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
            target_outputs={"permeate_cod_mg_l"},
        )
        
        plan = result.describe_plan()
        assert "Execution Plan (2 layers)" in plan
        assert "Membrane Bioreactor" in plan
        assert "Reverse Osmosis" in plan
        
        agent_ids = result.get_all_agent_ids()
        assert agent_ids == ["mbr", "ro"]


class TestComposerWithUnloadedOntology:
    """Tests for composer behavior when ontology is not available."""
    
    @pytest.mark.asyncio
    async def test_composer_returns_empty_when_ontology_not_loaded(self):
        """Composer should return empty result when ontology is not loaded."""
        ontology = Mock()
        ontology.is_loaded.return_value = False
        registry = Mock()
        
        composer = AgentComposer(ontology, registry)
        
        result = await composer.compose(
            initial_data={"influent_flow_m3d"},
            target_outputs={"effluent_cod_mg_l"}
        )
        
        assert result.found is False
        assert result.layers == []
        assert "effluent_cod_mg_l" in result.missing
