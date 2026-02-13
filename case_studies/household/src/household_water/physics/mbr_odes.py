"""MBR physics: Monod-CSTR ODE system, analytical steady-state, membrane flux."""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, List

MBR_DEFAULT_PARAMS = {
    "mu_max": 6.0,        # 1/d — max specific growth rate
    "K_s":    20.0,       # mg COD/L — half-saturation
    "Y":      0.67,       # g VSS/g COD — yield
    "b":      0.15,       # 1/d — decay rate
    "K_La":   240.0,      # 1/d — oxygen transfer rate
    "So_sat": 8.0,        # mg/L — DO saturation
    "V":      10.0,       # m³ — reactor volume
    "A_m":    50.0,       # m² — membrane area
    "TMP_Pa": 50000.0,    # Pa — transmembrane pressure
    "mu_water": 1e-3,     # Pa·s — water viscosity
    "R_m":    1e11,       # 1/m — membrane resistance
    "Q_waste_frac": 0.05, # fraction of Q_in wasted as sludge
}

MBR_PARAM_BOUNDS = {
    "mu_max": (0.1, 20.0),
    "K_s":    (1.0, 200.0),
    "Y":      (0.3, 0.8),
    "b":      (0.01, 1.0),
}


def mbr_ode_rhs(t: float, y: List[float], params: Dict, Q_in: float, S_in: float, V: float, Q_waste: float) -> List[float]:
    """RHS of MBR ODE system. State: [S (mg COD/L), X (mg VSS/L), So (mg DO/L)]."""
    S, X, So = max(y[0], 0.0), max(y[1], 0.0), max(y[2], 0.0)
    mu_max = params["mu_max"]
    K_s    = params["K_s"]
    Y      = params["Y"]
    b      = params["b"]
    K_La   = params["K_La"]
    So_sat = params["So_sat"]

    mu = mu_max * S / (K_s + S)

    dS  = Q_in/V * (S_in - S) - mu * X / Y
    dX  = mu * X - b * X - Q_waste/V * X
    dSo = K_La * (So_sat - So) - mu * X * (1 - Y) / Y * 1.07

    return [dS, dX, dSo]


def mbr_steady_state(params: Dict, Q_in: float, S_in: float, V: float, Q_waste: float) -> Dict:
    """Analytical steady-state solution for MBR."""
    mu_max = params["mu_max"]
    K_s    = params["K_s"]
    Y      = params["Y"]
    b      = params["b"]
    K_La   = params["K_La"]
    So_sat = params["So_sat"]

    mu_ss = b + Q_waste / V
    if mu_max <= mu_ss:
        return {"S_star": S_in, "X_star": 0.0, "So_star": So_sat}

    S_star = K_s * mu_ss / (mu_max - mu_ss)
    S_star = max(0.0, min(S_star, S_in))
    D = Q_in / V
    X_star = Y * D * (S_in - S_star) / mu_ss
    X_star = max(0.0, X_star)
    So_star = So_sat - mu_ss * X_star * (1 - Y) / Y * 1.07 / K_La
    So_star = max(0.0, So_star)

    return {"S_star": S_star, "X_star": X_star, "So_star": So_star}


def mbr_membrane_flux(params: Dict) -> Dict:
    """Darcy membrane flux calculation."""
    TMP_Pa = params["TMP_Pa"]
    mu_w   = params["mu_water"]
    R_m    = params["R_m"]
    A_m    = params["A_m"]

    Jw = TMP_Pa / (mu_w * R_m)
    Q_permeate = Jw * A_m * 86400

    return {"Jw_m_s": Jw, "Q_permeate_m3_d": Q_permeate}


def mbr_simulate_steady(inputs: Dict, params: Dict) -> Dict:
    """Full steady-state MBR simulation."""
    Q_in   = inputs.get("influent_flow_m3d", 1.5)
    S_in   = inputs.get("influent_cod_mg_l", 350.0)
    nh4_in = inputs.get("influent_nh4_mg_l", 50.0)
    tp_in  = inputs.get("influent_tp_mg_l", 8.0)

    V            = params.get("V", MBR_DEFAULT_PARAMS["V"])
    Q_waste_frac = params.get("Q_waste_frac", MBR_DEFAULT_PARAMS["Q_waste_frac"])
    Q_waste      = Q_in * Q_waste_frac

    ss   = mbr_steady_state(params, Q_in, S_in, V, Q_waste)
    S_star  = ss["S_star"]
    X_star  = ss["X_star"]
    So_star = ss["So_star"]

    cod_eff = S_star
    tss_eff = 0.1  # membrane retains all VSS
    nh4_removal = min(0.95, (S_in - S_star) / S_in * 0.9) if S_in > 0 else 0.85
    nh4_eff = nh4_in * (1 - nh4_removal)
    tp_eff  = tp_in * 0.4

    Y_param     = params.get("Y", MBR_DEFAULT_PARAMS["Y"])
    energy_kwh_d = Q_in * 0.4 + (X_star * V * 1e-6) * 0.1
    sludge_kg_d  = Y_param * (S_in - S_star) * Q_in * 1e-3
    recovery     = 0.95

    return {
        "effluent_flow_m3d":  round(Q_in * recovery, 4),
        "effluent_cod_mg_l":  round(cod_eff, 3),
        "effluent_tss_mg_l":  round(tss_eff, 3),
        "effluent_nh4_mg_l":  round(nh4_eff, 3),
        "effluent_tp_mg_l":   round(tp_eff, 3),
        "energy_kwh_d":       round(energy_kwh_d, 4),
        "sludge_kg_d":        round(sludge_kg_d, 4),
        "recovery_fraction":  recovery,
        "biomass_x_mg_l":     round(X_star, 3),
        "dissolved_o2_mg_l":  round(So_star, 3),
    }


def mbr_simulate_dynamic(inputs: Dict, params: Dict) -> Dict:
    """Dynamic MBR ODE simulation using solve_ivp."""
    Q_in         = inputs.get("influent_flow_m3d", 1.5)
    S_in         = inputs.get("influent_cod_mg_l", 350.0)
    V            = params.get("V", MBR_DEFAULT_PARAMS["V"])
    Q_waste_frac = params.get("Q_waste_frac", MBR_DEFAULT_PARAMS["Q_waste_frac"])
    Q_waste      = Q_in * Q_waste_frac
    t_start      = inputs.get("t_start", 0.0)
    t_end        = inputs.get("t_end", 10.0)
    n_points     = int(inputs.get("n_points", 100))

    So_sat = params.get("So_sat", MBR_DEFAULT_PARAMS["So_sat"])
    y0 = [S_in * 0.5, 500.0, So_sat * 0.5]
    t_eval = np.linspace(t_start, t_end, n_points)

    sol = solve_ivp(
        mbr_ode_rhs, [t_start, t_end], y0,
        args=(params, Q_in, S_in, V, Q_waste),
        t_eval=t_eval, method="RK45", rtol=1e-6, atol=1e-8,
    )

    return {
        "time_days":         sol.t.tolist(),
        "substrate_s_mg_l":  [max(0.0, v) for v in sol.y[0].tolist()],
        "biomass_x_mg_l":    [max(0.0, v) for v in sol.y[1].tolist()],
        "dissolved_o2_mg_l": [max(0.0, v) for v in sol.y[2].tolist()],
    }
