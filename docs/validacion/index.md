# Validación del modelo

Esta sección documenta la validación computacional del modelo basado en agentes. El objetivo no es contrastar el modelo con datos reales, sino comprobar que **la implementación reproduce la lógica económica descrita en los capítulos teóricos** y que los resultados son consistentes con los supuestos del modelo.

## Estructura de la validación

| Notebook | Qué se valida | Capítulo de la memoria |
|---|---|---|
| [00. Quickstart](00_quickstart.ipynb) | Que el modelo se instala, importa y ejecuta correctamente | — |
| [01. Validación de precios](01_validacion_precios.ipynb) | Mecanismo de *clearing* del mercado en ambos periodos | §5.3.1 |
| [02. Validación del almacenamiento](02_validacion_almacenamiento.ipynb) | Restricciones técnicas (capacidad $s_i$, eficiencia $\eta_i$), efecto intertemporal | §5.3.2 |
| [03. Validación del aprendizaje](03_validacion_aprendizaje.ipynb) | Convergencia adaptativa, ausencia de fijación inmediata | §5.3.3 |
| [04. Coherencia temporal](04_coherencia_temporal.ipynb) | Orden de las operaciones del día (decisiones → precios → aprendizaje) | §5.3.4 |
| [05. Reproducibilidad](05_reproducibilidad.ipynb) | Igualdad bit a bit de simulaciones con la misma semilla | — |
| [06. Diagnóstico del aprendizaje](06_diagnostico_aprendizaje.ipynb) | Histórico del proceso de diagnóstico de la regla de aprendizaje | (ver [notas](../extras/notas-aprendizaje.md)) |
| [Banco de pruebas](banco_pruebas.ipynb) | Referentes teóricos (cártel, Nash homogéneo y simétrico, precio-aceptantes) | §4.6 + anexos |

## Cómo ejecutar los notebooks

Desde la raíz del repositorio:

```bash
pip install -e .[test]
jupyter lab docs/validacion/
```

Cada notebook es **autocontenido**: importa `MarketModel` y `SolarAgent` de `src.model`, lee CSVs y figuras desde `data/` y `figures/`, y guarda nuevos resultados en esos mismos directorios.

## Estado actual

!!! warning "Validación pendiente de cierre"
    Los notebooks 01–06 están como **plantilla** mientras se decide la versión final de la regla de aprendizaje del modelo. Una vez fijada, se rellenarán con los experimentos definitivos. El [banco de pruebas teórico](banco_pruebas.ipynb) sí está completo (referencia §4.6 y anexos).
