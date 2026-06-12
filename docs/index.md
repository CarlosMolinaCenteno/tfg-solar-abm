# TFG — Modelo de almacenamiento solar adaptativo

**Trabajo de Fin de Grado** del Doble Grado en Economía y Matemáticas y Estadística (Universidad Complutense de Madrid).

**Autor:** Carlos Molina Centeno
**Tutores:** Francisco Álvarez González · María Jesús Moreta Santos

---

## Sobre el proyecto

Modelo basado en agentes (ABM) que simula un mercado eléctrico con productores
solares heterogéneos. Cada productor decide qué fracción de su energía matutina
almacena en una batería para venderla por la tarde. No optimiza: **aprende de
forma adaptativa** a partir de los beneficios observados, mediante una regla de
refuerzo (z-score del beneficio realizado sobre la fracción jugada).

El trabajo combina tres tipos de análisis:

- **Teórico** — equilibrios de cártel, de Nash (homogéneo y heterogéneo) y
  precio-aceptante que sirven de referente analítico (cap. 3 y anexos A–B).
- **Computacional** — simulación con [Mesa](https://mesa.readthedocs.io),
  banco de pruebas que ancla los referentes teóricos y validación reproducible
  del modelo (sección de validación).
- **Económico** — efecto del almacenamiento sobre precios, mix energético y
  excedentes de los agentes (cap. 5).

## Cómo navegar este sitio

- **[Memoria](memoria/index.md)** — los cinco capítulos del TFG, el resumen y la
  bibliografía.
- **[Anexos](anexos/a-agente-unico.md)** — derivaciones del agente único (A),
  Nash heterogéneo (B) y validación del modelo.
- **[Validación](validacion/index.md)** — banco de pruebas teórico y validación
  reproducible.
- **[Extras](extras/notas-aprendizaje.md)** — notas de aprendizaje (diagnóstico
  de las reglas exploradas).

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
