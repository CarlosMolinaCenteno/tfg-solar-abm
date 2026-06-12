# TFG — Modelo de almacenamiento solar adaptativo

Trabajo de Fin de Grado del **Doble Grado en Economía y Matemáticas y Estadística** (Universidad Complutense de Madrid).

**Autor:** Carlos Molina Centeno
**Tutores:** Francisco Álvarez González, María Jesús Moreta Santos

---

## ¿Qué es este proyecto?

Modelo basado en agentes (ABM) que simula un mercado eléctrico con productores
solares heterogéneos. Cada productor decide qué fracción de su energía matutina
almacena en una batería para venderla por la tarde, **sin resolver ningún
problema de optimización**: aprende de forma adaptativa a partir de los
beneficios que observa.

La regla de aprendizaje del modelo es el **z-score del beneficio realizado sobre
la fracción jugada, sin decaimiento** de las fracciones no elegidas. Los
beneficios contrafactuales de todas las fracciones se calculan únicamente para
fijar la escala (media y desviación típica del día) de la señal de refuerzo, no
para actualizar las atracciones de las fracciones no jugadas. La justificación y
las variantes descartadas están en el capítulo 4 y en las notas de aprendizaje.

El modelo se implementa con [Mesa](https://mesa.readthedocs.io) y permite
analizar la convergencia del aprendizaje hacia el equilibrio de Nash, el efecto
del almacenamiento sobre precios y mix energético, y los excedentes de los
agentes.

## Estructura del repositorio

```
tfg-solar-abm/
├── src/model.py            Modelo Mesa (MarketModel + SolarAgent + run_single)
├── scripts/                Scripts que regeneran figuras y datos del TFG
│   ├── generate_figures_cap3.py   Referentes teóricos (cártel, Nash, price-taker)
│   ├── generate_figures_cap4.py   Reglas de aprendizaje y comparativa
│   ├── generate_figures_cap5.py   Análisis económico del almacenamiento
│   ├── fig_A_concavidad.py        Figura del anexo A (concavidad/esquinas)
│   └── validacion_modelo.py       Validación reproducible (anexo)
├── tests/                  Tests con pytest (invariantes del modelo)
├── data/                   Datos generados por simulaciones (CSV)
├── figures/                Figuras del TFG
└── docs/                   Memoria + anexos + validación (sitio MkDocs)
    ├── memoria/            Capítulos 1–5, resumen y bibliografía
    ├── anexos/             Anexos A, B y validación del modelo
    ├── validacion/         Banco de pruebas teórico (notebook)
    └── extras/             Notas de aprendizaje
```

## Documentación web

El proyecto se publica como sitio navegable con [MkDocs](https://www.mkdocs.org). Para verlo en local:

```bash
pip install -r requirements.txt
mkdocs serve
```

Y abrir `http://localhost:8000`. La versión publicada vive en
[carlosmolinacenteno.github.io/tfg-solar-abm](https://carlosmolinacenteno.github.io/tfg-solar-abm/).

## Uso del modelo

```bash
pip install -e .
```

El modelo se parametriza con un diccionario; `DEFAULT_PARAMS` contiene la
configuración INTERIOR del TFG (N=30, demanda matutina D_M=80, capacidad solar
c=2.5, eficiencia η=0.9, etc.). La forma más cómoda de lanzar una simulación es
`run_single`:

```python
from src.model import run_single, DEFAULT_PARAMS

# Una simulación con almacenamiento, semilla fija, con los parámetros por defecto
model, df_model, df_agents = run_single(storage_enabled=True, days=500, seed=0)
print(df_model.tail())          # precios, gas, fracción media, beneficio medio por día

# Escenario sin almacenamiento (para comparar)
_, df_base, _ = run_single(storage_enabled=False, days=500, seed=0)
```

También se puede construir el modelo a mano y avanzar día a día:

```python
from src.model import MarketModel

model = MarketModel(params={'DEMAND_M': 80.0}, storage_enabled=True, seed=0)
for _ in range(500):
    model.step_day()
df = model.get_model_data()
```

## Reproducir las figuras y datos del TFG

Cada script deja sus salidas en `figures/` y `data/`:

```bash
python scripts/generate_figures_cap3.py    # cap. 3: referentes teóricos
python scripts/generate_figures_cap4.py    # cap. 4: reglas de aprendizaje
python scripts/generate_figures_cap5.py    # cap. 5: análisis económico
python scripts/fig_A_concavidad.py         # anexo A
python scripts/validacion_modelo.py        # anexo de validación (varios minutos)
```

Todos usan `seed=0` y los `DEFAULT_PARAMS` del modelo, de modo que las cifras
coinciden con las de la memoria.

## Tests

```bash
pytest tests/
```

Verifica invariantes del modelo: clearing del mercado, conservación de la
demanda, restricciones de almacenamiento, reproducibilidad por semilla
(ejecuciones secuenciales independientes) y coherencia de unidades.

## Licencia

Código bajo licencia MIT. Texto del TFG con todos los derechos reservados por el autor (consultar antes de reutilizar).
