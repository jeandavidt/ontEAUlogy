"""Tests for composition strategies (cascade, assembly, lumped)."""

import pytest
from household_water.schemas.common import (
    CompositionRequest,
    CompositionStrategy,
    SimulationMode,
)
from household_water.composition.lumped import lumped_simulate, _identify_unit_type


class TestLumpedComposition:
    """Tests for the lumped (algebraic) composition strategy."""

    def test_lumped_single_step_mbr(self):
        """Lumped composition with single MBR step applies correct removals."""
        request = CompositionRequest(
            unit_iri="https://example.com/test-train",
            sub_unit_iris=[
                "https://w3id.org/waterframe/case/household/Membrane_bioreactor"
            ],
            sub_unit_endpoints=["http://localhost:8101"],
            inputs={
                "influent_flow_m3d": 1.5,
                "influent_cod_mg_l": 350.0,
                "influent_tss_mg_l": 150.0,
            },
            simulation_mode=SimulationMode.steady_state,
            composition_strategy=CompositionStrategy.lumped,
        )

        result = lumped_simulate(request)

        assert result["composition_strategy"] == "lumped"
        assert result["n_steps"] == 1
        assert "final_outputs" in result
        assert "intermediate_outputs" in result

        # Check COD removal applied (default 95% for MBR)
        final = result["final_outputs"]
        assert final["effluent_cod_mg_l"] == pytest.approx(17.5, rel=0.1)  # 350 * 0.05

        # Check TSS removal applied (default 99% for MBR)
        assert final["effluent_tss_mg_l"] == pytest.approx(1.5, rel=0.1)  # 150 * 0.01

    def test_lumped_two_step_mbr_ro(self):
        """Lumped composition with MBR → RO chain."""
        request = CompositionRequest(
            unit_iri="https://example.com/test-train",
            sub_unit_iris=[
                "https://w3id.org/waterframe/case/household/Membrane_bioreactor",
                "https://w3id.org/waterframe/case/household/Reverse_osmosis",
            ],
            sub_unit_endpoints=["http://localhost:8101", "http://localhost:8102"],
            inputs={
                "influent_flow_m3d": 1.5,
                "influent_cod_mg_l": 350.0,
                "feed_tds_mg_l": 100.0,
            },
            simulation_mode=SimulationMode.steady_state,
            composition_strategy=CompositionStrategy.lumped,
        )

        result = lumped_simulate(request)

        assert result["composition_strategy"] == "lumped"
        assert result["n_steps"] == 2
        assert len(result["intermediate_outputs"]) == 2

        # Check removal summary recorded
        assert "removal_summary" in result
        assert "step_0" in result["removal_summary"]
        assert "step_1" in result["removal_summary"]

    def test_lumped_empty_sub_units(self):
        """Lumped composition with no sub-units returns inputs unchanged."""
        request = CompositionRequest(
            unit_iri="https://example.com/test-train",
            sub_unit_iris=[],
            sub_unit_endpoints=[],
            inputs={"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350.0},
            simulation_mode=SimulationMode.steady_state,
            composition_strategy=CompositionStrategy.lumped,
        )

        result = lumped_simulate(request)

        assert result["n_steps"] == 0
        assert result["final_outputs"] == request.inputs

    def test_identify_unit_type_mbr(self):
        """Unit type identification works for MBR."""
        iri = "https://w3id.org/waterframe/case/household/Membrane_bioreactor"
        assert _identify_unit_type(iri) == "Membrane_bioreactor"

    def test_identify_unit_type_ro(self):
        """Unit type identification works for RO."""
        iri = "https://w3id.org/waterframe/case/household/Reverse_osmosis"
        assert _identify_unit_type(iri) == "Reverse_osmosis"

    def test_identify_unit_type_unknown(self):
        """Unknown unit types return empty string."""
        iri = "https://example.com/unknown_unit"
        assert _identify_unit_type(iri) == ""


class TestCascadeComposition:
    """Tests for the cascade (HTTP) composition strategy.

    These tests verify the cascade_simulate function signature and
    basic validation. Full integration tests require running services.
    """

    def test_cascade_mismatched_lengths_raises(self):
        """Cascade raises error if iris and endpoints lengths mismatch."""
        import asyncio

        request = CompositionRequest(
            unit_iri="https://example.com/test-train",
            sub_unit_iris=["unit1", "unit2"],
            sub_unit_endpoints=["http://localhost:8101"],  # Only one endpoint
            inputs={"influent_flow_m3d": 1.5},
            simulation_mode=SimulationMode.steady_state,
            composition_strategy=CompositionStrategy.cascade,
        )

        from household_water.composition.cascade import cascade_simulate

        with pytest.raises(ValueError, match="must have same length"):
            asyncio.run(cascade_simulate(request))


class TestAssemblyComposition:
    """Tests for the assembly (coupled ODE) composition strategy."""

    def test_assemble_not_implemented(self):
        """Assembly strategy raises NotImplementedError."""
        request = CompositionRequest(
            unit_iri="https://example.com/test-train",
            sub_unit_iris=["unit1"],
            sub_unit_endpoints=["http://localhost:8101"],
            inputs={"influent_flow_m3d": 1.5},
            simulation_mode=SimulationMode.steady_state,
            composition_strategy=CompositionStrategy.assembly,
        )

        from household_water.composition.assembly import assemble_and_solve

        with pytest.raises(NotImplementedError):
            assemble_and_solve(request)
