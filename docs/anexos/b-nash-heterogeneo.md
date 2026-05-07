# Anexo B. Equilibrio de Nash con jugadores heterogéneos

Los apartados 4.6.2 y 4.6.3 caracterizan el equilibrio de Nash bajo el supuesto de que todos los productores comparten parámetros tecnológicos idénticos. El modelo basado en agentes implementado en este trabajo, en cambio, asigna a cada productor parámetros heterogéneos extraídos de distribuciones uniformes (Capítulo 3, sección 3.5). Para que el referente teórico pueda compararse directamente con los resultados emergentes del modelo, este anexo extiende el análisis al caso heterogéneo. La extensión preserva la estructura formal de la condición de primer orden del apartado 4.6.2 pero rompe la simetría del equilibrio: cada agente elige una fracción distinta $f_i^*$, monótonamente decreciente en su capacidad instalada.

El desarrollo se organiza en dos pasos. La sección B.1 considera heterogeneidad únicamente en la capacidad instalada $c_i$, manteniendo $\eta$ y $s$ comunes (con $s$ suficientemente grande para que la batería no sature en equilibrio). La sección B.2 incorpora heterogeneidad en la capacidad de almacenamiento $s_i$, lo que introduce una frontera de saturación distinta para cada agente y un kink en la derivada parcial de los beneficios.

## B.1. Heterogeneidad en la capacidad instalada

### B.1.1. Notación y planteamiento

Considérense $N$ agentes con capacidades instaladas heterogéneas $c_1, c_2, \ldots, c_N > 0$, eficiencia común $\eta$ y capacidad de almacenamiento $s$ grande (régimen interior). Las producciones brutas son ahora individuales:

$$\tilde{q}_i^M = \alpha_M \cdot c_i, \qquad \tilde{q}_i^E = \alpha_E \cdot c_i$$

Las cantidades vendidas en cada periodo dependen de la decisión propia y de la capacidad propia:

$$q_i^M(f_i) = (1 - f_i) \tilde{q}_i^M, \qquad q_i^E(f_i) = \tilde{q}_i^E + \eta f_i \tilde{q}_i^M$$

mientras que la oferta agregada y los precios siguen determinándose por la suma sobre todos los agentes:

$$Q^p(\mathbf{f}) = \sum_{i=1}^{N} q_i^p(f_i), \qquad p \in \{M, E\}$$

$$g^p(\mathbf{f}) = D_p - Q^p(\mathbf{f}), \qquad P_p(\mathbf{f}) = c_0 + \alpha_G \bigl[g^p(\mathbf{f})\bigr]^{\gamma_G}$$

donde $\mathbf{f} = (f_1, \ldots, f_N)$ es el vector de estrategias.

### B.1.2. Best-response y condición de primer orden del agente $i$

El cálculo de la derivada parcial $\partial \pi_i / \partial f_i$ es estructuralmente idéntico al del Anexo A.4. La única diferencia es que la producción bruta del agente $i$ es ahora $\tilde{q}_i^M$ —dependiente de su capacidad propia— en lugar del valor común $\tilde{q}^M$:

$$\frac{\partial q_i^p}{\partial f_i} = \frac{\partial Q^p}{\partial f_i}, \qquad \frac{\partial P_M}{\partial f_i} = \alpha_G \gamma_G \bigl[g^M\bigr]^{\gamma_G - 1} \tilde{q}_i^M, \qquad \frac{\partial P_E}{\partial f_i} = -\alpha_G \gamma_G \eta \bigl[g^E\bigr]^{\gamma_G - 1} \tilde{q}_i^M$$

Aplicando la regla del producto a $\pi_i = P_M \cdot q_i^M + P_E \cdot q_i^E$ y agrupando $\tilde{q}_i^M$ como factor común:

$$\frac{\partial \pi_i}{\partial f_i} = \tilde{q}_i^M \cdot \Bigl\{ \alpha_G \gamma_G \cdot q_i^M \bigl[g^M\bigr]^{\gamma_G - 1} - P_M - \alpha_G \gamma_G \eta \cdot q_i^E \bigl[g^E\bigr]^{\gamma_G - 1} + \eta P_E \Bigr\}$$

La condición de primer orden $\partial \pi_i / \partial f_i = 0$, dado que $\tilde{q}_i^M > 0$, equivale a anular la expresión entre llaves:

$$P_M(\mathbf{f}) - \eta P_E(\mathbf{f}) \;=\; \alpha_G \gamma_G \cdot \Bigl\{ q_i^M(f_i) \bigl[g^M(\mathbf{f})\bigr]^{\gamma_G - 1} - \eta q_i^E(f_i) \bigl[g^E(\mathbf{f})\bigr]^{\gamma_G - 1} \Bigr\} \qquad (\text{CPO}_i)$$

La forma es exactamente la misma que la del apartado 4.6.2, con dos diferencias importantes:

1. Las cantidades inframarginales $q_i^M, q_i^E$ son **individuales** y dependen de la capacidad propia del agente.
2. Los precios y cantidades de gas dependen del **vector completo** $\mathbf{f}$ a través de la oferta agregada heterogénea.

### B.1.3. Sistema de equilibrio

El equilibrio de Nash heterogéneo es un vector $\mathbf{f}^* \in [0, 1]^N$ que satisface simultáneamente las $N$ condiciones (CPO$_i$). Definiendo el residuo del agente $i$:

$$\mathcal{R}_i(\mathbf{f}) := \bigl[P_M(\mathbf{f}) - \eta P_E(\mathbf{f})\bigr] - \alpha_G \gamma_G \cdot \Bigl\{ q_i^M(f_i) \bigl[g^M(\mathbf{f})\bigr]^{\gamma_G - 1} - \eta q_i^E(f_i) \bigl[g^E(\mathbf{f})\bigr]^{\gamma_G - 1} \Bigr\}$$

el sistema de equilibrio es:

$$\mathcal{R}_i(\mathbf{f}^*) = 0, \qquad i = 1, \ldots, N$$

es decir, $N$ ecuaciones no lineales en $N$ incógnitas. Una observación útil: el primer corchete $P_M - \eta P_E$ es común a todos los agentes (depende solo de la oferta agregada). Restando dos ecuaciones cualesquiera, (CPO$_i$) − (CPO$_j$), se obtiene la **condición de igualación de los ingresos marginales individuales**:

$$\Bigl( q_i^M - q_j^M \Bigr) \bigl[g^M\bigr]^{\gamma_G - 1} \;=\; \eta \Bigl( q_i^E - q_j^E \Bigr) \bigl[g^E\bigr]^{\gamma_G - 1}$$

Esta restricción, válida para todo par $(i, j)$, liga las cantidades vendidas individuales con la estructura de precios agregada pero no resuelve directamente $f_i^*$ en función de $f_j^*$ porque las capacidades $c_i$ y $c_j$ son distintas.

### B.1.4. Heurística de monotonía

En equilibrio, los agentes con mayor capacidad instalada tienden a almacenar **menos** que los pequeños. La intuición es la siguiente: aumentar $f_i$ tiene un coste de poder de mercado proporcional a $\tilde{q}_i^M = \alpha_M c_i$, ya que la cuña en (CPO$_i$) escala linealmente con $c_i$. Los agentes grandes, al internalizar más cuña, son más reacios a almacenar; los pequeños, al sentir menos su impacto sobre los precios, almacenan más. En el límite $c_i / \sum_j c_j \to 0$ (agente muy pequeño respecto al agregado), la cuña individual se hace despreciable y el agente se aproxima al comportamiento precio-aceptante, $P_M = \eta P_E$, condición que es común a todos los agentes en el equilibrio heterogéneo.

Este resultado es la versión continua del factor $1/N$ del apartado 4.6.3: con heterogeneidad, cada agente diluye su cuña en proporción a su tamaño relativo respecto al agregado, no de forma uniforme.

### B.1.5. Resolución numérica

El sistema $\mathcal{R}_i(\mathbf{f}) = 0$ no admite solución cerrada y se resuelve numéricamente. La estrategia adoptada en este trabajo es:

1. **Punto inicial**: el equilibrio simétrico $f^N$ obtenido de `solve_nash_simetricos` con la capacidad media $\bar{c} = \frac{1}{N}\sum_i c_i$ y el resto de parámetros comunes. Bajo heterogeneidad leve, la solución heterogénea está cerca de la simétrica y la convergencia local es cuadrática.

2. **Solver**: `scipy.optimize.least_squares` con bounds $[0, 1]^N$. La elección de un solver de mínimos cuadrados con cotas (en lugar de un buscador de raíces puro como `fsolve`) es deliberada: garantiza que la solución permanezca en el dominio admisible y maneja de forma natural las soluciones de borde, que aparecerán en B.2 al considerar saturación.

3. **Homotopía** (en caso de no convergencia desde el simétrico): interpolar gradualmente entre el problema simétrico y el heterogéneo:

$$c_i(\lambda) = (1 - \lambda) \bar{c} + \lambda c_i, \qquad \lambda = 0, 0{,}1, 0{,}2, \ldots, 1$$

resolviendo cada subproblema usando la solución del anterior como punto inicial.

La existencia y unicidad del equilibrio heterogéneo no se demuestra formalmente en este anexo. Bajo los parámetros del modelo (heterogeneidad moderada, régimen interior bien definido), la concavidad estricta de cada $\pi_i$ en $f_i$ se preserva con los mismos argumentos del Anexo A.5, y la teoría clásica de juegos (Fudenberg y Tirole, 1991, Cap. 1) garantiza la existencia del equilibrio. La unicidad se verifica numéricamente probando distintos puntos iniciales.

## B.2. Heterogeneidad en la capacidad de almacenamiento

### B.2.1. Frontera de saturación heterogénea

Cuando los agentes tienen capacidades de almacenamiento $s_i$ distintas, cada uno tiene su propia frontera de saturación:

$$f_{\text{sat}, i} := \frac{s_i}{\eta \tilde{q}_i^M} = \frac{s_i}{\eta \alpha_M c_i}$$

Para $f_i \leq f_{\text{sat}, i}$ el agente está en régimen interior (la batería absorbe toda la energía que se le envía); para $f_i > f_{\text{sat}, i}$, la batería está llena y la energía almacenada queda fijada en $S_i = s_i$, independiente de $f_i$.

### B.2.2. Kink en la derivada parcial

La función de beneficios $\pi_i$ es continua en $f_i$, pero su derivada parcial $\partial \pi_i / \partial f_i$ presenta una discontinuidad en $f_{\text{sat}, i}$:

- **Para $f_i < f_{\text{sat}, i}$** (régimen interior): la (CPO$_i$) de B.1.2 se aplica.
- **Para $f_i > f_{\text{sat}, i}$** (régimen saturado): $\partial q_i^E / \partial f_i = 0$, y la derivada parcial se reduce a:

$$\frac{\partial \pi_i}{\partial f_i} \bigg|_{\text{saturado}} = -\tilde{q}_i^M \cdot \Bigl\{ P_M - \alpha_G \gamma_G \cdot q_i^M \bigl[g^M\bigr]^{\gamma_G - 1} \Bigr\}$$

El término entre llaves es el ingreso marginal de la oferta matutina del agente, estrictamente positivo cuando $P_M > 0$ y la cuña individual no excede al precio. Por tanto $\partial \pi_i / \partial f_i < 0$ en todo el régimen saturado: incrementar $f_i$ por encima de $f_{\text{sat}, i}$ reduce las ventas matutinas sin aumentar las vespertinas.

En consecuencia, el óptimo del agente $i$ se localiza en:

- $f_i^* = $ raíz interior de (CPO$_i$), si dicha raíz cumple $\leq f_{\text{sat}, i}$;
- $f_i^* = f_{\text{sat}, i}$ en caso contrario (saturación de borde).

### B.2.3. Algoritmo numérico con saturación

Las condiciones de Karush–Kuhn–Tucker (KKT) del problema con saturación pueden expresarse como:

$$\mathcal{R}_i(\mathbf{f}^*) \leq 0, \qquad f_i^* \leq f_{\text{sat}, i}, \qquad \mathcal{R}_i(\mathbf{f}^*) \cdot \bigl(f_{\text{sat}, i} - f_i^*\bigr) = 0$$

En el régimen interior, $f_i^* < f_{\text{sat}, i}$ implica $\mathcal{R}_i(\mathbf{f}^*) = 0$. En saturación, $f_i^* = f_{\text{sat}, i}$ y se admite $\mathcal{R}_i(\mathbf{f}^*) \leq 0$ (el agente querría almacenar más pero no puede).

La implementación práctica en este trabajo procede en una sola etapa: el solver `scipy.optimize.least_squares` se ejecuta con bounds individuales:

$$f_i \in \bigl[0, \min(1, f_{\text{sat}, i}) \bigr], \qquad i = 1, \ldots, N$$

Esto garantiza que la solución respete las cotas de saturación y, simultáneamente, minimice el residuo $\|\mathcal{R}\|^2$ en el dominio admisible. Cuando la (CPO) interior arrojaría un valor por encima de $f_{\text{sat}, i}$, el solver localiza $f_i^* = f_{\text{sat}, i}$ con $\mathcal{R}_i < 0$ (residuo no nulo, consistente con la condición KKT de saturación). Cuando la (CPO) interior es admisible, el solver alcanza $\mathcal{R}_i = 0$ en el interior del cuadrado.

El equilibrio heterogéneo así obtenido proporciona el referente teórico directamente comparable con los resultados emergentes del modelo basado en agentes con $N = 30$ heterogéneo, y permite cuantificar cuán cerca quedan los agentes adaptativos del óptimo estratégico individual.
