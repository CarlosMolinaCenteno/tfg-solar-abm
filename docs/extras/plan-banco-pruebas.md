# Plan: Banco de pruebas v2 — notebook definitivo para reglas de aprendizaje

## Contexto

`workspace/notebooks/banco_pruebas.ipynb` es el banco de pruebas para comparar de forma sistemática las 4 reglas de aprendizaje candidatas:

1. **Contrafactual raw** — actualiza todas las fracciones con `pi_f` sin normalizar.
2. **Contrafactual z-score** — actualiza todas con z-score de `pi_f`.
3. **Z-score solo elegida** — variante del profesor: solo actualiza la fracción elegida.
4. **EWA con δ** — Camerer-Ho con peso de imaginación δ ∈ [0,1].

Diseño:
- **Reproducibilidad por celda**: cada parametrización vive en una celda config editable.
- **Simulación única + visualización múltiple**: cambiar agentes / fracciones / días de visualización NO re-simula. Solo cambia el dibujo.
- **Plantilla idéntica por regla**: §6–§9 tienen la misma estructura de celdas.
- **Referencias claras para juzgar convergencia**: cartel, Nash, BR per-agente.

## Archivos afectados

- `workspace/notebooks/banco_pruebas.ipynb` — el notebook en sí.
- `workspace/scripts/_build_banco_pruebas.py` — generador del notebook desde cero (re-ejecutable).
- `workspace/scripts/model.py` — NO se toca. Todo por monkey-patch.
- `workspace/scripts/_patch_*.py` — patches incrementales aplicados en iteraciones posteriores (sección §2 sobre todo).

## Estructura del notebook

```
§0  Setup                          (autoreload, imports, paths)
§1  Parametrizaciones de mercado   (ESQUINA, INTERIOR)
§2  Referencias homogéneas         (cartel + Nash + BR per-agente)
§3  Runner + monkey-patch          (ejecuta una regla y empaqueta resultado)
§4  Métricas y visualizaciones     (trabajan sobre `resultado` almacenado)
§5  Definiciones de las 4 reglas
§6  Pruebas: contrafactual raw
§7  Pruebas: contrafactual z-score
§8  Pruebas: z-score solo elegida
§9  Pruebas: EWA con delta
§10 Comparativa cross-rule (opcional)
```

## §2 — Referencias homogéneas (tres conceptos distintos)

Aprendizaje clave del trabajo iterativo: hay **tres** referencias distintas, no dos. Confundirlas lleva a interpretaciones erróneas.

- **Cartel (óptimo cooperativo)**: f que maximiza `profit/agente` cuando todos hacen lo mismo. Equivale al óptimo del agente representativo. Es el techo si los agentes pudieran coordinarse. **NO** es el equilibrio al que convergen los ABM.
- **Nash homogéneo simétrico**: f tal que `BR(f) = f`. Es el equilibrio al que tienden los ABM individualmente racionales. Suele estar **por encima** del cartel (cada agente tiene incentivo a almacenar más para aprovechar el `P_E` que el cartel sostiene).
- **Aproximación price-taker (ratio = η)**: el Nash en el límite N→∞. Para N finito hay corrección de poder de mercado, pequeña pero no nula. Es **informativa** pero NO es el Nash real.

### §2.1 Cartel (óptimo cooperativo del agente representativo)

#### §2.1.1 CPO analítica (`solve_unico_cpo`)
- Resuelve `dπ/df = 0` con `scipy.optimize.brentq` para el agente representativo (cártel de N agentes homogéneos).
- Detecta automáticamente esquinas (inferior, superior, saturación de batería).
- Devuelve `f_star`, `pi_star`, `PM_star`, `PE_star`, `ratio_star`, `regimen`, `_pi`, `_dpi` (las funciones para plottear curva).
- Notación: `M = N·α_M·c`, `E = N·α_E·c`, `s_agg = N·s` (capacidad / batería agregadas).

#### §2.1.2 Cross-check via grid search (`compute_cartel_grid`)
- Grid search sobre `f ∈ [0,1]` corriendo `run_with_forced_f`. Cross-check del analítico (debería coincidir módulo paso del grid).
- Devuelve dict con top-level apuntando a cartel (compatible con `resumen_metricas`):
  - `f_star, profit_star, price_M_star, price_E_star, ratio_star`
  - `cooperativo`: subdict redundante para acceso explícito.
  - `price_taker_approx`: f donde ratio=η, INFORMATIVA. Marcada claramente como aproximación N→∞, NO es el Nash real.
  - `eta_referencia, detalle, resumen`.
- Alias `compute_optimal_f_homogeneo = compute_cartel_grid` por compatibilidad.

### §2.2 Nash homogéneo via best-response fixed-point (`compute_nash_homogeneo_BR`)

Algoritmo:
1. Para cada `f_h` en `f_h_grid`: corre simulación con todos a `f_h` excepto un agente representativo, evalúa BR(`f_h`) buscando el `f_i ∈ f_i_grid` que maximiza su profit.
2. Encuentra el `f_h` donde la curva BR(`f_h`) cruza la diagonal — interpolación lineal entre dos puntos adyacentes con cambio de signo del gap = BR − f_h.

**Limitación**: la función asume agentes **homogéneos**. Por simetría basta un agente representativo (factor N de ahorro). Para heterogéneos, el concepto Nash simétrico no aplica directamente y haría falta best-response dynamics en N dimensiones.

Devuelve `optimo_nash` con: `f_star, profit_star, price_M_star, price_E_star, ratio_star, curva_BR (DataFrame), corner`.

#### §2.2.1 Diagnóstico: el paisaje plano cerca del Nash

Cerca del Nash, `profit_i(f_i)` es **muy plana** (variación ~1% sobre todo `f_i ∈ [0,1]`). El argmax (BR) puede caer lejos de `f_h` aunque `f_h` sea casi Nash. La distancia entre `f_h` y BR(`f_h`) **NO mide qué tan lejos estamos del Nash** — el Nash es el punto fijo, no la BR de un `f_h` cualquiera.

### §2.3 Best-response per-agente (`compute_optimal_f_per_agente`, `compute_optimal_f_un_agente`)

Diagnóstico, no Nash. Para cada agente i: grid search sobre `f_i` con los demás fijos en algún `f_homogeneo` (típicamente `optimo_nash['f_star']`).

- Si los agentes son homogéneos: los `f_i*` deberían coincidir todos con `f_nash` (verificación de punto fijo).
- Si son heterogéneos: los `f_i*` se desvían según `storage_capacity`/`capacity`.
- Anclando en `optimo_homogeneo['cooperativo']`: muestra la "tentación a defectar" del cartel (`f_i*` saldrán por encima del cartel).

`compute_optimal_f_un_agente` es la versión rápida (1 agente representativo) para casos homogéneos.

## §3 — Runner unificado

`run_with_rule(rule_fn, params, seed, days, storage_enabled=True) → dict`:
```
{
  'model':      modelo Mesa tras simular,
  'df_model':   DataFrame modelo-nivel,
  'df_agents':  DataFrame agentes,
  'df_attract': DataFrame long (day, agent_id, f, attract),
  'df_probs':   DataFrame long (day, agent_id, f, prob),
  'params':     dict de params,
  'seed':       seed,
  'rule_name':  str,
}
```

Implementación: monkey-patch de `SolarAgent.update_learning`, loop manual de `step_day()`, tras cada día guarda atracciones y aplica softmax con el `beta` del agente para colectar probabilidades.

## §4 — Métricas y visualizaciones genéricas

### Métricas fijas

`resumen_metricas(resultado, optimo=None, last=100) → dict`:
- `f_media_temporal, f_final`
- `f_std_de_medias` (std entre días de la media poblacional)
- `f_std_intraday_mean` (media sobre días de std entre agentes el mismo día)
- `f_std_temporal_mean` (media sobre agentes de std temporal)
- `price_M_mean, price_E_mean, price_ratio_mean`
- `profit_agregado_mean, atraccion_elegida_media`
- Si `optimo` se pasa: `gap_profit_pct, gap_f_abs, ratio_vs_optimo`

Pasar `optimo=optimo_homogeneo` da gap vs cartel; `optimo=optimo_nash` da gap vs Nash real.

### Vistas por agente

- `ficha_agentes(model, agent_ids=None) → DataFrame` con `capacity, storage_capacity, eta, phi, beta`.
- `tabla_profits_por_agente`, `tabla_atraccion_elegida_por_agente`.

### Evoluciones (con filtros)

Todas aceptan `agent_ids=None`, `fracciones=None`, `day_range=None`:
- `plot_evolucion_f_media`
- `plot_evolucion_atracciones` + `tabla_atracciones`
- `plot_evolucion_probabilidades` + `tabla_probabilidades`
- `plot_evolucion_f_elegida` + `tabla_f_elegida`
- `plot_evolucion_atraccion_elegida`

Colormaps: `_cmap_sign_aware` elige `viridis` vs `coolwarm` según signo de los valores.

### Extras

- `entropia_softmax(resultado, agent_ids=None, last=100)`: entropía media de la softmax por agente. Baja = convergido, alta = explorando.
- `tiempo_convergencia(resultado, threshold=0.05, k=20)`: primer día en que `|f_i(t)-f_i_final| < threshold` durante `k` días consecutivos.
- `resumen_multiseed(rule_fn, params, seeds, days, last, optimo)`: corre N seeds, una fila por seed + agregada.
- `seleccionar_agentes_diversos(model, n)`: elige n agentes con `storage_capacity` distribuida.

## §5 — Las 4 reglas

- `regla_cf_raw(agent, profit)`: actualiza todas con `pi_f` sin normalizar.
- `regla_cf_zscore(agent, profit)`: actualiza todas con `(pi_f - mean)/std`.
- `regla_zscore_elegida(agent, profit)`: solo la fracción elegida, con z-score del realizado.
- `make_regla_ewa(delta=0.5, rho=0.9)`: factory de EWA Camerer-Ho. Mantiene `_ewa_N` por agente.

## §6–§9 — Secciones por regla

Plantilla idéntica:
1. **Config** — `params, seed, days`.
2. **Ejecución** — `resultado_<regla> = run_with_rule(...)`.
3. **Métricas** — `resumen_metricas(resultado_<regla>, optimo=optimo_homogeneo)`.
4. **Evolución agregada** — `plot_evolucion_f_media`.
5. **Agentes y filtros** — `AGENTES, FRACCIONES, DIAS` editables sin re-simular.
6. **Vistas detalladas** — atracciones, probabilidades, f elegida, atracción elegida (plot + tabla).
7. **Extras** — entropía + tiempo convergencia + tablas profit/atracción por agente.
8. **Multi-seed opcional** — comentado por defecto.

Default: `PARAMS_INTERIOR`, `seed=0`, `days=500`, 4 agentes seleccionados por diversidad.

## §10 — Comparativa cross-rule

Tabla con una fila por regla (todas con misma seed): `f_final, gap_profit_pct, f_std_intraday, f_std_temporal, entropia_norm, t_conv_mediano`.

## Verificación end-to-end

1. Restart Kernel → Run All en `PARAMS_INTERIOR, seed=0, days=500`.
2. **§2.1.1** (CPO analítica) debe dar `f_cartel ≈ 0.47` para INTERIOR (régimen interior).
3. **§2.1.2** (grid) debe coincidir con §2.1.1 módulo paso del grid.
4. **§2.2** (Nash BR) debe dar `f_nash ≈ 0.63` (entre cartel y price-taker, ratio ligeramente < η). La curva BR(f_h) es discontinua: salta de corner-up (=1) a interior alrededor del Nash. Se localiza el cruce por interpolación lineal del gap.
5. **§2.3** anclado en `optimo_nash['f_star']`: con homogéneos, los `f_i*` deberían quedar todos cerca del Nash. Anclando en cartel: deberían salir muy por encima (tentación a defectar).
6. Tras §6–§9: cambiar `AGENTES = [3, 7]` → `AGENTES = [1, 5, 10]` NO debe disparar re-simulación.
7. `resumen_metricas` con `optimo=optimo_homogeneo` (cartel) debería dar `gap_profit_pct` razonable para z-score-elegida; con `optimo=optimo_nash` el gap debería ser menor (los ABM convergen a Nash, no a cartel).

## Notas finales

- **Sobre el Nash en heterogéneos**: `compute_nash_homogeneo_BR` no aplica. El concepto de Nash simétrico falla. Habría que iterar best-response dynamics en N dimensiones (no implementado).
- **Sobre el grid de §2.2**: si la curva BR es discontinua (BR salta de 1 a un valor interior entre dos puntos adyacentes), el Nash interpolado es aproximación. Para precisión, refinar `f_h_grid` alrededor del salto.
- **Sobre `model.py`**: nunca se modifica. Todos los experimentos van por monkey-patch (`run_with_forced_f`, `run_with_forced_f_heterogeneo`, `run_with_rule`).
