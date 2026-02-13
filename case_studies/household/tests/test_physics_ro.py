"""Tests for RO physics engine."""
import sys
sys.path.insert(0, "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/household/src")

import pytest
from household_water.physics.ro_equations import (
    RO_DEFAULT_PARAMS, ro_simulate_steady, ro_simulate_dynamic, osmotic_pressure_pa
)


def test_osmotic_pressure_positive():
    params = dict(RO_DEFAULT_PARAMS)
    pi = osmotic_pressure_pa(100.0, params)
    assert pi > 0


def test_ro_steady_output_keys():
    params = dict(RO_DEFAULT_PARAMS)
    out = ro_simulate_steady({}, params)
    for key in ["permeate_flow_m3d", "permeate_tds_mg_l", "recovery_fraction", "water_flux_m_s"]:
        assert key in out


def test_ro_rejection():
    params = dict(RO_DEFAULT_PARAMS)
    out = ro_simulate_steady({"feed_tds_mg_l": 100.0}, params)
    assert out["permeate_tds_mg_l"] < 100.0


def test_ro_higher_pressure_higher_flux():
    params = dict(RO_DEFAULT_PARAMS)
    out_low  = ro_simulate_steady({"applied_pressure_bar": 5.0}, params)
    out_high = ro_simulate_steady({"applied_pressure_bar": 12.0}, params)
    assert out_high["water_flux_m_s"] > out_low["water_flux_m_s"]


def test_ro_dynamic_length():
    params = dict(RO_DEFAULT_PARAMS)
    inputs = {"t_end": 1.0, "n_points": 50}
    out = ro_simulate_dynamic(inputs, params)
    assert len(out["time_days"]) == 50
