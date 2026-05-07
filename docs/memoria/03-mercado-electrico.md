# 3. Descripción del mercado eléctrico y actores

En este capítulo se describe la estructura del mercado eléctrico considerada en el modelo, así como los agentes que participan en él y las reglas que determinan la formación de precios. El objetivo es definir con precisión los elementos fundamentales del sistema antes de introducir la dinámica de aprendizaje y adaptación que caracteriza al modelo basado en agentes.

El mercado se plantea como una representación simplificada, pero conceptualmente informada, del funcionamiento de un sistema eléctrico con alta penetración de energía solar y presencia de generación térmica de respaldo. Esta simplificación permite aislar y analizar de forma clara el papel del almacenamiento distribuido y su impacto sobre los precios y el uso de generación fósil.

## 3.1. Estructura temporal del mercado

El mercado eléctrico se organiza en una secuencia diaria de dos periodos claramente diferenciados:

- **Periodo de mañana** ($M$): caracterizado por una alta generación solar y una demanda relativamente baja.
- **Periodo de tarde** ($E$): caracterizado por una menor generación solar y una demanda más elevada.

Esta división temporal pretende capturar de forma estilizada uno de los principales retos de la integración de energías renovables: la desalineación entre los momentos de mayor generación solar y los picos de demanda eléctrica.

La demanda agregada en cada periodo se considera exógena y fija, denotándose por $D_M$ en el periodo de mañana y $D_E$ en el periodo de tarde, cumpliéndose que $D_E > D_M$. Esta asimetría es esencial para que exista un incentivo económico al almacenamiento de energía solar producida en el periodo de mañana para su venta posterior en el periodo de tarde.

Cada día constituye una unidad temporal completa del modelo. Al inicio de cada día, los productores solares toman decisiones estratégicas sobre el uso de su producción matutina, decisiones que afectarán tanto a la oferta en cada periodo como a la formación de precios.

## 3.2. Productores solares

El mercado está poblado por un conjunto de $N$ productores solares, que actúan como agentes independientes dentro del modelo. Cada productor solar se caracteriza por un conjunto de parámetros que determinan su capacidad productiva, su potencial de almacenamiento y su comportamiento estratégico.

En particular, cada agente solar $i$ dispone de una capacidad instalada $c_i$ que determina su nivel máximo de producción, y de una tecnología de almacenamiento asociada, caracterizada por una eficiencia $\eta_i$. Esta eficiencia recoge las pérdidas asociadas al ciclo de carga y descarga de la batería.

La producción de energía solar es estocástica y depende de condiciones meteorológicas variables. Formalmente, la producción bruta de energía del agente $i$ en cada periodo viene dada por:

$$\tilde{q}_i^M = \alpha_M \cdot c_i \cdot \varepsilon_i^t, \qquad \tilde{q}_i^E = \alpha_E \cdot c_i \cdot \varepsilon_i^t$$

donde $\alpha_M$ y $\alpha_E$ representan factores tecnológicos comunes que capturan la disponibilidad relativa de generación solar en cada periodo, y $\varepsilon_i^t$ es un shock idiosincrático asociado a las variaciones meteorológicas, definido alrededor de un valor medio igual a 1. Nótese que el mismo shock diario $\varepsilon_i^t$ afecta a ambos periodos, reflejando que las condiciones meteorológicas de un día determinan la producción global del agente. En concreto, este término se modeliza mediante una distribución uniforme en un intervalo centrado en dicho valor.

Los productores solares no presentan poder de mercado individual y actúan como tomadores de precios. Sin embargo, sus decisiones agregadas determinan de forma endógena la oferta total de energía solar en cada periodo y, por tanto, influyen indirectamente en los precios de mercado. En concreto, la única decisión estratégica que toman los agentes es la proporción de energía producida en el periodo de mañana que se destina al almacenamiento. Al inicio de cada día, cada agente decide qué parte de la energía generada se vende de forma inmediata y qué parte se almacena para su uso posterior, lo que afecta a la oferta agregada en ambos periodos y, en consecuencia, a la formación de precios.

El comportamiento de los agentes en este respecto, así como el proceso mediante el cual adaptan sus decisiones a lo largo del tiempo, se desarrollará detalladamente en el Capítulo 4.

## 3.3. Productor de gas

Además de los productores solares, el mercado incluye un productor de gas que actúa como generador de respaldo. Este productor entra en el mercado únicamente cuando la oferta total de energía solar es insuficiente para cubrir la demanda en alguno de los periodos.

El productor de gas se modeliza como un agente representativo con una función de coste marginal creciente, definida para $q > 0$ como:

$$c_G(q) = c_0 + \alpha_G \cdot q^{\gamma_G}$$

donde $q$ representa la cantidad total de energía producida mediante gas en el periodo correspondiente. Cuando no se requiere generación de gas ($q = 0$), el coste marginal no se evalúa y el precio de mercado se fija en cero. Esta especificación refleja el aumento progresivo del coste de generación conforme se recurre a unidades térmicas menos eficientes.

El productor de gas no toma decisiones estratégicas en el modelo: su producción se determina de manera residual para garantizar el equilibrio entre oferta y demanda. No obstante, su función de costes juega un papel central en la determinación del precio de mercado.

## 3.4. Mercado y formación de precios

La formación de precios en el mercado se basa en una regla de vaciado de mercado uniforme para cada periodo. En cada uno de los periodos $p \in \{M, E\}$, la oferta total de energía solar se define como la suma de la producción individual de los agentes solares:

$$Q^p(t) = \sum_{i=1}^{N} q_i^p(t)$$

Si la oferta solar total es suficiente para cubrir la demanda del periodo ($Q^p(t) \geq D_p$), el precio de mercado se fija en cero, reflejando una situación de abundancia de energía renovable.

En caso contrario ($Q^p(t) < D_p$), el productor de gas suministra la energía residual necesaria para cubrir la demanda, y el precio de mercado viene dado por su coste marginal:

$$P^p(t) = \begin{cases} 0, & \text{si } Q^p(t) \geq D_p \\ c_G\bigl(D_p - Q^p(t)\bigr), & \text{si } Q^p(t) < D_p \end{cases}$$

Esta regla de precios captura de manera simplificada el papel del gas como tecnología marginal en sistemas eléctricos con alta penetración de renovables, y permite analizar cómo las decisiones de almacenamiento afectan indirectamente al uso de generación fósil y a los precios finales.

## 3.5. Parametrización del modelo

En este apartado se presentan los valores numéricos asignados a los parámetros del modelo y se justifica su elección desde un punto de vista económico. El objetivo no es calibrar el modelo con datos reales de un mercado eléctrico específico, sino definir un entorno de simulación estilizado que permita observar de forma clara los mecanismos teóricos descritos en los capítulos anteriores.

### Estructura del mercado

La demanda exógena se fija en $D_M = 60$ para el periodo de mañana y $D_E = 120$ para el periodo de tarde, de modo que $D_E = 2 D_M$. Esta proporción de 1:2 captura de forma simplificada la asimetría característica de los sistemas eléctricos con alta penetración solar, en los que la demanda pico se concentra en las horas de menor disponibilidad de generación renovable. La magnitud absoluta de estos valores es arbitraria y puede interpretarse en unidades normalizadas; lo relevante es la relación entre ambos periodos, que genera un incentivo económico estructural al almacenamiento.

Los factores de producción solar se establecen en $\alpha_M = 0{,}7$ y $\alpha_E = 0{,}3$, reflejando una mayor disponibilidad de generación solar durante el periodo de mañana. Junto con los niveles de demanda, estos valores garantizan que la producción solar sea relativamente abundante por la mañana (donde puede aproximarse o superar la demanda) y escasa por la tarde (donde resulta claramente insuficiente por sí sola).

### Productor de gas

La función de coste marginal del gas viene dada por $c_G(q) = c_0 + \alpha_G \cdot q^{\gamma_G}$, con los parámetros $c_0 = 10$, $\alpha_G = 0{,}5$ y $\gamma_G = 1{,}3$. El término constante $c_0$ representa un coste fijo de arranque de las unidades térmicas, mientras que la potencia $\gamma_G > 1$ introduce convexidad en los costes, reflejando el encarecimiento progresivo de la generación térmica conforme se recurre a unidades menos eficientes. El valor $\gamma_G = 1{,}3$ genera una curva de costes moderadamente convexa, lo que permite que las decisiones de almacenamiento de los agentes produzcan variaciones apreciables en los precios sin que estos se disparen de forma excesiva.

### Productores solares

El modelo incluye $N = 30$ productores solares. Este número es suficiente para generar comportamientos agregados significativos y heterogeneidad entre agentes, sin imponer una carga computacional elevada. En el análisis de robustez (Capítulo 6) se examina cómo varían los resultados al modificar este parámetro.

Cada agente $i$ se inicializa con parámetros extraídos de distribuciones uniformes:

| Parámetro | Símbolo | Rango | Interpretación |
|---|---|---|---|
| Capacidad instalada | $c_i$ | $[0{,}8;\ 1{,}2]$ | Tamaño relativo de la planta solar |
| Capacidad de almacenamiento | $s_i$ | $[0{,}5;\ 2{,}0]$ | Límite físico de la batería |
| Eficiencia de la batería | $\eta_i$ | $[0{,}85;\ 0{,}95]$ | Ratio de energía recuperada del ciclo carga-descarga |
| Tasa de aprendizaje | $\phi_i$ | $[0{,}05;\ 0{,}3]$ | Peso de la experiencia reciente en la actualización |
| Sensibilidad de elección | $\beta_i$ | $[1{,}0;\ 5{,}0]$ | Grado de explotación vs. exploración |

La capacidad instalada se centra en torno a 1 con una variación del $\pm 20\%$, introduciendo diferencias moderadas entre productores. La eficiencia del almacenamiento se sitúa en el rango $[0{,}85;\ 0{,}95]$, coherente con los valores típicos de las baterías de ion-litio actuales.

Los parámetros de aprendizaje merecen especial atención. La tasa de aprendizaje $\phi_i$ determina la velocidad con la que el agente actualiza sus valoraciones: valores bajos implican un aprendizaje lento y estable, mientras que valores altos hacen que el agente responda de forma intensa a la experiencia más reciente. El parámetro de sensibilidad $\beta_i$ controla la relación entre exploración y explotación: valores bajos generan decisiones prácticamente aleatorias, mientras que valores altos concentran la elección en las estrategias con mayor atracción acumulada. Los rangos elegidos permiten que el sistema exhiba un espectro de comportamientos que va desde agentes conservadores (bajo $\phi$, bajo $\beta$) hasta agentes que reaccionan rápidamente y explotan la información disponible (alto $\phi$, alto $\beta$).

### Variabilidad meteorológica y granularidad de decisiones

El shock meteorológico $\varepsilon_i^t$ se modela como una variable aleatoria uniforme en el intervalo $[1 - \sigma;\ 1 + \sigma]$, con $\sigma = 0{,}15$. Este valor genera variaciones diarias en la producción solar de hasta un $\pm 15\%$, lo que introduce incertidumbre en los mercados sin dominar el comportamiento general del sistema.

La granularidad de las decisiones de almacenamiento se fija en $\Delta = 0{,}1$, de modo que los agentes eligen entre 11 fracciones posibles: $\mathcal{F} = \{0;\ 0{,}1;\ 0{,}2;\ \ldots;\ 1{,}0\}$. Esta discretización ofrece un compromiso razonable entre la flexibilidad de las decisiones y la complejidad del espacio de aprendizaje.

### Horizonte temporal

Las simulaciones se ejecutan a lo largo de $T = 200$ días. Este horizonte es suficiente para que el proceso de aprendizaje de los agentes alcance una fase de relativa estabilidad, tal como se verificará en el Capítulo 5 y se analizará con mayor detalle en los Capítulos 6 y 7.

La Tabla 3.1 recoge de forma resumida los valores de los principales parámetros del modelo.

**Tabla 3.1** — Parámetros del modelo

| Parámetro | Valor |
|---|---|
| Número de agentes ($N$) | 30 |
| Demanda mañana ($D_M$) | 60 |
| Demanda tarde ($D_E$) | 120 |
| Factor solar mañana ($\alpha_M$) | 0,7 |
| Factor solar tarde ($\alpha_E$) | 0,3 |
| Coste base gas ($c_0$) | 10 |
| Coeficiente gas ($\alpha_G$) | 0,5 |
| Exponente gas ($\gamma_G$) | 1,3 |
| Variabilidad meteorológica ($\sigma$) | 0,15 |
| Granularidad ($\Delta$) | 0,1 |
| Horizonte temporal ($T$) | 200 días |
