# generate_figures.py - Generate all TFG figures
# Produces: figures 5.1-5.2, 6.1-6.8+
# Run from workspace/scripts/

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Style
plt.rcParams.update({
    'figure.figsize': (10, 4),
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.dpi': 100,
    'savefig.bbox': 'tight',
    'savefig.dpi': 100,
})

from model import run_single, run_batch, MarketModel, DEFAULT_PARAMS

FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DAYS = 200
SEED = 42


def savefig(name):
    path = os.path.join(FIGURES_DIR, f'{name}.png')
    plt.savefig(path)
    plt.close()
    print(f'  Saved {path}')


# ═══════════════════════════════════════════════════════════════════════════
# Run the two core scenarios
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("Running core scenarios...")
print("=" * 60)

print("  Baseline (no storage)...")
model_base, df_base, df_agents_base = run_single(
    storage_enabled=False, days=DAYS, seed=SEED
)

print("  With storage and learning...")
model_stor, df_stor, df_agents_stor = run_single(
    storage_enabled=True, days=DAYS, seed=SEED
)

# Save CSVs
df_base.to_csv(os.path.join(DATA_DIR, 'baseline_model.csv'), index=False)
df_stor.to_csv(os.path.join(DATA_DIR, 'storage_model.csv'), index=False)
df_agents_base.to_csv(os.path.join(DATA_DIR, 'baseline_agents.csv'), index=False)
df_agents_stor.to_csv(os.path.join(DATA_DIR, 'storage_agents.csv'), index=False)
print("  CSVs saved.")


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 5 - Validation figures
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("Chapter 5 - Validation figures")
print("=" * 60)

# Figure 5.1 - Price evolution (with storage, for validation)
fig, ax = plt.subplots()
ax.plot(df_stor['day'], df_stor['price_M'], label='Precio mañana ($P_M$)', alpha=0.8)
ax.plot(df_stor['day'], df_stor['price_E'], label='Precio tarde ($P_E$)', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Precio')
ax.set_title('Figura 5.1 — Evolución de precios de mercado')
ax.legend()
savefig('fig_5_1_precios_validacion')

# Figure 5.2 - Average storage fraction evolution (with storage)
fig, ax = plt.subplots()
ax.plot(df_stor['day'], df_stor['avg_storage_fraction'], color='green', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Fracción media de almacenamiento')
ax.set_title('Figura 5.2 — Evolución de la fracción media de almacenamiento')
ax.set_ylim(0, 1)
savefig('fig_5_2_fraccion_almacenamiento_validacion')


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 6 - Scenario figures
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("Chapter 6 - Scenario figures")
print("=" * 60)

# ── 6.1 Baseline scenario ──────────────────────────────────────────────

# Figure 6.1 - Baseline prices
fig, ax = plt.subplots()
ax.plot(df_base['day'], df_base['price_M'], label='Precio mañana ($P_M$)', alpha=0.8)
ax.plot(df_base['day'], df_base['price_E'], label='Precio tarde ($P_E$)', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Precio')
ax.set_title('Figura 6.1 — Precios de mercado (escenario sin almacenamiento)')
ax.legend()
savefig('fig_6_1_precios_baseline')

# Figure 6.2 - Baseline gas usage
fig, ax = plt.subplots()
ax.plot(df_base['day'], df_base['gas_M'], label='Gas mañana', alpha=0.8)
ax.plot(df_base['day'], df_base['gas_E'], label='Gas tarde', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Producción de gas')
ax.set_title('Figura 6.2 — Uso de generación de gas (sin almacenamiento)')
ax.legend()
savefig('fig_6_2_gas_baseline')

# ── 6.2 Storage scenario ───────────────────────────────────────────────

# Figure 6.3 - Storage fraction evolution (mean + dispersion + sample agents)
# Compute per-day statistics from agent-level data
agent_choice_by_day = df_agents_stor.groupby('day')['agent_choice'].agg(['mean', 'std', 'min', 'max'])
agent_choice_by_day = agent_choice_by_day.reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
days = agent_choice_by_day['day']

# Shaded band: min-max range
ax.fill_between(days, agent_choice_by_day['min'], agent_choice_by_day['max'],
                alpha=0.15, color='green', label='Rango (mín–máx)')
# Shaded band: mean ± 1 std
ax.fill_between(days,
                agent_choice_by_day['mean'] - agent_choice_by_day['std'],
                agent_choice_by_day['mean'] + agent_choice_by_day['std'],
                alpha=0.3, color='green', label='Media ± 1 desv. típ.')
# Mean line
ax.plot(days, agent_choice_by_day['mean'], color='darkgreen', linewidth=2, label='Media')

# Sample individual agent trajectories
sample_agents = df_agents_stor['agent_id'].unique()[:5]
for aid in sample_agents:
    agent_data = df_agents_stor[df_agents_stor['agent_id'] == aid]
    ax.plot(agent_data['day'], agent_data['agent_choice'], alpha=0.3, linewidth=0.7)

ax.set_xlabel('Día')
ax.set_ylabel('Fracción de almacenamiento')
ax.set_title('Figura 6.3 — Evolución de las decisiones de almacenamiento')
ax.set_ylim(-0.05, 1.05)
ax.legend(loc='upper right', fontsize=9)
savefig('fig_6_3_fraccion_almacenamiento')

# Figure 6.4 - Storage scenario prices
fig, ax = plt.subplots()
ax.plot(df_stor['day'], df_stor['price_M'], label='Precio mañana ($P_M$)', alpha=0.8)
ax.plot(df_stor['day'], df_stor['price_E'], label='Precio tarde ($P_E$)', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Precio')
ax.set_title('Figura 6.4 — Precios de mercado (con almacenamiento)')
ax.legend()
savefig('fig_6_4_precios_storage')

# Figure 6.5 - Storage scenario gas usage
fig, ax = plt.subplots()
ax.plot(df_stor['day'], df_stor['gas_M'], label='Gas mañana', alpha=0.8)
ax.plot(df_stor['day'], df_stor['gas_E'], label='Gas tarde', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Producción de gas')
ax.set_title('Figura 6.5 — Uso de generación de gas (con almacenamiento)')
ax.legend()
savefig('fig_6_5_gas_storage')

# ── 6.3 Comparison ─────────────────────────────────────────────────────

# Table 6.1 - Summary comparison
comparison = pd.DataFrame({
    'Indicador': [
        'Precio medio mañana', 'Precio medio tarde',
        'Gas medio mañana', 'Gas medio tarde',
        'Beneficio medio agentes', 'Fracción media almac. (final)',
        'Desv. típ. precio mañana', 'Desv. típ. precio tarde',
    ],
    'Sin almacenamiento': [
        f"{df_base['price_M'].mean():.2f}",
        f"{df_base['price_E'].mean():.2f}",
        f"{df_base['gas_M'].mean():.2f}",
        f"{df_base['gas_E'].mean():.2f}",
        f"{df_base['avg_profit'].mean():.2f}",
        "0.00",
        f"{df_base['price_M'].std():.2f}",
        f"{df_base['price_E'].std():.2f}",
    ],
    'Con almacenamiento': [
        f"{df_stor['price_M'].mean():.2f}",
        f"{df_stor['price_E'].mean():.2f}",
        f"{df_stor['gas_M'].mean():.2f}",
        f"{df_stor['gas_E'].mean():.2f}",
        f"{df_stor['avg_profit'].mean():.2f}",
        f"{df_stor['avg_storage_fraction'].iloc[-1]:.2f}",
        f"{df_stor['price_M'].std():.2f}",
        f"{df_stor['price_E'].std():.2f}",
    ]
})
comparison.to_csv(os.path.join(DATA_DIR, 'table_6_1_comparison.csv'), index=False)
print(f"\n  Table 6.1:")
print(comparison.to_string(index=False))

# Figure 6.6 - Bar chart comparison
labels = ['Precio M', 'Precio E', 'Gas M', 'Gas E', 'Beneficio']
base_vals = [
    df_base['price_M'].mean(), df_base['price_E'].mean(),
    df_base['gas_M'].mean(), df_base['gas_E'].mean(),
    df_base['avg_profit'].mean()
]
stor_vals = [
    df_stor['price_M'].mean(), df_stor['price_E'].mean(),
    df_stor['gas_M'].mean(), df_stor['gas_E'].mean(),
    df_stor['avg_profit'].mean()
]

x = np.arange(len(labels))
width = 0.35
fig, ax = plt.subplots(figsize=(10, 5))
bars1 = ax.bar(x - width/2, base_vals, width, label='Sin almacenamiento', color='#d9534f')
bars2 = ax.bar(x + width/2, stor_vals, width, label='Con almacenamiento', color='#5cb85c')
ax.set_ylabel('Valor')
ax.set_title('Figura 6.6 — Comparación entre escenarios')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
# Add value labels on bars
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
            f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
            f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
savefig('fig_6_6_comparacion_barras')


# ═══════════════════════════════════════════════════════════════════════════
# 6.4 Sensitivity analysis
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("6.4 - Sensitivity analysis")
print("=" * 60)

N_REPLICAS_SENS = 5

# ── 6.4.1 Sensitivity to eta (battery efficiency) ──────────────────────

print("  Sensitivity to eta...")
eta_values = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
eta_results = []
for eta in eta_values:
    for rep in range(N_REPLICAS_SENS):
        params = {**DEFAULT_PARAMS, 'ETA_LOW': eta, 'ETA_HIGH': eta}
        model = MarketModel(params=params, storage_enabled=True, seed=rep)
        model.run(days=DAYS)
        df = model.get_model_data()
        eta_results.append({
            'eta': eta, 'replica': rep,
            'mean_gas_total': df['gas_M'].mean() + df['gas_E'].mean(),
            'mean_gas_M': df['gas_M'].mean(),
            'mean_gas_E': df['gas_E'].mean(),
            'mean_price_E': df['price_E'].mean(),
            'final_storage_frac': df['avg_storage_fraction'].iloc[-1],
        })

df_eta = pd.DataFrame(eta_results)
df_eta_agg = df_eta.groupby('eta').agg(
    gas_total_mean=('mean_gas_total', 'mean'),
    gas_total_std=('mean_gas_total', 'std'),
    storage_frac_mean=('final_storage_frac', 'mean'),
).reset_index()

fig, ax = plt.subplots()
ax.errorbar(df_eta_agg['eta'], df_eta_agg['gas_total_mean'],
            yerr=df_eta_agg['gas_total_std'], fmt='o-', capsize=4, color='darkred')
ax.set_xlabel('Eficiencia de la batería ($\\eta$)')
ax.set_ylabel('Uso total medio de gas')
ax.set_title('Figura 6.7 — Uso total de gas vs. eficiencia de la batería')
savefig('fig_6_7_sensibilidad_eta')

df_eta.to_csv(os.path.join(DATA_DIR, 'sensitivity_eta.csv'), index=False)

# ── 6.4.2 Sensitivity to phi (learning intensity) ──────────────────────

def _convergence_day(series, window=20, threshold=0.02):
    """Estimate convergence day: first day where rolling std < threshold."""
    if len(series) < window:
        return len(series)
    rolling_std = pd.Series(series).rolling(window).std()
    converged = rolling_std < threshold
    if converged.any():
        first = converged.idxmax()
        return first if converged.iloc[first] else len(series)
    return len(series)

print("  Sensitivity to phi...")
phi_values = [0.01, 0.05, 0.10, 0.20, 0.30, 0.50]
phi_results_ts = {}  # time series per phi
phi_results = []
for phi in phi_values:
    for rep in range(N_REPLICAS_SENS):
        params = {**DEFAULT_PARAMS, 'PHI_LOW': phi, 'PHI_HIGH': phi}
        model = MarketModel(params=params, storage_enabled=True, seed=rep)
        model.run(days=DAYS)
        df = model.get_model_data()

        if rep == 0:
            phi_results_ts[phi] = df['avg_storage_fraction'].values.copy()

        phi_results.append({
            'phi': phi, 'replica': rep,
            'final_storage_frac': df['avg_storage_fraction'].iloc[-1],
            'convergence_day': _convergence_day(df['avg_storage_fraction'].values),
        })

fig, ax = plt.subplots()
days_range = np.arange(1, DAYS + 1)
for phi in phi_values:
    ax.plot(days_range, phi_results_ts[phi], label=f'$\\phi = {phi}$', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Fracción media de almacenamiento')
ax.set_title('Figura 6.8 — Evolución de la fracción de almacenamiento según $\\phi$')
ax.legend(fontsize=9)
ax.set_ylim(0, 1)
savefig('fig_6_8_sensibilidad_phi')

df_phi = pd.DataFrame(phi_results)
df_phi.to_csv(os.path.join(DATA_DIR, 'sensitivity_phi.csv'), index=False)

# ── 6.4.3 Sensitivity to beta (exploration) ────────────────────────────

print("  Sensitivity to beta...")
beta_values = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
beta_results_ts = {}
beta_results = []
for beta in beta_values:
    for rep in range(N_REPLICAS_SENS):
        params = {**DEFAULT_PARAMS, 'BETA_LOW': beta, 'BETA_HIGH': beta}
        model = MarketModel(params=params, storage_enabled=True, seed=rep)
        model.run(days=DAYS)
        df = model.get_model_data()

        if rep == 0:
            beta_results_ts[beta] = df['avg_storage_fraction'].values.copy()

        beta_results.append({
            'beta': beta, 'replica': rep,
            'final_storage_frac': df['avg_storage_fraction'].iloc[-1],
            'mean_price_E': df['price_E'].mean(),
            'convergence_day': _convergence_day(df['avg_storage_fraction'].values),
        })

fig, ax = plt.subplots()
for beta in beta_values:
    ax.plot(days_range, beta_results_ts[beta], label=f'$\\beta = {beta}$', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Fracción media de almacenamiento')
ax.set_title('Figura 6.9 — Evolución de la fracción de almacenamiento según $\\beta$')
ax.legend(fontsize=9)
ax.set_ylim(0, 1)
savefig('fig_6_9_sensibilidad_beta')

df_beta = pd.DataFrame(beta_results)
df_beta.to_csv(os.path.join(DATA_DIR, 'sensitivity_beta.csv'), index=False)


# ═══════════════════════════════════════════════════════════════════════════
# 6.5 Robustness
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("6.5 - Robustness analysis")
print("=" * 60)

# Vary N agents and seeds
print("  Robustness: varying N and seeds...")
N_values = [10, 20, 30, 50, 100]
N_REPLICAS_ROB = 10
robustness_results = []
for n_agents in N_values:
    for rep in range(N_REPLICAS_ROB):
        params = {**DEFAULT_PARAMS, 'N': n_agents}
        model = MarketModel(params=params, storage_enabled=True, seed=rep * 100 + n_agents)
        model.run(days=DAYS)
        df = model.get_model_data()
        robustness_results.append({
            'N': n_agents, 'seed': rep,
            'mean_price_M': df['price_M'].mean(),
            'mean_price_E': df['price_E'].mean(),
            'mean_gas_total': df['gas_M'].mean() + df['gas_E'].mean(),
            'final_storage_frac': df['avg_storage_fraction'].iloc[-1],
            'mean_profit': df['avg_profit'].mean(),
        })

df_rob = pd.DataFrame(robustness_results)
df_rob_agg = df_rob.groupby('N').agg(
    price_E_mean=('mean_price_E', 'mean'),
    price_E_std=('mean_price_E', 'std'),
    storage_frac_mean=('final_storage_frac', 'mean'),
    storage_frac_std=('final_storage_frac', 'std'),
).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

ax1.errorbar(df_rob_agg['N'], df_rob_agg['price_E_mean'],
             yerr=df_rob_agg['price_E_std'], fmt='s-', capsize=4, color='steelblue')
ax1.set_xlabel('Número de agentes ($N$)')
ax1.set_ylabel('Precio medio tarde ($P_E$)')
ax1.set_title('Precio de tarde vs. $N$')

ax2.errorbar(df_rob_agg['N'], df_rob_agg['storage_frac_mean'],
             yerr=df_rob_agg['storage_frac_std'], fmt='s-', capsize=4, color='green')
ax2.set_xlabel('Número de agentes ($N$)')
ax2.set_ylabel('Fracción media de almac. (final)')
ax2.set_title('Fracción de almacenamiento vs. $N$')

plt.suptitle('Figura 6.10 — Robustez del comportamiento agregado', y=1.02)
plt.tight_layout()
savefig('fig_6_10_robustez')

df_rob.to_csv(os.path.join(DATA_DIR, 'robustness.csv'), index=False)


# ═══════════════════════════════════════════════════════════════════════════
# Additional: Agent-level heterogeneity (for Ch. 7)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("Additional figures for Chapter 7")
print("=" * 60)

# Distribution of agent choices at end of simulation
last_day_agents = df_agents_stor[df_agents_stor['day'] == DAYS]
fig, ax = plt.subplots()
ax.hist(last_day_agents['agent_choice'], bins=11, range=(0, 1),
        edgecolor='black', alpha=0.7, color='steelblue')
ax.set_xlabel('Fracción de almacenamiento elegida')
ax.set_ylabel('Número de agentes')
ax.set_title('Distribución de decisiones de almacenamiento (día final)')
savefig('fig_7_distribucion_decisiones')

# Profit comparison over time
fig, ax = plt.subplots()
ax.plot(df_base['day'], df_base['avg_profit'], label='Sin almacenamiento', alpha=0.7)
ax.plot(df_stor['day'], df_stor['avg_profit'], label='Con almacenamiento', alpha=0.7)
ax.set_xlabel('Día')
ax.set_ylabel('Beneficio medio')
ax.set_title('Evolución del beneficio medio por escenario')
ax.legend()
savefig('fig_7_beneficio_comparacion')

# Total system cost (gas cost as proxy for welfare)
# Gas cost = integral of marginal cost from 0 to q
def gas_total_cost(q, c0=10.0, alpha_g=0.5, gamma_g=1.3):
    if q <= 0:
        return 0.0
    return c0 * q + alpha_g * q**(gamma_g + 1) / (gamma_g + 1)

df_base['gas_cost_total'] = df_base.apply(
    lambda r: gas_total_cost(r['gas_M']) + gas_total_cost(r['gas_E']), axis=1)
df_stor['gas_cost_total'] = df_stor.apply(
    lambda r: gas_total_cost(r['gas_M']) + gas_total_cost(r['gas_E']), axis=1)

fig, ax = plt.subplots()
ax.plot(df_base['day'], df_base['gas_cost_total'].cumsum(), label='Sin almacenamiento', alpha=0.8)
ax.plot(df_stor['day'], df_stor['gas_cost_total'].cumsum(), label='Con almacenamiento', alpha=0.8)
ax.set_xlabel('Día')
ax.set_ylabel('Coste total acumulado del gas')
ax.set_title('Coste acumulado de generación de gas')
ax.legend()
savefig('fig_7_coste_gas_acumulado')


print("\n" + "=" * 60)
print("ALL FIGURES GENERATED SUCCESSFULLY")
print("=" * 60)
