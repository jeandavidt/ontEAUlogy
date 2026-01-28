#!/usr/bin/env python3
"""
Test suite for WaWO+ Ontology
Tests competency questions using rdflib and SPARQL queries
"""

import unittest
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from datetime import datetime, timedelta


class TestWaWOPlus(unittest.TestCase):
    """Test suite for WaWO+ ontology"""

    @classmethod
    def setUpClass(cls):
        """Load the ontology once for all tests"""
        cls.g = Graph()
        cls.wawo = Namespace("http://www.semanticweb.org/riverbasin#")
        cls.g.bind("wawo", cls.wawo)
        cls.g.bind("rdf", RDF)
        cls.g.bind("rdfs", RDFS)
        cls.g.bind("owl", OWL)
        cls.g.bind("xsd", XSD)

        # Load the ontology
        try:
            cls.g.parse("wawo_plus.ttl", format="turtle")
            print(f"\n✓ Ontology loaded successfully: {len(cls.g)} triples")
        except Exception as e:
            print(f"\n✗ Error loading ontology: {e}")
            raise

        # Add test data
        cls._add_test_data()

    @classmethod
    def _add_test_data(cls):
        """Add test instances for competency questions"""
        wawo = cls.wawo
        g = cls.g

        # Test Case 1: Clean drinking water
        clean_water = wawo.CleanWaterSample1
        g.add((clean_water, RDF.type, wawo.WaterMass))
        g.add((clean_water, wawo.biologicalOxygenDemandConcentration, Literal(3.5, datatype=XSD.float)))
        g.add((clean_water, wawo.chemicalOxygenDemandConcentration, Literal(8.0, datatype=XSD.float)))
        g.add((clean_water, wawo.suspendedSolidConcentration, Literal(7.0, datatype=XSD.float)))
        g.add((clean_water, wawo.totalNitrogenConcentration, Literal(1.5, datatype=XSD.float)))
        g.add((clean_water, wawo.totalPhosphorusConcentration, Literal(0.3, datatype=XSD.float)))
        g.add((clean_water, wawo.pH, Literal(7.2, datatype=XSD.float)))
        g.add((clean_water, wawo.temperature, Literal(15.5, datatype=XSD.float)))

        clean_comp = wawo.CleanWaterComposition1
        g.add((clean_comp, RDF.type, wawo.DrinkingWaterComposition))
        g.add((clean_water, wawo.hasWaterComposition, clean_comp))

        # Test Case 2: Contaminated wastewater
        contaminated_water = wawo.ContaminatedWaterSample1
        g.add((contaminated_water, RDF.type, wawo.WaterMass))
        g.add((contaminated_water, wawo.biologicalOxygenDemandConcentration, Literal(150.0, datatype=XSD.float)))
        g.add((contaminated_water, wawo.chemicalOxygenDemandConcentration, Literal(280.0, datatype=XSD.float)))
        g.add((contaminated_water, wawo.suspendedSolidConcentration, Literal(220.0, datatype=XSD.float)))
        g.add((contaminated_water, wawo.totalNitrogenConcentration, Literal(45.0, datatype=XSD.float)))
        g.add((contaminated_water, wawo.totalPhosphorusConcentration, Literal(8.5, datatype=XSD.float)))
        g.add((contaminated_water, wawo.heavyMetalConcentration, Literal(0.006, datatype=XSD.float)))

        wastewater_comp = wawo.WastewaterComposition1
        g.add((wastewater_comp, RDF.type, wawo.WastewaterComposition))
        g.add((contaminated_water, wawo.hasWaterComposition, wastewater_comp))

        # Test Case 3: WWTP with secondary treatment
        wwtp1 = wawo.WWTP_Barcelona1
        g.add((wwtp1, RDF.type, wawo.WWTP))
        g.add((wwtp1, wawo.populationEquivalent, Literal(15000, datatype=XSD.integer)))

        secondary_treatment = wawo.SecondaryTreatment1
        g.add((secondary_treatment, RDF.type, wawo.SecondaryTreatment))
        g.add((wwtp1, wawo.performs, secondary_treatment))

        # Received water (influent)
        influent = wawo.InfluentWater1
        g.add((influent, RDF.type, wawo.WaterMass))
        g.add((influent, wawo.biologicalOxygenDemandConcentration, Literal(200.0, datatype=XSD.float)))
        g.add((wwtp1, wawo.received, influent))

        # Discharged water (effluent)
        effluent = wawo.EffluentWater1
        g.add((effluent, RDF.type, wawo.WaterMass))
        g.add((effluent, wawo.biologicalOxygenDemandConcentration, Literal(25.0, datatype=XSD.float)))
        g.add((effluent, wawo.chemicalOxygenDemandConcentration, Literal(125.0, datatype=XSD.float)))
        g.add((wwtp1, wawo.discharged, effluent))

        # Test Case 4: Non-compliant WWTP (no secondary treatment)
        wwtp2 = wawo.WWTP_SmallTown1
        g.add((wwtp2, RDF.type, wawo.WWTP))
        g.add((wwtp2, wawo.populationEquivalent, Literal(12000, datatype=XSD.integer)))
        # Note: No secondary treatment process added - this is non-compliant

        primary_treatment = wawo.PrimaryTreatment1
        g.add((primary_treatment, RDF.type, wawo.WaterTreatment))
        g.add((wwtp2, wawo.performs, primary_treatment))

        # Test Case 5: Flow water mass
        river_flow = wawo.RiverFlow1
        g.add((river_flow, RDF.type, wawo.Flow_water_mass))
        g.add((river_flow, wawo.flow, Literal(12.5, datatype=XSD.float)))
        g.add((river_flow, wawo.biologicalOxygenDemandConcentration, Literal(4.2, datatype=XSD.float)))
        g.add((river_flow, wawo.chemicalOxygenDemandConcentration, Literal(9.1, datatype=XSD.float)))
        g.add((river_flow, wawo.suspendedSolidConcentration, Literal(8.5, datatype=XSD.float)))
        g.add((river_flow, wawo.totalNitrogenConcentration, Literal(1.8, datatype=XSD.float)))
        g.add((river_flow, wawo.totalPhosphorusConcentration, Literal(0.4, datatype=XSD.float)))

        # Test Case 6: River section with water mass
        river_section = wawo.BesosSectionA
        g.add((river_section, RDF.type, wawo.RiverSection))
        g.add((river_section, wawo.hasWaterMass, river_flow))

        river_basin = wawo.BesosBasin
        g.add((river_basin, RDF.type, wawo.RiverBasin))
        g.add((river_section, wawo.locatedIn, river_basin))

        # Test Case 7: Wastewater producers
        household = wawo.ResidentialArea1
        g.add((household, RDF.type, wawo.Household))
        g.add((household, wawo.populationEquivalent, Literal(5000, datatype=XSD.integer)))
        g.add((household, wawo.produces, contaminated_water))

        industry = wawo.ChemicalPlant1
        g.add((industry, RDF.type, wawo.Industry))
        g.add((industry, wawo.populationEquivalent, Literal(8000, datatype=XSD.integer)))

        industrial_wastewater = wawo.IndustrialWastewater1
        g.add((industrial_wastewater, RDF.type, wawo.WaterMass))
        g.add((industrial_wastewater, wawo.biologicalOxygenDemandConcentration, Literal(450.0, datatype=XSD.float)))
        g.add((industrial_wastewater, wawo.heavyMetalConcentration, Literal(0.008, datatype=XSD.float)))
        g.add((industry, wawo.produces, industrial_wastewater))

        # Test Case 8: Conveyor units
        pipe1 = wawo.Pipe1
        pipe2 = wawo.Pipe2
        g.add((pipe1, RDF.type, wawo.Pipe))
        g.add((pipe2, RDF.type, wawo.Pipe))
        g.add((pipe1, wawo.connectedTo, pipe2))
        g.add((pipe2, wawo.connectedTo, wwtp1))

        # Test Case 9: Heavy rain event
        rain_event = wawo.StormEvent20231115
        g.add((rain_event, RDF.type, wawo.Rainfall))
        g.add((rain_event, wawo.precipitationAmount, Literal(250.0, datatype=XSD.float)))
        g.add((rain_event, wawo.duration, Literal("PT2H30M", datatype=XSD.duration)))

        start_time = wawo.Timestamp20231115_1400
        end_time = wawo.Timestamp20231115_1630
        g.add((start_time, RDF.type, wawo.TimeStamp))
        g.add((end_time, RDF.type, wawo.TimeStamp))
        g.add((rain_event, wawo.hasTimestampStart, start_time))
        g.add((rain_event, wawo.hasTimestampEnd, end_time))

        # Test Case 10: River Basin Authority
        authority = wawo.CatalanWaterAuthority
        g.add((authority, RDF.type, wawo.RiverBasinAuthority))
        g.add((authority, wawo.manages, river_basin))

        # Test Case 11: Emerging contaminant
        pharma_water = wawo.PharmaceuticalContaminatedWater1
        g.add((pharma_water, RDF.type, wawo.WaterMass))
        g.add((pharma_water, wawo.emergingPollutantConcentration, Literal(0.15, datatype=XSD.float)))
        g.add((pharma_water, wawo.biologicalOxygenDemandConcentration, Literal(12.0, datatype=XSD.float)))

        print(f"✓ Test data added: {len(g)} total triples")

    def test_01_ontology_loaded(self):
        """Test that the ontology is loaded correctly"""
        # Check that we have triples
        self.assertGreater(len(self.g), 0, "Ontology should have triples")

        # Check for key classes
        key_classes = [
            self.wawo.WaterMass,
            self.wawo.WaterComposition,
            self.wawo.WaterIndicator,
            self.wawo.WWTP,
            self.wawo.DrinkingWaterComposition
        ]

        for cls in key_classes:
            self.assertIn((cls, RDF.type, OWL.Class), self.g,
                         f"Class {cls} should be defined")

        print("✓ Test 1: Ontology structure validated")

    def test_02_class_hierarchy(self):
        """Test class hierarchy relationships"""
        # Check that DrinkingWaterComposition is a subclass of WaterComposition
        result = self.g.query("""
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            ASK {
                wawo:DrinkingWaterComposition rdfs:subClassOf wawo:WaterComposition .
            }
        """)
        self.assertTrue(bool(result), "DrinkingWaterComposition should be subclass of WaterComposition")

        # Check Flow_water_mass is subclass of WaterMass
        result = self.g.query("""
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            ASK {
                wawo:Flow_water_mass rdfs:subClassOf wawo:WaterMass .
            }
        """)
        self.assertTrue(bool(result), "Flow_water_mass should be subclass of WaterMass")

        print("✓ Test 2: Class hierarchy validated")

    def test_03_disjoint_classes(self):
        """Test disjoint class axioms"""
        # Check that Flow_water_mass and Static_water_mass are disjoint
        result = self.g.query("""
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            ASK {
                wawo:Flow_water_mass owl:disjointWith wawo:Static_water_mass .
            }
        """)
        self.assertTrue(bool(result), "Flow and static water masses should be disjoint")

        print("✓ Test 3: Disjoint classes validated")

    def test_04_cq1_drinking_water_classification(self):
        """CQ1.1: Can the system identify drinking water quality?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?composition
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:hasWaterComposition ?composition .
                ?composition a wawo:DrinkingWaterComposition .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find drinking water compositions")
        print(f"✓ Test 4 (CQ1.1): Found {len(results)} drinking water samples")

    def test_05_cq1_contaminated_water(self):
        """CQ1.2: Can the system identify contaminated water?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?composition
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:hasWaterComposition ?composition .
                ?composition a wawo:WastewaterComposition .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find wastewater compositions")
        print(f"✓ Test 5 (CQ1.2): Found {len(results)} wastewater samples")

    def test_06_cq1_concentration_query(self):
        """CQ1.3: Can we query concentration levels?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?bod ?cod ?ss ?tn ?tp
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:biologicalOxygenDemandConcentration ?bod ;
                           wawo:chemicalOxygenDemandConcentration ?cod ;
                           wawo:suspendedSolidConcentration ?ss ;
                           wawo:totalNitrogenConcentration ?tn ;
                           wawo:totalPhosphorusConcentration ?tp .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find water masses with all concentrations")

        # Validate that we got numeric values
        for row in results:
            self.assertIsNotNone(row.bod, "BOD should have a value")
            self.assertIsNotNone(row.cod, "COD should have a value")

        print(f"✓ Test 6 (CQ1.3): Found {len(results)} water masses with full concentration data")

    def test_07_cq2_wwtps_with_treatment(self):
        """CQ2.1: Which WWTPs are performing treatment?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?wwtp ?process
            WHERE {
                ?wwtp a wawo:WWTP ;
                      wawo:performs ?process .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find WWTPs performing treatment")
        print(f"✓ Test 7 (CQ2.1): Found {len(results)} WWTP-process pairs")

    def test_08_cq2_wwtp_population_requirement(self):
        """CQ2.2: Which WWTPs should have secondary treatment?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?wwtp ?popEq
            WHERE {
                ?wwtp a wawo:WWTP ;
                      wawo:populationEquivalent ?popEq .
                FILTER(?popEq >= 10000)
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find WWTPs with PE >= 10000")

        for row in results:
            self.assertGreaterEqual(float(row.popEq), 10000,
                                   "All returned WWTPs should have PE >= 10000")

        print(f"✓ Test 8 (CQ2.2): Found {len(results)} WWTPs requiring secondary treatment")

    def test_09_cq2_non_compliant_wwtps(self):
        """CQ2.3: Which WWTPs are non-compliant?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?wwtp ?popEq
            WHERE {
                ?wwtp a wawo:WWTP ;
                      wawo:populationEquivalent ?popEq .
                FILTER(?popEq >= 10000)
                FILTER NOT EXISTS {
                    ?wwtp wawo:performs ?treatment .
                    ?treatment a wawo:SecondaryTreatment .
                }
            }
        """
        results = list(self.g.query(query))
        # We expect at least one non-compliant WWTP from our test data
        self.assertGreater(len(results), 0, "Should find non-compliant WWTPs")
        print(f"✓ Test 9 (CQ2.3): Found {len(results)} non-compliant WWTPs")

    def test_10_cq2_discharged_water(self):
        """CQ2.4: What water is being discharged?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?wwtp ?discharged ?bod ?cod
            WHERE {
                ?wwtp a wawo:WWTP ;
                      wawo:discharged ?discharged .
                ?discharged wawo:biologicalOxygenDemandConcentration ?bod ;
                            wawo:chemicalOxygenDemandConcentration ?cod .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find discharged water")
        print(f"✓ Test 10 (CQ2.4): Found {len(results)} discharge records")

    def test_11_cq3_water_sources(self):
        """CQ3.1: What sources are producing water?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?source ?waterMass ?sourceType
            WHERE {
                ?source a ?sourceType ;
                        wawo:produces ?waterMass .
                ?sourceType rdfs:subClassOf* wawo:WaterSource .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find water sources producing water")
        print(f"✓ Test 11 (CQ3.1): Found {len(results)} water source-production pairs")

    def test_12_cq3_flow_water_masses(self):
        """CQ3.2: Can we distinguish flow vs static water?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?flow
            WHERE {
                ?waterMass a wawo:Flow_water_mass ;
                           wawo:flow ?flow .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find flowing water masses")

        for row in results:
            self.assertGreater(float(row.flow), 0, "Flow should be positive")

        print(f"✓ Test 12 (CQ3.2): Found {len(results)} flowing water masses")

    def test_13_cq3_river_section_water(self):
        """CQ3.3: What is the water composition in river sections?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?riverSection ?waterMass ?composition
            WHERE {
                ?riverSection a wawo:RiverSection ;
                              wawo:hasWaterMass ?waterMass .
                OPTIONAL {
                    ?waterMass wawo:hasWaterComposition ?composition .
                }
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find river sections with water")
        print(f"✓ Test 13 (CQ3.3): Found {len(results)} river sections")

    def test_14_cq4_heavy_metals(self):
        """CQ4.1: Which water masses contain heavy metals?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?concentration
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:heavyMetalConcentration ?concentration .
                FILTER(?concentration > 0.0)
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find water with heavy metals")
        print(f"✓ Test 14 (CQ4.1): Found {len(results)} water masses with heavy metals")

    def test_15_cq4_mercury_limits(self):
        """CQ4.2: Are there mercury levels exceeding limits?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?mercury
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:heavyMetalConcentration ?mercury .
                FILTER(?mercury >= 0.005)
            }
        """
        results = list(self.g.query(query))
        # We have one sample with 0.006 and one with 0.008 mg/L
        self.assertGreater(len(results), 0, "Should find water exceeding mercury limits")
        print(f"✓ Test 15 (CQ4.2): Found {len(results)} samples exceeding mercury limits")

    def test_16_cq4_emerging_contaminants(self):
        """CQ4.3: Which water masses contain emerging contaminants?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?waterMass ?concentration
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:emergingPollutantConcentration ?concentration .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find emerging contaminants")
        print(f"✓ Test 16 (CQ4.3): Found {len(results)} water masses with emerging contaminants")

    def test_17_cq5_heavy_rain(self):
        """CQ5.1: Can we identify heavy rain events?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?event ?amount ?duration
            WHERE {
                ?event a wawo:Rainfall ;
                       wawo:precipitationAmount ?amount ;
                       wawo:duration ?duration .
                FILTER(?amount >= 200)
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find heavy rain events")
        print(f"✓ Test 17 (CQ5.1): Found {len(results)} heavy rain events")

    def test_18_cq5_precipitation_timestamps(self):
        """CQ5.3: Can we query temporal information?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?event ?startTime ?endTime ?amount
            WHERE {
                ?event a wawo:Rainfall ;
                       wawo:hasTimestampStart ?startTime ;
                       wawo:hasTimestampEnd ?endTime ;
                       wawo:precipitationAmount ?amount .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find precipitation with timestamps")
        print(f"✓ Test 18 (CQ5.3): Found {len(results)} precipitation events with timestamps")

    def test_19_cq6_conveyor_connections(self):
        """CQ6.1: Can we trace infrastructure connections?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?unit1 ?unit2
            WHERE {
                ?unit1 wawo:connectedTo ?unit2 .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find connected conveyor units")
        print(f"✓ Test 19 (CQ6.1): Found {len(results)} infrastructure connections")

    def test_20_cq6_facility_processes(self):
        """CQ6.2: What processes are performed at facilities?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?facility ?process
            WHERE {
                ?facility wawo:performs ?process .
                FILTER EXISTS {
                    { ?facility a wawo:WWTP } UNION
                    { ?facility a wawo:WaterTreatmentFacility }
                }
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find facility processes")
        print(f"✓ Test 20 (CQ6.2): Found {len(results)} facility-process pairs")

    def test_21_cq7_basin_management(self):
        """CQ7.2: Which authorities oversee river basins?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?authority ?basin
            WHERE {
                ?authority a wawo:RiverBasinAuthority ;
                           wawo:manages ?basin .
                ?basin a wawo:RiverBasin .
            }
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find river basin authorities")
        print(f"✓ Test 21 (CQ7.2): Found {len(results)} authority-basin pairs")

    def test_22_cq8_population_equivalent(self):
        """CQ8.2: What is the population equivalent of producers?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT ?producer ?popEq
            WHERE {
                ?producer wawo:populationEquivalent ?popEq .
                FILTER EXISTS {
                    { ?producer a wawo:Household } UNION
                    { ?producer a wawo:Industry } UNION
                    { ?producer a wawo:Commerce } UNION
                    { ?producer a wawo:WastewaterProducer }
                }
            }
            ORDER BY DESC(?popEq)
        """
        results = list(self.g.query(query))
        self.assertGreater(len(results), 0, "Should find wastewater producers with PE")

        total_pe = sum(float(row.popEq) for row in results)
        print(f"✓ Test 22 (CQ8.2): Found {len(results)} producers with total PE = {total_pe}")

    def test_23_cq10_water_quality_stats(self):
        """CQ10.1: Can we compute aggregate statistics?"""
        query = """
            PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

            SELECT
                (AVG(?bod) as ?avgBOD) (MAX(?bod) as ?maxBOD) (MIN(?bod) as ?minBOD)
                (AVG(?cod) as ?avgCOD) (MAX(?cod) as ?maxCOD) (MIN(?cod) as ?minCOD)
            WHERE {
                ?waterMass a wawo:WaterMass ;
                           wawo:biologicalOxygenDemandConcentration ?bod ;
                           wawo:chemicalOxygenDemandConcentration ?cod .
            }
        """
        results = list(self.g.query(query))
        self.assertEqual(len(results), 1, "Should get one row of statistics")

        row = results[0]
        self.assertIsNotNone(row.avgBOD, "Should compute average BOD")
        self.assertIsNotNone(row.maxBOD, "Should compute max BOD")

        print(f"✓ Test 23 (CQ10.1): Computed aggregate statistics")
        print(f"  Avg BOD: {float(row.avgBOD):.2f}, Max: {float(row.maxBOD):.2f}")

    def test_24_object_properties(self):
        """Test that object properties are defined"""
        key_properties = [
            self.wawo.hasWaterMass,
            self.wawo.hasWaterComposition,
            self.wawo.hasIndicator,
            self.wawo.received,
            self.wawo.discharged,
            self.wawo.performs,
            self.wawo.produces
        ]

        for prop in key_properties:
            self.assertIn((prop, RDF.type, OWL.ObjectProperty), self.g,
                         f"Property {prop} should be defined as ObjectProperty")

        print("✓ Test 24: Object properties validated")

    def test_25_data_properties(self):
        """Test that data properties are defined"""
        key_properties = [
            self.wawo.biologicalOxygenDemandConcentration,
            self.wawo.chemicalOxygenDemandConcentration,
            self.wawo.suspendedSolidConcentration,
            self.wawo.totalNitrogenConcentration,
            self.wawo.totalPhosphorusConcentration,
            self.wawo.flow,
            self.wawo.populationEquivalent
        ]

        for prop in key_properties:
            self.assertIn((prop, RDF.type, OWL.DatatypeProperty), self.g,
                         f"Property {prop} should be defined as DatatypeProperty")

        print("✓ Test 25: Data properties validated")


def run_tests():
    """Run all tests and print summary"""
    print("\n" + "="*80)
    print("WaWO+ ONTOLOGY TEST SUITE")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWaWOPlus)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe WaWO+ ontology successfully:")
        print("  • Loads and parses correctly")
        print("  • Defines all required classes and properties")
        print("  • Supports SPARQL queries for water quality classification")
        print("  • Tracks WWTP compliance with regulations")
        print("  • Monitors water flow through the system")
        print("  • Detects contaminants and heavy metals")
        print("  • Identifies meteorological events")
        print("  • Maps infrastructure connections")
        print("  • Manages stakeholder responsibilities")
        print("  • Computes aggregate statistics")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease review the failures above and check:")
        print("  • Ontology syntax and structure")
        print("  • Test data completeness")
        print("  • SPARQL query correctness")

    print("="*80 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
