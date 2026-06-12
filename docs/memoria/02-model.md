# Capítulo 2. El mercado y los agentes

En este capítulo se describe la estructura del mercado eléctrico considerada en el modelo, así como los agentes que participan en él y las reglas que determinan la formación de precios. El objetivo es definir con precisión los elementos fundamentales del sistema antes de abordar el análisis de su comportamiento en los capítulos posteriores.

El mercado se plantea como una representación simplificada, pero conceptualmente informada, del funcionamiento de un sistema eléctrico con alta penetración de energía solar y presencia de generación térmica de respaldo. Esta simplificación permite aislar y analizar de forma clara el papel del almacenamiento distribuido y su impacto sobre los precios y el uso de generación fósil.

El presente capítulo define el entorno común a todo el trabajo: la estructura temporal del mercado, los productores solares y su tecnología de almacenamiento, el productor de gas como tecnología marginal, la regla de formación de precios y el mecanismo formal por el que cada productor solar reparte su producción matutina entre venta inmediata y almacenamiento. La cuestión que recorre el resto del trabajo es cómo se toma esa decisión en un entorno descentralizado e incierto: el Capítulo 3 ofrece una caracterización analítica de las soluciones bajo racionalidad estratégica, que poseen interés económico propio y proporcionan a la vez el referente contra el que se evalúa, en el Capítulo 4, el modelo de aprendizaje adaptativo que constituye el núcleo del trabajo.

## 2.1. Estructura temporal y agentes del mercado

El mercado eléctrico se organiza en una secuencia diaria de dos periodos claramente diferenciados:

- **Periodo de mañana** ($M$): caracterizado por una alta generación solar y una demanda relativamente baja.
- **Periodo de tarde** ($E$): caracterizado por una menor generación solar y una demanda más elevada.

Esta división temporal pretende capturar de forma estilizada uno de los principales retos de la integración de energías renovables: la desalineación entre los momentos de mayor generación solar y los picos de demanda eléctrica.

La demanda agregada en cada periodo se considera exógena y fija, denotándose por $D_M$ en el periodo de mañana y $D_E$ en el periodo de tarde, cumpliéndose que $D_E > D_M$. Esta asimetría es esencial para que exista un incentivo económico al almacenamiento de energía solar producida en el periodo de mañana para su venta posterior en el periodo de tarde.

Cada día constituye una unidad temporal independiente del modelo: los productores solares toman sus decisiones al inicio del día y los efectos se agotan en ese mismo día, por lo que el problema económico que cada agente resuelve es el mismo en todos los días. Estas decisiones afectarán tanto a la oferta en cada periodo como a la formación de precios.

El mercado está habitado por dos clases de agentes. Por una parte, un conjunto de $N$ productores solares heterogéneos, descritos en la sección 2.2, que generan energía renovable y disponen de tecnología de almacenamiento. Por otra, un único productor de gas, descrito en la sección 2.3, que actúa como generador de respaldo y entra en juego únicamente cuando la oferta solar agregada es insuficiente para cubrir la demanda del periodo correspondiente.

## 2.2. Productores solares: capacidad, almacenamiento, eficiencia

El mercado está poblado por un conjunto de $N$ productores solares, que actúan como agentes independientes dentro del modelo. Cada productor solar se caracteriza por un conjunto de parámetros que determinan su capacidad productiva, su potencial de almacenamiento y su comportamiento estratégico.

En particular, cada agente solar $i$ dispone de una capacidad instalada $c_i$ que escala su nivel de producción, y de una tecnología de almacenamiento caracterizada por una capacidad máxima $s_i$ y una eficiencia $\eta \in (0, 1)$ común a todos los agentes. La eficiencia recoge las pérdidas asociadas al ciclo de carga y descarga de la batería: por cada unidad de energía que el agente decide almacenar al inicio del día, solo $\eta$ unidades quedan disponibles para su venta vespertina. La capacidad $s_i$ impone una cota física superior a la cantidad que puede almacenarse cada día, con independencia de la decisión del agente.

La producción de energía solar es estocástica y depende de condiciones meteorológicas variables. Formalmente, la producción bruta de energía del agente $i$ en cada periodo viene dada por:

$$\tilde{q}_i^M = \alpha_M \cdot c_i \cdot \varepsilon_i^t, \qquad \tilde{q}_i^E = \alpha_E \cdot c_i \cdot \varepsilon_i^t$$

donde $\alpha_M$ y $\alpha_E$ representan factores tecnológicos comunes que capturan la disponibilidad relativa de generación solar en cada periodo, y $\varepsilon_i^t$ es un shock idiosincrático asociado a las variaciones meteorológicas, definido alrededor de un valor medio igual a 1. Nótese que el mismo shock diario $\varepsilon_i^t$ afecta a ambos periodos, reflejando que las condiciones meteorológicas de un día determinan la producción global del agente. En concreto, este término se modeliza mediante una distribución uniforme en un intervalo centrado en dicho valor.

La única decisión estratégica que toman los agentes es la proporción de la producción matutina que se destina al almacenamiento. Al inicio de cada día, cada agente decide qué parte de la energía generada por la mañana se vende de forma inmediata y qué parte se almacena para su uso posterior, lo que afecta a la oferta agregada en ambos periodos y, en consecuencia, a la formación de precios. El mecanismo formal por el que esta fracción determina la oferta efectiva en cada periodo se desarrolla en la sección 2.4; el modo en que cada agente elige dicha fracción se aborda en los Capítulos 3 y 4.

## 2.3. Productor de gas: función de coste marginal convexa

Además de los productores solares, el mercado incluye un productor de gas que actúa como generador de respaldo. Este productor entra en el mercado únicamente cuando la oferta total de energía solar es insuficiente para cubrir la demanda en alguno de los periodos.

El productor de gas se modeliza como un agente representativo con una función de coste marginal a tramos:

$$c_G(q) = \begin{cases} 0, & \text{si } q = 0 \\ \alpha_G \cdot q^{\gamma_G}, & \text{si } q > 0 \end{cases}$$

donde $q$ representa la cantidad de energía producida mediante gas en el periodo correspondiente y $\gamma_G > 1$. La rama positiva es estrictamente convexa: el coste de la siguiente unidad térmica crece de forma más que proporcional con la cantidad ya producida, reflejando el encarecimiento progresivo de la generación conforme se recurre a unidades menos eficientes. En ausencia de generación térmica ($q = 0$), el coste marginal es nulo y el precio del mercado correspondiente se fija en cero.

El productor de gas se comporta de forma perfectamente competitiva: cubre la demanda residual no atendida por los solares y fija el precio igual a su coste marginal, precio que también reciben los productores solares.

## 2.4. Mecanismo de almacenamiento (decisión f, oferta por periodo)

La decisión estratégica del agente $i$ en el día $t$ consiste en elegir la fracción de su producción matutina destinada al almacenamiento, $f_i(t)$. Por razones de tratabilidad —y para acotar el espacio sobre el que más adelante operarán las reglas de elección— esta fracción se restringe a un conjunto discreto:

$$\mathcal{F} = \left\{ 0,\; \Delta,\; 2\Delta,\; \ldots,\; 1 \right\}$$

donde $\Delta$ determina la granularidad de las decisiones posibles. Esta discretización permite capturar decisiones de almacenamiento sin incurrir en mayores complejidades de cálculo en el proceso de optimización ni en la dinámica de aprendizaje que se introducirán más adelante.

El almacenamiento permite al agente trasladar parte de la energía producida en el periodo de mañana al periodo de tarde, donde la demanda y los precios esperados son mayores. Dada una producción bruta matutina $\tilde{q}_i^M$ y una fracción de almacenamiento $f_i(t) \in \mathcal{F}$, la cantidad de energía efectivamente almacenada por el agente viene dada por:

$$S_i(t) = \min\bigl\{s_i,\; \eta \cdot f_i(t) \cdot \tilde{q}_i^M\bigr\}$$

donde $\eta$ representa la eficiencia del ciclo de carga y descarga de la batería (las pérdidas se aplican en el momento del almacenamiento) y $s_i$ es la capacidad máxima de almacenamiento del agente.[^perdidas]

[^perdidas]: De las $f_i(t) \cdot \tilde{q}_i^M$ unidades brutas que el agente decide almacenar al inicio del día, solo $\eta \cdot f_i(t) \cdot \tilde{q}_i^M$ quedan efectivamente en la batería; la diferencia $(1 - \eta)\, f_i(t)\, \tilde{q}_i^M$ se pierde en el ciclo de carga. La capacidad $s_i$ está expresada por tanto en términos de energía efectivamente almacenable (post-pérdidas), y la batería satura cuando $f_i(t)\, \tilde{q}_i^M \geq s_i / \eta$: el agente debe sacrificar más oferta matutina de la que finalmente llega a la tarde.

Como consecuencia, la energía efectivamente ofertada por el agente en cada periodo es:

- en el periodo de mañana:

$$q_i^M(t) = \bigl(1 - f_i(t)\bigr) \cdot \tilde{q}_i^M$$

- en el periodo de tarde:

$$q_i^E(t) = \tilde{q}_i^E + S_i(t)$$

Este mecanismo introduce una interdependencia temporal entre las decisiones del agente, ya que la elección realizada al inicio del día afecta simultáneamente a la oferta en ambos periodos y, por tanto, a los precios de mercado.

## 2.5. Formación de precios y vaciado del mercado

La formación de precios en el mercado se basa en una regla de vaciado de mercado uniforme para cada periodo. En cada uno de los periodos $p \in \{M, E\}$, la oferta total de energía solar se define como la suma de la energía efectivamente ofertada por los agentes solares (sección 2.4):

$$Q^p(t) = \sum_{i=1}^{N} q_i^p(t)$$

Si la oferta solar total es suficiente para cubrir la demanda del periodo ($Q^p(t) \geq D_p$), el precio de mercado se fija en cero, reflejando una situación de abundancia de energía renovable.

En caso contrario ($Q^p(t) < D_p$), el productor de gas suministra la energía residual necesaria para cubrir la demanda, y el precio de mercado viene dado por su coste marginal:

$$P^p(t) = \begin{cases} 0, & \text{si } Q^p(t) \geq D_p \\ c_G\bigl(D_p - Q^p(t)\bigr), & \text{si } Q^p(t) < D_p \end{cases}$$

Esta regla de precios captura de manera simplificada el papel del gas como tecnología marginal en sistemas eléctricos con alta penetración de renovables, y permite analizar cómo las decisiones de almacenamiento afectan indirectamente al uso de generación fósil y a los precios finales.

La dinámica del sistema en cada día puede resumirse en dos pasos:

1. Cada agente $i$ elige de forma simultánea su fracción de almacenamiento $f_i(t) \in \mathcal{F}$, sin observar todavía el shock meteorológico $\varepsilon_i^t$ del día ni las elecciones del resto de agentes.
2. Una vez realizado el shock, se determinan las ofertas $q_i^M(t)$ y $q_i^E(t)$, se agregan en $Q^M(t)$ y $Q^E(t)$, se vacían los mercados conforme a la regla anterior y se fijan los precios $P_M(t)$ y $P_E(t)$ junto con los beneficios diarios de cada agente.

La regla por la que cada agente elige $f_i(t)$ —bien como solución de un problema de optimización estratégica, bien como decisión emergente de un proceso de aprendizaje adaptativo— es el objeto de los Capítulos 3 y 4 respectivamente.
