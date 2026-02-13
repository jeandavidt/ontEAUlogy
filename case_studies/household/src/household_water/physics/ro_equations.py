"""RO physics: solution-diffusion model with concentration polarisation."""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict

RO_DEFAULT_PARAMS = {
    "A":        3.5e-7,  # m/s/Pa — water permeability
    "B":        8e-8,    # m/s — salt permeability
    "k_m":      1e-5,    # m/s — mass transfer coefficient
    "R":        8.314,   # J/mol/K
    "T":        298.15,  # K
    "M_s":      0.058,   # kg/mol — molar mass NaCl
    "rho_water": 997.0,  # kg/m³
}

RO_PARAM_BOUNDS = {
    "A": (1e-9, 1e-5),
    "B": (1e-10, 1e-4),
}

BAR_TO_PA = 1e5


def osmotic_pressure_pa(C_mg_l: float, params: Dict) -> float:
    """Van't Hoff osmotic pressure (Pa). 2-ion NaCl equivalent."""
    R   = params.get("R",   RO_DEFAULT_PARAMS["R"])
    T   = params.get("T",   RO_DEFAULT_PARAMS["T"])
    M_s = params.get("M_s", RO_DEFAULT_PARAMS["M_s"])
    C_mol_m3 = (C_mg_l * 1e-3) / M_s
    return 2 * C_mol_m3 * R * T


def ro_simulate_steady(inputs: Dict, params: Dict) -> Dict:
    """Steady-state RO with iterative concentration polarisation."""
    A   = params.get("A",   RO_DEFAULT_PARAMS["A"])
    B   = params.get("B",   RO_DEFAULT_PARAMS["B"])
    k_m = params.get("k_m", RO_DEFAULT_PARAMS["k_m"])

    TMP_Pa    = inputs.get("applied_pressure_bar", 8.0) * BAR_TO_PA
    C_feed    = inputs.get("feed_tds_mg_l", 100.0)
    Q_feed    = inputs.get("feed_flow_m3d", 0.8)
    A_m       = inputs.get("membrane_area_m2", 2.0)
    cond_feed = inputs.get("feed_conductivity_us_cm", 200.0)

    Jw  = A * TMP_Pa
    C_p = 0.0

    for _ in range(50):
        ratio     = min(Jw / k_m, 500.0)
        C_m       = C_feed * np.exp(ratio)
        delta_pi  = osmotic_pressure_pa(C_m, params) - osmotic_pressure_pa(C_p, params)
        Jw_new    = A * max(0.0, TMP_Pa - delta_pi)
        Js        = B * (C_m - C_p)
        C_p_new   = Js / Jw_new if Jw_new > 1e-12 else C_feed
        if abs(Jw_new - Jw) < 1e-12 and abs(C_p_new - C_p) < 1e-3:
            break
        Jw, C_p = Jw_new, C_p_new

    Q_permeate    = Jw * A_m * 86400
    Q_concentrate = max(0.0, Q_feed - Q_permeate)
    recovery      = min(Q_permeate / Q_feed, 1.0) if Q_feed > 0 else 0.0
    cond_reject   = 1 - (C_p / C_feed) if C_feed > 0 else 0.99
    cond_permeate = cond_feed * (1 - cond_reject)
    energy_kwh_d  = Q_permeate * 0.3

    return {
        "permeate_flow_m3d":           round(Q_permeate, 4),
        "concentrate_flow_m3d":        round(Q_concentrate, 4),
        "permeate_tds_mg_l":           round(C_p, 4),
        "permeate_conductivity_us_cm": round(cond_permeate, 2),
        "recovery_fraction":           round(recovery, 4),
        "energy_kwh_d":               round(energy_kwh_d, 4),
        "water_flux_m_s":             Jw,
        "osmotic_pressure_pa":        osmotic_pressure_pa(C_feed, params),
    }


def ro_simulate_dynamic(inputs: Dict, params: Dict) -> Dict:
    """Dynamic RO simulation — CP build-up over time."""
    C_feed = inputs.get("feed_tds_mg_l", 100.0)
    TMP_Pa = inputs.get("applied_pressure_bar", 8.0) * BAR_TO_PA
    A      = params.get("A",   RO_DEFAULT_PARAMS["A"])
    B      = params.get("B",   RO_DEFAULT_PARAMS["B"])
    k_m    = params.get("k_m", RO_DEFAULT_PARAMS["k_m"])
    t_start  = inputs.get("t_start", 0.0)
    t_end    = inputs.get("t_end", 1.0)
    n_points = int(inputs.get("n_points", 50))

    def rhs(t, y):
        C_p   = max(y[0], 0.0)
        Jw    = A * TMP_Pa
        ratio = min(Jw / k_m, 500.0)  # clip to avoid overflow
        C_m   = C_feed * np.exp(ratio)
        Js    = B * (C_m - C_p) if np.isfinite(C_m) else 0.0
        dCp   = (Js - Jw * C_p) / 0.1
        return [dCp]

    t_eval = np.linspace(t_start, t_end, n_points)
    sol    = solve_ivp(rhs, [t_start, t_end], [0.0], t_eval=t_eval, rtol=1e-6, atol=1e-8)
    Jw_ss  = A * TMP_Pa

    t_list  = sol.t.tolist() if hasattr(sol.t, "tolist") else list(sol.t)
    cp_list = sol.y[0].tolist() if hasattr(sol.y[0], "tolist") else list(sol.y[0])

    return {
        "time_days":         t_list,
        "permeate_tds_mg_l": [max(0.0, v) for v in cp_list],
        "water_flux_m_s":    [Jw_ss] * len(t_list),
    }
