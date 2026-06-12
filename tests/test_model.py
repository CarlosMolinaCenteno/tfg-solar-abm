"""Tests de invariantes del modelo de almacenamiento solar adaptativo.

Estos tests no validan la lógica económica ni la convergencia del aprendizaje;
verifican que el modelo respeta las restricciones técnicas en cada paso, que
las semillas son reproducibles y que las cantidades agregadas son coherentes.

Ejecutar con: `pytest tests/`
"""
import pytest

from src.model import MarketModel


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def model():
    return MarketModel(seed=42)


@pytest.fixture
def run_30_days():
    m = MarketModel(seed=42)
    for _ in range(30):
        m.step_day()
    return m


# ── Construcción y ejecución básica ────────────────────────────────────────

def test_construye_sin_error():
    MarketModel(seed=42)


def test_corre_30_dias_sin_error(run_30_days):
    assert run_30_days.current_day == 30


def test_datacollector_registra_30_filas(run_30_days):
    df = run_30_days.datacollector.get_model_vars_dataframe()
    assert len(df) == 30


# ── Reproducibilidad por semilla ───────────────────────────────────────────

def test_misma_semilla_resultados_identicos():
    """Dos ejecuciones independientes con la misma semilla son idénticas.

    El modelo reseed-ea el RNG global de Python y de numpy en el constructor, por
    lo que la reproducibilidad se cumple para ejecuciones *secuenciales*
    independientes (construir+ejecutar, construir+ejecutar). No se cumple —ni se
    pretende— para pasos entrelazados de dos modelos que comparten el mismo flujo
    global. Es la propiedad que valida el anexo de validación (V.1).
    """
    m1 = MarketModel(seed=42)
    for _ in range(50):
        m1.step_day()
    df1 = m1.datacollector.get_model_vars_dataframe()

    m2 = MarketModel(seed=42)
    for _ in range(50):
        m2.step_day()
    df2 = m2.datacollector.get_model_vars_dataframe()

    assert df1.equals(df2)


def test_semillas_distintas_resultados_distintos():
    m1 = MarketModel(seed=1)
    m2 = MarketModel(seed=2)
    for _ in range(50):
        m1.step_day()
        m2.step_day()
    df1 = m1.datacollector.get_model_vars_dataframe()
    df2 = m2.datacollector.get_model_vars_dataframe()
    assert not df1.equals(df2)


# ── Clearing del mercado ───────────────────────────────────────────────────

def test_clearing_M_consistente(run_30_days):
    """price_M == 0 ⟺ total_solar_M >= demand_M."""
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    demand_M = m.params['DEMAND_M']
    for _, row in df.iterrows():
        if row['price_M'] == 0:
            assert row['total_solar_M'] >= demand_M - 1e-9
            assert row['gas_M'] == 0
        else:
            assert row['total_solar_M'] < demand_M + 1e-9
            assert row['gas_M'] > 0


def test_clearing_E_consistente(run_30_days):
    """price_E == 0 ⟺ total_solar_E >= demand_E."""
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    demand_E = m.params['DEMAND_E']
    for _, row in df.iterrows():
        if row['price_E'] == 0:
            assert row['total_solar_E'] >= demand_E - 1e-9
            assert row['gas_E'] == 0
        else:
            assert row['total_solar_E'] < demand_E + 1e-9
            assert row['gas_E'] > 0


def test_conservacion_demanda_M(run_30_days):
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    demand_M = m.params['DEMAND_M']
    for _, row in df.iterrows():
        if row['gas_M'] > 0:
            total = row['total_solar_M'] + row['gas_M']
            assert abs(total - demand_M) < 1e-9


def test_conservacion_demanda_E(run_30_days):
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    demand_E = m.params['DEMAND_E']
    for _, row in df.iterrows():
        if row['gas_E'] > 0:
            total = row['total_solar_E'] + row['gas_E']
            assert abs(total - demand_E) < 1e-9


# ── Restricciones técnicas del almacenamiento ──────────────────────────────

def test_stored_no_supera_capacidad(run_30_days):
    """agent.stored <= agent.storage_capacity para todos los agentes y días."""
    m = run_30_days
    for a in m.agents:
        assert 0 <= a.stored <= a.storage_capacity + 1e-9


def test_fraccion_elegida_valida(run_30_days):
    """agent.last_choice ∈ [0, 1] tras cada paso."""
    m = run_30_days
    for a in m.agents:
        assert 0.0 <= a.last_choice <= 1.0


def test_qM_no_negativo(run_30_days):
    m = run_30_days
    for a in m.agents:
        assert a.qM >= 0


def test_qE_no_negativo(run_30_days):
    m = run_30_days
    for a in m.agents:
        assert a.qE >= 0


# ── Coherencia de unidades ─────────────────────────────────────────────────

def test_precio_no_negativo(run_30_days):
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    assert (df['price_M'] >= 0).all()
    assert (df['price_E'] >= 0).all()


def test_gas_no_negativo(run_30_days):
    m = run_30_days
    df = m.datacollector.get_model_vars_dataframe()
    assert (df['gas_M'] >= 0).all()
    assert (df['gas_E'] >= 0).all()
