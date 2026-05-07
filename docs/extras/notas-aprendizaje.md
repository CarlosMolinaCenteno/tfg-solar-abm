# Notas sobre el diseño de la regla de aprendizaje

Este documento recoge el proceso de diagnóstico y corrección del mecanismo de aprendizaje del modelo ABM. Puede servir como base para un anexo del TFG.

---

## 1. Problema inicial: fijación de los agentes

### Diagnóstico

Al analizar los resultados del modelo original, se observó que la fracción media de almacenamiento era completamente estática en el tiempo. La investigación reveló que **los 30 agentes elegían una fracción al azar el día 1 y jamás la cambiaban**.

**Causa raíz**: desajuste de escala entre las atracciones iniciales y el beneficio diario.

- Atracciones iniciales: $A_i(f, 0) \sim U(-0{,}1;\; 0{,}1)$
- Beneficio diario: $\pi_i \approx 180$

Tras un solo día, la atracción de la fracción elegida se actualiza:

$$A_i(f^*, 1) = (1 - \phi_i) \times 0 + \phi_i \times 180 \approx 13 \quad (\text{con } \phi_i = 0{,}07)$$

Mientras que el resto permanece en $\approx 0$. Con $\beta_i \approx 3{,}8$:

$$\Pr[f^*] = \frac{\exp(3{,}8 \times 13)}{\exp(3{,}8 \times 13) + 10 \times \exp(0)} \approx 1{,}000$$

La probabilidad de cambiar de estrategia es virtualmente cero después de un solo día.

### Verificación

```python
# Verificar que los agentes no cambian de estrategia
import pandas as pd
df = pd.read_csv('storage_agents.csv')
changes = df.groupby('agent_id')['agent_choice'].nunique()
print(f'Agentes que nunca cambiaron: {(changes == 1).sum()} de {len(changes)}')
# Resultado: 30 de 30
```

### Verificación de suboptimalidad

Se comprobó que los agentes no estaban fijados en la fracción óptima, sino en fracciones aleatorias:

```python
# Para cada agente: comparar fracción fijada vs fracción óptima
from model import MarketModel, DEFAULT_PARAMS

model = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=0)
model.run(days=200)

fracs = [i/10 for i in range(11)]
n_suboptimal = 0

for a in model.agents:
    locked_f = a.last_choice
    pm, pe = model.price_M, model.price_E
    qm_raw = DEFAULT_PARAMS['ALPHA_M'] * a.capacity * 1.0
    qe_raw = DEFAULT_PARAMS['ALPHA_E'] * a.capacity * 1.0

    best_f, best_profit = None, -999
    for f in fracs:
        stored = min(a.storage_capacity, a.eta * f * qm_raw)
        sold_m = (1 - f) * qm_raw
        sold_e = qe_raw + stored
        profit = pm * sold_m + pe * sold_e
        if profit > best_profit:
            best_profit = profit
            best_f = f

    locked_profit = pm * (1 - locked_f) * qm_raw + pe * (qe_raw + min(a.storage_capacity, a.eta * locked_f * qm_raw))
    if abs(locked_f - best_f) > 0.05:
        n_suboptimal += 1

print(f'Agentes subóptimos: {n_suboptimal} / 30')
# Resultado: 26 / 30
```

---

## 2. Primera propuesta de solución: normalización por beneficio máximo contrafactual

### Idea

Al final de cada día, el agente calcula el beneficio máximo que podría haber obtenido con cualquier fracción $f \in \mathcal{F}$, dados los precios observados $P_M(t)$ y $P_E(t)$:

$$\pi_i^{\max}(t) = \max_{f \in \mathcal{F}} \left[ P_M(t) \cdot (1-f) \cdot \tilde{q}_i^M + P_E(t) \cdot \left(\tilde{q}_i^E + \min\{s_i,\; \eta_i \cdot f \cdot \tilde{q}_i^M\}\right) \right]$$

El beneficio normalizado es:

$$\pi_i^{\text{norm}}(t) = \frac{\pi_i(t)}{\pi_i^{\max}(t)}$$

La regla de actualización se mantiene igual, pero usando $\pi_i^{\text{norm}} \in [0, 1]$ en vez de $\pi_i$:

$$A_i(f, t+1) = \begin{cases} (1-\phi_i) \cdot A_i(f, t) + \phi_i \cdot \pi_i^{\text{norm}}(t), & \text{si } f = f_i(t) \\ (1-\phi_i) \cdot A_i(f, t), & \text{si } f \neq f_i(t) \end{cases}$$

### Resultado

La normalización $\pi / \pi^{\max}$ resuelve el problema de fijación: las atracciones permanecen en una escala comparable a la señal de aprendizaje, y los agentes siguen explorando.

Sin embargo, se observó que los agentes **no convergen al óptimo** después de 500 días. La causa es que $\pi / \pi^{\max} \in [0, 1]$ siempre es positiva — incluso una fracción muy mala recibe un refuerzo positivo (menor, pero positivo). La señal dice "esto fue regular" pero nunca "esto fue malo, cambia".

### Verificación

```python
from model import MarketModel, DEFAULT_PARAMS
import numpy as np

model = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=0)
for day in range(1, 501):
    model.step_day()

# Trayectorias de agentes: siguen explorando pero no convergen
for i, a in enumerate(model.agents):
    if i >= 5:
        break
    # Ver que eligen fracciones variadas pero sin tendencia clara
    print(f'Agent {i}: last_choice={a.last_choice}')
```

---

## 3. Resultado de la primera propuesta

### Verificación detallada

Se ejecutó la simulación con 500 días y se verificó que los agentes ahora exploran activamente (10 fracciones distintas usadas en 20 días). Sin embargo, después de 500 días, 23 de 30 agentes siguen en fracciones subóptimas con un gap medio del 16,8%.

```python
from model import MarketModel, DEFAULT_PARAMS
import numpy as np

model = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=42)
for day in range(1, 501):
    model.step_day()

# Trayectorias: agentes exploran pero no convergen
agent_history = {}
model2 = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=42)
for day in range(1, 501):
    model2.step_day()
    for i, a in enumerate(model2.agents):
        if i < 5:
            agent_history.setdefault(i, []).append(a.last_choice)

for i in range(5):
    last20 = agent_history[i][-20:]
    vals, counts = np.unique(last20, return_counts=True)
    print(f'Agent {i}: last 20 days = {last20}')
    print(f'  Most common: {vals[np.argmax(counts)]} ({counts.max()}/20)')
```

Resultado: el agente 0 elige 10 fracciones distintas en 20 días, sin convergencia clara.

Se verificó también con 2000 días:

```python
model = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=42)
for day in range(1, 2001):
    model.step_day()
    if day in [500, 1000, 1500, 2000]:
        choices = [a.last_choice for a in model.agents]
        n_sub = 0
        gaps = []
        for a in model.agents:
            pm, pe = model.price_M, model.price_E
            best_pi = 0
            for f in a.fractions:
                s = min(a.storage_capacity, a.eta * f * a.qM_raw)
                pi = pm * (1-f)*a.qM_raw + pe * (a.qE_raw + s)
                if pi > best_pi:
                    best_pi = pi
            gap = (best_pi - a.profit) / best_pi * 100
            gaps.append(gap)
            if gap > 5:
                n_sub += 1
        print(f'Day {day}: mean={np.mean(choices):.3f}, subopt={n_sub}/30, gap={np.mean(gaps):.1f}%')
```

Resultados:
- Day 500:  mean=0.520, subopt=23/30, gap=16.8%
- Day 1000: mean=0.560, subopt=23/30, gap=14.9%
- Day 1500: mean=0.427, subopt=28/30, gap=21.3%
- Day 2000: mean=0.550, subopt=23/30, gap=15.2%

### Diagnóstico

La señal negativa reduce la atracción de la fracción elegida cuando es subóptima, pero el agente no recibe ninguna información sobre las alternativas. Solo sabe "esto fue malo", no "aquello habría sido mejor". Con 11 fracciones posibles y las atracciones de las no elegidas decayendo continuamente, el agente olvida lo aprendido sobre fracciones que no ha probado recientemente. El resultado es exploración aleatoria sin convergencia.

---

## 4. Segunda propuesta: normalización centrada en cero

### Idea

En vez de $\pi / \pi^{\max}$ (rango $[0, 1]$), usar $(\pi - \pi^{\max}) / \pi^{\max}$ (rango $[-1, 0]$):

$$\pi_i^{\text{norm}}(t) = \frac{\pi_i(t) - \pi_i^{\max}(t)}{\pi_i^{\max}(t)}$$

Así:

- Si la fracción elegida fue la óptima: señal = 0 (no cambia la atracción, solo decae)
- Si fue subóptima: señal negativa (reduce activamente la atracción de esa fracción)

### Interpretación económica

El agente no se pregunta "¿gané mucho?", sino "¿cuánto dejé de ganar?". Esto es análogo al concepto de *regret* en teoría de la decisión: la diferencia entre lo obtenido y lo mejor que se podría haber obtenido.

---

### Resultado de la normalización centrada en cero (solo fracción elegida)

Se implementó y se verificó con 2000 días. Los agentes exploran y la señal negativa castiga las malas elecciones, pero sigue sin converger: 23/30 agentes subóptimos con gap medio ~16%. La razón: sin información sobre las alternativas, el castigo solo produce exploración aleatoria, no dirigida.

---

## 5. Tercera propuesta: EWA (caso particular, actualizar todas las fracciones)

La conclusión del proceso anterior es que la normalización por beneficio máximo contrafactual es necesaria, pero insuficiente si solo se aplica a la fracción elegida. La extensión natural es usar el cálculo contrafactual para actualizar **todas** las fracciones. Además, tiene consistencia con lo esperable de la psicología de un agente: si sabe cuál es la mejor opción, en lugar de utilizarla solo para contextualizar qué tan buena es otra opción elegida, también debería cambiar el peso de dicha opción (y así con todas).

$$\text{Para cada } f \in \mathcal{F}: \quad \pi_i(f, t) = P_M(t) \cdot (1-f) \cdot \tilde{q}_i^M + P_E(t) \cdot \left(\tilde{q}_i^E + \min\{s_i,\; \eta_i \cdot f \cdot \tilde{q}_i^M\}\right)$$

$$\pi_i^{\text{norm}}(f, t) = \frac{\pi_i(f, t) - \pi_i^{\max}(t)}{\pi_i^{\max}(t)}$$

$$A_i(f, t+1) = (1 - \phi_i) \cdot A_i(f, t) + \phi_i \cdot \pi_i^{\text{norm}}(f, t) \quad \forall f \in \mathcal{F}$$

Esto combina:
- La normalización por máximo contrafactual
- La actualización de todas las fracciones con información contrafactual

Nótese que el modelo EWA completo de Camerer y Ho (1999) es más general: incluye un parámetro $\delta$ que pondera de forma distinta las acciones elegidas frente a las no elegidas, un factor de depreciación de la experiencia acumulada, y una normalización por el número de experiencias. Lo que aquí se implementa es un **caso particular** de la estructura EWA en el que todas las acciones se tratan simétricamente y la depreciación se controla únicamente por $\phi_i$.

### Interpretación económica

El agente observa los precios del mercado al final del día y calcula ex-post cuánto habría ganado con cada fracción posible. Es un supuesto más fuerte que el aprendizaje por tanteo puro (el agente "sabe" los contrafactuales), pero es razonable en un mercado con precios públicos: dado que los precios son observables, un agente puede calcular qué habría pasado con otra decisión.

### Justificación del camino recorrido

Se llegó a esta formulación por un proceso iterativo:
1. Se detectó la fijación por desajuste de escala
2. Se normalizó por π_max → resolvió fijación pero no convergencia
3. Se centró en cero (π-π_max)/π_max → añadió castigo pero sin dirección
4. Se extendió a todas las fracciones → aprendizaje completo y dirigido

Cada paso resolvió un problema e hizo visible el siguiente.

### Variantes de normalización probadas

Se probaron tres variantes de la señal de aprendizaje con la actualización contrafactual de todas las fracciones:

**Variante A**: $(\pi(f) - \pi^{\max}) / \pi^{\max}$ — Rango $[-1, 0]$

Resultado: las diferencias entre fracciones se comprimen demasiado. Con atracciones en un rango de 0.26, la softmax produce una distribución casi uniforme. Los agentes siguen explorando sin concentrarse en las buenas fracciones. Después de 500 días: 22/30 subóptimos, gap medio 12.5%.

```python
# Verificación de las probabilidades softmax con la variante A
# Atracciones del agente 0 tras 200 días:
# f=0.0: -0.274, f=0.5: -0.102, f=0.8: -0.013, f=1.0: -0.054
# Con beta=3.95: P(f=0.8)=0.131, P(f=0.0)=0.047
# Distribución casi uniforme -> sin convergencia
```

**Variante B**: $\pi(f) - \pi^{\max}$ — Sin normalizar (regret absoluto)

Caracterización inicial (incorrecta): se reportó que la softmax se colapsaba instantáneamente en el día 2 sin dinámica de aprendizaje. Esta caracterización fue corregida posteriormente (ver sección 9).

Resultado real: con actualización de todas las fracciones, el regret sin normalizar es **matemáticamente equivalente** a usar el beneficio bruto (la diferencia es una constante aditiva igual para todas las fracciones, y la softmax es invariante ante constantes aditivas). Ambas formulaciones convergen al óptimo individual con dinámica gradual.

Los detalles de esta corrección y la verificación empírica se documentan en la sección 9.

**Variante C (definitiva)**: $(\pi(f) - \pi^{\max}) / \sigma(\pi)$ — Normalización por desviación típica

Resultado: las diferencias se mantienen informativas (rango de ~3 unidades de desviación) sin ser excesivas. La softmax produce una distribución concentrada en las buenas fracciones pero con exploración residual. Convergencia gradual en ~25-50 días.

```python
from model import MarketModel, DEFAULT_PARAMS
import numpy as np

model = MarketModel(params=DEFAULT_PARAMS, storage_enabled=True, seed=42)
for day in range(1, 501):
    model.step_day()
    if day in [1, 5, 10, 25, 50, 100, 200, 500]:
        choices = [a.last_choice for a in model.agents]
        print(f'Day {day:3d}: mean={np.mean(choices):.3f}, std={np.std(choices):.3f}')

# Resultados:
# Day   1: mean=0.437, std=0.308
# Day   5: mean=0.860, std=0.174
# Day  25: mean=0.933, std=0.122
# Day 100: mean=0.960, std=0.071
# Day 500: mean=0.923, std=0.117
# Subóptimos: 5/30, gap medio: 1.8%

# Distribución softmax del agente 0 (día 500):
# f=0.8: P=0.546, f=0.7: P=0.197, f=0.9: P=0.187
# Concentrada pero con exploración residual
```

### Comprobación: ¿es necesario el aprendizaje contrafactual?

Se probó la normalización por desviación típica **sin** actualizar todas las fracciones (solo la elegida, como en el modelo original). Es decir, aislando el efecto de la normalización del efecto del aprendizaje contrafactual.

```python
# Test autocontenido: normalización por std + solo fracción elegida
# Semilla: random.seed(42), np.random.seed(42)
# Parámetros: DEFAULT_PARAMS (N=30, DAYS=500)
# Regla:
#   pi_norm = (pi_chosen - pi_max) / std(pi_all)
#   A(f_chosen) = (1-phi)*A(f_chosen) + phi*pi_norm
#   A(f_other)  = (1-phi)*A(f_other)              [solo decae]
```

Resultado tras 500 días:
- Day 500: mean=0.560, std=0.324
- Subóptimos (>5% gap): 22/30, gap medio: 14.8%

**Conclusión**: la normalización por std **no es suficiente** por sí sola. Resuelve el problema de fijación (los agentes exploran), pero no produce convergencia hacia el óptimo porque la información contrafactual no llega a las fracciones no elegidas. El agente solo sabe "esto fue malo" pero no "aquello habría sido mejor".

**Ambos componentes son necesarios (conclusión precipitada, ver más adelante)**:
- La normalización por std controla la escala de la señal
- El aprendizaje contrafactual da dirección al aprendizaje

### Comparación de normalizaciones (con aprendizaje contrafactual)

Se compararon tres normalizaciones, todas con actualización contrafactual de todas las fracciones. Test autocontenido, seed=42, N=30, 500 días, parámetros por defecto.

**Min-max**: `pi_norm(f) = (pi(f) - pi_min) / (pi_max - pi_min)`, rango [0, 1].

**Z-score**: `pi_norm(f) = (pi(f) - pi_media) / pi_std`, rango aprox [-2, +2].

**Regret/std** (nuestra): `pi_norm(f) = (pi(f) - pi_max) / pi_std`, rango aprox [-3, 0].

| Normalización | Subóptimos | Gap medio |
|---|---|---|
| Min-max [0,1] | 14/30 | 7.0% |
| Z-score [-2,+2] | 4/30 | 2.2% |
| Regret/std [-3,0] | 4/30 | 2.2% |

Z-score y regret/std dan resultados idénticos. Esto es esperable: la diferencia entre ambas es una constante aditiva (la media), y la softmax depende solo de las diferencias entre atracciones, no de sus valores absolutos. Formalmente, si $A'(f) = A(f) + c$ para todo $f$, entonces $\exp(\beta A'(f)) / \sum \exp(\beta A'(f')) = \exp(\beta A(f)) / \sum \exp(\beta A(f'))$.

Min-max es inferior porque las señales siempre positivas refuerzan todas las fracciones, ralentizando la diferenciación entre buenas y malas.

### Formulación definitiva

$$\pi_i(f, t) = P_M(t) \cdot (1-f) \cdot \tilde{q}_i^M + P_E(t) \cdot \left(\tilde{q}_i^E + \min\{s_i,\; \eta_i \cdot f \cdot \tilde{q}_i^M\}\right)$$

$$\pi_i^{\max}(t) = \max_{f \in \mathcal{F}} \pi_i(f, t)$$

$$\sigma_i(t) = \text{std}\left(\{\pi_i(f, t)\}_{f \in \mathcal{F}}\right)$$

$$r_i(f, t) = \frac{\pi_i(f, t) - \pi_i^{\max}(t)}{\sigma_i(t)}$$

$$A_i(f, t+1) = (1 - \phi_i) \cdot A_i(f, t) + \phi_i \cdot r_i(f, t) \quad \forall f \in \mathcal{F}$$

---

## 6. Bug adicional: semilla aleatoria no funcional

Se descubrió que el parámetro `seed` de Mesa no controla el módulo `random` de Python, que es el que usa el modelo para generar shocks meteorológicos, atracciones iniciales y elecciones. Esto implica que las simulaciones no eran reproducibles.

```python
# Verificación: misma seed, resultados distintos
from model import MarketModel, DEFAULT_PARAMS
for run in range(2):
    model = MarketModel(params=DEFAULT_PARAMS, seed=0)
    model.step_day()
    choices = [a.last_choice for a in model.agents]
    print(f'Run {run}: {choices[:5]}')
# Resultado: elecciones distintas entre ejecuciones
```

Este bug se debe corregir haciendo que el modelo controle explícitamente el estado del generador aleatorio de Python.

---

## 7. Propuesta de Paco: solo elegida, sin decaimiento, z-score

### Motivación

Tras la reunión con los tutores, se ha planteado una variante distinta de las exploradas hasta ahora:

1. **Solo actualizar la atracción de la fracción elegida** (como en el modelo original).
2. **No aplicar decaimiento a las demás fracciones** (eliminar el factor $(1 - \phi)$ del resto). Las fracciones no elegidas conservan intacta la atracción que tenían.
3. **Normalizar con z-score**: $(\pi - \bar{\pi}) / \sigma$, restando la media y dividiendo entre la desviación típica de los contrafactuales.

### Por qué z-score y no regret/std en este caso

Con la actualización contrafactual de todas las fracciones, z-score y regret/std son equivalentes: la diferencia entre ambos es una constante aditiva que se aplica a TODAS las atracciones por igual, y la softmax es invariante ante desplazamientos constantes.

Sin embargo, cuando solo se actualiza la fracción elegida, esa constante aditiva se aplica solo a UNA atracción, no a todas. La softmax ya no la cancela. En concreto:

- Con **regret/std** la señal es siempre $\leq 0$ (nula para la fracción óptima, negativa para el resto). Si solo actualizamos la elegida, su atracción solo puede bajar o quedarse igual. Esto penaliza sistemáticamente la exploración: el agente "castiga" cualquier fracción que prueba (salvo que sea la óptima), pero nunca "premia" una fracción buena.
- Con **z-score** la señal puede ser positiva (si la fracción elegida estuvo por encima de la media) o negativa (si estuvo por debajo). Esto permite premiar las buenas elecciones y castigar las malas, produciendo convergencia dirigida.

### Formulación

Se calculan los contrafactuales para todas las fracciones (necesarios para obtener media y desviación típica), pero solo se actualiza la atracción de la fracción elegida:

$$\bar{\pi}_i(t) = \frac{1}{|\mathcal{F}|} \sum_{f \in \mathcal{F}} \pi_i(f, t), \qquad \sigma_i(t) = \text{std}\left(\{\pi_i(f, t)\}_{f \in \mathcal{F}}\right)$$

$$z_i(t) = \frac{\pi_i(t) - \bar{\pi}_i(t)}{\sigma_i(t)}$$

$$A_i(f, t+1) = \begin{cases} (1 - \phi_i) \cdot A_i(f, t) + \phi_i \cdot z_i(t), & \text{si } f = f_i(t) \\ A_i(f, t), & \text{si } f \neq f_i(t) \end{cases}$$

### Resultados comparativos

Test autocontenido. Parámetros: `DEFAULT_PARAMS` (N=30, T=500). Promedio sobre 10 semillas (seed 0-9).

```python
# Código de comparación: 4 configuraciones x 10 semillas
# (ver script completo en la sección anterior de estas notas)
# Cada configuración ejecuta 500 días con N=30 agentes y parámetros por defecto.
```

| Configuración | Subóptimos (media) | Gap medio | Fracción media |
|---|---|---|---|
| Contrafactual + regret/std | 5.1/30 | 2.6% | 0.894 |
| Contrafactual + z-score | 5.1/30 | 2.6% | 0.894 |
| **Solo elegida sin decay + z-score** | **4.9/30** | **2.5%** | **0.895** |
| Solo elegida sin decay + regret/std | 6.2/30 | 2.9% | 0.880 |

### Análisis

- Las dos variantes contrafactuales (regret/std y z-score) dan resultados idénticos, confirmando la equivalencia teórica por invarianza de la softmax ante constantes aditivas.
- La variante del tutor (solo elegida + z-score) obtiene resultados ligeramente mejores que la contrafactual, con 4.9/30 agentes subóptimos y un gap medio del 2.5%.
- La variante solo elegida + regret/std es peor (6.2/30 subóptimos), confirmando que en este caso la normalización NO es equivalente y que z-score es superior.
- La eliminación del decaimiento es clave: el agente recuerda lo que aprendió de cada fracción cuando la probó. Si una fracción dio buen resultado, su atracción se mantiene indefinidamente hasta que el agente la pruebe de nuevo.

### Ventajas de la propuesta del tutor

1. **Menor supuesto de racionalidad**: el agente no "calcula" contrafactuales. Solo observa su propio resultado y lo compara con la distribución de posibles resultados para normalizar. La información contrafactual se usa para la escala, no para actualizar atracciones.
2. **Aprendizaje por experiencia directa**: el agente descubre las buenas fracciones probándolas, no deduciéndolas. Esto es más realista desde el punto de vista de racionalidad acotada.
3. **Memoria persistente**: al no depreciar las fracciones no elegidas, el agente conserva la información de pruebas pasadas. Esto evita el problema de "olvidar" fracciones buenas que se probaron hace tiempo.
4. **Convergencia comparable**: a pesar de la menor información por iteración, los resultados son prácticamente iguales (o ligeramente mejores) que la actualización contrafactual completa.

---

## 8. Variante "bandit feedback" sin normalización (propuesta posterior del tutor)

### Motivación

En un correo posterior a la primera reunión, el tutor ha propuesto explorar una variante adicional: aplicar la regla "solo elegida, sin decay" pero usando el **beneficio bruto sin normalizar**, partiendo de **atracciones iniciales nulas** A(f, 0) = 0 para todas las fracciones.

La intuición teórica es elegante:
- La actualización A(f, t+1) = A(f, t) + phi·(pi(f, t) - A(f, t)) es matemáticamente equivalente a (1-phi)·A(f, t) + phi·pi(f, t)
- El punto fijo de esta dinámica es A = pi (la atracción converge al beneficio esperado)
- Si A ya refleja correctamente el beneficio (A = pi), no hay razón para modificarla
- A = 0 representa el beneficio "garantizado" si el productor no hace nada — es un anclaje natural

### Formulación

Para la fracción elegida:

$$A_i(f_i(t), t+1) = A_i(f_i(t), t) + \phi_i \cdot (\pi_i(t) - A_i(f_i(t), t))$$

Para las fracciones no elegidas: sin cambio.

Condiciones iniciales: A(f, 0) = 0 para todo f.

### Resultado

Test autocontenido. Parámetros: DEFAULT_PARAMS (N=30, T=500). Promedio sobre 10 semillas (seed 0-9).

```
Aciertos (Métrica 2): 5.2/30
Gap esperado (Métrica 3): 17.49%
Fracción media: 0.505
```

Comparado con la variante anterior del tutor (con normalización z-score):
- Aciertos: 4.9/30 vs 5.2/30
- Gap esperado: 2.5% vs 17.49%
- Fracción media: 0.895 vs 0.505

### Diagnóstico

La variante sin normalización **reproduce el problema de fijación original**. La razón es la misma que en el modelo original, agravada por la inicialización A(f, 0) = 0:

Tras el día 1 con phi = 0.10 y beneficio bruto pi ≈ 180:
- A(f_elegida, 1) = (1 - 0.10) · 0 + 0.10 · 180 = 18.0
- A(f_otras, 1) = 0 (sin decay y sin actualización)

Con beta ≈ 4: exp(4 · 18) = exp(72) ≈ 10³¹ → P(f_elegida) ≈ 1

El agente queda fijado en su elección aleatoria del día 1 y nunca explora otras fracciones. La atracción de f_elegida converge correctamente al beneficio esperado (~180), validando la intuición teórica del tutor, pero las atracciones de las demás fracciones permanecen en 0 indefinidamente porque nunca son seleccionadas.

### Trayectoria observada (agente 0, seed 42)

```
Day  1: choice=0.7, A(0.7)= 22.47, resto=0
Day  5: choice=0.7, A(0.7)= 85.48, resto=0
Day 50: choice=0.7, A(0.7)=188.04, resto=0  (convergencia al beneficio esperado)
Últimas 20 elecciones: [0.7] x 20
```

### Conclusión

La regla del tutor es **teóricamente correcta** (la atracción es un estimador insesgado del beneficio esperado), pero **numéricamente inviable** con los parámetros del modelo. El problema reside en la interacción entre tres elementos:

1. La escala del beneficio bruto (~180) frente a las atracciones iniciales (0)
2. La sensibilidad de la regla logit (beta en [1, 5])
3. La tasa de aprendizaje (phi en [0.05, 0.30])

Para que la regla del tutor funcionara sin normalización, harían falta valores extremadamente bajos de beta (exploración casi pura) o de phi (aprendizaje extremadamente lento), lo que comprometería la dinámica del modelo en otros aspectos. La normalización por z-score resuelve el problema preservando la intuición económica de "atracción = beneficio relativo esperado".


---

## 9. Corrección: la variante "todas las fracciones, sin normalizar" funciona

### Motivación de la verificación

Al recibir el correo del tutor proponiendo la regla "bandit feedback" (solo elegida + sin normalizar), surgió la pregunta de qué pasaría si esa misma regla se aplicara con actualización de **todas** las fracciones. Inicialmente se afirmó que esto produciría fijación instantánea (sección 5, variante B). Esta caracterización resultó ser incorrecta.

La caracterización inicial errónea de esta fue causada por confundir esta variante con otra prueba en la que solo se actualizaba la fracción elegida. El error se detectó al recibir la propuesta del tutor y querer compararla rigurosamente con todas las variantes anteriores. 

### Verificación matemática

Bajo actualización de todas las fracciones con decaimiento $(1 - \phi)$, las dos formulaciones siguientes son matemáticamente equivalentes:

- **Beneficio bruto**: A(f, t+1) = (1 - phi)·A(f, t) + phi·pi(f, t)
- **Regret sin normalizar**: A(f, t+1) = (1 - phi)·A(f, t) + phi·(pi(f, t) - pi_max(t))

La diferencia entre las dos atracciones (raw - regret) evoluciona como:

(A_raw - A_regret)(t+1) = (1 - phi)·(A_raw - A_regret)(t) + phi·pi_max(t)

Esta diferencia es **idéntica para todas las fracciones** en cada paso (porque pi_max(t) no depende de f). Por tanto, la diferencia entre A_raw(f) y A_regret(f) es la misma constante para todo f, y la softmax es invariante ante constantes aditivas.

### Verificación empírica

Test con 50 días, semilla 42, parámetros por defecto. Ambas variantes producen exactamente las mismas elecciones de los agentes y las mismas atracciones salvo una constante aditiva igual para todas las fracciones.

```
ALL FRACTIONS + RAW PROFIT + DECAY (50 dias):
Choices finales: [0.8 x3, 0.9 x3, 1.0 x24]

ALL FRACTIONS + REGRET (pi-pi_max) + DECAY (50 dias):
Choices finales: [0.8 x3, 0.9 x3, 1.0 x24]   <-- idénticas

Diferencia atracciones (raw - regret) por fracción:
f=0.0: diff=177.57
f=0.1: diff=177.57
...
f=1.0: diff=177.57   <-- constante, como predice la teoría
```

### Resultados

Con 500 días y 10 semillas:

```
ALL FRACTIONS + RAW PROFIT + DECAY:
Aciertos (Métrica 2): 28-30/30
Fracción media: 0.977
Dinámica: agentes parten de elección aleatoria día 1,
          se mueven a su óptimo individual entre días 5-25,
          se estabilizan ahí
```

Trayectoria del agente 0 (seed 42, stor_cap=0.54 → óptimo individual f=0.8):
- Días 1-10: f=0.7 (su elección aleatoria del día 1)
- Días 10-50: transición progresiva hacia f=0.8
- Días 50-500: estable en f=0.8 (su verdadero óptimo)

### Implicaciones

1. **La normalización por z-score no es estrictamente necesaria** si se usa actualización contrafactual de todas las fracciones. Bajo softmax, raw y regret son equivalentes.

2. **La regla del tutor sí funciona** si se aplica a todas las fracciones (no solo a la elegida). El problema de fijación en su variante "solo elegida" se debe a que las fracciones no elegidas nunca reciben información y se quedan en A=0, no a la falta de normalización.

3. **El verdadero diferenciador** entre variantes que funcionan y variantes que fallan es el aprendizaje contrafactual, no la normalización. Esto es, considerando que la normalización que utilizamos cuando no actualizamos todas las fracciones está teniendo en cuenta el resto de fracciones también aunque solo actualice una.

### Tabla comparativa actualizada

| Variante | Actualización | Normalización | Aciertos | Funciona |
|---|---|---|---|---|
| Original | Solo elegida + decay | Sin normalizar | 0/30 | No (fijación) |
| Bandit (tutor) | Solo elegida sin decay | Sin normalizar | 5/30 | No (fijación) |
| Solo elegida sin decay | Solo elegida sin decay | z-score | 28/30 | Sí |
| Solo elegida sin decay | Solo elegida sin decay | regret/std | 24/30 | Sí (algo peor) |
| Todas (raw) | Todas + decay | Sin normalizar | 28-30/30 | Sí |
| Todas (regret) | Todas + decay | Sin normalizar | 28-30/30 | Sí (idéntico al raw) |
| Todas (z-score / regret-std) | Todas + decay | Por std o media | 28-30/30 | Sí (idéntico bajo softmax) |
| Todas (min-max) | Todas + decay | $[0,1]$ | 16-20/30 | Funciona peor (señales positivas refuerzan todas) |

**Nota importante sobre la tabla anterior**: estos resultados se obtuvieron con los parámetros originales (N=30, alpha_M=0.7, alpha_E=0.3, D_M=60, D_E=120), que producen solución de esquina (f*=1.0). Los aciertos altos (28-30/30) reflejan convergencia al óptimo de esquina. La sección 10 analiza qué ocurre cuando se busca una solución interior.

---

## 10. Reparametrización: búsqueda de solución interior

### 10.1. Diagnóstico de la solución de esquina

Con los parámetros originales del modelo:

| Parámetro | Valor |
|---|---|
| N | 30 |
| $\alpha_M$, $\alpha_E$ | 0.7, 0.3 |
| $D_M$, $D_E$ | 60, 120 |
| $\eta$ | [0.85, 0.95] |

La producción solar total (con $\varepsilon = 1$ y capacidad media 1.0) es:

- Mañana: $30 \times 0{,}7 \times 1{,}0 = 21$ unidades (35% de $D_M = 60$)
- Tarde: $30 \times 0{,}3 \times 1{,}0 = 9$ unidades (7.5% de $D_E = 120$)

La solar es insuficiente para cubrir la demanda en ninguno de los dos periodos. El gas domina la formación de precios en ambos, y la convexidad de su función de costes ($\gamma_G = 1{,}3$) hace que el precio de la tarde sea desproporcionadamente mayor. El ratio $P_M / P_E \approx 0{,}58$, muy por debajo de $\bar{\eta} \approx 0{,}90$.

Consecuencia: almacenar es siempre rentable (la ganancia de precio al pasar energía a la tarde supera ampliamente las pérdidas de eficiencia). El óptimo individual de todos los agentes es $f = 1{,}0$ (o el máximo permitido por su capacidad de almacenamiento). Esto se verifica con simulaciones: tanto la regla contrafactual raw como la z-score solo elegida convergen a $f \approx 0{,}93$ (el margen respecto a 1.0 se explica por agentes con baterías pequeñas que saturan antes de $f = 1{,}0$).

Se verificó que el problema no es la restricción de batería: con stor_cap = 10 (batería ilimitada), todos los agentes tienen $f^* = 1{,}0$ y el ratio sigue en $\approx 0{,}60$. La insuficiencia de producción solar es la causa.

### 10.2. Búsqueda sistemática de parametrización

Se realizó un barrido sobre N, capacidad media ($\bar{c}$), $D_M$ y $D_E$, manteniendo $\alpha_M = 0{,}7$ y $\alpha_E = 0{,}3$ fijos (representan el ratio de producción mañana/tarde y no deben modificarse para cambiar el nivel de producción).

El criterio para solución interior es que exista un $f^* \in (0{,}05;\; 0{,}95)$ tal que $P_M(f^*) = \eta \cdot P_E(f^*)$, calculado con un agente representativo.

Selección de candidatos con $f^*$ entre 0.3 y 0.8 y ratio $P_M / (\eta P_E) \in [0{,}85;\; 1{,}05]$:

```
   N  c_avg   D_M   D_E    f*   PM/PE  Solar%M  Solar%E
  30   2.0    80   120   0.72   0.895     52%     15%     <-- candidato elegido
  30   2.0    60   100   0.74   0.894     70%     18%
  30   2.0    60    90   0.62   0.894     70%     20%
  30   1.5    60    90   0.72   0.899     52%     15%
  40   1.0    60    90   0.77   0.900     47%     13%
  50   1.0    80   120   0.80   0.898     44%     12%
```

Se eligió **N=30, $\bar{c} = 2{,}0$ ($c_i \in [1{,}6;\; 2{,}4]$), $D_M = 80$, $D_E = 120$** porque:
- Mantiene N=30
- Mantiene $D_E = 120$
- Solar cubre el 52% de la demanda matutina (realista: no satura el mercado de mañana en el baseline)
- f* numérico = 0.72, ratio 0.895

### 10.2.1. Cómo se calculó f* = 0.72 (y qué significa)

**Método**: barrido numérico, NO derivación analítica. Se asumió un agente representativo que acapara toda la producción solar (equivalente a que los N=30 agentes elijan todos la misma f). Para cada f de 0 a 1 (en pasos de 0.01) se calcularon los precios resultantes y se buscó la f donde $P_M(f) = \eta \cdot P_E(f)$.

```python
# Cálculo numérico del f* (agente representativo, sin shocks, sin stor_cap)
N, avg_cap, eta = 30, 2.0, 0.90
alpha_M, alpha_E = 0.7, 0.3
D_M, D_E = 80, 120
c0, alpha_G, gamma_G = 10, 0.5, 1.3

for f in [i/100 for i in range(101)]:
    solar_M = N * (1-f) * alpha_M * avg_cap
    solar_E = N * (alpha_E * avg_cap + eta * f * alpha_M * avg_cap)
    gas_M = D_M - solar_M
    gas_E = D_E - solar_E
    if gas_M <= 0 or gas_E <= 0:
        continue
    P_M = c0 + alpha_G * gas_M**gamma_G
    P_E = c0 + alpha_G * gas_E**gamma_G
    # Buscar f donde P_M = eta * P_E
    # Resultado: f* = 0.72, P_M = 131.1, P_E = 146.4, P_M/(eta*P_E) = 0.995
```

**Interpretación económica**: $f^*$ es la fracción de almacenamiento en la que un agente marginal es indiferente entre vender una unidad de energía solar por la mañana al precio $P_M$ o almacenarla (con pérdida $\eta$) para venderla por la tarde a $P_E$. En el equilibrio $P_M = \eta \cdot P_E$, la ganancia de precio al pasar energía a la tarde iguala exactamente las pérdidas de eficiencia.

**Equivalencia**: este cálculo es idéntico al óptimo de un solo agente que acaparase toda la producción solar. La pregunta del TFG es si los 30 agentes descentralizados, cada uno tomando decisiones independientes con información limitada, llegan al mismo punto.

**Limitaciones del cálculo** (pendientes de resolver en la sección 4.6 del TFG):
- Asume agentes homogéneos ($\eta = 0{,}90$ para todos, capacidad = 2.0 para todos)
- Asume f continuo (el modelo usa pasos discretos de $\Delta = 0{,}1$)
- No incluye shocks meteorológicos ($\varepsilon = 1$)
- No incluye restricción de capacidad de almacenamiento
- Asume equilibrio simétrico (todos eligen la misma f)
- **No está formalizado analíticamente**: es un resultado numérico, no una demostración. La derivación formal del equilibrio (agente único, 2 agentes Nash, N agentes) está pendiente de la sección 4.6.

### 10.3. Error de medición en pruebas intermedias

En las primeras simulaciones con la nueva parametrización, se reportó "0 agentes con f_opt interior" y se concluyó erróneamente que las reglas no funcionaban. El error consistió en medir el f óptimo contrafactual **del último día concreto de la simulación**, que depende de los precios de ese día específico. Si ese día la oscilación estocástica llevó los precios a una configuración extrema, el óptimo puntual puede ser $f = 0$ o $f = 1$ para todos los agentes, aunque la **media temporal** esté en torno a $f = 0{,}70$.

La métrica correcta es la media temporal de $f$ a lo largo de un bloque de días suficientemente largo, no el óptimo de un día aislado.

### 10.4. Prueba de convergencia con 1000 días

Parametrización: N=30, $c_i \in [1{,}6;\; 2{,}4]$, $D_M = 80$, $D_E = 120$, stor_cap = 10 (sin restricción de batería), $\eta \in [0{,}85;\; 0{,}95]$, $\phi \in [0{,}05;\; 0{,}3]$, $\beta \in [1;\; 5]$.

Semilla: seed=42. Atracciones iniciales: $A(f, 0) = 0$ para todo $f$.

```python
# Regla contrafactual raw:
# A(f, t+1) = (1-phi)*A(f,t) + phi*pi(f,t)   para todo f
# pi(f,t) = beneficio contrafactual con precios observados

# Regla z-score solo elegida sin decay:
# z = (pi_elegida - media(pi_all)) / std(pi_all)
# A(f_elegida, t+1) = (1-phi)*A(f_elegida, t) + phi*z
# A(f_otra, t+1) = A(f_otra, t)
```

Resultados por bloques de 100 días:

**Contrafactual raw**:

```
d   1- 100: mean=0.686, std=0.192, min=0.153, max=0.993
d 101- 200: mean=0.688, std=0.149, min=0.420, max=0.903
d 201- 300: mean=0.688, std=0.156, min=0.417, max=0.930
d 301- 400: mean=0.685, std=0.163, min=0.407, max=0.970
d 401- 500: mean=0.689, std=0.163, min=0.337, max=0.950
d 501- 600: mean=0.685, std=0.179, min=0.317, max=0.970
d 601- 700: mean=0.688, std=0.150, min=0.397, max=0.907
d 701- 800: mean=0.687, std=0.148, min=0.413, max=0.930
d 801- 900: mean=0.686, std=0.171, min=0.367, max=0.910
d 901-1000: mean=0.688, std=0.153, min=0.340, max=0.950
Global:     mean=0.687, std=0.163
```

**Z-score solo elegida sin decay**:

```
d   1- 100: mean=0.664, std=0.064, min=0.490, max=0.800
d 101- 200: mean=0.684, std=0.040, min=0.553, max=0.770
d 201- 300: mean=0.685, std=0.041, min=0.580, max=0.803
d 301- 400: mean=0.683, std=0.040, min=0.563, max=0.773
d 401- 500: mean=0.686, std=0.043, min=0.557, max=0.780
d 501- 600: mean=0.678, std=0.043, min=0.590, max=0.787
d 601- 700: mean=0.685, std=0.042, min=0.583, max=0.783
d 701- 800: mean=0.684, std=0.038, min=0.593, max=0.763
d 801- 900: mean=0.684, std=0.035, min=0.580, max=0.757
d 901-1000: mean=0.682, std=0.037, min=0.580, max=0.773
Global:     mean=0.681, std=0.044
```

### 10.5. CORRECCIÓN: la contrafactual raw entra en ciclo f=0 ↔ f=1

El análisis por bloques de 100 días (sección 10.4) mostraba una media de $\bar{f} \approx 0{,}687$ para la contrafactual raw, lo que inicialmente se interpretó como convergencia al $f^*$ teórico. Sin embargo, un examen día a día revela que esta media es un **artefacto de una distribución bimodal**, no una convergencia real.

Prueba detallada: misma parametrización (N=30, c=[1.6, 2.4], DM=80, DE=120, stor_cap=10), regla contrafactual raw, seed=42, 100 días. Se registra la distribución de elecciones de los 30 agentes en cada día.

```python
# Código: regla contrafactual raw, tracking dia a dia
# A(f, t+1) = (1-phi)*A(f,t) + phi*pi(f,t) para todo f
# seed=42, N=30, c=[1.6,2.4], DM=80, DE=120, stor_cap=10
```

Resultados seleccionados:

```
Day  1: f_mean=0.513 | f=0: 2 mid:26 f=1: 2 | PM/PE=0.668
Day  2: f_mean=0.980 | f=0: 0 mid: 4 f=1:26 | PM/PE=1.299
Day  3: f_mean=0.153 | f=0:14 mid:16 f=1: 0 | PM/PE=0.395
Day  4: f_mean=0.993 | f=0: 0 mid: 2 f=1:28 | PM/PE=1.355
Day  5: f_mean=0.730 | f=0: 2 mid:16 f=1:12 | PM/PE=0.936
...
Day 11: f_mean=0.987 | f=0: 0 mid: 3 f=1:27 | PM/PE=1.306
Day 12: f_mean=0.270 | f=0:16 mid:12 f=1: 2 | PM/PE=0.461
Day 13: f_mean=0.993 | f=0: 0 mid: 2 f=1:28 | PM/PE=1.286
...
Day 50: f_mean=0.933 | f=0: 0 mid: 4 f=1:26 | PM/PE=1.253
...
Day 90: f_mean=0.557 | f=0: 7 mid:13 f=1:10 | PM/PE=0.727
Day100: f_mean=0.530 | f=0:12 mid: 7 f=1:11 | PM/PE=0.692
```

**Diagnóstico**: el sistema oscila entre dos estados:

1. **Estado "todos almacenan"**: la mayoría de agentes elige f≈1.0. Esto retira toda la oferta solar de la mañana, disparando $P_M$ y hundiendo $P_E$. El ratio $P_M/P_E > 1$ — almacenar es un MAL negocio.

2. **Estado "nadie almacena"**: la mayoría reacciona eligiendo f≈0.0. Esto restaura la oferta solar matutina, hundiendo $P_M$ y disparando $P_E$. El ratio $P_M/P_E < \eta$ — almacenar vuelve a ser BUEN negocio.

El ciclo no es estrictamente alternante. Hay días en los que el sistema **pasa por el equilibrio**: por ejemplo, el día 5 tiene f_media=0.73 con PM/PE=0.94, muy cerca del f* teórico. Pero no puede quedarse ahí — al día siguiente la perturbación lo desplaza de nuevo.

La dificultad para mantenerse en el equilibrio está dada porque los agentes que el anterior periodo decidieron ir con su beneficio contrafactual a la tarde, ahora inciden en los precios de forma que lo rentable resulta ser pasar muy poco a la tarde. Esto a su vez incentiva a los agentes a mandarlo todo a la tarde de nuevo. Esto, sumado a las decisiones deterministas ($P(f^*) \approx 0{,}99$), hace imposible el suavizado. Todos los agentes saltan simultáneamente en la misma dirección.

La media temporal de $\bar{f} \approx 0{,}68$ es la media de esta distribución bimodal. **No es una convergencia al equilibrio interior**, es un artefacto del ciclo. La media no es 0.50 (como sería en un ciclo simétrico f=0↔f=1) porque el ciclo no es simétrico: los agentes pasan más días cerca de f=1 que de f=0, posiblemente porque la regla contrafactual raw con decay acumula más "memoria" de los periodos con f alto (donde los beneficios brutos son mayores).

**Nota sobre inicialización**: se descartó que el problema fuera de inicialización (A(f,0)=0 para todo f). El ciclo no es un artefacto transitorio del arranque — se mantiene indefinidamente a lo largo de 1000 días sin atenuarse (std por bloques de 100 días: 0.19, 0.15, 0.16, 0.16, 0.16, 0.18, 0.15, 0.15, 0.17, 0.15).

**Causa raíz**: la regla contrafactual raw produce señales tan grandes (~100-200 unidades de beneficio) que la softmax colapsa a $P(f^*) \approx 1{,}0$ en cada día. TODOS los agentes saltan simultáneamente a la misma fracción, magnificando la retroalimentación precios→decisiones→precios. No hay amortiguación.

### 10.6. La z-score solo elegida no entra en el ciclo

Con la misma parametrización, la regla z-score solo elegida (sin decay en las no elegidas) produce una dinámica cualitativamente distinta:

```
d   1- 100: mean=0.664, std=0.064, min=0.490, max=0.800
d 901-1000: mean=0.682, std=0.037, min=0.580, max=0.773
```

La distribución no es bimodal. Los agentes eligen fracciones intermedias (rango 0.49-0.80) y la dispersión se REDUCE con el tiempo. No hay ciclo f=0↔f=1.

**Mecanismo**: con la z-score, la señal está normalizada (~1 unidad de desviación típica), produciendo $P(f^*) \approx 0{,}57$ en vez de $\approx 0{,}99$. Esto introduce suficiente dispersión: en cada día, algunos agentes eligen f=0.6, otros f=0.8, otros f=0.7. Como no saltan todos al unísono, la retroalimentación precios→decisiones se amortigua y el sistema se mantiene estable cerca del equilibrio.

**Limitación**: la probabilidad de la fracción preferida ($\approx 0{,}57$) no aumenta significativamente aunque se refuerce con más periodos donde sigue siendo la mejor. Esto significa que los agentes mantienen exploración residual indefinidamente, lo que puede verse como una virtud (robustez ante cambios de entorno) o como un defecto (los agentes nunca llegan a estar "seguros" de su estrategia).

### 10.7. Tabla comparativa corregida

| Métrica | Contrafactual raw | Z-score solo elegida |
|---|---|---|
| Media global $\bar{f}$ | 0.687 | 0.681 |
| Desv. típ. global | 0.163 | 0.044 |
| Distribución día a día | **Bimodal** (f≈0 y f≈1) | **Unimodal** (centrada en ~0.68) |
| ¿Ciclo f=0↔f=1? | **Sí** — permanente | **No** |
| ¿Convergencia real al equilibrio? | **No** — media artefactual | **Sí** — convergencia gradual |
| P(f_prefer) por agente | ≈ 0.99 (determinista) | ≈ 0.57 (exploración residual) |

### 10.8. Implicaciones para la elección de regla

La contrafactual raw **no funciona para solución interior**. Funciona perfectamente cuando el óptimo es de esquina (f=1.0 para todos, como en la parametrización original), porque allí la retroalimentación precios→decisiones es estable: todos almacenan al máximo y los precios no se invierten. Pero cuando el óptimo es interior, la falta de amortiguación produce un ciclo inestable.

La z-score solo elegida sin decay **sí funciona para solución interior**, precisamente porque la exploración residual evita los saltos colectivos.

| Regla | Esquina (params originales) | Interior (params nuevos) |
|---|---|---|
| Contrafactual raw | Converge correctamente | **Ciclo f=0↔f=1** (inestable) |
| Z-score solo elegida sin decay | Converge correctamente | **Converge al equilibrio** (estable) |

### 10.9. Preguntas abiertas y variantes por probar

**Sobre la regla**: ¿existe una variante de la regla contrafactual (actualizando todas las fracciones) con algún tipo de amortiguación que evite el ciclo? Posibilidades no probadas:

- Reducir $\beta$ (más exploración en la softmax — reduce el determinismo de las decisiones)
- Reducir $\phi$ (la atracción cambia más despacio, menos reactivo a los precios de un solo día)
- Usar media móvil de precios en vez de precios del día (suaviza la señal)
- Contrafactual con normalización z-score (todas las fracciones + señal normalizada)
- Incluir alguno de los parámetros adicionales del EWA completo (Camerer y Ho, 1999), como el parámetro $\delta$ que pondera de forma diferente las acciones elegidas vs. las no elegidas, lo que podría evitar el colapso inicial de la softmax sin sacrificar la convergencia a largo plazo

**Sobre la parametrización**: los parámetros originales del modelo producen un escenario donde la solar cubre una parte menor de la demanda (realista), pero el resultado es trivial (almacenar todo lo posible). Se plantean dos opciones:

1. Aumentar la capacidad de producción solar para obtener solución interior (más interesante teóricamente)
2. Mantener los parámetros originales y analizar el escenario de esquina en términos de coste de oportunidad por falta de inversión en baterías (más realista pero menos rico analíticamente)

**Objetivo**: encontrar una regla de aprendizaje que lleve a los agentes al óptimo con independencia de las condiciones iniciales y de si el equilibrio es interior o de esquina.

### 10.10. Correspondencia con el tutor (correo del 21 de abril de 2026)

Se envió un correo al tutor (Francisco Álvarez) exponiendo:

1. La confirmación de que la contrafactual raw funciona para esquina pero no para interior
2. La naturaleza del ciclo f=0↔f=1 y por qué no es un problema de inicialización
3. Que el sistema pasa por el equilibrio (ej. día 5: f=0.73, PM/PE=0.94) pero no puede mantenerse
4. Que la z-score solo elegida sin decay sí funciona para interior
5. Las preguntas abiertas sobre variantes por probar y parametrización
6. La condición de equilibrio $P_M = \eta \cdot P_E$ y su interpretación intuitiva

Se solicitó discusión sobre la elección de regla y parametrización en la próxima reunión.
