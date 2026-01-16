"""
Pytest tests for the ontology modules.

Run with: uv run pytest tests/test_ontology_modules.py -v
"""

import pytest
from pathlib import Path

try:
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF, RDFS, OWL
    HAS_RDFLIB = True
except ImportError:
    HAS_RDFLIB = False


# Namespace definitions
WF = Namespace("https://ugentbiomath.github.io/waterframe#")
CAP = Namespace("https://ugentbiomath.github.io/waterframe/capability#")


@pytest.fixture
def ontology_graph():
    """Load the main ontology and test instances."""
    if not HAS_RDFLIB:
        pytest.skip("rdflib not installed")
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    g.parse(str(base_path / "waterframe.ttl"), format="turtle")
    g.parse(str(base_path / "instances" / "ghent_case_study_test.ttl"), format="turtle")
    return g


@pytest.fixture
def base_path():
    """Return the base path to the ontology directory."""
    return Path(__file__).parent.parent / "data" / "ontology"


@pytest.fixture
def full_ontology_graph():
    """Load all ontology modules and test instances."""
    if not HAS_RDFLIB:
        pytest.skip("rdflib not installed")
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    # Load core modules
    g.parse(str(base_path / "modules" / "core" / "material_entities.ttl"), format="turtle")
    g.parse(str(base_path / "modules" / "core" / "properties.ttl"), format="turtle")
    # Load extended modules
    g.parse(str(base_path / "modules" / "information.ttl"), format="turtle")
    g.parse(str(base_path / "modules" / "capabilities.ttl"), format="turtle")
    g.parse(str(base_path / "modules" / "qualities.ttl"), format="turtle")
    # Load test instances
    g.parse(str(base_path / "instances" / "ghent_case_study_test.ttl"), format="turtle")
    return g


class TestInformationModule:
    """Tests for the information.ttl module (Model Metadata)."""
    
    def test_ontology_loads(self, ontology_graph):
        """Test that the ontology loads correctly."""
        assert len(ontology_graph) > 0, "Ontology should load with triples"
    
    def test_process_model_class_exists(self, full_ontology_graph):
        """Test that ProcessModel class exists."""
        found = any(WF.ProcessModel in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
        assert found, "ProcessModel class should exist"
    
    def test_simulation_model_class_exists(self, full_ontology_graph):
        """Test that SimulationModel class exists."""
        found = any(WF.SimulationModel in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
        assert found, "SimulationModel class should exist"
    
    def test_model_variable_classes_exist(self, full_ontology_graph):
        """Test that ModelVariable and subclasses exist."""
        required_classes = [
            WF.ModelVariable,
            WF.StateVariable,
            WF.InputVariable,
            WF.OutputVariable,
            WF.Parameter,
            WF.DecisionVariable,
        ]
        
        for cls in required_classes:
            found = any(cls in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
            assert found, f"{cls.split('#')[-1]} class should exist"
    
    def test_software_system_class_exists(self, full_ontology_graph):
        """Test that SoftwareSystem class exists."""
        found = any(WF.SoftwareSystem in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
        assert found, "SoftwareSystem class should exist"
    
    def test_model_properties_exist(self, full_ontology_graph):
        """Test that required model properties exist."""
        required_properties = [
            WF.hasInput,
            WF.hasOutput,
            WF.hasModelVariable,
            WF.hasParameter,
            WF.hasStateVariable,
            WF.hasInputVariable,
            WF.hasOutputVariable,
            WF.representsEntity,
            WF.isDecisionVariable,
            WF.parameterName,
            WF.numericalValue,
            WF.minValue,
            WF.maxValue,
        ]
        
        for prop in required_properties:
            found = (
                any(prop in s for s in full_ontology_graph.subjects(RDF.type, OWL.ObjectProperty)) or
                any(prop in s for s in full_ontology_graph.subjects(RDF.type, OWL.DatatypeProperty))
            )
            prop_name = str(prop).split('#')[-1].split('/')[-1]
            assert found, f"{prop_name} property should exist"
    
    def test_asm1_model_exists(self, ontology_graph):
        """Test that ASM1 model instance exists in test data."""
        found = any(
            str(s).endswith("ASM1_Model") 
            for s in ontology_graph.subjects(RDF.type, WF.SimulationModel)
        )
        assert found, "ASM1_Model instance should exist in test data"
    
    def test_model_inputs_query(self, ontology_graph):
        """Test CQ18: Find model input variables."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?var WHERE {
            wf:ASM1_Model wf:hasInputVariable ?var .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "ASM1_Model should have input variables"
    
    def test_model_outputs_query(self, ontology_graph):
        """Test CQ19: Find model output variables."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?var WHERE {
            wf:ASM1_Model wf:hasOutputVariable ?var .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "ASM1_Model should have output variables"
    
    def test_decision_variables_query(self, ontology_graph):
        """Test CQ20: Find decision variables."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?var WHERE {
            wf:ASM1_Model wf:hasInputVariable ?var .
            ?var wf:isDecisionVariable "true"^^xsd:boolean .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "ASM1_Model should have decision variables"


class TestCapabilitiesModule:
    """Tests for the capabilities.ttl module (Simulation Capabilities)."""
    
    def test_capability_classes_exist(self, full_ontology_graph):
        """Test that required capability classes exist."""
        required_capabilities = [
            CAP.ModelCapability,
            CAP.SteadyStateSimulation,
            CAP.DynamicSimulation,
            CAP.SensitivityAnalysis,
            CAP.UncertaintyQuantification,
            CAP.Optimization,
            CAP.MassBalance,
            CAP.EnergyBalance,
            CAP.WaterQualityPrediction,
            CAP.CostEstimation,
        ]
        
        for cap in required_capabilities:
            found = any(cap in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
            cap_name = str(cap).split('#')[-1].split('/')[-1]
            assert found, f"{cap_name} class should exist"
    
    def test_capability_properties_exist(self, full_ontology_graph):
        """Test that capability properties exist."""
        required_properties = [
            CAP.description,
            CAP.requiredInputs,
            CAP.producesOutputs,
            CAP.implementedByModel,
            WF.hasCapability,
        ]
        
        for prop in required_properties:
            found = (
                any(prop in s for s in full_ontology_graph.subjects(RDF.type, OWL.ObjectProperty)) or
                any(prop in s for s in full_ontology_graph.subjects(RDF.type, OWL.DatatypeProperty))
            )
            prop_name = str(prop).split('#')[-1].split('/')[-1]
            assert found, f"{prop_name} property should exist"
    
    def test_asm1_capabilities_query(self, ontology_graph):
        """Test CQ23: Find model capabilities."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX cap: <https://ugentbiomath.github.io/waterframe/capability#>
        SELECT ?cap WHERE {
            wf:ASM1_Model wf:hasCapability ?cap .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "ASM1_Model should have capabilities"
        
        # Check that it has MassBalance capability
        cap_names = [str(row[0]).split('#')[-1].split('/')[-1] for row in results]
        assert "MassBalance" in cap_names, "ASM1_Model should have MassBalance capability"
    
    def test_software_capabilities_query(self, ontology_graph):
        """Test that software has capabilities."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?sw ?cap WHERE {
            ?sw a wf:SoftwareSystem ;
                wf:hasCapability ?cap .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "Software systems should have capabilities"


class TestQualitiesModule:
    """Tests for the qualities.ttl module (Water Quality Parameters)."""
    
    def test_water_quality_parameter_classes_exist(self, full_ontology_graph):
        """Test that required water quality parameter classes exist."""
        required_parameters = [
            WF.WaterQualityParameter,
            WF.BOD,
            WF.COD,
            WF.TSS,
            WF.TDS,
            WF.pH,
            WF.Temperature,
            WF.Turbidity,
            WF.Conductivity,
            WF.DissolvedOxygen,
            WF.TotalNitrogen,
            WF.TotalPhosphorus,
        ]
        
        for param in required_parameters:
            found = any(param in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
            param_name = str(param).split('#')[-1].split('/')[-1]
            assert found, f"{param_name} class should exist"
    
    def test_water_quality_requirement_classes_exist(self, full_ontology_graph):
        """Test that water quality requirement classes exist."""
        required_classes = [
            WF.WaterQualityRequirement,
            WF.WaterQualityObservation,
            WF.RegulatoryStandard,
            WF.LimitType,
            WF.MaximumLimit,
            WF.MinimumLimit,
        ]
        
        for cls in required_classes:
            found = any(cls in s for s in full_ontology_graph.subjects(RDF.type, OWL.Class))
            cls_name = str(cls).split('#')[-1].split('/')[-1]
            assert found, f"{cls_name} class should exist"
    
    def test_water_quality_observations_query(self, ontology_graph):
        """Test CQ10: Find water quality observations."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?obs ?param ?value WHERE {
            ?obs wf:observedParameter ?param ;
                 wf:observedValue ?value .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "Should have water quality observations"
    
    def test_regulatory_limits_query(self, ontology_graph):
        """Test CQ11: Find regulatory limits."""
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?req ?param ?limit WHERE {
            ?req wf:hasWaterQualityParameter ?param ;
                 wf:hasLimitValue ?limit ;
                 wf:hasLimitType wf:MaximumLimit .
        }
        """
        results = list(ontology_graph.query(query))
        assert len(results) > 0, "Should have regulatory limits"
    
    def test_eu_standard_exists(self, ontology_graph):
        """Test that EU Water Framework Directive standard exists."""
        found = any(
            str(s).endswith("EU_Water_Framework_Directive")
            for s in ontology_graph.subjects(RDF.type, WF.RegulatoryStandard)
        )
        assert found, "EU_Water_Framework_Directive should exist"


class TestMaterialEntitiesModule:
    """Tests for the updated material_entities.ttl module."""
    
    def test_wwtp_entities_exist(self, full_ontology_graph):
        """Test that WWTP entity classes exist."""
        required_entities = [
            WF.WastewaterTreatmentPlant,
            WF.DrinkingWaterPlant,
            WF.PrimaryTreatment,
            WF.SecondaryTreatment,
            WF.TertiaryTreatment,
            WF.AerationTank,
            WF.SecondarySettler,
            WF.MembraneBioreactor,
            WF.DisinfectionUnit,
        ]
        
        for entity in required_entities:
            # Check if entity appears as subject of rdfs:subClassOf (shorthand class declaration)
            found = any(entity in s for s in full_ontology_graph.subjects(RDFS.subClassOf, None))
            entity_name = str(entity).split('#')[-1].split('/')[-1]
            assert found, f"{entity_name} should exist"
    
    def test_industrial_facilities_exist(self, full_ontology_graph):
        """Test that industrial facility classes exist."""
        required_facilities = [
            WF.IndustrialFacility,
            WF.TextileIndustry,
            WF.FoodProcessingIndustry,
            WF.ElectronicsManufacturing,
            WF.PharmaceuticalIndustry,
            WF.Brewery,
        ]
        
        for facility in required_facilities:
            found = any(facility in s for s in full_ontology_graph.subjects(RDFS.subClassOf, None))
            facility_name = str(facility).split('#')[-1].split('/')[-1]
            assert found, f"{facility_name} should exist"
    
    def test_water_bodies_exist(self, full_ontology_graph):
        """Test that natural water body classes exist."""
        required_bodies = [
            WF.River,
            WF.RiverSegment,
            WF.Lake,
            WF.Groundwater,
            WF.Catchment,
        ]
        
        for body in required_bodies:
            found = any(body in s for s in full_ontology_graph.subjects(RDFS.subClassOf, None))
            body_name = str(body).split('#')[-1].split('/')[-1]
            assert found, f"{body_name} should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
