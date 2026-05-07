# TFG — Modelo de almacenamiento solar adaptativo

Trabajo de Fin de Grado del **Doble Grado en Economía y Matemáticas y Estadística** (Universidad Complutense de Madrid).

**Autor:** Carlos Molina Centeno
**Tutores:** Francisco Álvarez González, María Jesús Moreta Santos

---

## ¿Qué es este proyecto?

Modelo basado en agentes (ABM) que simula un mercado eléctrico con productores solares heterogéneos. Cada productor decide qué fracción de su energía matutina almacena en una batería para venderla por la tarde, sin resolver problemas de optimización: aprende de forma adaptativa a partir de los precios observados.

El modelo se implementa con [Mesa](https://mesa.readthedocs.io) y permite analizar la dinámica del mercado, la convergencia del aprendizaje, el efecto del almacenamiento sobre el mix energético y los excedentes de los agentes.

## Estructura del repositorio

```
tfg-solar-abm/
├── src/model.py             Modelo Mesa (MarketModel + SolarAgent)
├── tests/                   Tests con pytest (invariantes del modelo)
├── notebooks/ ...           Notebooks de validación (en docs/validacion/)
├── data/                    Datos generados por simulaciones (CSV)
├── figures/                 Figuras del TFG
└── docs/                    Memoria + validación + extras (sitio MkDocs)
    ├── memoria/             Capítulos 1–8 del TFG
    ├── anexos/              Anexos A y B
    ├── validacion/          Notebooks ejecutables que validan el modelo
    └── extras/              Notas de aprendizaje, índice, plan de pruebas
```

## Documentación web

El proyecto se publica como sitio navegable con [MkDocs](https://www.mkdocs.org). Para verlo en local:

```bash
pip install -r requirements.txt
mkdocs serve
```

Y abrir `http://localhost:8000`.

La versión publicada vive en
[carlosmolinacenteno.github.io/tfg-solar-abm](https://carlosmolinacenteno.github.io/tfg-solar-abm/).

## Uso del modelo

```bash
pip install -e .
```

```python
from src.model import MarketModel

model = MarketModel(n_agents=30, demand_M=60.0, demand_E=120.0, seed=42)
for _ in range(200):
    model.step_day()

df = model.datacollector.get_model_vars_dataframe()
print(df.tail())
```

## Reproducir las figuras y datos del TFG

```bash
python notebooks/genera_figuras.py
```

Esto regenera todos los CSV de `data/` y todas las figuras de `figures/` a partir del modelo.

## Tests

```bash
pytest tests/
```

Verifica invariantes del modelo: clearing del mercado, restricciones de almacenamiento, reproducibilidad por semilla y otros.

## Licencia

Código bajo licencia MIT. Texto del TFG con todos los derechos reservados por el autor (consultar antes de reutilizar).
