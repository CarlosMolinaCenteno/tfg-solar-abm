# Datos generados por las simulaciones

Cada CSV se genera ejecutando `python notebooks/genera_figuras.py`. Los datos
contenidos en este directorio corresponden a la versión **actual** del modelo
(no a la final, pendiente de migración).

| Archivo | Contenido | Generado por |
|---|---|---|
| `baseline_model.csv` | Series diarias agregadas en escenario sin almacenamiento (200 días, seed=42) | escenario *Baseline* del cap. 6 |
| `baseline_agents.csv` | Series diarias por agente, mismo escenario | idem |
| `storage_model.csv` | Series diarias agregadas con almacenamiento activo | escenario *Storage* del cap. 6 |
| `storage_agents.csv` | Series diarias por agente, con almacenamiento | idem |
| `sensitivity_eta.csv` | Barrido de sensibilidad sobre $\eta$ (eficiencia de la batería) | §6.4 |
| `sensitivity_phi.csv` | Barrido sobre $\phi$ (tasa de aprendizaje) | §6.4 |
| `sensitivity_beta.csv` | Barrido sobre $\beta$ (sensibilidad de la regla logit) | §6.4 |
| `robustness.csv` | Resultados agregados sobre múltiples semillas | §6.5 |
| `table_6_1_comparison.csv` | Tabla resumen de comparación entre escenarios | tabla 6.1 del cap. 6 |

## Reproducir desde cero

```bash
python notebooks/genera_figuras.py
```

Esto regenera todos los CSV de este directorio y todas las figuras de
[`figures/`](../figures/) a partir del modelo.
