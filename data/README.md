# Datos generados por las simulaciones

Los CSV de este directorio se generan ejecutando los scripts de `scripts/` y
corresponden a la **versión actual** del modelo (regla z-score sobre la fracción
jugada, parametrización INTERIOR, `seed=0`).

## Cap. 5 — análisis económico (`scripts/generate_figures_cap5.py`)

| Archivo | Contenido |
|---|---|
| `baseline_model.csv` | Series diarias agregadas, escenario **sin** almacenamiento (500 días, seed=0) |
| `baseline_agents.csv` | Series diarias por agente, mismo escenario |
| `storage_model.csv` | Series diarias agregadas **con** almacenamiento |
| `storage_agents.csv` | Series diarias por agente, con almacenamiento |
| `table_5_1_comparison.csv` | Tabla 5.1 — comparación de escenarios (precios, gas, beneficio) |
| `table_5_2_bienestar.csv` | Tabla 5.2 — descomposición de excedentes y bienestar |

## Validación del modelo (`scripts/validacion_modelo.py`)

| Archivo | Contenido |
|---|---|
| `validacion_v1_reproducibilidad.csv` | Métricas estacionarias por semilla (reproducibilidad) |
| `validacion_v2_invariantes.csv` | Invariantes y *sanity checks* |
| `validacion_v3_traza_update.csv` | Trazabilidad ejecutable de un paso de actualización |
| `validacion_v4_resumen.csv`, `validacion_v4_robustez.csv`, `validacion_v4_signos.csv` | Robustez de las cifras del cap. 5 (seeds × horizontes; estabilidad de signos) |
| `validacion_v5_sensibilidad_{eta,phi,beta}.csv` | Sensibilidad a η, φ y β |
| `validacion_v6_N.csv` | Robustez agregada a N (con N·c = 75 constante) |
| `sensitivity_{eta,phi,beta}.csv`, `robustness.csv` | Barridos de sensibilidad/robustez auxiliares |

## Reproducir desde cero

```bash
python scripts/generate_figures_cap5.py     # baseline/storage + tablas 5.x
python scripts/validacion_modelo.py         # validacion_v* (varios minutos)
```

Cada script deja sus salidas en este directorio y en
[`figures/`](../figures/).
