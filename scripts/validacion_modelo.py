# validacion_modelo.py — Anexo de validación del modelo (solo repositorio GitHub)
# TFG: Modelo de almacenamiento solar adaptativo — Carlos Molina Centeno
#
# Ejecuta, en orden, las seis pruebas de validación del anexo:
#   V.1  Reproducibilidad por semilla
#   V.2  Invariantes y sanity checks
#   V.3  Verificación cuerpo <-> código (trazabilidad ejecutable)
#   V.4  Robustez de las cifras del cap. 5 (seeds {0..19} x T {200,500,1000})
#   V.5  Sensibilidad a parámetros (eta, phi, beta)
#   V.6  Robustez agregada (N con N*c = 75 constante, s escalado = 4c)
#
# Importa de model.py SIN MODIFICARLO. Genera data/validacion_*.csv y figures/validacion_*.png.
# Uso:  python scripts/validacion_modelo.py
#
# NOTA: la regla de aprendizaje y la parametrización INTERIOR son las DEFAULT de model.py
# (z-score del beneficio realizado, solo la fracción jugada, sin decay).

import os
import sys
import time
import math

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from model import (MarketModel, run_single, DEFAULT_PARAMS, stable_softmax,
                   gas_marginal_cost)

# Consola Windows (cp1252) no codifica Δ/η/acentos: forzamos UTF-8.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Rutas ────────────────────────────────────────────────────────────────────
FIGDIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
DATADIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(DATADIR, exist_ok=True)

# ── Constantes del modelo (leídas de DEFAULT_PARAMS, no recodificadas) ────────
C0 = DEFAULT_PARAMS['C0']
ALPHA_G = DEFAULT_PARAMS['ALPHA_G']
GAMMA_G = DEFAULT_PARAMS['GAMMA_G']
ALPHA_M = DEFAULT_PARAMS['ALPHA_M']
ALPHA_E = DEFAULT_PARAMS['ALPHA_E']
D_M = DEFAULT_PARAMS['DEMAND_M']
D_E = DEFAULT_PARAMS['DEMAND_E']
N_DEFAULT = DEFAULT_PARAMS['N']
ETA_DEFAULT = DEFAULT_PARAMS['ETA_LOW']
LAST = 100   # ventana estacionaria (últimos 100 días), igual que cap. 5

# Referencias analíticas del cap. 3 (homogéneas)
NASH_F = 0.639
NASH_PROFIT = 275.14
NASH_RATIO = 0.880
PRICETAKER_RATIO = ETA_DEFAULT   # límite precio-aceptante: P_M/P_E -> eta

# Cifras del cap. 5 (seed=0, T=500) que V.4 contrasta
CAP5 = {
    'f': 0.633, 'ratio': 0.874, 'profit': 275.19,
    'gas_M': 60.68, 'gas_E': 67.48, 'gas_total': 128.17,
    'gas_total_pct': 2.4, 'cost_pct': -27.1,
    'dCS': 3461.0, 'dSolar': 1972.0, 'dGasRent': -3071.0, 'dTotal': 2362.0,
}

plt.rcParams.update({
    'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.3,
    'figure.dpi': 100, 'savefig.bbox': 'tight',
})
COL_BASE = '#c0392b'
COL_STOR = '#27ae60'
COL_REF = '#2c3e50'


def _save(fig, name):
    fig.savefig(os.path.join(FIGDIR, name), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  guardada figura: {name}')


# ── Funciones de coste de gas y bienestar (réplica de generate_figures_cap5) ──
def gas_total_cost(q):
    """Coste total del gas en un periodo = integral del coste marginal."""
    if q <= 0:
        return 0.0
    return C0 * q + ALPHA_G * q ** (GAMMA_G + 1) / (GAMMA_G + 1)


def gas_marg_cost(q):
    return 0.0 if q <= 0 else C0 + ALPHA_G * q ** GAMMA_G


def gas_rent(q):
    """Renta (excedente) del productor de gas: precio*cantidad - coste total."""
    return gas_marg_cost(q) * q - gas_total_cost(q)


def daily_ratio(df):
    """Cociente diario P_M/P_E (definición del cap. 4/5: media de cocientes)."""
    pe = df['price_E'].clip(lower=1e-9)
    return df['price_M'] / pe


def welfare_components(df, n=N_DEFAULT, last=LAST):
    """Medias estacionarias de los componentes de excedente (como cap. 5)."""
    d = df.tail(last)
    expend = (d['price_M'] * D_M + d['price_E'] * D_E).mean()
    solar = (d['avg_profit'] * n).mean()
    rent = (d['gas_M'].apply(gas_rent) + d['gas_E'].apply(gas_rent)).mean()
    cost = (d['gas_M'].apply(gas_total_cost) + d['gas_E'].apply(gas_total_cost)).mean()
    return expend, solar, rent, cost


def steady_metrics(df, n=N_DEFAULT, last=LAST):
    """Métricas del régimen estacionario (últimos `last` días) de una corrida."""
    d = df.tail(last)
    cost_daily = (d['gas_M'].apply(gas_total_cost) + d['gas_E'].apply(gas_total_cost)).mean()
    return {
        'f': d['avg_storage_fraction'].mean(),
        'pm': d['price_M'].mean(), 'pe': d['price_E'].mean(),
        'ratio': daily_ratio(d).mean(),
        'profit': d['avg_profit'].mean(),
        'gas_M': d['gas_M'].mean(), 'gas_E': d['gas_E'].mean(),
        'gas_total': d['gas_M'].mean() + d['gas_E'].mean(),
        'cost_daily': cost_daily,
    }


def mean_entropy(model):
    """Entropía de Shannon de la softmax de cada agente (estado final), normalizada
    por log|F| (1 = uniforme, 0 = determinista), promediada sobre la población."""
    Hs = []
    for a in model.agents:
        arr = np.array([a.attract[f] for f in a.fractions], dtype=float)
        p = stable_softmax(arr, a.beta)
        p = p[p > 0]
        Hs.append(-np.sum(p * np.log(p)) / np.log(len(a.fractions)))
    return float(np.mean(Hs))


def pct(new, old):
    return 100.0 * (new - old) / old if old else float('nan')


# ═══════════════════════════════════════════════════════════════════════════════
# V.1  Reproducibilidad por semilla
# ═══════════════════════════════════════════════════════════════════════════════
def v1_reproducibilidad(seeds=range(20), days=500):
    print('\n[V.1] Reproducibilidad por semilla')

    # (a) misma seed -> trayectoria idéntica
    _, dfa, _ = run_single(storage_enabled=True, days=days, seed=0)
    _, dfb, _ = run_single(storage_enabled=True, days=days, seed=0)
    cols = ['price_M', 'price_E', 'avg_storage_fraction', 'avg_profit']
    max_diff = max(float((dfa[c] - dfb[c]).abs().max()) for c in cols)
    print(f'  (a) misma seed=0, diff máx. sobre {cols}: {max_diff:.2e}')

    # (b) seeds {0..19}: distribución asintótica común
    rows, trayectorias = [], []
    for s in seeds:
        _, df, _ = run_single(storage_enabled=True, days=days, seed=s)
        sm = steady_metrics(df)
        rows.append({'seed': s, 'f_estac': sm['f'], 'profit_estac': sm['profit'],
                     'ratio_estac': sm['ratio']})
        trayectorias.append(df['avg_storage_fraction'].values)
    dfres = pd.DataFrame(rows)
    f_mean, f_std = dfres['f_estac'].mean(), dfres['f_estac'].std()
    print(f'  (b) {len(dfres)} seeds: f_estac = {f_mean:.4f} ± {f_std:.4f} '
          f'(min {dfres.f_estac.min():.3f}, max {dfres.f_estac.max():.3f})')

    dfres.to_csv(os.path.join(DATADIR, 'validacion_v1_reproducibilidad.csv'), index=False)

    # Figura: trayectorias superpuestas + media
    fig, ax = plt.subplots(figsize=(9, 4))
    arr = np.array(trayectorias)
    for tr in arr:
        ax.plot(range(1, len(tr) + 1), tr, color='#999999', lw=0.5, alpha=0.4)
    ax.plot(range(1, arr.shape[1] + 1), arr.mean(axis=0), color=COL_STOR, lw=2,
            label=f'media sobre {len(arr)} semillas')
    ax.axhline(NASH_F, color=COL_REF, ls='--', lw=1, label=f'Nash $f^N={NASH_F}$')
    ax.set_xlabel('día'); ax.set_ylabel(r'fracción media $\bar f(t)$')
    ax.set_title('V.1 — Trayectorias de $\\bar f(t)$ para 20 semillas: distribución asintótica común')
    ax.legend(fontsize=9)
    fig.tight_layout()
    _save(fig, 'validacion_v1_trayectorias.png')

    return {'max_diff_same_seed': max_diff, 'f_mean': f_mean, 'f_std': f_std,
            'f_min': float(dfres.f_estac.min()), 'f_max': float(dfres.f_estac.max())}


# ═══════════════════════════════════════════════════════════════════════════════
# V.2  Invariantes y sanity checks
# ═══════════════════════════════════════════════════════════════════════════════
def v2_invariantes(days=500, seed=0, tol=1e-9):
    print('\n[V.2] Invariantes y sanity checks')
    model, dfm, dfa = run_single(storage_enabled=True, days=days, seed=seed)

    # s_i homogéneo en DEFAULT (STOR_CAP_LOW == STOR_CAP_HIGH): batería = 10
    s_cap = DEFAULT_PARAMS['STOR_CAP_LOW']
    assert DEFAULT_PARAMS['STOR_CAP_LOW'] == DEFAULT_PARAMS['STOR_CAP_HIGH'], \
        'V.2 asume s homogéneo'

    checks = []

    def record(nombre, mask_ok, n_cells, errmax=0.0):
        viol = int((~mask_ok).sum()) if hasattr(mask_ok, 'sum') else int(not mask_ok)
        checks.append({'invariante': nombre, 'celdas': int(n_cells),
                       'violaciones': viol, 'error_max': float(errmax)})
        flag = 'OK' if viol == 0 else f'!! {viol} VIOLACIONES'
        print(f'  {nombre:48s} celdas={n_cells:7d}  err_max={errmax:.2e}  {flag}')

    a = dfa.copy()
    choice = a['agent_choice'].values
    qM = a['agent_qM'].values
    qE = a['agent_qE'].values
    stored = a['agent_stored'].values
    eta = a['agent_eta'].values

    # --- Reconstrucción de la producción bruta (solo donde choice < 1) ---
    interior = choice < 1.0 - 1e-12
    qM_raw = np.where(interior, qM / np.where(interior, 1.0 - choice, 1.0), np.nan)
    qE_raw = (ALPHA_E / ALPHA_M) * qM_raw   # qE_raw = (alpha_E/alpha_M) * qM_raw

    # Invariante almacenamiento: stored == min(s, eta*choice*qM_raw)
    stored_pred = np.minimum(s_cap, eta * choice * qM_raw)
    err_st = np.abs(stored[interior] - stored_pred[interior])
    record('stored == min(s, eta*f*q~M)', err_st < tol, interior.sum(),
           err_st.max() if interior.sum() else 0.0)

    # Invariante venta tarde: qE == qE_raw + stored
    qE_pred = qE_raw + stored
    err_qe = np.abs(qE[interior] - qE_pred[interior])
    record('qE == q~E + stored', err_qe < tol, interior.sum(),
           err_qe.max() if interior.sum() else 0.0)

    # No-negatividad (agentes)
    nn = (qM >= -tol) & (qE >= -tol) & (stored >= -tol)
    record('qM,qE,stored >= 0', nn, len(a))
    # stored <= s
    record('stored <= s', stored <= s_cap + tol, len(a))
    # stored <= eta*choice*qM_raw (no se crea energía)
    cap_phys = eta * choice * qM_raw + tol
    record('stored <= eta*f*q~M', stored[interior] <= cap_phys[interior], interior.sum())

    # f decidida ∈ malla {0,0.1,...,1} (sin drift)
    on_grid = np.abs(choice * 10 - np.round(choice * 10)) < tol
    record('f en malla {0,0.1,..,1}', on_grid, len(a))

    # --- Clearing de mercado (datos del modelo) ---
    m = dfm.copy()
    # Mañana
    ge_M = np.where(m['total_solar_M'] >= D_M, 0.0, D_M - m['total_solar_M'])
    pm_pred = np.where(m['total_solar_M'] >= D_M, 0.0,
                       np.array([gas_marginal_cost(g, C0, ALPHA_G, GAMMA_G) for g in ge_M]))
    err_gm = np.abs(m['gas_M'].values - ge_M)
    err_pm = np.abs(m['price_M'].values - pm_pred)
    record('clearing mañana: gas_M y P_M', (err_gm < tol) & (err_pm < tol), len(m),
           max(err_gm.max(), err_pm.max()))
    # Tarde
    ge_E = np.where(m['total_solar_E'] >= D_E, 0.0, D_E - m['total_solar_E'])
    pe_pred = np.where(m['total_solar_E'] >= D_E, 0.0,
                       np.array([gas_marginal_cost(g, C0, ALPHA_G, GAMMA_G) for g in ge_E]))
    err_ge = np.abs(m['gas_E'].values - ge_E)
    err_pe = np.abs(m['price_E'].values - pe_pred)
    record('clearing tarde: gas_E y P_E', (err_ge < tol) & (err_pe < tol), len(m),
           max(err_ge.max(), err_pe.max()))
    # No-negatividad precios/gas
    record('P_M,P_E,gas_M,gas_E >= 0',
           (m['price_M'] >= -tol).all() and (m['price_E'] >= -tol).all()
           and (m['gas_M'] >= -tol).all() and (m['gas_E'] >= -tol).all(), len(m))

    dfc = pd.DataFrame(checks)
    dfc.to_csv(os.path.join(DATADIR, 'validacion_v2_invariantes.csv'), index=False)
    total_viol = int(dfc['violaciones'].sum())
    print(f'  -> total violaciones: {total_viol}')
    return {'total_violaciones': total_viol, 'n_checks': len(dfc)}


# ═══════════════════════════════════════════════════════════════════════════════
# V.3  Trazabilidad ejecutable: reproducir a mano un paso de actualización
# ═══════════════════════════════════════════════════════════════════════════════
def v3_trazabilidad(seed=0):
    print('\n[V.3] Trazabilidad ejecutable (un paso de actualización)')
    model = MarketModel(storage_enabled=True, seed=seed)
    agent = list(model.agents)[0]

    attract_before = dict(agent.attract)     # pre-update (produce_and_decide no toca attract)
    model.step_day()                          # decide -> clearing -> update_learning

    # Datos tras el paso
    pM, pE = model.price_M, model.price_E
    choice = agent.last_choice
    qM_raw, qE_raw = agent.qM_raw, agent.qE_raw
    eta, s_cap, phi = agent.eta, agent.storage_capacity, agent.phi

    # Reproducción a mano de la fórmula del cap. 4 §4.2.3
    pi_all = {}
    for f in agent.fractions:
        stored_f = min(s_cap, eta * f * qM_raw)
        pi_all[f] = pM * (1 - f) * qM_raw + pE * (qE_raw + stored_f)
    pi_vals = np.array(list(pi_all.values()))
    mean_pi, std_pi = pi_vals.mean(), pi_vals.std()
    profit_real = pM * agent.qM + pE * agent.qE

    if std_pi < 1e-8:
        expected_chosen = attract_before[choice]   # día degenerado: sin actualización
        z = float('nan')
    else:
        z = (profit_real - mean_pi) / std_pi
        expected_chosen = (1 - phi) * attract_before[choice] + phi * z

    obs_chosen = agent.attract[choice]
    diff_chosen = abs(expected_chosen - obs_chosen)

    # Las no jugadas deben permanecer intactas
    diff_otras = max(abs(agent.attract[f] - attract_before[f])
                     for f in agent.fractions if f != choice)
    # El contrafactual de la jugada == beneficio realizado
    diff_realizado = abs(pi_all[choice] - profit_real)

    print(f'  z={z:.6f}  attract[f_elegida]: esperado={expected_chosen:.8f} '
          f'observado={obs_chosen:.8f}  diff={diff_chosen:.2e}')
    print(f'  diff máx. fracciones no jugadas (deben ser 0): {diff_otras:.2e}')
    print(f'  diff contrafactual(jugada) vs beneficio realizado: {diff_realizado:.2e}')

    pd.DataFrame([{
        'z': z, 'attract_esperado': expected_chosen, 'attract_observado': obs_chosen,
        'diff_elegida': diff_chosen, 'diff_no_jugadas': diff_otras,
        'diff_realizado': diff_realizado,
    }]).to_csv(os.path.join(DATADIR, 'validacion_v3_traza_update.csv'), index=False)

    return {'diff_elegida': diff_chosen, 'diff_no_jugadas': diff_otras,
            'diff_realizado': diff_realizado}


# ═══════════════════════════════════════════════════════════════════════════════
# V.4  Robustez de las cifras del cap. 5
# ═══════════════════════════════════════════════════════════════════════════════
def v4_robustez(seeds=range(20), horizons=(200, 500, 1000)):
    print('\n[V.4] Robustez de las cifras del cap. 5')
    long_rows = []
    for T in horizons:
        for s in seeds:
            _, df_b, _ = run_single(storage_enabled=False, days=T, seed=s)
            _, df_s, _ = run_single(storage_enabled=True, days=T, seed=s)
            mb, ms = steady_metrics(df_b), steady_metrics(df_s)

            # bienestar (deltas con − sin almacenamiento)
            eb, sb, rb, cb = welfare_components(df_b)
            es, ss, rs, cs = welfare_components(df_s)
            metrics = {
                'f': ms['f'], 'ratio': ms['ratio'], 'profit': ms['profit'],
                'gas_M': ms['gas_M'], 'gas_E': ms['gas_E'], 'gas_total': ms['gas_total'],
                'gas_total_pct': pct(ms['gas_total'], mb['gas_total']),
                'cost_pct': pct(ms['cost_daily'], mb['cost_daily']),
                'dCS': -(es - eb), 'dSolar': ss - sb,
                'dGasRent': rs - rb, 'dTotal': -(cs - cb),
            }
            for k, v in metrics.items():
                long_rows.append({'T': T, 'seed': s, 'metric': k, 'value': v})

    dl = pd.DataFrame(long_rows)
    dl.to_csv(os.path.join(DATADIR, 'validacion_v4_robustez.csv'), index=False)

    # Resumen media±std por T y comprobación del criterio (cifra cap.5 en media±2sd a T=500)
    summary_rows = []
    for metric in dl['metric'].unique():
        cap5_val = CAP5.get(metric, np.nan)
        for T in horizons:
            sub = dl[(dl['metric'] == metric) & (dl['T'] == T)]['value']
            mean, std = sub.mean(), sub.std()
            within = (abs(cap5_val - mean) <= 2 * std) if not np.isnan(cap5_val) else None
            summary_rows.append({'metric': metric, 'T': T, 'mean': mean, 'std': std,
                                 'min': sub.min(), 'max': sub.max(),
                                 'cap5': cap5_val, 'within_2sd': within})
    ds = pd.DataFrame(summary_rows)
    ds.to_csv(os.path.join(DATADIR, 'validacion_v4_resumen.csv'), index=False)

    print('  Resumen a T=500 (media ± std sobre 20 seeds vs cifra cap. 5):')
    for _, r in ds[ds['T'] == 500].iterrows():
        flag = '' if r['within_2sd'] is None else ('  OK' if r['within_2sd'] else '  <-- FUERA 2sd')
        print(f"    {r['metric']:14s} {r['mean']:10.3f} ± {r['std']:8.3f}   "
              f"cap5={r['cap5']:9.3f}{flag}")

    # Comprobación de signos clave en >=90% de seeds (T=500)
    signos = {'gas_total_pct': '>0', 'cost_pct': '<0', 'dCS': '>0',
              'dSolar': '>0', 'dGasRent': '<0', 'dTotal': '>0'}
    print('  Estabilidad de signos (T=500, fracción de seeds con el signo esperado):')
    signo_rows = []
    for metric, signo in signos.items():
        vals = dl[(dl['metric'] == metric) & (dl['T'] == 500)]['value']
        frac = (vals > 0).mean() if signo == '>0' else (vals < 0).mean()
        signo_rows.append({'metric': metric, 'signo_esperado': signo, 'frac_ok': frac})
        print(f"    {metric:14s} esperado {signo:>2s}: {frac*100:.0f}% de seeds")
    pd.DataFrame(signo_rows).to_csv(
        os.path.join(DATADIR, 'validacion_v4_signos.csv'), index=False)

    # ── Figura A: métricas de mercado (boxplots por T, cifra cap.5 marcada) ──
    market = ['f', 'ratio', 'profit', 'gas_M', 'gas_E', 'gas_total', 'gas_total_pct', 'cost_pct']
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for ax, metric in zip(axes.flat, market):
        data = [dl[(dl['metric'] == metric) & (dl['T'] == T)]['value'].values for T in horizons]
        ax.boxplot(data, tick_labels=[str(t) for t in horizons])
        if metric in CAP5:
            ax.axhline(CAP5[metric], color=COL_BASE, ls='--', lw=1.2,
                       label=f'cap.5 = {CAP5[metric]:g}')
            ax.legend(fontsize=8)
        ax.set_title(metric); ax.set_xlabel('T (días)')
    fig.suptitle('V.4 — Distribución de las métricas del cap. 5 sobre 20 semillas y 3 horizontes', y=1.0)
    fig.tight_layout()
    _save(fig, 'validacion_v4_distribuciones.png')

    # ── Figura B: descomposición de excedentes ──
    welf = ['dCS', 'dSolar', 'dGasRent', 'dTotal']
    fig, axes = plt.subplots(1, 4, figsize=(15, 4))
    for ax, metric in zip(axes.flat, welf):
        data = [dl[(dl['metric'] == metric) & (dl['T'] == T)]['value'].values for T in horizons]
        ax.boxplot(data, tick_labels=[str(t) for t in horizons])
        ax.axhline(CAP5[metric], color=COL_BASE, ls='--', lw=1.2, label=f'cap.5 = {CAP5[metric]:g}')
        ax.axhline(0, color='#888', lw=0.8)
        ax.set_title(metric); ax.set_xlabel('T (días)'); ax.legend(fontsize=8)
    fig.suptitle('V.4 — Descomposición de excedentes (Δ con − sin almacenamiento) sobre 20 semillas', y=1.02)
    fig.tight_layout()
    _save(fig, 'validacion_v4_excedentes.png')

    return {'resumen': ds, 'signos': pd.DataFrame(signo_rows)}


# ═══════════════════════════════════════════════════════════════════════════════
# V.5  Sensibilidad a parámetros (eta, phi, beta)
# ═══════════════════════════════════════════════════════════════════════════════
def _run_homogeneo(param_low, param_high, value, n_replicas, days):
    """Corre n_replicas con el par (LOW,HIGH) fijado homogéneo a `value`."""
    out = []
    for s in range(n_replicas):
        p = {param_low: value, param_high: value}
        model, df, _ = run_single(params=p, storage_enabled=True, days=days, seed=s)
        sm = steady_metrics(df)
        sm['entropy'] = mean_entropy(model)
        sm['seed'] = s
        out.append(sm)
    return pd.DataFrame(out)


def v5_sensibilidad(n_replicas=10, days=500):
    print('\n[V.5] Sensibilidad a parámetros')
    results = {}

    # Base (gas total sin almacenamiento) — no depende de eta/phi/beta
    base_gt = np.mean([steady_metrics(run_single(storage_enabled=False, days=days, seed=s)[1])['gas_total']
                       for s in range(n_replicas)])
    print(f'  gas_total base (sin almac.), media {n_replicas} seeds: {base_gt:.2f}')

    # V.5.1 eta
    etas = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
    rows = []
    for e in etas:
        df = _run_homogeneo('ETA_LOW', 'ETA_HIGH', e, n_replicas, days)
        rows.append({'eta': e, 'f': df['f'].mean(), 'f_std': df['f'].std(),
                     'gas_total': df['gas_total'].mean(),
                     'gas_total_pct_vs_base': pct(df['gas_total'].mean(), base_gt),
                     'profit': df['profit'].mean()})
    deta = pd.DataFrame(rows)
    deta.to_csv(os.path.join(DATADIR, 'validacion_v5_sensibilidad_eta.csv'), index=False)
    eta1 = deta[deta['eta'] == 1.00]['gas_total_pct_vs_base'].iloc[0]
    print(f'  V.5.1 eta: gas_total_pct vs base en eta=0.90 -> '
          f"{deta[deta.eta==0.90]['gas_total_pct_vs_base'].iloc[0]:+.2f}%, "
          f'en eta=1.00 -> {eta1:+.2f}% (debe ~0)')
    results['eta'] = deta

    # V.5.2 phi
    phis = [0.01, 0.05, 0.10, 0.20, 0.30, 0.50]
    rows = []
    for ph in phis:
        df = _run_homogeneo('PHI_LOW', 'PHI_HIGH', ph, n_replicas, days)
        rows.append({'phi': ph, 'f': df['f'].mean(), 'f_std': df['f'].std(),
                     'profit': df['profit'].mean(), 'entropy': df['entropy'].mean()})
    dphi = pd.DataFrame(rows)
    dphi.to_csv(os.path.join(DATADIR, 'validacion_v5_sensibilidad_phi.csv'), index=False)
    print(f"  V.5.2 phi: f varía de {dphi['f'].min():.3f} a {dphi['f'].max():.3f} "
          f"(rango {dphi['f'].max()-dphi['f'].min():.3f}) — debe ser pequeño")
    results['phi'] = dphi

    # V.5.3 beta — se extiende a valores extremos para mostrar el colapso de la
    # exploración (fijación) fuera del rango plausible
    betas = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 7.0, 10.0, 20.0, 50.0]
    rows = []
    for b in betas:
        df = _run_homogeneo('BETA_LOW', 'BETA_HIGH', b, n_replicas, days)
        gap = pct(df['profit'].mean(), NASH_PROFIT)
        rows.append({'beta': b, 'f': df['f'].mean(), 'f_std': df['f'].std(),
                     'gap_profit_pct': gap, 'entropy': df['entropy'].mean()})
    dbeta = pd.DataFrame(rows)
    dbeta.to_csv(os.path.join(DATADIR, 'validacion_v5_sensibilidad_beta.csv'), index=False)
    print(f"  V.5.3 beta: f varía de {dbeta['f'].min():.3f} a {dbeta['f'].max():.3f} "
          f"(rango {dbeta['f'].max()-dbeta['f'].min():.3f}) — con la regla nueva debe ser "
          f"mucho menor que el 0.69->0.97 de la regla antigua")
    print(f"             entropía cae de {dbeta['entropy'].max():.3f} a {dbeta['entropy'].min():.3f} "
          f"(β alto -> fijación: colapsa la exploración, no el nivel)")
    results['beta'] = dbeta

    # ── Figuras ──
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(deta['eta'], deta['gas_total_pct_vs_base'], 'o-', color=COL_STOR)
    ax.axhline(0, color='#888', lw=0.8)
    ax.axvline(0.90, color=COL_REF, ls=':', lw=1, label='η operativo = 0.90')
    ax.set_xlabel('eficiencia η'); ax.set_ylabel('Δ gas total vs base (%)')
    ax.set_title('V.5.1 — El exceso de gas total se desvanece al crecer η (→0 en η=1)')
    ax.legend(fontsize=9); fig.tight_layout()
    _save(fig, 'validacion_v5_eta.png')

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(dphi['phi'], dphi['f'], yerr=dphi['f_std'], fmt='o-', color=COL_STOR, capsize=3)
    ax.axhline(NASH_F, color=COL_REF, ls='--', lw=1, label=f'Nash {NASH_F}')
    ax.set_xlabel('tasa de aprendizaje φ'); ax.set_ylabel(r'fracción media $\bar f$')
    ax.set_ylim(0, 1); ax.set_title('V.5.2 — φ no altera el nivel de equilibrio (afecta solo a la velocidad)')
    ax.legend(fontsize=9); fig.tight_layout()
    _save(fig, 'validacion_v5_phi.png')

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.errorbar(dbeta['beta'], dbeta['f'], yerr=dbeta['f_std'], fmt='o-', color=COL_STOR,
                capsize=3, label=r'$\bar f$ (nivel)')
    ax.axhline(NASH_F, color=COL_REF, ls='--', lw=1, label=f'Nash {NASH_F}')
    ax.set_xscale('log'); ax.set_xlabel('exploración β (escala log)')
    ax.set_ylabel(r'fracción media $\bar f$', color=COL_STOR); ax.set_ylim(0, 1)
    ax.tick_params(axis='y', labelcolor=COL_STOR)
    ax2 = ax.twinx()
    ax2.plot(dbeta['beta'], dbeta['entropy'], 's--', color=COL_BASE, label='entropía (exploración)')
    ax2.set_ylabel('entropía normalizada', color=COL_BASE); ax2.set_ylim(0, 1)
    ax2.tick_params(axis='y', labelcolor=COL_BASE); ax2.grid(False)
    ax.set_title('V.5.3 — El nivel $\\bar f$ es estable en β, pero la exploración colapsa (β alto → fijación)')
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc='center left')
    fig.tight_layout()
    _save(fig, 'validacion_v5_beta.png')

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# V.6  Robustez agregada (N con N*c = 75 constante, s escalado = 4c)
# ═══════════════════════════════════════════════════════════════════════════════
def v6_robustez_N(Ns=(2, 5, 10, 20, 30, 50), n_replicas=10, days=500, agg_supply=75.0):
    print('\n[V.6] Robustez agregada (N*c=75 constante, s=4c)')
    rows = []
    for N in Ns:
        c = agg_supply / N
        s_cap = 4.0 * c     # mantiene s/c = 10/2.5 = 4 -> batería holgada en todo N
        p = {'N': N, 'CAP_LOW': c, 'CAP_HIGH': c,
             'STOR_CAP_LOW': s_cap, 'STOR_CAP_HIGH': s_cap}
        fs, ratios = [], []
        for seed in range(n_replicas):
            _, df, _ = run_single(params=p, storage_enabled=True, days=days, seed=seed)
            sm = steady_metrics(df, n=N)
            fs.append(sm['f']); ratios.append(sm['ratio'])
        rows.append({'N': N, 'c': c, 's': s_cap,
                     'f': np.mean(fs), 'f_std': np.std(fs),
                     'ratio': np.mean(ratios), 'ratio_std': np.std(ratios)})
        print(f'  N={N:3d} (c={c:5.2f}, s={s_cap:6.2f}): f={np.mean(fs):.3f}±{np.std(fs):.3f}, '
              f'ratio={np.mean(ratios):.3f}')
    dN = pd.DataFrame(rows)
    dN.to_csv(os.path.join(DATADIR, 'validacion_v6_N.csv'), index=False)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.5))
    a1.errorbar(dN['N'], dN['f'], yerr=dN['f_std'], fmt='o-', color=COL_STOR, capsize=3)
    a1.axhline(NASH_F, color=COL_REF, ls='--', lw=1, label=f'Nash $f^N$ (N=30) = {NASH_F}')
    a1.set_xscale('log'); a1.set_xlabel('N (escala log)'); a1.set_ylabel(r'$\bar f$')
    a1.set_title('Fracción media vs N'); a1.legend(fontsize=9)
    a2.errorbar(dN['N'], dN['ratio'], yerr=dN['ratio_std'], fmt='o-', color=COL_STOR, capsize=3)
    a2.axhline(PRICETAKER_RATIO, color=COL_REF, ls=':', lw=1.2,
               label=f'precio-aceptante η = {PRICETAKER_RATIO}')
    a2.axhline(NASH_RATIO, color='#888', ls='--', lw=1, label=f'Nash (N=30) = {NASH_RATIO}')
    a2.set_xscale('log'); a2.set_xlabel('N (escala log)'); a2.set_ylabel('$P_M/P_E$')
    a2.set_title('Ratio de precios vs N: converge a η al crecer N'); a2.legend(fontsize=9)
    fig.suptitle('V.6 — Estática comparativa en N con oferta agregada N·c=75 constante', y=1.02)
    fig.tight_layout()
    _save(fig, 'validacion_v6_N.png')

    return {'tabla_N': dN}


# ═══════════════════════════════════════════════════════════════════════════════
def main():
    t0 = time.time()
    print('=' * 78)
    print('VALIDACIÓN DEL MODELO — anexo solo-GitHub')
    print('=' * 78)
    r1 = v1_reproducibilidad()
    r2 = v2_invariantes()
    r3 = v3_trazabilidad()
    r4 = v4_robustez()
    r5 = v5_sensibilidad()
    r6 = v6_robustez_N()
    dt = time.time() - t0
    print('\n' + '=' * 78)
    print(f'TODAS LAS PRUEBAS COMPLETADAS en {dt:.1f} s')
    print('=' * 78)
    return dict(v1=r1, v2=r2, v3=r3, v4=r4, v5=r5, v6=r6, segundos=dt)


if __name__ == '__main__':
    main()
