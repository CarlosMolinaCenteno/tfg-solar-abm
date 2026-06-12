# Validación del modelo

Esta sección reúne las dos piezas de comprobación del modelo. El objetivo no es
contrastar el modelo con datos reales, sino verificar que **la implementación
reproduce la lógica económica descrita en los capítulos** y que las cifras del
TFG son robustas.

## Banco de pruebas (referentes teóricos)

El [banco de pruebas](banco_pruebas.ipynb) calcula de forma independiente los
referentes analíticos del capítulo 3 —cártel, Nash homogéneo, Nash heterogéneo y
límite precio-aceptante— y los contrasta con las reglas de decisión del modelo.
Es el soporte numérico de las secciones 3.5–3.6 y de los anexos A y B.

## Anexo de validación del modelo

La validación reproducible —reproducibilidad por semilla, invariantes y *sanity
checks*, trazabilidad cuerpo↔código, robustez de las cifras del capítulo 5 y
sensibilidad a los parámetros (η, φ, β) y a N— está documentada en el
[anexo de validación](../anexos/validacion.md).

Todo el anexo se regenera con un único script:

```bash
python scripts/validacion_modelo.py
```

que deja sus tablas (`data/validacion_v*.csv`) y figuras
(`figures/validacion_v*.png`) en el repositorio.

## Cómo ejecutar

Desde la raíz del repositorio:

```bash
pip install -e .
python scripts/validacion_modelo.py      # validación reproducible (anexo)
jupyter lab docs/validacion/             # abrir el banco de pruebas
```

El banco de pruebas importa `MarketModel` y `SolarAgent` de `src.model` y es
autocontenido.
