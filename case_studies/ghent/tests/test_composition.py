"""Tests for agent composition algorithm."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add src to path for direct imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import directly from file to avoid triggering __init__.py imports
import importlib.util
agent_composer_path = Path(__file__).parent.parent / "src" / "ghent_water" / "orchestrator" / "services" / "agent_composer.py"
spec = importlib.util.spec_from_file_location("agent_composer", agent_composer_path)
agent_composer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_composer_module)

AgentComposer = agent_composer_module.AgentComposer
Agent = agent_composer_module.Agent
CompositionLayer = agent_composer_module.CompositionLayer
CompositionResult = agent_composer_module.CompositionResult


@pytest.fixture
def mock_ontology():
    """Mock ontology store."""
    ontology = Mock()
    ontology.is_loaded.return_value = True
    return ontology


@pytest.fixture
def mock_registry():
    """Mock model registry."""
    return Mock()


@pytest.fixture
def composer(mock_ontology, mock_registry):
    """AgentComposer instance with mocks."""
    return AgentComposer(mock_ontology, mock_registry, max_iterations=5)


@pytest.mark.asyncio
async def test_mbr_to_ro_composition(composer, mock_ontology):
    """Test discovering MBR→RO chain."""
    
    # Setup: MBR agent available
    mbr_agent = Agent(
        id="mbr",
        name="MBR Model",
        operation_uri="case:MBR_Simulation",
        endpoint="http://localhost:8101",
        required_inputs={"influent_flow_m3d", "influent_cod_mg_l"},
        produced_outputs={"effluent_flow_m3d", "effluent_cod_mg_l", "energy_kwh_d"},
        model_id="mbr"
    )
    
    ro_agent = Agent(
        id="ro",
        name="RO Model",
        operation_uri="case:RO_Simulation",
        endpoint="http://localhost:8102",
        required_inputs={"feed_flow_m3d", "feed_cod_mg_l"},
        produced_outputs={"permeate_flow_m3d", "permeate_cod_mg_l"},
        model_id="ro"
    )
    
    # Mock discovery to return agents in sequence
    discovery_calls = [
        [mbr_agent],  # First call: only MBR inputs satisfied
        [ro_agent],   # Second call: after MBR outputs added, RO inputs satisfied
    ]
    
    composer._discover_agents = AsyncMock(side_effect=discovery_calls)
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    # Execute
    result = await composer.compose(
        initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
        target_outputs={"permeate_cod_mg_l"}
    )
    
    # Assert
    assert result.found is True
    assert len(result.layers) == 2
    assert result.layers[0].agents[0].id == "mbr"
    assert result.layers[1].agents[0].id == "ro"


@pytest.mark.asyncio
async def test_parallel_agent_discovery(composer, mock_ontology):
    """Test that independent agents are grouped in same layer."""
    
    # Two agents that can both run with initial data
    agent1 = Agent(
        id="agent1",
        name="Agent 1",
        operation_uri="op:1",
        endpoint="http://localhost:8001",
        required_inputs={"input_a"},
        produced_outputs={"output_1"}
    )
    
    agent2 = Agent(
        id="agent2",
        name="Agent 2",
        operation_uri="op:2",
        endpoint="http://localhost:8002",
        required_inputs={"input_a"},
        produced_outputs={"output_2"}
    )
    
    composer._discover_agents = AsyncMock(return_value=[agent1, agent2])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"output_1", "output_2"}
    )
    
    # Both agents should be in layer 0 (can run in parallel)
    assert result.found is True
    assert len(result.layers) == 1
    assert len(result.layers[0].agents) == 2


@pytest.mark.asyncio
async def test_no_composition_possible(composer, mock_ontology):
    """Test when target cannot be reached."""
    
    composer._discover_agents = AsyncMock(return_value=[])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"unreachable_output"}
    )
    
    assert result.found is False
    assert "unreachable_output" in result.missing


@pytest.mark.asyncio
async def test_target_already_available(composer, mock_ontology):
    """Test when target is already in initial data."""
    
    result = await composer.compose(
        initial_data={"param_a", "param_b"},
        target_outputs={"param_a"}
    )
    
    # Should return immediately with no layers needed
    assert result.found is True
    assert len(result.layers) == 0
    assert result.discovery_iterations == 1


@pytest.mark.asyncio
async def test_three_layer_composition(composer, mock_ontology):
    """Test a three-layer chain: A → B → C"""
    
    agent_a = Agent(
        id="a",
        name="Agent A",
        operation_uri="op:a",
        endpoint="http://localhost:8001",
        required_inputs={"input_1"},
        produced_outputs={"intermediate_1"}
    )
    
    agent_b = Agent(
        id="b",
        name="Agent B",
        operation_uri="op:b",
        endpoint="http://localhost:8002",
        required_inputs={"intermediate_1"},
        produced_outputs={"intermediate_2"}
    )
    
    agent_c = Agent(
        id="c",
        name="Agent C",
        operation_uri="op:c",
        endpoint="http://localhost:8003",
        required_inputs={"intermediate_2"},
        produced_outputs={"final_output"}
    )
    
    composer._discover_agents = AsyncMock(side_effect=[
        [agent_a],
        [agent_b],
        [agent_c],
    ])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_1"},
        target_outputs={"final_output"}
    )
    
    assert result.found is True
    assert len(result.layers) == 3
    assert result.layers[0].agents[0].id == "a"
    assert result.layers[1].agents[0].id == "b"
    assert result.layers[2].agents[0].id == "c"


@pytest.mark.asyncio
async def test_agent_with_multiple_inputs(composer, mock_ontology):
    """Test agent that requires multiple inputs from different sources."""
    
    agent_source1 = Agent(
        id="source1",
        name="Source 1",
        operation_uri="op:s1",
        endpoint="http://localhost:8001",
        required_inputs={"initial_a"},
        produced_outputs={"intermediate_a"}
    )
    
    agent_source2 = Agent(
        id="source2",
        name="Source 2",
        operation_uri="op:s2",
        endpoint="http://localhost:8002",
        required_inputs={"initial_b"},
        produced_outputs={"intermediate_b"}
    )
    
    agent_combiner = Agent(
        id="combiner",
        name="Combiner",
        operation_uri="op:comb",
        endpoint="http://localhost:8003",
        required_inputs={"intermediate_a", "intermediate_b"},
        produced_outputs={"final_output"}
    )
    
    composer._discover_agents = AsyncMock(side_effect=[
        [agent_source1, agent_source2],  # Both sources in layer 0
        [agent_combiner],                 # Combiner in layer 1
    ])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"initial_a", "initial_b"},
        target_outputs={"final_output"}
    )
    
    assert result.found is True
    assert len(result.layers) == 2
    assert len(result.layers[0].agents) == 2  # Parallel sources
    assert result.layers[1].agents[0].id == "combiner"


@pytest.mark.asyncio
async def test_prevents_duplicate_agents(composer, mock_ontology):
    """Test that same agent is not added multiple times."""
    
    agent = Agent(
        id="agent1",
        name="Agent 1",
        operation_uri="op:1",
        endpoint="http://localhost:8001",
        required_inputs={"input_a"},
        produced_outputs={"output_a"}
    )
    
    # Same agent returned twice
    composer._discover_agents = AsyncMock(return_value=[agent])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"output_a"}
    )
    
    # Should only have one layer with one agent, even if discovered multiple times
    assert result.found is True
    assert len(result.layers) == 1
    assert len(result.layers[0].agents) == 1


class TestAgent:
    """Tests for the Agent dataclass."""
    
    def test_can_execute_with_satisfied_inputs(self):
        agent = Agent(
            id="test",
            name="Test Agent",
            operation_uri="op:test",
            endpoint="http://localhost:8000",
            required_inputs={"input_a", "input_b"},
            produced_outputs={"output_a"}
        )
        
        assert agent.can_execute_with({"input_a", "input_b", "input_c"}) is True
        assert agent.can_execute_with({"input_a"}) is False
        assert agent.can_execute_with({"input_a", "input_b"}) is True


class TestCompositionLayer:
    """Tests for the CompositionLayer dataclass."""
    
    def test_layer_properties(self):
        agent1 = Agent(
            id="a1",
            name="Agent 1",
            operation_uri="op:1",
            endpoint="http://localhost:8001",
            required_inputs={"input_a"},
            produced_outputs={"output_a"}
        )
        
        agent2 = Agent(
            id="a2",
            name="Agent 2",
            operation_uri="op:2",
            endpoint="http://localhost:8002",
            required_inputs={"input_b"},
            produced_outputs={"output_b"}
        )
        
        layer = CompositionLayer(layer_index=0, agents=[agent1, agent2])
        
        assert layer.required_inputs == {"input_a", "input_b"}
        assert layer.produced_outputs == {"output_a", "output_b"}


class TestCompositionResult:
    """Tests for the CompositionResult dataclass."""
    
    def test_describe_plan_success(self):
        agent = Agent(
            id="test",
            name="Test Agent",
            operation_uri="op:test",
            endpoint="http://localhost:8000",
            required_inputs=set(),
            produced_outputs=set()
        )
        
        result = CompositionResult(
            found=True,
            layers=[CompositionLayer(layer_index=0, agents=[agent])],
            initial_data=set(),
            target_outputs=set()
        )
        
        plan = result.describe_plan()
        assert "Execution Plan (1 layers)" in plan
        assert "Test Agent" in plan
    
    def test_describe_plan_failure(self):
        result = CompositionResult(
            found=False,
            layers=[],
            initial_data=set(),
            target_outputs=set(),
            missing={"missing_param"}
        )
        
        plan = result.describe_plan()
        assert "Cannot answer query" in plan
        assert "missing_param" in plan
    
    def test_get_all_agent_ids(self):
        agent1 = Agent(
            id="agent1",
            name="Agent 1",
            operation_uri="op:1",
            endpoint="http://localhost:8001",
            required_inputs=set(),
            produced_outputs=set()
        )
        
        agent2 = Agent(
            id="agent2",
            name="Agent 2",
            operation_uri="op:2",
            endpoint="http://localhost:8002",
            required_inputs=set(),
            produced_outputs=set()
        )
        
        result = CompositionResult(
            found=True,
            layers=[
                CompositionLayer(layer_index=0, agents=[agent1]),
                CompositionLayer(layer_index=1, agents=[agent2])
            ],
            initial_data=set(),
            target_outputs=set()
        )
        
        ids = result.get_all_agent_ids()
        assert ids == ["agent1", "agent2"]


@pytest.mark.asyncio
async def test_composer_with_ontology_not_loaded(composer, mock_ontology):
    """Test behavior when ontology is not loaded."""
    
    mock_ontology.is_loaded.return_value = False
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"output_b"}
    )
    
    assert result.found is False
    assert "output_b" in result.missing
