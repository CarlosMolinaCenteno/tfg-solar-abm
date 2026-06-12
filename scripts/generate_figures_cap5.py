# generate_figures_cap5.py — Figuras del Capítulo 5 (Papel de las baterías)
# TFG: Modelo de almacenamiento solar adaptativo — Carlos Molina Centeno
#
# Genera las figuras y los CSV del cap. 5 con la REGLA ELEGIDA (z-score del beneficio
# realizado, solo la fracción jugada, sin decay) — que es ya la regla por defecto de
# model.py, de modo que aquí NO hace falta monkey-patch (a diferencia de cap. 4).
#
# Parametrización INTERIOR (DEFAULT_PARAMS), seed=0 y horizonte 500 días IGUAL que
# generate_figures_cap4.py: así el escenario "con almacenamiento" coincide cifra a cifra
# con el cap. 4 (f≈0.633, beneficio≈275.2, ratio P_M/P_E≈0.874).
#
# Material de SENSIBILIDAD (η/φ/β) y ROBUSTEZ (N) NO se genera aquí: va al anexo GitHub
# (script legacy generate_figures.py).
#
# Uso:  python scripts/generate_figures_cap5.py

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from model import run_single, DEFAULT_PARAMS

# La consola de Windows (cp1252) no codifica caracteres como Δ o acentos: forzamos UTF-8.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Referencias del cap. 3 (homogéneas con cap. 4) ───────────────────────────
NASH_F = 0.639
NASH_PROFIT = 275.14
NASH_RATIO = 0.880
ETA = DEFAULT_PARAMS['ETA_LOW']   # eficiencia (0.9 homogénea)

FIGDIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
DATADIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(DATADIR, exist_ok=True)

DAYS = 500
SEED = 0
LAST = 100   # ventana estacionaria (últimos 100 días)

# Coste del gas: C0 leído de params (=0), coherente con el modelo.
C0 = DEFAULT_PARAMS['C0']
ALPHA_G = DEFAULT_PARAMS['ALPHA_G']
GAMMA_G = DEFAULT_PARAMS['GAMMA_G']

plt.rcParams.update({
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.dpi': 100,
    'savefig.bbox': 'tight',
})

COL_BASE = '#c0392b'   # rojo: sin almacenamiento
COL_STOR = '#27ae60'   # verde: con almacenamiento
COL_M = '#e67e22'      # naranja: mañana
COL_E = '#2980b9'      # azul: tarde


def _save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  guardada: {name}')


def gas_total_cost(q):
    """Coste total del gas = integral del coste marginal c0 + alpha_g q^gamma_g."""
    if q <= 0:
        return 0.0
    return C0 * q + ALPHA_G * q ** (GAMMA_G + 1) / (GAMMA_G + 1)


def daily_ratio(df):
    """Cociente diario P_M/P_E (definición del cap. 4: media de cocientes)."""
    pe = df['price_E'].clip(lower=1e-9)
    return df['price_M'] / pe


# ── Corridas ─────────────────────────────────────────────────────────────────
print(f'Generando material del cap. 5 (INTERIOR, regla elegida, seed={SEED}, {DAYS} días)...')

mb, df_base, dfa_base = run_single(storage_enabled=False, days=DAYS, seed=SEED)
ms, df_stor, dfa_stor = run_single(storage_enabled=True, days=DAYS, seed=SEED)

# CSVs
df_base.to_csv(os.path.join(DATADIR, 'baseline_model.csv'), index=False)
df_stor.to_csv(os.path.join(DATADIR, 'storage_model.csv'), index=False)
dfa_base.to_csv(os.path.join(DATADIR, 'baseline_agents.csv'), index=False)
dfa_stor.to_csv(os.path.join(DATADIR, 'storage_agents.csv'), index=False)
print('  CSVs de modelo y agentes guardados.')

# Coste total de gas por día y acumulado
for df in (df_base, df_stor):
    df['gas_cost_total'] = df.apply(
        lambda r: gas_total_cost(r['gas_M']) + gas_total_cost(r['gas_E']), axis=1)

# ── Métricas estacionarias (últimos 100 días) ────────────────────────────────
bt, st = df_base.tail(LAST), df_stor.tail(LAST)


def m(df, col):
    return df[col].mean()


metrics = {
    'pm_base': m(bt, 'price_M'), 'pm_stor': m(st, 'price_M'),
    'pe_base': m(bt, 'price_E'), 'pe_stor': m(st, 'price_E'),
    'gm_base': m(bt, 'gas_M'), 'gm_stor': m(st, 'gas_M'),
    'ge_base': m(bt, 'gas_E'), 'ge_stor': m(st, 'gas_E'),
    'prof_base': m(bt, 'avg_profit'), 'prof_stor': m(st, 'avg_profit'),
    'f_stor': m(st, 'avg_storage_fraction'),
    'ratio_base': daily_ratio(bt).mean(), 'ratio_stor': daily_ratio(st).mean(),
    'std_pm_base': bt['price_M'].std(), 'std_pm_stor': st['price_M'].std(),
    'std_pe_base': bt['price_E'].std(), 'std_pe_stor': st['price_E'].std(),
    'gas_tot_base': m(bt, 'gas_M') + m(bt, 'gas_E'),
    'gas_tot_stor': m(st, 'gas_M') + m(st, 'gas_E'),
    'cost_cum_base': df_base['gas_cost_total'].sum(),
    'cost_cum_stor': df_stor['gas_cost_total'].sum(),
}


def pct(new, old):
    return 100 * (new - old) / old if old else float('nan')


# ── Tabla 5.1 (comparación) ──────────────────────────────────────────────────
tabla = pd.DataFrame({
    'Indicador': [
        'Precio medio mañana (P_M)', 'Precio medio tarde (P_E)', 'Ratio P_M/P_E',
        'Gas medio mañana (Q_G^M)', 'Gas medio tarde (Q_G^E)', 'Gas total',
        'Beneficio medio agente', 'Fracción media almac.',
        'Desv. típ. temporal P_M', 'Desv. típ. temporal P_E',
        'Coste de gas acumulado',
    ],
    'Sin almacenamiento': [
        f"{metrics['pm_base']:.2f}", f"{metrics['pe_base']:.2f}", f"{metrics['ratio_base']:.3f}",
        f"{metrics['gm_base']:.2f}", f"{metrics['ge_base']:.2f}", f"{metrics['gas_tot_base']:.2f}",
        f"{metrics['prof_base']:.2f}", "0.00",
        f"{metrics['std_pm_base']:.2f}", f"{metrics['std_pe_base']:.2f}",
        f"{metrics['cost_cum_base']:.0f}",
    ],
    'Con almacenamiento': [
        f"{metrics['pm_stor']:.2f}", f"{metrics['pe_stor']:.2f}", f"{metrics['ratio_stor']:.3f}",
        f"{metrics['gm_stor']:.2f}", f"{metrics['ge_stor']:.2f}", f"{metrics['gas_tot_stor']:.2f}",
        f"{metrics['prof_stor']:.2f}", f"{metrics['f_stor']:.3f}",
        f"{metrics['std_pm_stor']:.2f}", f"{metrics['std_pe_stor']:.2f}",
        f"{metrics['cost_cum_stor']:.0f}",
    ],
    'Variación': [
        f"{pct(metrics['pm_stor'], metrics['pm_base']):+.1f}%",
        f"{pct(metrics['pe_stor'], metrics['pe_base']):+.1f}%", '—',
        f"{pct(metrics['gm_stor'], metrics['gm_base']):+.1f}%",
        f"{pct(metrics['ge_stor'], metrics['ge_base']):+.1f}%",
        f"{pct(metrics['gas_tot_stor'], metrics['gas_tot_base']):+.1f}%",
        f"{pct(metrics['prof_stor'], metrics['prof_base']):+.1f}%", '—', '—', '—',
        f"{pct(metrics['cost_cum_stor'], metrics['cost_cum_base']):+.1f}%",
    ],
})
tabla.to_csv(os.path.join(DATADIR, 'table_5_1_comparison.csv'), index=False)

print('\nTabla 5.1 — comparación (medias últimos 100 días):')
print(tabla.to_string(index=False))
print(f"\n  Referencias Nash: f={NASH_F}, beneficio={NASH_PROFIT}, ratio={NASH_RATIO}, eta={ETA}")


# ── Tabla 5.2: descomposición de excedentes (bienestar) ──────────────────────
# Con demanda rígida (D_M, D_E fijas), el valor bruto para el consumidor es una
# constante, de modo que el excedente total = valor fijo − coste de recursos, y el
# único recurso con coste es el gas (la solar es gratis). Por tanto, la variación del
# excedente total coincide con el coste de gas evitado. El reparto se obtiene de:
#   - Gasto del consumidor = P_M·D_M + P_E·D_E  (su excedente sube cuando el gasto baja)
#   - Excedente solar = suma de beneficios solares (coste solar ~0)
#   - Renta del productor de gas = precio·cantidad − coste total = c_G(q)·q − C_G(q)
D_M, D_E, N = DEFAULT_PARAMS['DEMAND_M'], DEFAULT_PARAMS['DEMAND_E'], DEFAULT_PARAMS['N']


def gas_marg_cost(q):
    return 0.0 if q <= 0 else C0 + ALPHA_G * q ** GAMMA_G


def gas_rent(q):
    """Renta (excedente) del productor de gas: precio·cantidad − coste total."""
    return gas_marg_cost(q) * q - gas_total_cost(q)


def _welfare(df):
    """Medias estacionarias (últimos LAST días) de los componentes de excedente."""
    d = df.tail(LAST)
    expend = (d['price_M'] * D_M + d['price_E'] * D_E).mean()      # gasto del consumidor
    solar = (d['avg_profit'] * N).mean()                           # excedente solar
    rent = (d['gas_M'].apply(gas_rent) + d['gas_E'].apply(gas_rent)).mean()
    cost = (d['gas_M'].apply(gas_total_cost) + d['gas_E'].apply(gas_total_cost)).mean()
    return expend, solar, rent, cost


exp_b, sol_b, rent_b, cost_b = _welfare(df_base)
exp_s, sol_s, rent_s, cost_s = _welfare(df_stor)

# Variación del EXCEDENTE de cada agente (con − sin almac.). Matiz de signo:
#   - consumidor y sistema: el flujo tabulado (gasto / coste de recursos) es lo que se
#     paga, así que su descenso ES una ganancia de excedente -> signo invertido.
#   - solar y gas: el flujo tabulado (ingreso / renta) es ya el propio excedente.
dCS = -(exp_s - exp_b)
dSolar = sol_s - sol_b
dGasRent = rent_s - rent_b
dTotal = -(cost_s - cost_b)   # = coste de gas evitado = ΔCS + Δsolar + ΔgasRent (identidad)

tabla_w = pd.DataFrame({
    'Componente': [
        'Consumidor (gasto en electricidad)',
        'Productores solares (ingreso = excedente)',
        'Productor de gas (renta inframarginal)',
        'Sistema (coste de generación de gas)',
    ],
    'Sin almacenamiento': [f"{exp_b:.0f}", f"{sol_b:.0f}", f"{rent_b:.0f}", f"{cost_b:.0f}"],
    'Con almacenamiento': [f"{exp_s:.0f}", f"{sol_s:.0f}", f"{rent_s:.0f}", f"{cost_s:.0f}"],
    'Δ excedente': [f"{dCS:+.0f}", f"{dSolar:+.0f}", f"{dGasRent:+.0f}", f"{dTotal:+.0f}"],
})
tabla_w.to_csv(os.path.join(DATADIR, 'table_5_2_bienestar.csv'), index=False)

print('\nTabla 5.2 — flujos y variación del excedente (medias últimos 100 días):')
print(tabla_w.to_string(index=False))
print(f"\n  comprobación: ΔCS+Δsolar+ΔgasRent = {dCS + dSolar + dGasRent:+.0f}  "
      f"?= Δexcedente total (= coste de gas evitado) = {dTotal:+.0f}")


# ── Figuras ──────────────────────────────────────────────────────────────────
d_base = df_base['day']
d_stor = df_stor['day']

# fig 5.1 — precios escenario base
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(d_base, df_base['price_M'], color=COL_M, alpha=0.85, label='$P_M$ (mañana)')
ax.plot(d_base, df_base['price_E'], color=COL_E, alpha=0.85, label='$P_E$ (tarde)')
ax.set_xlabel('día'); ax.set_ylabel('precio')
ax.set_title('Escenario base (sin almacenamiento): asimetría de precios mañana/tarde')
ax.legend(fontsize=9)
fig.tight_layout()
_save(fig, 'fig_5_1_precios_base.png')

# fig 5.2 — precios con almacenamiento (referencia: medias del escenario base)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(d_stor, df_stor['price_M'], color=COL_M, alpha=0.85, label='$P_M$ (mañana)')
ax.plot(d_stor, df_stor['price_E'], color=COL_E, alpha=0.85, label='$P_E$ (tarde)')
ax.axhline(metrics['pm_base'], color=COL_M, ls=':', lw=1, alpha=0.7, label='$\\bar P_M$ base')
ax.axhline(metrics['pe_base'], color=COL_E, ls=':', lw=1, alpha=0.7, label='$\\bar P_E$ base')
ax.set_xlabel('día'); ax.set_ylabel('precio')
ax.set_title('Con almacenamiento: los precios convergen (sube $P_M$, baja $P_E$)')
ax.legend(fontsize=9, ncol=2)
fig.tight_layout()
_save(fig, 'fig_5_2_precios_almacenamiento.png')

# fig 5.3 — uso de gas, base vs almacenamiento (redistribución)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
a1.plot(d_base, df_base['gas_M'], color=COL_M, alpha=0.85, label='gas mañana')
a1.plot(d_base, df_base['gas_E'], color=COL_E, alpha=0.85, label='gas tarde')
a1.set_title('Sin almacenamiento'); a1.set_xlabel('día'); a1.set_ylabel('producción de gas')
a1.legend(fontsize=9)
a2.plot(d_stor, df_stor['gas_M'], color=COL_M, alpha=0.85, label='gas mañana')
a2.plot(d_stor, df_stor['gas_E'], color=COL_E, alpha=0.85, label='gas tarde')
a2.set_title('Con almacenamiento'); a2.set_xlabel('día')
a2.legend(fontsize=9)
fig.suptitle('Uso de gas: el almacenamiento redistribuye respaldo de la tarde a la mañana', y=1.02)
fig.tight_layout()
_save(fig, 'fig_5_3_gas_comparacion.png')

# fig 5.4 — barras comparativas
labels = ['$P_M$', '$P_E$', 'gas M', 'gas E', 'beneficio']
base_vals = [metrics['pm_base'], metrics['pe_base'], metrics['gm_base'], metrics['ge_base'], metrics['prof_base']]
stor_vals = [metrics['pm_stor'], metrics['pe_stor'], metrics['gm_stor'], metrics['ge_stor'], metrics['prof_stor']]
x = np.arange(len(labels)); w = 0.38
fig, ax = plt.subplots(figsize=(9, 4.5))
b1 = ax.bar(x - w/2, base_vals, w, color=COL_BASE, label='sin almacenamiento')
b2 = ax.bar(x + w/2, stor_vals, w, color=COL_STOR, label='con almacenamiento')
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel('valor (medias últimos 100 días)')
ax.set_title('Comparación directa entre escenarios')
ax.legend(fontsize=9)
for bars in (b1, b2):
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=8)
fig.tight_layout()
_save(fig, 'fig_5_4_comparacion_barras.png')

# fig 5.5 — beneficio medio en el tiempo
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(d_base, df_base['avg_profit'], color=COL_BASE, alpha=0.8, label='sin almacenamiento')
ax.plot(d_stor, df_stor['avg_profit'], color=COL_STOR, alpha=0.8, label='con almacenamiento')
ax.axhline(NASH_PROFIT, color='#2c3e50', ls='--', lw=1, label=f'beneficio Nash ({NASH_PROFIT:.0f})')
ax.set_xlabel('día'); ax.set_ylabel('beneficio medio por agente')
ax.set_title('Beneficio de los productores solares: el almacenamiento alcanza el pago de Nash')
ax.legend(fontsize=9)
fig.tight_layout()
_save(fig, 'fig_5_5_beneficio_tiempo.png')

# fig 5.6 — la convexidad del coste explica el ahorro (mecanismo, estilo Jensen)
qq = np.linspace(0, 110, 400)
cc = np.array([gas_total_cost(q) for q in qq])
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(qq, cc, color='#555555', lw=1.6, label='$C_G(q)$, coste del gas en un periodo')


def _plot_escenario(qm, qe, color, name):
    cm, ce = gas_total_cost(qm), gas_total_cost(qe)
    ax.plot([qm, qe], [cm, ce], color=color, ls='--', lw=1.1, alpha=0.85)   # cuerda
    ax.scatter([qm, qe], [cm, ce], color=color, s=55, zorder=5)
    mx, my = (qm + qe) / 2, (cm + ce) / 2
    ax.scatter([mx], [my], color=color, s=110, marker='D', zorder=6,
               label=f'{name}: coste medio/periodo = {my:,.0f}')
    for q, lab in ((qm, 'mañana'), (qe, 'tarde')):
        ax.annotate(f'{lab}\n$q={q:.0f}$', (q, gas_total_cost(q)),
                    textcoords='offset points', xytext=(6, -14), fontsize=8, color=color)
    return my


_plot_escenario(metrics['gm_base'], metrics['ge_base'], COL_BASE, 'sin almac.')
_plot_escenario(metrics['gm_stor'], metrics['ge_stor'], COL_STOR, 'con almac.')
ax.set_xlabel('gas en un periodo, $q$'); ax.set_ylabel('coste del periodo, $C_G(q)$')
ax.set_title('Por qué baja el coste: la convexidad de $C_G$ penaliza concentrar el gas')
ax.legend(fontsize=8, loc='upper left')
fig.tight_layout()
_save(fig, 'fig_5_6_convexidad_coste.png')

# fig 5.7 — coste de gas acumulado (magnitud del bienestar)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(d_base, df_base['gas_cost_total'].cumsum(), color=COL_BASE, alpha=0.85, label='sin almacenamiento')
ax.plot(d_stor, df_stor['gas_cost_total'].cumsum(), color=COL_STOR, alpha=0.85, label='con almacenamiento')
ax.set_xlabel('día'); ax.set_ylabel('coste acumulado de generación de gas')
ax.set_title('Coste de gas acumulado: el ahorro del almacenamiento se acumula en el tiempo')
ax.legend(fontsize=9)
fig.tight_layout()
_save(fig, 'fig_5_7_coste_gas_acumulado.png')

print('\nListo.')
