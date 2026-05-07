# model.py - Adaptive Solar Storage ABM (Mesa 3.x)
# TFG: Modelo de almacenamiento solar adaptativo
# Autor: Carlos Molina Centeno

import random
import math
import numpy as np
from mesa import Agent, Model
from mesa.datacollection import DataCollector


# ── Default parameters ──────────────────────────────────────────────────────

DEFAULT_PARAMS = dict(
    N=30,
    DAYS=200,
    STORAGE_GRAN=10,
    ALPHA_M=0.7,
    ALPHA_E=0.3,
    DEMAND_M=60.0,
    DEMAND_E=120.0,
    C0=10.0,
    ALPHA_G=0.5,
    GAMMA_G=1.3,
    WEATHER_VAR=0, #se ha dejado a 0 para hacer pruebas
    CAP_LOW=0.8,
    CAP_HIGH=1.2,
    STOR_CAP_LOW=0.5,
    STOR_CAP_HIGH=2.0,
    ETA_LOW=0.9,
    ETA_HIGH=0.9, #se han dejado ambas iguales para que el almacenamiento sea igual de eficiente para todos los agentes, pero se pueden variar para estudiar el impacto de eficiencia heterogénea en los resultados
    PHI_LOW=0.05,
    PHI_HIGH=0.3,
    BETA_LOW=1.0,
    BETA_HIGH=5.0,
)


# ── Utility functions ───────────────────────────────────────────────────────

def gas_marginal_cost(q, c0=10.0, alpha_g=0.5, gamma_g=1.3):
    """Coste marginal del gas: c0 + alpha_g * q^gamma_g."""
    if q <= 0:
        return 0.0
    return c0 + alpha_g * (q ** gamma_g)


def stable_softmax(values: np.ndarray, beta: float) -> np.ndarray:
    """Softmax numericamente estable."""
    scaled = beta * values
    scaled = scaled - np.max(scaled)
    exps = np.exp(scaled)
    return exps / exps.sum()

# ── Agent ───────────────────────────────────────────────────────────────────

class SolarAgent(Agent):
    def __init__(self, model, params, storage_enabled=True):
        super().__init__(model)
        p = params

        # Technological parameters
        self.capacity = random.uniform(p['CAP_LOW'], p['CAP_HIGH'])
        self.storage_capacity = random.uniform(p['STOR_CAP_LOW'], p['STOR_CAP_HIGH'])
        self.eta = random.uniform(p['ETA_LOW'], p['ETA_HIGH'])

        # Learning parameters
        self.phi = random.uniform(p['PHI_LOW'], p['PHI_HIGH'])
        self.beta = random.uniform(p['BETA_LOW'], p['BETA_HIGH'])

        # Storage decision space
        gran = p['STORAGE_GRAN']
        self.fractions = [i / gran for i in range(gran + 1)]
        self.attract = {f: random.uniform(-0.1, 0.1) for f in self.fractions}

        # Storage enabled flag (False for baseline scenario)
        self.storage_enabled = storage_enabled

        # State variables (updated each day)
        self.last_choice = 0.0
        self.qM = 0.0
        self.qE = 0.0
        self.stored = 0.0
        self.profit = 0.0
        self.qM_raw = 0.0
        self.qE_raw = 0.0

    def produce_and_decide(self):
        p = self.model.params
        eps = random.uniform(1 - p['WEATHER_VAR'], 1 + p['WEATHER_VAR'])
        self.qM_raw = p['ALPHA_M'] * self.capacity * eps
        self.qE_raw = p['ALPHA_E'] * self.capacity * eps

        if self.storage_enabled:
            # Choose storage fraction from attractions via softmax
            arr = np.array([self.attract[f] for f in self.fractions], dtype=float)
            probs = stable_softmax(arr, self.beta)
            choice = random.choices(self.fractions, weights=probs, k=1)[0]
        else:
            # Baseline: no storage
            choice = 0.0

        self.last_choice = choice
        self.stored = min(self.storage_capacity, self.eta * choice * self.qM_raw)
        self.qM = (1.0 - choice) * self.qM_raw
        self.qE = self.qE_raw + self.stored

    def update_learning(self, profit):
        self.profit = profit
        if not self.storage_enabled:
            return

        price_M = self.model.price_M
        price_E = self.model.price_E

        # Compute counterfactual profit for ALL fractions
        pi_all = {}
        max_profit = 0.0
        for f in self.fractions:
            stored_f = min(self.storage_capacity, self.eta * f * self.qM_raw)
            sold_M_f = (1.0 - f) * self.qM_raw
            sold_E_f = self.qE_raw + stored_f
            pi_all[f] = price_M * sold_M_f + price_E * sold_E_f
            if pi_all[f] > max_profit:
                max_profit = pi_all[f]

        # Normalize counterfactual profits: (pi - pi_max) / std(pi)
        # Preserves relative ranking, controls scale for softmax interaction
        pi_values = np.array(list(pi_all.values()))
        pi_std = pi_values.std()
        if pi_std < 1e-8:
            pi_std = 1.0  # avoid division by zero when all fractions yield same profit

        for f in self.fractions:
            regret_norm = (pi_all[f] - max_profit) / pi_std
            self.attract[f] = (1 - self.phi) * self.attract[f] + self.phi * regret_norm


# ── Model ───────────────────────────────────────────────────────────────────

class MarketModel(Model):
    def __init__(self, params=None, storage_enabled=True, seed=None):
        super().__init__(seed=seed)
        # Fix Python's random and numpy RNG for reproducibility
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.params = {**DEFAULT_PARAMS, **(params or {})}
        self.storage_enabled = storage_enabled

        n = self.params['N']
        for _ in range(n):
            SolarAgent(self, self.params, storage_enabled=storage_enabled)

        # Model-level state
        self.price_M = 0.0
        self.price_E = 0.0
        self.gas_M = 0.0
        self.gas_E = 0.0
        self.total_solar_M = 0.0
        self.total_solar_E = 0.0
        self.avg_storage_fraction = 0.0
        self.avg_profit = 0.0
        self.current_day = 0

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                'day': lambda m: m.current_day,
                'price_M': lambda m: m.price_M,
                'price_E': lambda m: m.price_E,
                'gas_M': lambda m: m.gas_M,
                'gas_E': lambda m: m.gas_E,
                'total_solar_M': lambda m: m.total_solar_M,
                'total_solar_E': lambda m: m.total_solar_E,
                'avg_storage_fraction': lambda m: m.avg_storage_fraction,
                'avg_profit': lambda m: m.avg_profit,
            },
            agent_reporters={
                'agent_qM': 'qM',
                'agent_qE': 'qE',
                'agent_choice': 'last_choice',
                'agent_stored': 'stored',
                'agent_profit': 'profit',
                'agent_eta': 'eta',
                'agent_phi': 'phi',
                'agent_beta': 'beta',
            }
        )

    def step_day(self):
        self.current_day += 1
        self._time += 1  # Advance Mesa internal clock for DataCollector
        p = self.params

        # 1. Agents produce and decide
        self.agents.shuffle_do('produce_and_decide')

        # 2. Morning market clearing
        self.total_solar_M = sum(a.qM for a in self.agents)
        if self.total_solar_M >= p['DEMAND_M']:
            self.price_M = 0.0
            self.gas_M = 0.0
        else:
            self.gas_M = p['DEMAND_M'] - self.total_solar_M
            self.price_M = gas_marginal_cost(self.gas_M, p['C0'], p['ALPHA_G'], p['GAMMA_G'])

        # 3. Evening market clearing
        self.total_solar_E = sum(a.qE for a in self.agents)
        if self.total_solar_E >= p['DEMAND_E']:
            self.price_E = 0.0
            self.gas_E = 0.0
        else:
            self.gas_E = p['DEMAND_E'] - self.total_solar_E
            self.price_E = gas_marginal_cost(self.gas_E, p['C0'], p['ALPHA_G'], p['GAMMA_G'])

        # 4. Profits and learning
        profits = []
        for a in self.agents:
            profit = self.price_M * a.qM + self.price_E * a.qE
            a.update_learning(profit)
            profits.append(profit)

        # 5. Aggregate statistics
        self.avg_storage_fraction = np.mean([a.last_choice for a in self.agents])
        self.avg_profit = np.mean(profits)

        # 6. Collect data
        self.datacollector.collect(self)

    def run(self, days=None):
        """Run the model for a given number of days."""
        days = days or self.params['DAYS']
        for _ in range(days):
            self.step_day()
        return self

    def get_model_data(self):
        """Return model-level DataFrame."""
        return self.datacollector.get_model_vars_dataframe().reset_index(drop=True)

    def get_agent_data(self):
        """Return agent-level DataFrame with correct day column."""
        df = self.datacollector.get_agent_vars_dataframe().reset_index()
        # Mesa 3 uses ('Step', 'AgentID') as multi-index
        if 'Step' in df.columns:
            df = df.rename(columns={'Step': 'day', 'AgentID': 'agent_id'})
            df['day'] = df['day'] + 1  # 1-indexed days
        return df


# ── Runner utilities ────────────────────────────────────────────────────────

def run_single(params=None, storage_enabled=True, days=None, seed=None):
    """Run a single simulation and return (model, df_model, df_agents)."""
    model = MarketModel(params=params, storage_enabled=storage_enabled, seed=seed)
    model.run(days=days)
    return model, model.get_model_data(), model.get_agent_data()


def run_batch(param_grid, base_params=None, n_replicas=5, days=None, storage_enabled=True):
    """
    Run batch simulations over a parameter grid.

    param_grid: dict of {param_name: [values]}
        e.g. {'N': [20, 30], 'STORAGE_GRAN': [5, 10]}
    Returns a list of dicts with config + summary metrics.
    """
    import itertools

    base = {**DEFAULT_PARAMS, **(base_params or {})}
    keys = list(param_grid.keys())
    combos = list(itertools.product(*[param_grid[k] for k in keys]))

    results = []
    for combo in combos:
        run_params = {**base}
        for k, v in zip(keys, combo):
            run_params[k] = v

        for rep in range(n_replicas):
            model = MarketModel(params=run_params, storage_enabled=storage_enabled, seed=rep)
            model.run(days=days)
            df = model.get_model_data()

            res = {k: v for k, v in zip(keys, combo)}
            res['replica'] = rep
            res['mean_price_M'] = df['price_M'].mean()
            res['mean_price_E'] = df['price_E'].mean()
            res['mean_gas_M'] = df['gas_M'].mean()
            res['mean_gas_E'] = df['gas_E'].mean()
            res['mean_avg_profit'] = df['avg_profit'].mean()
            res['final_avg_storage_fraction'] = df['avg_storage_fraction'].iloc[-1]
            res['std_price_M'] = df['price_M'].std()
            res['std_price_E'] = df['price_E'].std()
            results.append(res)

    import pandas as pd
    return pd.DataFrame(results)


if __name__ == '__main__':
    # Quick test
    print("Running baseline (no storage)...")
    _, df_base, _ = run_single(storage_enabled=False, days=50)
    print(f"  Mean price_M: {df_base['price_M'].mean():.2f}")
    print(f"  Mean price_E: {df_base['price_E'].mean():.2f}")

    print("Running with storage...")
    _, df_stor, _ = run_single(storage_enabled=True, days=50)
    print(f"  Mean price_M: {df_stor['price_M'].mean():.2f}")
    print(f"  Mean price_E: {df_stor['price_E'].mean():.2f}")
    print(f"  Final avg storage fraction: {df_stor['avg_storage_fraction'].iloc[-1]:.3f}")
    print("Done.")
