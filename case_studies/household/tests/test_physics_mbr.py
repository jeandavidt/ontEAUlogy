"""Tests for MBR physics engine."""
import sys
sys.path.insert(0, "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/household/src")

import pytest
from household_water.physics.mbr_odes import (
    MBR_DEFAULT_PARAMS, mbr_steady_state, mbr_membrane_flux,
    mbr_simulate_steady, mbr_simulate_dynamic
)


def test_steady_state_returns_positive():
    params = dict(MBR_DEFAULT_PARAMS)
    Q_in, S_in, V = 1.5, 350.0, 10.0
    Q_waste = Q_in * params["Q_waste_frac"]
    ss = mbr_steady_state(params, Q_in, S_in, V, Q_waste)
    assert ss["S_star"] >= 0
    assert ss["X_star"] >= 0
    assert ss["So_star"] >= 0


def test_effluent_cod_varies_with_flow():
    """Physics model: effluent COD must change with flow (not fixed fraction)."""
    params = dict(MBR_DEFAULT_PARAMS)
    out_low  = mbr_simulate_steady({"influent_flow_m3d": 1.0, "influent_cod_mg_l": 350}, params)
    out_high = mbr_simulate_steady({"influent_flow_m3d": 3.0, "influent_cod_mg_l": 350}, params)
    assert out_low["effluent_cod_mg_l"] != out_high["effluent_cod_mg_l"]


def test_mbr_simulate_steady_keys():
    params = dict(MBR_DEFAULT_PARAMS)
    out = mbr_simulate_steady({"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350}, params)
    for key in ["effluent_cod_mg_l", "biomass_x_mg_l", "dissolved_o2_mg_l", "sludge_kg_d"]:
        assert key in out


def test_mbr_simulate_dynamic_length():
    params = dict(MBR_DEFAULT_PARAMS)
    inputs = {"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350, "t_end": 5, "n_points": 50}
    out = mbr_simulate_dynamic(inputs, params)
    assert len(out["time_days"]) == 50
    assert len(out["substrate_s_mg_l"]) == 50


def test_mbr_dynamic_approaches_steady():
    """After long simulation, dynamic should approach steady-state."""
    params = dict(MBR_DEFAULT_PARAMS)
    inputs_dyn = {"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350, "t_end": 50, "n_points": 200}
    dyn    = mbr_simulate_dynamic(inputs_dyn, params)
    steady = mbr_simulate_steady({"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350}, params)
    final_S = dyn["substrate_s_mg_l"][-1]
    ss_S    = steady["effluent_cod_mg_l"]
    assert abs(final_S - ss_S) / (ss_S + 1e-6) < 0.15, \
        f"Dynamic ({final_S:.2f}) not close to steady-state ({ss_S:.2f})"


def test_membrane_flux_positive():
    params = dict(MBR_DEFAULT_PARAMS)
    flux = mbr_membrane_flux(params)
    assert flux["Jw_m_s"] > 0
    assert flux["Q_permeate_m3_d"] > 0
