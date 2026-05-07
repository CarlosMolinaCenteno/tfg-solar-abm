# 4. Modelo basado en agentes: fundamentos teóricos

En este capítulo se presenta el modelo basado en agentes que constituye el núcleo analítico del trabajo. A partir de la estructura de mercado definida en el capítulo anterior, se formaliza el comportamiento de los productores solares, su proceso de toma de decisiones y la dinámica de aprendizaje que gobierna la evolución del sistema a lo largo del tiempo.

El enfoque basado en agentes permite representar de forma explícita la heterogeneidad de los productores, así como la adaptación progresiva de sus decisiones en un entorno incierto. A diferencia de modelos estáticos u optimizadores, el sistema no converge necesariamente a un equilibrio impuesto ex ante, sino que este emerge endógenamente como resultado de la interacción entre agentes y mercado.

## 4.1. Representación del agente solar

Cada productor solar se modeliza como un agente independiente que toma decisiones de forma descentralizada. El estado del agente $i$ en cada periodo viene determinado por:

- su capacidad instalada $c_i$,
- la eficiencia de su sistema de almacenamiento $\eta_i$,
- un conjunto de variables internas asociadas al aprendizaje,
- la información de precios observada en periodos anteriores.

La decisión fundamental del agente consiste en determinar qué fracción de su producción solar matutina destinar al almacenamiento, con el objetivo de maximizar sus beneficios diarios. Formalmente, el espacio de decisiones del agente viene dado por un conjunto discreto de fracciones:

$$\mathcal{F} = \left\{ 0,\; \Delta,\; 2\Delta,\; \ldots,\; 1 \right\}$$

donde $\Delta$ determina la granularidad de las decisiones posibles. Esta discretización permite capturar decisiones de almacenamiento sin incurrir en mayores complejidades de cálculo en el proceso de optimización de los agentes.

A partir de esta decisión, el agente determina la cantidad de energía vendida en cada periodo y, en consecuencia, sus ingresos diarios.

## 4.2. Mecanismo de almacenamiento

El almacenamiento permite al agente trasladar parte de la energía producida en el periodo de mañana al periodo de tarde, donde la demanda y los precios esperados son mayores.

Dada una producción bruta matutina $\tilde{q}_i^M$ y una fracción de almacenamiento $f_i(t) \in \mathcal{F}$, la cantidad de energía efectivamente almacenada por el agente viene dada por:

$$S_i(t) = \min\bigl\{s_i,\; \eta_i \cdot f_i(t) \cdot \tilde{q}_i^M\bigr\}$$

donde $\eta_i$ representa la eficiencia del ciclo de carga y descarga de la batería (las pérdidas se aplican en el momento del almacenamiento) y $s_i$ es la capacidad máxima de almacenamiento del agente.

Como consecuencia, la energía efectivamente ofertada por el agente en cada periodo es:

- en el periodo de mañana:

$$q_i^M(t) = \bigl(1 - f_i(t)\bigr) \cdot \tilde{q}_i^M$$

- en el periodo de tarde:

$$q_i^E(t) = \tilde{q}_i^E + S_i(t)$$

Este mecanismo introduce una interdependencia temporal entre las decisiones del agente, ya que la elección realizada al inicio del día afecta simultáneamente a la oferta en ambos periodos y, por tanto, a los precios de mercado.

## 4.3. Regla de aprendizaje adaptativo

Los agentes no conocen a priori cuál es la estrategia óptima de almacenamiento. En su lugar, aprenden de forma adaptativa a partir de la experiencia, utilizando un mecanismo de aprendizaje por refuerzo basado en atracciones (*reinforcement learning*). Cada agente mantiene una atracción $A_i(f, t)$ asociada a cada fracción de almacenamiento $f \in \mathcal{F}$, que representa la valoración acumulada de dicha estrategia en función de los beneficios observados hasta el momento.

### Beneficio realizado y beneficios contrafactuales

El beneficio diario efectivamente obtenido por el agente $i$, dada la fracción elegida $f_i(t)$, es:

$$\pi_i(t) = P_M(t) \cdot q_i^M(t) + P_E(t) \cdot q_i^E(t)$$

Al final del día, una vez observados los precios de mercado $P_M(t)$ y $P_E(t)$, el agente puede calcular también el beneficio que habría obtenido con cualquier otra fracción de almacenamiento $f \in \mathcal{F}$. Este beneficio *contrafactual* se define como:

$$\pi_i(f, t) = P_M(t) \cdot (1 - f) \cdot \tilde{q}_i^M + P_E(t) \cdot \left[\tilde{q}_i^E + \min\bigl\{s_i,\; \eta_i \cdot f \cdot \tilde{q}_i^M\bigr\}\right]$$

Dado que los precios de mercado son públicos, el agente dispone de toda la información necesaria para evaluar retrospectivamente la calidad de cada fracción posible. Sea $\pi_i^{\max}(t) = \max_{f \in \mathcal{F}} \pi_i(f, t)$ el beneficio óptimo contrafactual del agente en el día $t$, y $\sigma_i(t)$ la desviación típica del conjunto $\{\pi_i(f, t)\}_{f \in \mathcal{F}}$.

### Normalización por coste de oportunidad estandarizado

Para que la regla de actualización produzca una dinámica de aprendizaje bien formada, es necesario que la señal de refuerzo tenga una escala compatible con el rango de las atracciones y con el parámetro de sensibilidad $\beta_i$. Si la señal es demasiado grande en valor absoluto, la regla de decisión logit se colapsa hacia una elección casi determinista tras pocas iteraciones (fijación prematura); si es demasiado pequeña, la dinámica es indistinguible de una elección aleatoria (ausencia de aprendizaje).

La normalización adoptada combina dos elementos: el coste de oportunidad respecto al óptimo contrafactual y una estandarización por la dispersión de los beneficios contrafactuales del día:

$$r_i(f, t) = \frac{\pi_i(f, t) - \pi_i^{\max}(t)}{\sigma_i(t)}$$

La señal $r_i(f, t)$ es nula para la fracción óptima del día y negativa para el resto. Cuanto peor sea una fracción en términos relativos, más negativa será su señal. La estandarización por $\sigma_i(t)$ garantiza que la escala de la señal se adapte automáticamente a la variabilidad de los beneficios del día: en días con precios extremos (gran dispersión entre fracciones) la señal se atenúa, mientras que en días con escasa diferenciación entre estrategias la señal se amplifica, preservando en todos los casos la información relativa sobre el ranking de las fracciones.

### Actualización de las atracciones

Una vez calculada la señal normalizada, el agente actualiza las atracciones de **todas** las fracciones en el espacio de decisiones:

$$A_i(f, t+1) = (1 - \phi_i) \cdot A_i(f, t) + \phi_i \cdot r_i(f, t) \qquad \forall f \in \mathcal{F}$$

donde $\phi_i \in (0, 1)$ es el parámetro de aprendizaje del agente, que controla la importancia relativa de la experiencia reciente frente al pasado. Un valor alto de $\phi_i$ implica que el agente da más peso a los resultados más recientes, mientras que un valor bajo favorece una acumulación más gradual de información.

Esta regla difiere de los esquemas de refuerzo clásicos, en los que solo se actualiza la atracción de la acción efectivamente elegida. En el presente modelo, el uso de los beneficios contrafactuales permite que el agente aprenda simultáneamente sobre todas las estrategias posibles a partir de la información de precios del día. Esta formulación puede entenderse como un caso particular del modelo *Experience-Weighted Attraction* (EWA) de Camerer y Ho (1999), que generaliza distintos esquemas de aprendizaje por refuerzo y por creencias en un marco unificado. En nuestro caso, todas las acciones se tratan simétricamente y la depreciación de la experiencia pasada se controla exclusivamente mediante $\phi_i$.

### Regla de decisión

La elección de la fracción de almacenamiento en cada día se realiza mediante una regla logit, de forma que la probabilidad de seleccionar una fracción $f$ viene dada por:

$$\Pr\bigl[f_i(t) = f\bigr] = \frac{\exp\bigl[\beta_i \cdot A_i(f, t)\bigr]}{\displaystyle\sum_{f' \in \mathcal{F}} \exp\bigl[\beta_i \cdot A_i(f', t)\bigr]}$$

donde $\beta_i$ es un parámetro de sensibilidad que regula el equilibrio entre exploración y explotación. Valores bajos de $\beta_i$ inducen decisiones más aleatorias, mientras que valores elevados conducen a una selección más determinista de las estrategias con mayor atracción.

Con este esquema se consigue capturar procesos de aprendizaje gradual y adaptación estratégica en un entorno incierto y dinámico. La combinación de la actualización contrafactual y de la normalización por coste de oportunidad estandarizado garantiza que los agentes extraigan información útil de cada observación de precios sin incurrir en fijación prematura ni en exploración indefinida.

## 4.4. Dinámica del sistema

La compleja dinámica del sistema nace de la interacción entre agentes en el mercado. Las decisiones individuales de almacenamiento afectan a la oferta agregada en cada periodo, lo que influye en los precios de mercado. Estos precios determinan los beneficios obtenidos por los agentes, que a su vez actualizan sus atracciones y condicionan decisiones futuras.

De este modo, el sistema evoluciona a través de una secuencia de días en los que:

1. los agentes toman decisiones de almacenamiento,
2. se determina la oferta agregada y los precios en cada periodo,
3. los agentes observan los resultados y actualizan su comportamiento.

Esta dinámica puede dar lugar a patrones emergentes, como la convergencia hacia estrategias de almacenamiento similares, ciclos de comportamiento o resultados dependientes de los parámetros de aprendizaje.

## 4.5. Escenario sin baterías

Como referencia, se considera un escenario alternativo en el que los productores solares no disponen de almacenamiento. En este caso, la fracción de almacenamiento es nula para todos los agentes ($f_i(t) = 0 \;\forall i, t$), y toda la energía producida se vende en el periodo correspondiente.

Este escenario actúa como base y permite evaluar de forma comparativa el impacto de la introducción del almacenamiento distribuido. La comparación entre ambos escenarios resulta clave para analizar cómo cambian los precios, el uso de generación de gas y los beneficios de los agentes cuando se introduce la posibilidad de desplazar energía en el tiempo.

## 4.6. Análisis teórico del equilibrio

En los apartados anteriores las decisiones de almacenamiento emergen de un proceso adaptativo: los agentes no resuelven un problema de optimización, sino que ajustan sus elecciones a partir de la experiencia. Este apartado construye el referente teórico contra el que se contrastará el equilibrio emergente del modelo: la fracción de almacenamiento que maximizaría los beneficios si el agente pudiese resolver el problema directamente.

El análisis se desarrolla en dos niveles. Primero se estudia el caso de un agente único, que internaliza completamente el efecto de sus decisiones sobre los precios y que coincide con el resultado de $N$ agentes que cooperan como cártel. Después se introduce la interacción estratégica entre $N$ agentes simétricos como un juego de Nash, recuperando como caso límite ($N \to \infty$) el supuesto de competencia perfecta empleado en el Capítulo 3.

#### Simplificaciones comunes

A lo largo de la sección se trabaja bajo tres simplificaciones que no alteran la estructura económica del problema y que se usarán también en 4.6.2:

1. **Análisis determinista**: el shock meteorológico se fija en su esperanza, $\varepsilon = 1$, de modo que las producciones brutas son constantes. Como $\varepsilon$ es i.i.d. y entra de forma multiplicativa, el análisis preserva la estructura del problema en esperanza.
2. **Separabilidad temporal**: si se prescinde de la dinámica adaptativa (las atracciones $A(f,t)$ son la única variable de estado intertemporal), maximizar el beneficio agregado equivale a maximizar el beneficio diario.
3. **Régimen interior**: se asume batería no saturada y gas presente en ambos periodos. Las soluciones de borde se discuten al final.

### 4.6.1. Agente único (cártel): fracción óptima de almacenamiento

Bajo un único productor solar, el agente concentra toda la oferta renovable y sus decisiones determinan por completo la energía solar disponible en cada periodo. Aunque este escenario se aleja de la hipótesis de competencia del Capítulo 3, aísla la lógica decisional sin la complicación de la interacción estratégica. El resultado coincide con el de $N$ agentes que cooperan o actúan como cártel.

#### Beneficio en función de la fracción de almacenamiento

Las cantidades vendidas, las cantidades de gas y los precios pueden expresarse en función de $f$:

$$q^M(f) = (1 - f) \tilde{q}^M, \qquad q^E(f) = \tilde{q}^E + \eta f \tilde{q}^M$$
$$g^p(f) = D_p - q^p(f), \qquad P_p(f) = c_0 + \alpha_G \bigl[g^p(f)\bigr]^{\gamma_G}, \qquad p \in \{M, E\}$$

El beneficio diario es entonces $\pi(f) = P_M(f) q^M(f) + P_E(f) q^E(f)$, que recoge dos canales: la reasignación directa de cantidades entre periodos y el impacto indirecto de esa reasignación sobre los precios.

#### Derivada y descomposición económica

Aplicando la regla del producto y la de la cadena, y agrupando $\tilde{q}^M$ como factor común, la derivada $d\pi/df$ se separa de forma natural en dos bloques (el detalle paso a paso se recoge en el Anexo A):

$$\frac{d\pi}{df} = \tilde{q}^M \cdot \Bigl\{ \underbrace{\eta P_E(f) - P_M(f)}_{\text{arbitraje temporal}} \;+\; \underbrace{\alpha_G \gamma_G \bigl[ q^M(f)\, g^M(f)^{\gamma_G - 1} - \eta\, q^E(f)\, g^E(f)^{\gamma_G - 1} \bigr]}_{\text{efecto sobre precios inframarginales}} \Bigr\}$$

Esta forma agrupada hace transparente la lectura económica:

- **Arbitraje temporal** $\eta P_E - P_M$: almacenar una fracción adicional $df$ obliga a renunciar a vender $\tilde{q}^M df$ en la mañana al precio $P_M$ a cambio de vender $\eta \tilde{q}^M df$ en la tarde al precio $P_E$. Si $\eta P_E > P_M$, almacenar resulta rentable y el término empuja $f$ al alza.
- **Efecto sobre precios inframarginales**: como el agente concentra toda la oferta solar, modificar $f$ desplaza los precios. Reducir $q^M$ aumenta $P_M$, lo que **revaloriza las $q^M$ unidades restantes** (sumando $\alpha_G \gamma_G\, q^M g^{M,\gamma_G - 1}$); aumentar $q^E$ reduce $P_E$, lo que **devalúa las $q^E$ unidades vendidas en la tarde** (restando $\alpha_G \gamma_G \eta\, q^E g^{E,\gamma_G - 1}$). Las potencias $\alpha_G \gamma_G g^{p,\gamma_G - 1}$ son la sensibilidad del precio en el periodo $p$ a una variación marginal de la oferta.

#### Condición de primer orden

Como $\tilde{q}^M > 0$, anular $d\pi/df$ equivale a anular el corchete. Reordenando se obtiene la (CPO):

$$P_M(f^*) - \eta P_E(f^*) \;=\; \alpha_G \gamma_G \bigl\{ q^M(f^*)\, g^M(f^*)^{\gamma_G - 1} - \eta\, q^E(f^*)\, g^E(f^*)^{\gamma_G - 1} \bigr\} \qquad (\text{CPO})$$

El lado izquierdo es la cuña de arbitraje (cuánto cuesta dejar de vender en la mañana frente a la mañana corregida por eficiencia); el lado derecho es la cuña de poder de mercado, esto es, el efecto neto del agente sobre sus precios inframarginales. Ambas cuñas se igualan en el óptimo. Esta es la análoga, en clave de almacenamiento intradiario, de la regla clásica del monopolista que internaliza el impacto inframarginal de sus decisiones sobre los precios.

#### Caso límite: agente precio-aceptante

Si los precios fueran insensibles a la oferta del agente, el efecto sobre precios desaparece y la (CPO) colapsa a la **condición de arbitraje pura**:

$$P_M(f^*) = \eta P_E(f^*)$$

Un agente con poder de mercado se desviará de este punto en la dirección que indique el signo del efecto precio en su entorno.

#### Régimen con batería saturada

Si $\eta f \tilde{q}^M \geq s$, la energía almacenada queda fijada en $S = s$: incrementos adicionales de $f$ reducen $q^M$ pero ya no aumentan $q^E$. La derivada se simplifica a $d\pi/df = -\tilde{q}^M [P_M - \alpha_G \gamma_G q^M g^{M,\gamma_G-1}]$, que es estrictamente negativa siempre que el ingreso marginal en la mañana lo sea. En consecuencia, si la (CPO) interior arrojase un valor superior, el óptimo se localiza en la cota $f^*_{\text{borde}} = s / (\eta \tilde{q}^M)$.

#### Concavidad y resolución numérica

El cálculo de la segunda derivada (Anexo A) muestra que $\pi(f)$ es estrictamente cóncava en el régimen interior siempre que las ratios $q^M/g^M$ y $q^E/g^E$ se mantengan por debajo de $2/(\gamma_G - 1) \approx 6{,}7$. Con los parámetros del modelo, donde la oferta solar es minoritaria respecto a la cobertura por gas, esta condición se cumple holgadamente. La (CPO) no admite solución cerrada para $\gamma_G = 1{,}3$; la resolución numérica y la comparación con el modelo basado en agentes se aborda en el Capítulo 7.

### 4.6.2. $N$ agentes simétricos: equilibrio de Nash

Cuando la oferta solar se reparte entre varios productores, ninguno internaliza por completo el efecto de sus decisiones sobre los precios: cada uno elige tomando como dadas las decisiones del resto. La solución natural es el equilibrio de Nash (Fudenberg y Tirole, 1991). El análisis se plantea directamente para $N$ agentes simétricos; el caso $N = 2$ aparece como instancia particular y el límite $N \to \infty$ recupera el supuesto de competencia perfecta del Capítulo 3.

#### Planteamiento del juego

Considérense $N$ productores con parámetros tecnológicos comunes $c$, $\eta$ y $s$, que eligen simultáneamente $f_i \in [0, 1]$. Las cantidades **individuales** vendidas dependen solo de la decisión propia, mientras que la **oferta agregada** y los precios dependen de todas:

$$q_i^M(f_i) = (1 - f_i)\tilde{q}^M, \qquad q_i^E(f_i) = \tilde{q}^E + \eta f_i \tilde{q}^M$$
$$Q^p = \sum_{j=1}^N q_j^p, \qquad g^p = D_p - Q^p, \qquad P_p = c_0 + \alpha_G [g^p]^{\gamma_G}, \quad p \in \{M, E\}$$

#### CPO del agente $i$

El beneficio del agente $i$ es $\pi_i = P_M q_i^M + P_E q_i^E$. La diferencia esencial respecto al cártel es que, al subir $f_i$, el agente modifica los precios pero **solo internaliza el efecto sobre sus propias cantidades** $q_i^M, q_i^E$, no sobre las del resto. Repitiendo la derivación del apartado 4.6.1 (detalle en el Anexo A), la condición de primer orden tiene exactamente la misma forma, sustituyendo la cantidad del cártel por la individual:

$$P_M - \eta P_E \;=\; \alpha_G \gamma_G \bigl\{ q_i^M(f_i)\, g^{M,\gamma_G - 1} - \eta\, q_i^E(f_i)\, g^{E,\gamma_G - 1} \bigr\} \qquad (\text{CPO}_i)$$

Imponiendo simetría, $f_1 = \cdots = f_N = f^N$, las cantidades agregadas satisfacen $Q^p = N \cdot q_i^p(f^N)$ y la (CPO$_i$) se reduce a una única ecuación implícita en $f^N$.

#### Estructura unificada y dilución del poder de mercado

Las tres caracterizaciones del óptimo (cártel, Nash con $N$ agentes y precio-aceptante) comparten la misma forma:

$$P_M - \eta P_E \;=\; \alpha_G \gamma_G \bigl\{ \kappa^M\, g^{M,\gamma_G - 1} - \eta \kappa^E\, g^{E,\gamma_G - 1} \bigr\}$$

donde $\kappa^p$ es la cantidad inframarginal que el agente representativo internaliza:

| Régimen | $\kappa^M$ | $\kappa^E$ |
|---|---|---|
| Cártel ($N=1$ ó cooperación) | $Q^M$ | $Q^E$ |
| Nash con $N$ agentes | $Q^M / N$ | $Q^E / N$ |
| Precio-aceptante ($N \to \infty$) | $0$ | $0$ |

La cuña de poder de mercado se reduce **linealmente con $N$**: cada agente solo internaliza la fracción $1/N$ del efecto que su decisión tiene sobre los precios. La fracción de equilibrio se desplaza por tanto monótonamente con $N$:

$$f^*_{\text{cártel}} \;\leq\; f^N \;\leq\; f^*_{\text{precio-aceptante}}$$

El cártel restringe colectivamente el almacenamiento para no hundir $P_E$ ni elevar $P_M$ sobre la totalidad de su oferta; los agentes Nash compiten parcialmente por capturar la renta intradiaria, almacenando más; y el precio-aceptante ignora el efecto sobre los precios y almacena hasta agotar el arbitraje $P_M = \eta P_E$. La estructura es formalmente análoga a la del oligopolio de Cournot: a mayor número de agentes simétricos, menor el margen de monopolio individual y más competitivo el resultado.

El caso $N = 2$ se obtiene sustituyendo directamente $\kappa^p = Q^p / 2$, sin necesidad de un tratamiento separado.

#### Convergencia al precio-aceptante ($N \to \infty$)

Manteniendo la oferta agregada $Q^p$ constante (escalando inversamente la capacidad individual de modo que $N \cdot c$ permanezca fijo), la cantidad vendida por cada agente $q_i^p = Q^p / N$ tiende a cero, mientras que $g^p$ y los precios $P_p$ permanecen acotados. El lado derecho de la (CPO$_i$) se anula, y la ecuación de equilibrio converge a $P_M(f^*) = \eta P_E(f^*)$, esto es, al **arbitraje puro del precio-aceptante**.

Este resultado fundamenta el supuesto de competencia adoptado en el Capítulo 3: los productores solares se consideraron tomadores de precios precisamente porque ese es el comportamiento asintótico del juego cuando el número de agentes es grande, situación característica de los mercados eléctricos con alta penetración solar distribuida. La formalización rigurosa del límite (reescritura de la CPO con factor $1/N$ explícito y argumento de convergencia vía Bolzano–Weierstrass) se recoge en el Anexo A.

#### Existencia, unicidad y resolución numérica

La concavidad estricta de $\pi_i$ en $f_i$ se preserva bajo las condiciones del apartado 4.6.1, que se vuelven incluso menos restrictivas a medida que $N$ aumenta. La continuidad de la mejor respuesta sobre el dominio compacto $[0,1]$ garantiza la existencia del Nash por el teorema de Brouwer, y la monotonía de la función auxiliar $\Phi(f) := \partial \pi_i / \partial f_i \big|_{f_1 = \cdots = f_N = f}$ garantiza la unicidad del equilibrio simétrico (Anexo A). El equilibrio $f^N$ existe y es único, y se resuelve numéricamente como una familia de soluciones parametrizada por $N$.

Conviene subrayar que la búsqueda numérica del Nash homogéneo actualmente implementada en el código del modelo emplea la aproximación $P_M / P_E = \eta$, equivalente al límite precio-aceptante. La (CPO$_i$) derivada aquí permite cuantificar el sesgo introducido por dicha aproximación cuando $N$ es finito. El cálculo concreto y la comparación con los resultados del modelo basado en agentes se aborda en el Capítulo 7.
