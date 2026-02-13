"""Tests for infiltration physics engine."""
import sys
sys.path.insert(0, "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/household/src")

import pytest
from household_water.physics.infiltration_equations import (
    INFIL_DEFAULT_PARAMS, infiltration_simulate_steady, infiltration_simulate_dynamic
)


def test_steady_removal_positive():
    params = dict(INFIL_DEFAULT_PARAMS)
    out = infiltration_simulate_steady({}, params)
    assert out["removed_cod_fraction"] > 0
    # At default (long HRT), both fractions saturate near 1.0; TSS >= COD
    assert out["removed_tss_fraction"] >= out["removed_cod_fraction"]


def test_tss_removal_higher_than_cod_at_short_hrt():
    """At short HRT, higher k_TSS yields strictly more removal than COD."""
    params = dict(INFIL_DEFAULT_PARAMS)
    # High flow → short HRT so fractions don't both saturate at 1.0
    inputs = {"influent_flow_m3d": 4.0, "area_m2": 10.0, "soil_depth_m": 1.0}
    out = infiltration_simulate_steady(inputs, params)
    assert out["removed_tss_fraction"] > out["removed_cod_fraction"]


def test_steady_effluent_less_than_influent():
    params = dict(INFIL_DEFAULT_PARAMS)
    inputs = {"influent_cod_mg_l": 200, "influent_tss_mg_l": 50, "influent_nh4_mg_l": 40}
    out = infiltration_simulate_steady(inputs, params)
    assert out["effluent_cod_mg_l"] < 200
    assert out["effluent_tss_mg_l"] < 50
    assert out["effluent_nh4_mg_l"] < 40


def test_hrt_decreases_with_higher_flow():
    params = dict(INFIL_DEFAULT_PARAMS)
    out_low  = infiltration_simulate_steady({"influent_flow_m3d": 0.1}, params)
    out_high = infiltration_simulate_steady({"influent_flow_m3d": 3.0}, params)
    assert out_low["hrt_days"] > out_high["hrt_days"]


def test_dynamic_length():
    params = dict(INFIL_DEFAULT_PARAMS)
    inputs = {"t_end": 10, "n_points": 100}
    out = infiltration_simulate_dynamic(inputs, params)
    assert len(out["time_days"]) == 100
    assert len(out["effluent_cod_mg_l"]) == 100


def test_dynamic_cod_decreases():
    params = dict(INFIL_DEFAULT_PARAMS)
    inputs = {"influent_cod_mg_l": 200, "t_end": 20, "n_points": 100}
    out = infiltration_simulate_dynamic(inputs, params)
    assert out["effluent_cod_mg_l"][-1] < out["effluent_cod_mg_l"][0]
