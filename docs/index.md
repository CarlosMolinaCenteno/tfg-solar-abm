# TFG — Modelo de almacenamiento solar adaptativo

**Trabajo de Fin de Grado** del Doble Grado en Economía y Matemáticas y Estadística (Universidad Complutense de Madrid).

**Autor:** Carlos Molina Centeno
**Tutores:** Francisco Álvarez González · María Jesús Moreta Santos

---

## Sobre el proyecto

Modelo basado en agentes (ABM) que simula un mercado eléctrico con productores solares heterogéneos. Cada productor decide qué fracción de su energía matutina almacena en una batería para venderla por la tarde. No optimiza: aprende de forma adaptativa a partir de los precios observados.

El trabajo combina tres tipos de análisis:

- **Teórico** — equilibrios cooperativos, de Nash y precio-aceptantes que sirven de referente analítico (cap. 4 §4.6 y anexos).
- **Computacional** — simulación con [Mesa](https://mesa.readthedocs.io) y banco de pruebas que valida cada elemento del modelo (sección de validación).
- **Económico** — interpretación de los resultados en términos de excedentes, precios y mix energético (cap. 6 y 7).

## Cómo navegar este sitio

- **[Memoria](memoria/index.md)** — los ocho capítulos del TFG y la bibliografía.
- **[Anexos](anexos/a-agente-unico.md)** — derivaciones analíticas que apoyan el cap. 4.
- **[Validación](validacion/index.md)** — notebooks ejecutables que comprueban que la implementación reproduce la lógica económica del modelo.
- **[Extras](extras/notas-aprendizaje.md)** — notas de aprendizaje (diagnóstico del proceso), plan del banco de pruebas e índice aprobado.

## Repositorio

El código fuente, los datos y este sitio se publican en
[GitHub: CarlosMolinaCenteno/tfg-solar-abm](https://github.com/CarlosMolinaCenteno/tfg-solar-abm).

```bash
git clone https://github.com/CarlosMolinaCenteno/tfg-solar-abm.git
cd tfg-solar-abm
pip install -e .
pytest                  # ejecuta los tests del modelo
mkdocs serve            # sirve este sitio en local
```
