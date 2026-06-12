# generate_figures_cap4.py — Figuras del Capítulo 4 (Aprendizaje de los agentes)
# TFG: Modelo de almacenamiento solar adaptativo — Carlos Molina Centeno
#
# Genera las figuras del cap. 4 reproduciendo las reglas de aprendizaje del banco de
# pruebas por monkey-patch sobre model.py (que NO se modifica para esto), con la
# parametrización INTERIOR (DEFAULT_PARAMS) y beta heterogéneo en [2,3] para todas las
# reglas (comparación manzanas-con-manzanas).
#
# Referencias homogéneas (de cap. 3 / banco de pruebas §2):
#   cártel f*=0.475 | Nash f^N=0.639 | beneficio Nash/agente=275.14 | ratio P_M/P_E Nash=0.880
#
# Uso:  python scripts/generate_figures_cap4.py

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import model as M
from model import MarketModel, DEFAULT_PARAMS, stable_softmax

# ── Referencias del cap. 3 ───────────────────────────────────────────────────
CARTEL_F = 0.475
NASH_F = 0.639
NASH_PROFIT = 275.14      # beneficio por agente en el Nash homogéneo
NASH_RATIO = 0.880        # P_M / P_E en el Nash homogéneo

FIGDIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
DAYS = 500
SEED = 0


# ── Definición de las reglas (idénticas al banco §5) ─────────────────────────
def _pi_all(agent):
    m = agent.model
    res = {}
    for f in agent.fractions:
        stored = min(agent.storage_capacity, agent.eta * f * agent.qM_raw)
        res[f] = m.price_M * (1 - f) * agent.qM_raw + m.price_E * (agent.qE_raw + stored)
    return res


def regla_cf_raw(self, profit):
    self.profit = profit
    if not self.storage_enabled:
        return
    for f, pi_f in _pi_all(self).items():
        self.attract[f] = (1 - self.phi) * self.attract[f] + self.phi * pi_f


def regla_cf_zscore(self, profit):
    self.profit = profit
    if not self.storage_enabled:
        return
    pi = _pi_all(self)
    arr = np.array(list(pi.values()))
    mean, std = arr.mean(), arr.std()
    if std < 1e-8:
        return
    for f, pi_f in pi.items():
        self.attract[f] = (1 - self.phi) * self.attract[f] + self.phi * (pi_f - mean) / std


def regla_zscore_elegida(self, profit):
    self.profit = profit
    if not self.storage_enabled:
        return
    pi = _pi_all(self)
    arr = np.array(list(pi.values()))
    mean, std = arr.mean(), arr.std()
    if std < 1e-8:
        return
    z = (profit - mean) / std
    f = self.last_choice
    self.attract[f] = (1 - self.phi) * self.attract[f] + self.phi * z


def make_regla_ewa(delta=0.5, rho=0.9, phi=0.95):
    def rule(self, profit):
        self.profit = profit
        if not self.storage_enabled:
            return
        if not hasattr(self, '_ewa_N'):
            self._ewa_N = 1.0
        N_old = self._ewa_N
        N_new = rho * N_old + 1.0
        for f, pi_f in _pi_all(self).items():
            I_f = 1.0 if abs(f - self.last_choice) < 1e-9 else 0.0
            w = delta + (1 - delta) * I_f
            self.attract[f] = (phi * N_old * self.attract[f] + w * pi_f) / N_new
        self._ewa_N = N_new
    return rule


def make_regla_ewa_zscore(delta=0.5, rho=0.9, phi=0.95):
    def rule(self, profit):
        self.profit = profit
        if not self.storage_enabled:
            return
        pi = _pi_all(self)
        arr = np.array(list(pi.values()))
        mean, std = arr.mean(), arr.std()
        if std < 1e-8:
            return
        if not hasattr(self, '_ewa_zs_N'):
            self._ewa_zs_N = 1.0
        N_old = self._ewa_zs_N
        N_new = rho * N_old + 1.0
        for f, pi_f in pi.items():
            z = (pi_f - mean) / std
            I_f = 1.0 if abs(f - self.last_choice) < 1e-9 else 0.0
            w = delta + (1 - delta) * I_f
            self.attract[f] = (phi * N_old * self.attract[f] + w * z) / N_new
        self._ewa_zs_N = N_new
    return rule


# ── Runner: ejecuta una regla y recoge trayectorias ──────────────────────────
def run_rule(rule_fn, seed=SEED, days=DAYS, rep_agent=0, params=None):
    """Corre el modelo con `rule_fn` (monkey-patch) y devuelve trayectorias diarias.
    `params` permite sobreescribir DEFAULT_PARAMS (p. ej. beta) para una regla concreta."""
    M.SolarAgent.update_learning = rule_fn
    mdl = MarketModel(params=params, storage_enabled=True, seed=seed)
    fractions = mdl.agents[0].fractions
    f_mean, f_std_intra, profit_mean, ratio = [], [], [], []
    attract_rep, prob_rep = [], []   # del agente representativo
    prob_pop = []                    # perfil de probabilidad promediado sobre la poblacion
    entropy_pop = []                 # entropia normalizada media sobre la poblacion (por dia)
    for _ in range(days):
        mdl.step_day()
        choices = np.array([a.last_choice for a in mdl.agents])
        f_mean.append(choices.mean())
        f_std_intra.append(choices.std())
        profit_mean.append(mdl.avg_profit)
        pe = mdl.price_E if mdl.price_E > 1e-9 else 1e-9
        ratio.append(mdl.price_M / pe)
        a = mdl.agents[rep_agent]
        att = np.array([a.attract[f] for f in fractions])
        attract_rep.append(att.copy())
        prob_rep.append(stable_softmax(att, a.beta))
        pp = np.zeros(len(fractions))
        H_sum = 0.0
        for ag in mdl.agents:
            p_ag = stable_softmax(np.array([ag.attract[f] for f in fractions]), ag.beta)
            pp += p_ag
            pc = np.clip(p_ag, 1e-12, 1.0)
            H_sum += float(-(pc * np.log(pc)).sum())
        prob_pop.append(pp / len(mdl.agents))
        entropy_pop.append(H_sum / len(mdl.agents) / np.log(len(fractions)))
    return {
        'fractions': np.array(fractions),
        'f_mean': np.array(f_mean),
        'f_std_intra': np.array(f_std_intra),
        'profit_mean': np.array(profit_mean),
        'ratio': np.array(ratio),
        'attract_rep': np.array(attract_rep),   # (days, n_frac)
        'prob_rep': np.array(prob_rep),
        'prob_pop': np.array(prob_pop),          # (days, n_frac)
        'entropy_pop': np.array(entropy_pop),    # (days,) entropia normalizada media poblacional
    }


def summary(res, last=100):
    last_f = res['f_mean'][-last:]
    daily = res['f_mean']
    return {
        'f_media': last_f.mean(),
        'f_std_temporal': last_f.std(),
        'f_std_intra': float(np.mean(res['f_std_intra'][-last:])),
        'profit': res['profit_mean'][-last:].mean(),
        'gap_profit_pct': 100 * (NASH_PROFIT - res['profit_mean'][-last:].mean()) / NASH_PROFIT,
        'ratio': res['ratio'][-last:].mean(),
        'extremos_pct': 100 * np.mean((daily < 0.15) | (daily > 0.95)),
        'entropia_norm': float(np.mean(res['entropy_pop'][-last:])),
    }


def _entropia(probs):
    p = np.clip(probs, 1e-12, 1.0)
    H = -(p * np.log(p)).sum(axis=1)
    return float((H / np.log(probs.shape[1])).mean())


# ── Figuras ──────────────────────────────────────────────────────────────────
def fig_ciclo_cfraw(res):
    fig, ax = plt.subplots(figsize=(8, 4))
    d = np.arange(1, len(res['f_mean']) + 1)
    n = 100
    ax.plot(d[:n], res['f_mean'][:n], color='#c0392b', lw=1.2, marker='o', ms=3)
    ax.axhline(NASH_F, color='#2c3e50', ls='--', lw=1, label=f'Nash $f^N$={NASH_F}')
    ax.axhline(CARTEL_F, color='#7f8c8d', ls=':', lw=1, label=f'Cártel $f^*$={CARTEL_F}')
    ax.set_xlabel('día'); ax.set_ylabel('fracción media $\\bar{f}(t)$')
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(r'Contrafactual raw: ciclo entre $f \approx 1$ y valores bajos (primeros 100 días)')
    ax.legend(loc='center right', fontsize=8)
    fig.tight_layout()
    _save(fig, 'fig_4_2_1_ciclo_cfraw.png')


def fig_convergencia(res, fname, title):
    """Figura f_media ± banda intradía, 500 días, con referencias Nash/cártel.
    Mismo estilo para §4.2.2 (z-score todas) y §4.2.3 (z-score elegida): la única
    diferencia visible debe ser la anchura de la banda (la dispersión)."""
    fig, ax = plt.subplots(figsize=(8, 4))
    d = np.arange(1, len(res['f_mean']) + 1)
    ax.plot(d, res['f_mean'], color='#27ae60', lw=1.1, label='$\\bar{f}(t)$')
    ax.fill_between(d, res['f_mean'] - res['f_std_intra'], res['f_mean'] + res['f_std_intra'],
                    color='#27ae60', alpha=0.18, label='$\\pm$ std intradía')
    ax.axhline(NASH_F, color='#2c3e50', ls='--', lw=1, label=f'Nash $f^N$={NASH_F}')
    ax.axhline(CARTEL_F, color='#7f8c8d', ls=':', lw=1, label=f'Cártel $f^*$={CARTEL_F}')
    ax.set_xlabel('día'); ax.set_ylabel('fracción media $\\bar{f}(t)$')
    ax.set_ylim(0, 1.0)
    ax.set_title(title)
    ax.legend(loc='lower right', fontsize=8, ncol=2)
    fig.tight_layout()
    _save(fig, fname)


def fig_cross_rule(metrics):
    # Orden agrupado por alcance: actualizan-todas (con las dos betas de cf_raw) | solo-elegida
    names = ['cf_raw', 'cf_raw_b02', 'cf_zscore', 'ewa_zscore', 'zscore_elegida']
    names = [n for n in names if n in metrics]
    labels = {'cf_raw': 'cf raw\n$\\beta\\in[2,3]$', 'cf_raw_b02': 'cf raw\n$\\beta=0.2$',
              'cf_zscore': 'z-score\ntodas', 'zscore_elegida': 'z-score\nelegida',
              'ewa_delta': 'EWA $\\delta$', 'ewa_zscore': 'EWA\nz-score'}
    x = np.arange(len(names))
    gap = [metrics[n]['gap_profit_pct'] for n in names]
    fmed = [metrics[n]['f_media'] for n in names]
    fstd = [metrics[n]['f_std_temporal'] for n in names]
    colors = ['#c0392b' if abs(g) > 2 else '#27ae60' for g in gap]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.bar(x, gap, color=colors)
    a1.axhline(0, color='k', lw=0.6)
    a1.set_xticks(x); a1.set_xticklabels([labels[n] for n in names], fontsize=8)
    a1.set_ylabel('gap de beneficio vs Nash (%)')
    a1.set_title('Pérdida de beneficio respecto al Nash')
    a2.errorbar(x, fmed, yerr=fstd, fmt='o', color='#2c3e50', capsize=4, ms=6)
    a2.axhline(NASH_F, color='#2c3e50', ls='--', lw=1, label=f'Nash {NASH_F}')
    a2.axhline(CARTEL_F, color='#7f8c8d', ls=':', lw=1, label=f'Cártel {CARTEL_F}')
    a2.set_xticks(x); a2.set_xticklabels([labels[n] for n in names], fontsize=8)
    a2.set_ylabel('$\\bar{f}$ (últimos 100 días) $\\pm$ std temporal')
    a2.set_ylim(0, 1.0)
    a2.set_title('Fracción media: la media engaña sin la dispersión')
    a2.legend(fontsize=8)
    fig.tight_layout()
    _save(fig, 'fig_4_3_cross_rule.png')


def fig_perfil_probabilidades(res_cfz, res_zel):
    """Perfil de probabilidad de elección por fracción (media poblacional, cola 100 días):
    z-score-todas (moda en la esquina f=1) frente a z-score-elegida (moda interior)."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fr = res_zel['fractions']
    p_cfz = res_cfz['prob_pop'][-100:].mean(axis=0)
    p_zel = res_zel['prob_pop'][-100:].mean(axis=0)
    ax.plot(fr, p_cfz, 'o-', color='#2980b9', lw=1.4, label='$z$-score (todas las fracciones)')
    ax.plot(fr, p_zel, 's-', color='#27ae60', lw=1.4, label='$z$-score (solo la elegida)')
    ax.axhline(1.0 / len(fr), color='gray', ls=':', lw=0.9, label='uniforme ($1/11$)')
    ax.axvline(NASH_F, color='#2c3e50', ls='--', lw=1, label=f'Nash $f^N$={NASH_F}')
    ax.set_xlabel('fracción de almacenamiento $f$')
    ax.set_ylabel('probabilidad media de elección')
    ax.set_title('Perfil de elección: esquina (actualiza todas) vs. interior (solo elegida)')
    ax.legend(fontsize=8)
    fig.tight_layout()
    _save(fig, 'fig_4_2_3_perfil_probabilidades.png')


def _save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  guardada: {name}')


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print('Generando figuras del cap. 4 (params INTERIOR, beta in [2,3], seed=%d, %d días)...' % (SEED, DAYS))
    rules = {
        'cf_raw': regla_cf_raw,
        'cf_zscore': regla_cf_zscore,
        'zscore_elegida': regla_zscore_elegida,
        'ewa_delta': make_regla_ewa(delta=0.5, rho=0.9, phi=0.95),
        'ewa_zscore': make_regla_ewa_zscore(delta=0.5, rho=0.9, phi=0.95),
    }
    res = {name: run_rule(fn) for name, fn in rules.items()}
    # cf_raw a su mejor beta (~0.2): sin colapso, comparable a las demas (fairness)
    res['cf_raw_b02'] = run_rule(regla_cf_raw,
                                 params={**DEFAULT_PARAMS, 'BETA_LOW': 0.2, 'BETA_HIGH': 0.2})
    metrics = {name: summary(r) for name, r in res.items()}

    print('\nMétricas (últimos 100 días):')
    hdr = f"  {'regla':16s} {'f_media':>8s} {'std_temp':>9s} {'std_intra':>10s} {'gap%':>7s} {'ratio':>7s} {'extr%':>6s} {'entropía':>9s}"
    print(hdr)
    _order = ['cf_raw', 'cf_raw_b02', 'cf_zscore', 'ewa_delta', 'ewa_zscore', 'zscore_elegida']
    for name in _order:
        m = metrics[name]
        print(f"  {name:16s} {m['f_media']:8.3f} {m['f_std_temporal']:9.3f} {m['f_std_intra']:10.3f} "
              f"{m['gap_profit_pct']:7.2f} {m['ratio']:7.3f} {m['extremos_pct']:6.0f} {m['entropia_norm']:9.3f}")
    print(f'\n  (Nash: f={NASH_F}, beneficio={NASH_PROFIT}, ratio={NASH_RATIO})\n')

    fig_ciclo_cfraw(res['cf_raw'])
    fig_convergencia(res['cf_zscore'], 'fig_4_2_2_dispersion_zscore_todas.png',
                     'Z-score (todas las fracciones): convergencia con mayor dispersión')
    fig_convergencia(res['zscore_elegida'], 'fig_4_2_3_convergencia_zscore.png',
                     'Z-score solo elegida: convergencia a la banda del Nash')
    fig_perfil_probabilidades(res['cf_zscore'], res['zscore_elegida'])
    fig_cross_rule(metrics)
    print('\nListo.')


if __name__ == '__main__':
    main()
