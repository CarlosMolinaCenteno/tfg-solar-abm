# generate_figures_cap3.py — Figuras del Capítulo 3 (Soluciones bajo racionalidad)
# TFG: Modelo de almacenamiento solar adaptativo — Carlos Molina Centeno
#
# Genera las 5 figuras del cap. 3 que originalmente vivían en el notebook
# `banco_pruebas.ipynb` (§§2.1–2.4). Es la contrapartida reproducible del
# notebook: mismo cálculo, mismas cifras (cártel f*=0,4753; Nash N=30
# f^N=0,6393; Nash N=2 f=0,5370; precio-aceptante f=0,6496;
# ρ(c_i,f_i*)=-0,9956).
#
# Figuras generadas (escritas en workspace/figures/):
#   - fig_3_6_1_cartel_pi_f.png      §3.6.1  π(f) y dπ/df del cártel
#   - fig_3_6_2_BR_diagonal.png      §3.6.2  curva BR(f_h) vs diagonal
#   - fig_3_6_2_paisaje_plano.png    §3.6.2  paisaje plano cerca del Nash
#   - fig_3_6_3_comparativa.png      §3.6.3  2x2: N=30 (arriba) y N=2 (abajo)
#   - fig_3_6_4_nash_heterogeneo.png §3.6.4  scatter f_i* vs c_i + orden
#
# Uso:  python scripts/generate_figures_cap3.py
#
# Aviso de tiempo: el cálculo del Nash BR fixed-point para N=30 con grid
# 101x101 tarda varios minutos. La constante FAST=False replica las
# rejillas del notebook (figuras tal cual están en el .md); FAST=True
# usa rejillas reducidas (figuras visualmente equivalentes, ~5x más
# rápidas).

import os
import sys
import random

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq, least_squares

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from model import SolarAgent, MarketModel, DEFAULT_PARAMS

# Consola Windows (cp1252) no codifica los caracteres de caja del log: forzar UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Parametrizaciones del cap. 3 ─────────────────────────────────────────────
PARAMS_INTERIOR = {
    'N': 30, 'DEMAND_M': 80.0, 'DEMAND_E': 120.0,
    'CAP_LOW': 2.5, 'CAP_HIGH': 2.5,
    'STOR_CAP_LOW': 10, 'STOR_CAP_HIGH': 10,
    'STORAGE_GRAN': 10,
}

# Caso N=2 con capacidad escalada para conservar la oferta agregada N·c = 75
PARAMS_INTERIOR_N2 = {
    **PARAMS_INTERIOR,
    'N': 2,
    'CAP_LOW': 37.5, 'CAP_HIGH': 37.5,
    'STOR_CAP_LOW': 150.0, 'STOR_CAP_HIGH': 150.0,
}

# Heterogeneidad en c_i ~ U[2,3] (preserva N·c̄ = 75 frente al homogéneo)
PARAMS_INTERIOR_HET = {
    'N': 30, 'DEMAND_M': 80.0, 'DEMAND_E': 120.0,
    'CAP_LOW': 3, 'CAP_HIGH': 2,
    'STOR_CAP_LOW': 10, 'STOR_CAP_HIGH': 10,
    'STORAGE_GRAN': 10,
}

FIGDIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
SEED = 0
FAST = False  # True → grids reducidos; figuras visualmente equivalentes pero ~5x más rápidas


# ─── Solvers analíticos ──────────────────────────────────────────────────────

def solve_unico_cpo(params=None):
    """CPO del cártel (§3.1): resuelve dπ/df = 0 con Brent sobre [0,1].

    Notación (régimen interior):
        M  = N·α_M·c   (producción bruta agregada de mañana, ε=1)
        E  = N·α_E·c   (producción bruta agregada de tarde,  ε=1)
        Q^M = (1-f)M,  Q^E = E + η f M
        g^p = D_p - Q^p,  P_p = c_0 + α_G g_p^{γ_G}
    """
    p = {**DEFAULT_PARAMS, **(params or {})}
    n = p['N']
    c_agg = n * (p['CAP_LOW'] + p['CAP_HIGH']) / 2.0
    M = p['ALPHA_M'] * c_agg
    E = p['ALPHA_E'] * c_agg
    eta = (p['ETA_LOW'] + p['ETA_HIGH']) / 2.0
    D_M, D_E = p['DEMAND_M'], p['DEMAND_E']
    c0, ag, gg = p['C0'], p['ALPHA_G'], p['GAMMA_G']
    s_agg = n * (p['STOR_CAP_LOW'] + p['STOR_CAP_HIGH']) / 2.0
    f_sat = s_agg / (eta * M) if eta * M > 0 else float('inf')

    def pi(f):
        qM = (1 - f) * M
        S = min(s_agg, eta * f * M)
        qE = E + S
        gM = max(D_M - qM, 0.0); gE = max(D_E - qE, 0.0)
        PM = c0 + ag * gM**gg if gM > 0 else 0.0
        PE = c0 + ag * gE**gg if gE > 0 else 0.0
        return PM * qM + PE * qE

    def dpi(f):
        qM = (1 - f) * M
        qE = E + eta * f * M
        gM = D_M - qM; gE = D_E - qE
        PM = c0 + ag * gM**gg
        PE = c0 + ag * gE**gg
        return M * (ag * gg * qM * gM**(gg - 1) - PM
                    - ag * gg * eta * qE * gE**(gg - 1) + eta * PE)

    f_max = min(0.999, f_sat - 1e-6) if f_sat <= 1 else 0.999
    if dpi(1e-3) <= 0:
        f_star, regimen = 0.0, 'esquina_inferior'
    elif dpi(f_max) >= 0:
        f_star = min(1.0, f_sat)
        regimen = 'saturacion' if f_sat <= 1 else 'esquina_superior'
    else:
        f_star = brentq(dpi, 1e-3, f_max, xtol=1e-8)
        regimen = 'interior'

    qM = (1 - f_star) * M
    qE = E + min(s_agg, eta * f_star * M)
    gM = max(D_M - qM, 0.0); gE = max(D_E - qE, 0.0)
    PM = c0 + ag * gM**gg if gM > 0 else 0.0
    PE = c0 + ag * gE**gg if gE > 0 else 0.0
    return {
        'f_star': f_star, 'pi_star': pi(f_star),
        'PM_star': PM, 'PE_star': PE,
        'ratio_star': PM / PE if PE > 0 else float('inf'),
        'regimen': regimen, 'f_sat': f_sat,
        '_pi': pi, '_dpi': dpi,
    }


def solve_nash_simetricos(params=None, n_agentes=2):
    """CPO del Nash simétrico (§3.2) generalizada a n agentes."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    c_i = (p['CAP_LOW'] + p['CAP_HIGH']) / 2.0
    M_i = p['ALPHA_M'] * c_i; E_i = p['ALPHA_E'] * c_i
    eta = (p['ETA_LOW'] + p['ETA_HIGH']) / 2.0
    D_M, D_E = p['DEMAND_M'], p['DEMAND_E']
    c0, ag, gg = p['C0'], p['ALPHA_G'], p['GAMMA_G']
    s_i = (p['STOR_CAP_LOW'] + p['STOR_CAP_HIGH']) / 2.0
    f_sat = s_i / (eta * M_i) if eta * M_i > 0 else float('inf')

    def pi_i(f):
        qM_i = (1 - f) * M_i
        S_i = min(s_i, eta * f * M_i)
        qE_i = E_i + S_i
        QM = n_agentes * qM_i; QE = n_agentes * qE_i
        gM = max(D_M - QM, 0.0); gE = max(D_E - QE, 0.0)
        PM = c0 + ag * gM**gg if gM > 0 else 0.0
        PE = c0 + ag * gE**gg if gE > 0 else 0.0
        return PM * qM_i + PE * qE_i

    def dpi(f):
        qM_i = (1 - f) * M_i
        qE_i = E_i + eta * f * M_i
        QM = n_agentes * qM_i; QE = n_agentes * qE_i
        gM = D_M - QM; gE = D_E - QE
        if gM <= 0 or gE <= 0:
            return float('nan')
        PM = c0 + ag * gM**gg; PE = c0 + ag * gE**gg
        return M_i * (ag * gg * qM_i * gM**(gg - 1) - PM
                      - ag * gg * eta * qE_i * gE**(gg - 1) + eta * PE)

    f_max = min(0.999, f_sat - 1e-6) if f_sat <= 1 else 0.999
    d0 = dpi(1e-3); d1 = dpi(f_max)
    if not np.isfinite(d0) or not np.isfinite(d1):
        f_star, regimen = float('nan'), 'fuera_interior'
    elif d0 <= 0:
        f_star, regimen = 0.0, 'esquina_inferior'
    elif d1 >= 0:
        f_star = min(1.0, f_sat)
        regimen = 'saturacion' if f_sat <= 1 else 'esquina_superior'
    else:
        f_star = brentq(dpi, 1e-3, f_max, xtol=1e-8)
        regimen = 'interior'

    if np.isfinite(f_star):
        qM_i = (1 - f_star) * M_i
        qE_i = E_i + min(s_i, eta * f_star * M_i)
        QM = n_agentes * qM_i; QE = n_agentes * qE_i
        gM = max(D_M - QM, 0.0); gE = max(D_E - QE, 0.0)
        PM = c0 + ag * gM**gg if gM > 0 else 0.0
        PE = c0 + ag * gE**gg if gE > 0 else 0.0
    else:
        PM = PE = float('nan')

    return {
        'f_star': f_star,
        'pi_i_star': pi_i(f_star) if np.isfinite(f_star) else float('nan'),
        'PM_star': PM, 'PE_star': PE,
        'ratio_star': PM / PE if PE > 0 else float('inf'),
        'regimen': regimen, 'n_agentes': n_agentes,
        'f_sat': f_sat, '_pi_i': pi_i, '_dpi': dpi,
    }


def _solve_nash_simetricos_robust(params, n_agentes):
    """Variante interna que devuelve esquina cuando la CPO no cambia de signo."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    c_i = (p['CAP_LOW'] + p['CAP_HIGH']) / 2.0
    M_i = p['ALPHA_M'] * c_i; E_i = p['ALPHA_E'] * c_i
    eta = (p['ETA_LOW'] + p['ETA_HIGH']) / 2.0
    D_M, D_E = p['DEMAND_M'], p['DEMAND_E']
    c0, ag, gg = p['C0'], p['ALPHA_G'], p['GAMMA_G']

    def dpi(f):
        qM = (1 - f) * M_i; qE = E_i + eta * f * M_i
        QM = n_agentes * qM; QE = n_agentes * qE
        gM = D_M - QM; gE = D_E - QE
        if gM <= 0 or gE <= 0:
            return float('nan')
        PM = c0 + ag * gM**gg; PE = c0 + ag * gE**gg
        return M_i * (ag * gg * qM * gM**(gg - 1) - PM
                      - ag * gg * eta * qE * gE**(gg - 1) + eta * PE)

    d0 = dpi(0.001); d1 = dpi(0.999)
    if not np.isfinite(d0) or not np.isfinite(d1):
        return 0.5
    if d0 <= 0:
        return 0.001
    if d1 >= 0:
        return 0.999
    return brentq(dpi, 0.001, 0.999, xtol=1e-8)


def solve_nash_heterogeneo(params=None, c_array=None, s_array=None, eta=None,
                            f_init=None, max_nfev=2000, xtol=1e-10):
    """Sistema R_i(f) = 0 del Nash heterogéneo (§3.4) vía least_squares con cotas."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    if c_array is None:
        c_mean = (p['CAP_LOW'] + p['CAP_HIGH']) / 2.0
        c_array = np.full(p['N'], c_mean)
    c_array = np.asarray(c_array, dtype=float)
    N = len(c_array)
    if eta is None:
        eta = (p['ETA_LOW'] + p['ETA_HIGH']) / 2.0
    M = p['ALPHA_M'] * c_array
    E = p['ALPHA_E'] * c_array
    D_M, D_E = p['DEMAND_M'], p['DEMAND_E']
    c0, ag, gg = p['C0'], p['ALPHA_G'], p['GAMMA_G']

    if s_array is None:
        f_sat = np.full(N, np.inf)
    else:
        s_array = np.asarray(s_array, dtype=float)
        f_sat = np.where(M * eta > 0, s_array / (eta * M), np.inf)
    upper = np.minimum(0.9999, np.where(f_sat <= 1, np.maximum(f_sat - 1e-6, 1e-6), 0.9999))
    lower = np.full(N, 1e-6)

    if f_init is None:
        c_mean = c_array.mean()
        f0_scalar = _solve_nash_simetricos_robust(
            {**p, 'CAP_LOW': c_mean, 'CAP_HIGH': c_mean, 'N': N}, n_agentes=N)
        f0 = np.full(N, f0_scalar)
    else:
        f0 = np.asarray(f_init, dtype=float)
    f0 = np.clip(f0, lower, upper)

    def residual(f):
        qM = (1 - f) * M
        S = np.minimum(s_array, eta * f * M) if s_array is not None else eta * f * M
        qE = E + S
        QM = qM.sum(); QE = qE.sum()
        gM = D_M - QM; gE = D_E - QE
        if gM <= 0 or gE <= 0:
            return np.full(N, 1e6)
        PM = c0 + ag * gM**gg; PE = c0 + ag * gE**gg
        return (PM - eta * PE) - ag * gg * (qM * gM**(gg - 1) - eta * qE * gE**(gg - 1))

    sol = least_squares(residual, f0, bounds=(lower, upper),
                        max_nfev=max_nfev, xtol=xtol)
    f = sol.x
    qM = (1 - f) * M
    S = np.minimum(s_array, eta * f * M) if s_array is not None else eta * f * M
    qE = E + S
    QM = qM.sum(); QE = qE.sum()
    gM = max(D_M - QM, 0.0); gE = max(D_E - QE, 0.0)
    PM = c0 + ag * gM**gg if gM > 0 else 0.0
    PE = c0 + ag * gE**gg if gE > 0 else 0.0
    return {
        'f_array': f, 'qM_array': qM, 'qE_array': qE,
        'PM': PM, 'PE': PE, 'ratio': PM / PE if PE > 0 else float('inf'),
        'c_array': c_array, 's_array': s_array, 'eta': eta,
        'residual_norm': float(np.linalg.norm(sol.fun)),
        'f_sat': f_sat, 'sol_status': int(sol.status),
    }


# ─── Runner ABM con monkey-patch (sin aprendizaje) ───────────────────────────

def _run_forced(f_assign_or_value, params, seed, days, storage_enabled=True):
    """Núcleo del monkey-patch para los runs de elección forzada.
    `f_assign_or_value` puede ser float (todos en f) o dict {agent_id → f}."""
    is_dict = isinstance(f_assign_or_value, dict)
    original_produce = SolarAgent.produce_and_decide
    original_update = SolarAgent.update_learning

    def patched_produce(self):
        p = self.model.params
        eps = random.uniform(1 - p['WEATHER_VAR'], 1 + p['WEATHER_VAR'])
        self.qM_raw = p['ALPHA_M'] * self.capacity * eps
        self.qE_raw = p['ALPHA_E'] * self.capacity * eps
        choice = f_assign_or_value[self.unique_id] if is_dict else f_assign_or_value
        self.last_choice = choice
        self.stored = min(self.storage_capacity, self.eta * choice * self.qM_raw)
        self.qM = (1.0 - choice) * self.qM_raw
        self.qE = self.qE_raw + self.stored

    def patched_update(self, profit):
        self.profit = profit

    SolarAgent.produce_and_decide = patched_produce
    SolarAgent.update_learning = patched_update
    try:
        model = MarketModel(params=params, storage_enabled=storage_enabled, seed=seed)
        for _ in range(days):
            model.step_day()
        return model, model.get_model_data(), model.get_agent_data()
    finally:
        SolarAgent.produce_and_decide = original_produce
        SolarAgent.update_learning = original_update


def run_with_forced_f(f_fixed, params=None, seed=SEED, days=200):
    return _run_forced(float(f_fixed), params, seed, days, storage_enabled=True)


def run_with_forced_f_heterogeneo(f_per_agent, params=None, seed=SEED, days=200):
    return _run_forced(f_per_agent, params, seed, days, storage_enabled=True)


def compute_cartel_grid(params=None, grid=201, seeds=range(3), days=200, last=100):
    """Cártel via barrido en f homogéneo. Devuelve el f del cártel y el f
    donde el ratio P_M/P_E cruza η (aproximación al precio-aceptante)."""
    fs = np.linspace(0, 1, grid)
    rows = []
    for f in fs:
        for sd in seeds:
            _, df, _ = run_with_forced_f(float(f), params=params, seed=sd, days=days)
            tail = df.tail(last)
            rows.append({'f': float(f), 'seed': sd,
                         'profit': tail['avg_profit'].mean(),
                         'price_M': tail['price_M'].mean(),
                         'price_E': tail['price_E'].mean()})
    detalle = pd.DataFrame(rows)
    resumen = detalle.groupby('f').mean(numeric_only=True).reset_index()
    resumen['ratio'] = resumen['price_M'] / resumen['price_E'].clip(lower=1e-9)

    idx = int(resumen['profit'].idxmax())
    coop = {'f_star': float(resumen.loc[idx, 'f']),
            'profit_star': float(resumen.loc[idx, 'profit']),
            'price_M_star': float(resumen.loc[idx, 'price_M']),
            'price_E_star': float(resumen.loc[idx, 'price_E']),
            'ratio_star': float(resumen.loc[idx, 'ratio'])}

    p_eff = {**DEFAULT_PARAMS, **(params or {})}
    eta_ref = (p_eff['ETA_LOW'] + p_eff['ETA_HIGH']) / 2.0
    diff = (resumen['ratio'] - eta_ref).values
    if diff[0] * diff[-1] < 0:
        signs = np.sign(diff)
        i = int(np.where(signs[:-1] * signs[1:] <= 0)[0][0])
        d0, d1 = diff[i], diff[i + 1]
        t = -d0 / (d1 - d0) if abs(d1 - d0) > 1e-12 else 0.0
        def lerp(col):
            v0 = resumen.loc[i, col]; v1 = resumen.loc[i + 1, col]
            return float(v0 + t * (v1 - v0))
        pt = {'f_star': lerp('f'), 'profit_star': lerp('profit'),
              'price_M_star': lerp('price_M'), 'price_E_star': lerp('price_E'),
              'ratio_star': lerp('ratio'), 'corner': False}
    elif (diff < 0).all():
        n = len(resumen) - 1
        pt = {'f_star': 1.0, 'profit_star': float(resumen.loc[n, 'profit']),
              'price_M_star': float(resumen.loc[n, 'price_M']),
              'price_E_star': float(resumen.loc[n, 'price_E']),
              'ratio_star': float(resumen.loc[n, 'ratio']), 'corner': True}
    else:
        pt = {'f_star': 0.0, 'profit_star': float(resumen.loc[0, 'profit']),
              'price_M_star': float(resumen.loc[0, 'price_M']),
              'price_E_star': float(resumen.loc[0, 'price_E']),
              'ratio_star': float(resumen.loc[0, 'ratio']), 'corner': True}

    return {**coop, 'cooperativo': coop, 'price_taker_approx': pt,
            'eta_referencia': eta_ref, 'detalle': detalle, 'resumen': resumen}


def compute_nash_homogeneo_BR(params=None, f_h_grid=None, f_i_grid=None,
                               seed=SEED, days=150, last=50):
    """Nash homogéneo via BR fixed-point: para cada f_h evalúa la BR de un
    agente representativo (todos los demás en f_h) y busca el cruce con la
    diagonal."""
    if f_h_grid is None:
        f_h_grid = np.round(np.linspace(0.45, 0.70, 101 if not FAST else 21), 3)
    if f_i_grid is None:
        f_i_grid = np.linspace(0.0, 1.0, 101 if not FAST else 21)

    template = MarketModel(params=params, seed=seed)
    agent_ids = sorted(a.unique_id for a in template.agents)
    target = agent_ids[0]

    rows = []
    for f_h in f_h_grid:
        profits = []
        for f_i in f_i_grid:
            f_assign = {aid: float(f_h) for aid in agent_ids}
            f_assign[target] = float(f_i)
            _, _, df_a = run_with_forced_f_heterogeneo(f_assign, params=params,
                                                       seed=seed, days=days)
            tail = df_a[(df_a['agent_id'] == target) & (df_a['day'] >= days - last + 1)]
            profits.append(tail['agent_profit'].mean())
        profits = np.array(profits)
        br = float(f_i_grid[int(np.argmax(profits))])
        rows.append({'f_h': float(f_h), 'BR': br, 'gap': br - float(f_h),
                     'profit_at_BR': float(profits.max())})
    curva = pd.DataFrame(rows)

    gap = curva['gap'].values
    if gap[0] * gap[-1] >= 0:
        if (gap > 0).all():
            f_nash, corner = 1.0, 'corner_up'
        elif (gap < 0).all():
            f_nash, corner = 0.0, 'corner_down'
        else:
            f_nash = float(curva.loc[np.abs(gap).argmin(), 'f_h']); corner = 'no_crossing'
    else:
        signs = np.sign(gap)
        i = int(np.where(signs[:-1] * signs[1:] <= 0)[0][0])
        g0, g1 = gap[i], gap[i + 1]
        t = -g0 / (g1 - g0) if abs(g1 - g0) > 1e-12 else 0.0
        f0, f1 = float(curva.loc[i, 'f_h']), float(curva.loc[i + 1, 'f_h'])
        f_nash = f0 + t * (f1 - f0); corner = None

    _, df_m, _ = run_with_forced_f(float(f_nash), params=params, seed=seed, days=days)
    tail_m = df_m.tail(last)
    return {
        'f_star': float(f_nash),
        'profit_star': float(tail_m['avg_profit'].mean()),
        'price_M_star': float(tail_m['price_M'].mean()),
        'price_E_star': float(tail_m['price_E'].mean()),
        'ratio_star': float(tail_m['price_M'].mean() / max(tail_m['price_E'].mean(), 1e-9)),
        'curva_BR': curva, 'corner': corner,
    }


# ─── Figuras ────────────────────────────────────────────────────────────────

def fig_3_6_1_cartel(optimo_unico):
    f_upper = min(0.999, optimo_unico['f_sat'] - 1e-3) if optimo_unico['f_sat'] <= 1 else 0.999
    fs = np.linspace(0.001, f_upper, 300)
    pis = np.array([optimo_unico['_pi'](f) for f in fs])
    dpis = np.array([optimo_unico['_dpi'](f) for f in fs])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
    ax1.plot(fs, pis, color='black')
    ax1.axvline(optimo_unico['f_star'], color='red', linestyle='--',
                label=f"f* = {optimo_unico['f_star']:.3f}")
    ax1.set_xlabel('f'); ax1.set_ylabel('$\\pi(f)$ agregado')
    ax1.set_title('Beneficio del cártel vs $f$')
    ax1.legend(); ax1.grid(alpha=0.3)

    ax2.plot(fs, dpis, color='black')
    ax2.axhline(0, color='gray', linestyle=':')
    ax2.axvline(optimo_unico['f_star'], color='red', linestyle='--',
                label=f"f* = {optimo_unico['f_star']:.3f}")
    ax2.set_xlabel('f'); ax2.set_ylabel('$d\\pi/df$')
    ax2.set_title('Derivada (raíz = CPO)')
    ax2.legend(); ax2.grid(alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig_3_6_1_cartel_pi_f.png')


def fig_3_6_2_BR(optimo_nash, optimo_unico, optimo_homogeneo):
    fig, ax = plt.subplots(figsize=(8, 5))
    c = optimo_nash['curva_BR']
    pt = optimo_homogeneo['price_taker_approx']
    ax.plot(c['f_h'], c['BR'], 'o-', color='black', label='$\\mathrm{BR}(f_h)$', ms=3)
    ax.plot(c['f_h'], c['f_h'], '--', color='gray', label='diagonal $f_h$')
    ax.axvline(optimo_nash['f_star'], color='red', linestyle='--',
               label=f"Nash $f^N$ = {optimo_nash['f_star']:.3f}")
    ax.axvline(optimo_unico['f_star'], color='blue', linestyle=':',
               label=f"Cártel $f^*$ = {optimo_unico['f_star']:.3f}")
    ax.axvline(pt['f_star'], color='orange', linestyle='-.',
               label=f"Precio-aceptante $f^*$ = {pt['f_star']:.3f}")
    ax.set_xlabel('$f_h$ (todos los demás)'); ax.set_ylabel('$\\mathrm{BR}(f_h)$')
    ax.set_title('Curva $\\mathrm{BR}(f_h)$ y Nash como punto fijo')
    ax.legend(); ax.grid(alpha=0.3); ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    _save(fig, 'fig_3_6_2_BR_diagonal.png')


def fig_3_6_2_paisaje(f_h_test, params=PARAMS_INTERIOR):
    template = MarketModel(params=params, seed=SEED)
    agent_ids = sorted(a.unique_id for a in template.agents)
    target = agent_ids[0]

    f_i_grid = np.linspace(0.0, 1.0, 21)
    profits = []
    for f_i in f_i_grid:
        f_assign = {aid: float(f_h_test) for aid in agent_ids}
        f_assign[target] = float(f_i)
        _, _, df_a = run_with_forced_f_heterogeneo(f_assign, params=params,
                                                   seed=SEED, days=150)
        tail = df_a[(df_a['agent_id'] == target) & (df_a['day'] >= 100)]
        profits.append(tail['agent_profit'].mean())
    profits = np.array(profits)
    rng = profits.max() - profits.min()
    print(f'    paisaje plano: variación = {rng:.3f} unidades '
          f'({rng / profits.max() * 100:.2f}% del nivel)')

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(f_i_grid, profits, 'o-', color='black')
    ax.axvline(f_h_test, color='gray', linestyle=':',
               label=f'$f_h$ (resto) = {f_h_test:.3f}')
    ax.axvline(f_i_grid[profits.argmax()], color='red', linestyle='--',
               label=f'$\\mathrm{{BR}}$ (argmax) = {f_i_grid[profits.argmax()]:.3f}')
    ax.set_xlabel('$f_i$ (agente focal)'); ax.set_ylabel('$\\pi_i$')
    ax.set_title(f'Paisaje $\\pi_i(f_i)$ con el resto en $f_h = {f_h_test:.3f}$\n'
                 '(curva plana → $\\mathrm{BR}$ muy sensible)')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig_3_6_2_paisaje_plano.png')


def fig_3_6_3_comparativa(refs_n30, refs_n2):
    """2x2: fila superior N=30, fila inferior N=2.
    Cada fila: izq π_i(f), der ∂π_i/∂f_i."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    (ax1, ax2), (ax3, ax4) = axes

    for (axL, axR, refs, N) in [(ax1, ax2, refs_n30, 30), (ax3, ax4, refs_n2, 2)]:
        nash_cpo = refs['nash_cpo']
        cartel_cpo = refs['cartel_cpo']
        cartel_grid = refs['cartel_grid']
        nash_br = refs['nash_br']
        pt = refs['pt']

        f_upper = min(0.999, nash_cpo['f_sat'] - 1e-3) if nash_cpo['f_sat'] <= 1 else 0.999
        fs = np.linspace(0.001, f_upper, 300)
        pis = np.array([nash_cpo['_pi_i'](f) for f in fs])
        dpis = np.array([nash_cpo['_dpi'](f) for f in fs])

        axL.plot(fs, pis, color='black')
        axL.axvline(cartel_cpo['f_star'], color='red', linestyle='--',
                    label=f"Cártel CPO: {cartel_cpo['f_star']:.3f}")
        axL.axvline(cartel_grid['cooperativo']['f_star'], color='red', linestyle=':',
                    alpha=0.6, label=f"Cártel grid: {cartel_grid['cooperativo']['f_star']:.3f}")
        if np.isfinite(nash_cpo['f_star']):
            axL.axvline(nash_cpo['f_star'], color='green', linestyle='-.',
                        label=f"Nash CPO: {nash_cpo['f_star']:.3f}")
        axL.axvline(nash_br['f_star'], color='blue', linestyle=':', alpha=0.7,
                    label=f"Nash BR: {nash_br['f_star']:.3f}")
        axL.axvline(pt['f_star'], color='purple', linestyle='--', alpha=0.7,
                    label=f"Precio-acept.: {pt['f_star']:.3f}")
        axL.set_xlabel('f'); axL.set_ylabel('$\\pi_i(f)$ individual')
        axL.set_title(f'Beneficio individual en simetría ($N={N}$)')
        axL.legend(fontsize=8); axL.grid(alpha=0.3)

        axR.plot(fs, dpis, color='black')
        axR.axhline(0, color='gray', linestyle=':')
        axR.axvline(cartel_cpo['f_star'], color='red', linestyle='--', label='Cártel')
        if np.isfinite(nash_cpo['f_star']):
            axR.axvline(nash_cpo['f_star'], color='green', linestyle='-.', label='Nash CPO')
        axR.axvline(nash_br['f_star'], color='blue', linestyle=':', alpha=0.7, label='Nash BR')
        axR.axvline(pt['f_star'], color='purple', linestyle='--', alpha=0.7,
                    label='Precio-acept.')
        axR.set_xlabel('f'); axR.set_ylabel('$\\partial\\pi_i/\\partial f_i$')
        axR.set_title(f'Derivada del best-response simétrico ($N={N}$)')
        axR.legend(fontsize=8); axR.grid(alpha=0.3)

    fig.tight_layout()
    _save(fig, 'fig_3_6_3_comparativa.png')


def fig_3_6_4_heterogeneo(res_c, res_cs, c_modelo, optimo_unico,
                           nash_cpo_n30, optimo_homogeneo):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.5))

    ax1.scatter(c_modelo, res_c['f_array'], color='black', s=40, alpha=0.7,
                label='Caso A: solo $c_i$ heterogéneo')
    ax1.scatter(c_modelo, res_cs['f_array'], color='orange', s=40, alpha=0.7,
                marker='x', label='Caso B: $c_i$ y $s_i$ heterogéneos')
    ax1.axhline(optimo_unico['f_star'], color='red', linestyle='--',
                label=f"Cártel: {optimo_unico['f_star']:.3f}")
    ax1.axhline(nash_cpo_n30['f_star'], color='green', linestyle='-.',
                label=f"Nash simétrico N=30: {nash_cpo_n30['f_star']:.3f}")
    pt = optimo_homogeneo['price_taker_approx']
    ax1.axhline(pt['f_star'], color='purple', linestyle=':',
                label=f"Precio-acept.: {pt['f_star']:.3f}")
    ax1.set_xlabel('$c_i$ (capacidad instalada)')
    ax1.set_ylabel('$f_i^*$ (Nash heterogéneo)')
    ax1.set_title('Equilibrio Nash heterogéneo: $f_i^*$ vs $c_i$')
    ax1.legend(fontsize=8, loc='best'); ax1.grid(alpha=0.3)

    order = np.argsort(c_modelo)
    x = np.arange(len(c_modelo))
    ax2.plot(x, res_c['f_array'][order], 'o-', color='black', label='Caso A')
    ax2.plot(x, res_cs['f_array'][order], 's-', color='orange', label='Caso B')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x, c_modelo[order], '--', color='blue', alpha=0.4,
                  label='$c_i$ (eje derecho)')
    ax2.set_xlabel('Agente (ordenado por $c_i$ creciente)')
    ax2.set_ylabel('$f_i^*$')
    ax2_twin.set_ylabel('$c_i$', color='blue')
    ax2.set_title('$f_i^*$ y $c_i$ ordenados por capacidad')
    ax2.legend(loc='upper right', fontsize=8); ax2.grid(alpha=0.3)

    fig.tight_layout()
    _save(fig, 'fig_3_6_4_nash_heterogeneo.png')


def _save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  guardada: {name}')


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f'Generando figuras del cap. 3 (FAST={FAST}, seed={SEED})...')
    print('  ' + '─' * 60)

    # 1. Cártel CPO (instantáneo) + figura 3.6.1
    print('  [1] Cártel CPO + figura 3.6.1')
    optimo_unico = solve_unico_cpo(PARAMS_INTERIOR)
    print(f"      cártel f* = {optimo_unico['f_star']:.4f}, "
          f"PM/PE = {optimo_unico['ratio_star']:.3f}, "
          f"régimen = {optimo_unico['regimen']}")
    fig_3_6_1_cartel(optimo_unico)

    # 2. Cártel via grid + price-taker approx (lento, ~30s)
    print('  [2] Cártel via grid (para price-taker approx)')
    optimo_homogeneo = compute_cartel_grid(
        PARAMS_INTERIOR, grid=201 if not FAST else 51,
        seeds=range(3), days=200, last=100,
    )
    print(f"      cártel grid f* = {optimo_homogeneo['cooperativo']['f_star']:.4f}, "
          f"price-taker f* = {optimo_homogeneo['price_taker_approx']['f_star']:.4f}")

    # 3. Nash BR fixed-point N=30 (LENTO: 101x101x150 días) + figura 3.6.2
    print(f'  [3] Nash BR fixed-point N=30 (puede tardar varios minutos)')
    optimo_nash = compute_nash_homogeneo_BR(
        params=PARAMS_INTERIOR,
        f_h_grid=np.round(np.linspace(0.45, 0.70, 101 if not FAST else 21), 3),
        f_i_grid=np.linspace(0.0, 1.0, 101 if not FAST else 21),
        seed=SEED, days=150, last=50,
    )
    print(f"      Nash N=30  f^N = {optimo_nash['f_star']:.4f}, "
          f"PM/PE = {optimo_nash['ratio_star']:.3f}")
    fig_3_6_2_BR(optimo_nash, optimo_unico, optimo_homogeneo)

    # 4. Paisaje plano anclado en el precio-aceptante
    print('  [4] Paisaje plano cerca del Nash')
    fig_3_6_2_paisaje(optimo_homogeneo['price_taker_approx']['f_star'])

    # 5. Caso N=2 + comparativa (figura 3.6.3)
    print('  [5] Caso N=2 (cártel + Nash CPO + Nash BR)')
    cartel_cpo_n2 = solve_unico_cpo(PARAMS_INTERIOR_N2)
    nash_cpo_n2 = solve_nash_simetricos(PARAMS_INTERIOR_N2, n_agentes=2)
    nash_br_n2 = compute_nash_homogeneo_BR(
        PARAMS_INTERIOR_N2,
        f_h_grid=np.round(np.linspace(0.4, 0.85, 12), 3),
        f_i_grid=np.linspace(0.0, 1.0, 21),
        seed=SEED, days=150, last=50,
    )
    cartel_grid_n2 = compute_cartel_grid(
        PARAMS_INTERIOR_N2, grid=201 if not FAST else 51,
        seeds=range(1), days=200, last=100,
    )
    nash_cpo_n30 = solve_nash_simetricos(PARAMS_INTERIOR, n_agentes=PARAMS_INTERIOR['N'])
    refs_n30 = {'nash_cpo': nash_cpo_n30, 'cartel_cpo': optimo_unico,
                'cartel_grid': optimo_homogeneo, 'nash_br': optimo_nash,
                'pt': optimo_homogeneo['price_taker_approx']}
    refs_n2 = {'nash_cpo': nash_cpo_n2, 'cartel_cpo': cartel_cpo_n2,
               'cartel_grid': cartel_grid_n2, 'nash_br': nash_br_n2,
               'pt': cartel_grid_n2['price_taker_approx']}
    print(f"      Nash N=2  f^N = {nash_cpo_n2['f_star']:.4f}, "
          f"BR = {nash_br_n2['f_star']:.4f}")
    fig_3_6_3_comparativa(refs_n30, refs_n2)

    # 6. Nash heterogéneo (instantáneo) + figura 3.6.4
    print('  [6] Nash heterogéneo')
    template = MarketModel(params=PARAMS_INTERIOR_HET, seed=SEED)
    c_modelo = np.array([a.capacity for a in template.agents])
    s_modelo = np.array([a.storage_capacity for a in template.agents])
    eta_modelo = float(np.mean([a.eta for a in template.agents]))
    res_c = solve_nash_heterogeneo(params=PARAMS_INTERIOR_HET,
                                    c_array=c_modelo, s_array=None,
                                    eta=eta_modelo)
    res_cs = solve_nash_heterogeneo(params=PARAMS_INTERIOR_HET,
                                     c_array=c_modelo, s_array=s_modelo,
                                     eta=eta_modelo)
    rho = np.corrcoef(c_modelo, res_c['f_array'])[0, 1]
    print(f"      f_i* ∈ [{res_c['f_array'].min():.4f}, {res_c['f_array'].max():.4f}], "
          f"ρ(c_i, f_i*) = {rho:+.4f}, residuo = {res_c['residual_norm']:.2e}")
    fig_3_6_4_heterogeneo(res_c, res_cs, c_modelo,
                           optimo_unico, nash_cpo_n30, optimo_homogeneo)

    print('  ' + '─' * 60)
    print('Listo.')


if __name__ == '__main__':
    main()
