"""Infiltration physics: plug-flow first-order + simplified Richards ODE."""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict

INFIL_DEFAULT_PARAMS = {
    "k_COD":     1.5,   # 1/d
    "k_TSS":     3.0,   # 1/d
    "k_NH4":     0.8,   # 1/d
    "K_sat":     0.5,   # m/d
    "theta_eff": 0.3,   # -
    "theta_sat": 0.45,  # -
    "theta_res": 0.05,  # -
    "n_vg":      2.0,   # van Genuchten n
}

INFIL_PARAM_BOUNDS = {
    "k_COD": (0.01, 10.0),
    "k_TSS": (0.01, 20.0),
    "k_NH4": (0.01, 5.0),
}


def _hydraulic_conductivity(theta: float, params: Dict) -> float:
    """van Genuchten relative hydraulic conductivity."""
    K_sat     = params.get("K_sat",     INFIL_DEFAULT_PARAMS["K_sat"])
    theta_sat = params.get("theta_sat", INFIL_DEFAULT_PARAMS["theta_sat"])
    theta_res = params.get("theta_res", INFIL_DEFAULT_PARAMS["theta_res"])
    n_vg      = params.get("n_vg",      INFIL_DEFAULT_PARAMS["n_vg"])
    Se = max(0.0, min(1.0, (theta - theta_res) / (theta_sat - theta_res)))
    return K_sat * Se ** (2 + 3 / n_vg)


def infiltration_simulate_steady(inputs: Dict, params: Dict) -> Dict:
    """Steady-state infiltration: plug-flow first-order removal."""
    Q_in      = inputs.get("influent_flow_m3d", 0.3)
    C_cod_in  = inputs.get("influent_cod_mg_l", 200.0)
    C_tss_in  = inputs.get("influent_tss_mg_l", 50.0)
    C_nh4_in  = inputs.get("influent_nh4_mg_l", 40.0)
    area_m2   = inputs.get("area_m2", 10.0)
    soil_depth = inputs.get("soil_depth_m", 1.0)

    k_COD     = params.get("k_COD",     INFIL_DEFAULT_PARAMS["k_COD"])
    k_TSS     = params.get("k_TSS",     INFIL_DEFAULT_PARAMS["k_TSS"])
    k_NH4     = params.get("k_NH4",     INFIL_DEFAULT_PARAMS["k_NH4"])
    K_sat     = params.get("K_sat",     INFIL_DEFAULT_PARAMS["K_sat"])
    theta_eff = params.get("theta_eff", INFIL_DEFAULT_PARAMS["theta_eff"])

    q_inf = min(Q_in / area_m2, K_sat)
    HRT   = theta_eff * soil_depth / q_inf if q_inf > 0 else 99.0

    C_cod_out = C_cod_in * np.exp(-k_COD * HRT)
    C_tss_out = C_tss_in * np.exp(-k_TSS * HRT)
    C_nh4_out = C_nh4_in * np.exp(-k_NH4 * HRT)

    rem_cod = 1 - C_cod_out / C_cod_in if C_cod_in > 0 else 0.0
    rem_tss = 1 - C_tss_out / C_tss_in if C_tss_in > 0 else 0.0
    rem_nh4 = 1 - C_nh4_out / C_nh4_in if C_nh4_in > 0 else 0.0

    return {
        "infiltrated_flow_m3d": round(Q_in, 4),
        "removed_cod_fraction": round(rem_cod, 4),
        "removed_tss_fraction": round(rem_tss, 4),
        "removed_nh4_fraction": round(rem_nh4, 4),
        "effluent_cod_mg_l":    round(C_cod_out, 3),
        "effluent_tss_mg_l":    round(C_tss_out, 3),
        "effluent_nh4_mg_l":    round(C_nh4_out, 3),
        "hrt_days":             round(HRT, 4),
    }


def infiltration_simulate_dynamic(inputs: Dict, params: Dict) -> Dict:
    """Dynamic infiltration: simplified Richards + advective transport."""
    Q_in      = inputs.get("influent_flow_m3d", 0.3)
    C_cod_in  = inputs.get("influent_cod_mg_l", 200.0)
    C_tss_in  = inputs.get("influent_tss_mg_l", 50.0)
    C_nh4_in  = inputs.get("influent_nh4_mg_l", 40.0)
    area_m2   = inputs.get("area_m2", 10.0)
    soil_depth = inputs.get("soil_depth_m", 1.0)
    t_start   = inputs.get("t_start", 0.0)
    t_end     = inputs.get("t_end", 10.0)
    n_points  = int(inputs.get("n_points", 100))

    k_COD     = params.get("k_COD",     INFIL_DEFAULT_PARAMS["k_COD"])
    k_TSS     = params.get("k_TSS",     INFIL_DEFAULT_PARAMS["k_TSS"])
    k_NH4     = params.get("k_NH4",     INFIL_DEFAULT_PARAMS["k_NH4"])
    theta_sat = params.get("theta_sat", INFIL_DEFAULT_PARAMS["theta_sat"])
    theta_res = params.get("theta_res", INFIL_DEFAULT_PARAMS["theta_res"])

    q = Q_in / area_m2
    L = soil_depth

    def rhs(t, y):
        theta, C_cod, C_tss, C_nh4 = y
        theta = max(theta_res + 1e-4, min(theta_sat - 1e-4, theta))
        K     = _hydraulic_conductivity(theta, params)
        dtheta = (q - K) / L
        dCcod  = (q/L) * (C_cod_in - C_cod) - k_COD * C_cod
        dCtss  = (q/L) * (C_tss_in - C_tss) - k_TSS * C_tss
        dCnh4  = (q/L) * (C_nh4_in - C_nh4) - k_NH4 * C_nh4
        return [dtheta, dCcod, dCtss, dCnh4]

    theta0 = (theta_sat + theta_res) / 2
    y0     = [theta0, C_cod_in * 0.8, C_tss_in * 0.5, C_nh4_in * 0.7]
    t_eval = np.linspace(t_start, t_end, n_points)
    sol    = solve_ivp(rhs, [t_start, t_end], y0, t_eval=t_eval, rtol=1e-6, atol=1e-8)

    return {
        "time_days":         sol.t.tolist(),
        "soil_moisture":     sol.y[0].tolist(),
        "effluent_cod_mg_l": [max(0.0, v) for v in sol.y[1].tolist()],
        "effluent_tss_mg_l": [max(0.0, v) for v in sol.y[2].tolist()],
        "effluent_nh4_mg_l": [max(0.0, v) for v in sol.y[3].tolist()],
    }
