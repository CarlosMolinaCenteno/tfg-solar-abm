# Anexo A. Derivaciones detalladas de la sección 4.6

Este anexo recoge los cálculos paso a paso que sustentan los resultados de la sección 4.6 del Capítulo 4. Las secciones A.1–A.3 corresponden al caso del agente único (apartado 4.6.1) e incluyen la derivada primera y segunda de la función de beneficios $\pi(f)$. Las secciones A.4–A.5 corresponden al juego entre dos agentes simétricos (apartado 4.6.2) e incluyen el best-response del agente $i$ y el análisis de unicidad del equilibrio simétrico. La sección A.6 formaliza la convergencia del equilibrio de Nash al óptimo precio-aceptante en el límite $N \to \infty$ (apartado 4.6.3). Se reproducen las definiciones de las cantidades y precios al inicio de cada bloque para que las secciones puedan leerse de forma autocontenida.

## A.1. Notación y función de beneficios

Bajo las simplificaciones del apartado 4.6.1 (análisis determinista con $\varepsilon = 1$, separabilidad temporal y régimen interior), las producciones brutas son constantes:

$$\tilde{q}^M = \alpha_M \cdot c, \qquad \tilde{q}^E = \alpha_E \cdot c$$

Las cantidades efectivamente vendidas, las cantidades de gas y los precios de mercado, expresados como función de la fracción de almacenamiento $f$, son:

$$q^M(f) = (1 - f) \tilde{q}^M, \qquad q^E(f) = \tilde{q}^E + \eta f \tilde{q}^M$$

$$g^M(f) = D_M - q^M(f), \qquad g^E(f) = D_E - q^E(f)$$

$$P_M(f) = c_0 + \alpha_G \bigl[g^M(f)\bigr]^{\gamma_G}, \qquad P_E(f) = c_0 + \alpha_G \bigl[g^E(f)\bigr]^{\gamma_G}$$

El beneficio diario del agente, escrito explícitamente como función de $f$, es:

$$\pi(f) = \underbrace{\bigl[c_0 + \alpha_G (D_M - (1-f) \tilde{q}^M)^{\gamma_G}\bigr] \cdot (1-f) \tilde{q}^M}_{=:\, U(f) \cdot V(f)} + \underbrace{\bigl[c_0 + \alpha_G (D_E - \tilde{q}^E - \eta f \tilde{q}^M)^{\gamma_G}\bigr] \cdot (\tilde{q}^E + \eta f \tilde{q}^M)}_{=:\, W(f) \cdot Z(f)}$$

## A.2. Primera derivada

La derivada se calcula aplicando la regla del producto a cada uno de los dos sumandos. Para mantener la exposición autocontenida se identifican los factores como se indica arriba: $\pi(f) = U(f) V(f) + W(f) Z(f)$.

### Derivada del primer sumando

Las derivadas individuales son:

$$\frac{dV}{df} = \frac{d}{df}\bigl[(1-f) \tilde{q}^M\bigr] = -\tilde{q}^M$$

Para $dU/df$ se aplica la regla de la cadena. La derivada interior es $d/df\bigl[D_M - (1-f) \tilde{q}^M\bigr] = \tilde{q}^M$, y la derivada exterior $d/dx\bigl[c_0 + \alpha_G x^{\gamma_G}\bigr] = \alpha_G \gamma_G x^{\gamma_G - 1}$, con $x = g^M(f)$:

$$\frac{dU}{df} = \alpha_G \gamma_G \bigl[g^M(f)\bigr]^{\gamma_G - 1} \cdot \tilde{q}^M$$

Por la regla del producto:

$$\frac{d}{df}\bigl[U(f) V(f)\bigr] = \alpha_G \gamma_G \tilde{q}^M \bigl[g^M(f)\bigr]^{\gamma_G - 1} \cdot (1-f) \tilde{q}^M \;-\; \tilde{q}^M \bigl[c_0 + \alpha_G (g^M(f))^{\gamma_G}\bigr]$$

$$= \tilde{q}^M \cdot \Bigl\{ \alpha_G \gamma_G \cdot q^M(f) \bigl[g^M(f)\bigr]^{\gamma_G - 1} - P_M(f) \Bigr\}$$

donde se ha usado $(1-f) \tilde{q}^M = q^M(f)$ y la definición de $P_M(f)$.

### Derivada del segundo sumando

De forma análoga:

$$\frac{dZ}{df} = \frac{d}{df}\bigl[\tilde{q}^E + \eta f \tilde{q}^M\bigr] = \eta \tilde{q}^M$$

La derivada interior es ahora $d/df\bigl[D_E - \tilde{q}^E - \eta f \tilde{q}^M\bigr] = -\eta \tilde{q}^M$, de modo que:

$$\frac{dW}{df} = \alpha_G \gamma_G \bigl[g^E(f)\bigr]^{\gamma_G - 1} \cdot (-\eta \tilde{q}^M) = -\alpha_G \gamma_G \eta \tilde{q}^M \bigl[g^E(f)\bigr]^{\gamma_G - 1}$$

Aplicando la regla del producto:

$$\frac{d}{df}\bigl[W(f) Z(f)\bigr] = -\alpha_G \gamma_G \eta \tilde{q}^M \bigl[g^E(f)\bigr]^{\gamma_G - 1} \cdot \bigl(\tilde{q}^E + \eta f \tilde{q}^M\bigr) \;+\; \eta \tilde{q}^M \bigl[c_0 + \alpha_G (g^E(f))^{\gamma_G}\bigr]$$

$$= \tilde{q}^M \cdot \Bigl\{ -\alpha_G \gamma_G \eta \cdot q^E(f) \bigl[g^E(f)\bigr]^{\gamma_G - 1} + \eta P_E(f) \Bigr\}$$

### Suma y forma final

Sumando ambas contribuciones y agrupando $\tilde{q}^M$ como factor común:

$$\boxed{\,\frac{d\pi}{df} = \tilde{q}^M \cdot \Bigl\{ \alpha_G \gamma_G \cdot q^M(f) \bigl[g^M(f)\bigr]^{\gamma_G - 1} - P_M(f) - \alpha_G \gamma_G \eta \cdot q^E(f) \bigl[g^E(f)\bigr]^{\gamma_G - 1} + \eta P_E(f) \Bigr\}\,}$$

Como $\tilde{q}^M > 0$, la condición de primer orden $d\pi/df = 0$ equivale a anular la expresión entre llaves, lo que reordenado da la (CPO) del apartado 4.6.1.

## A.3. Segunda derivada

Para verificar que la solución de la (CPO) es un máximo se calcula $d^2\pi/df^2$. Para abreviar, en lo que sigue se omite la dependencia explícita en $f$. Partiendo de la expresión de $d\pi/df$, se deriva término a término.

### Derivadas de los precios y de las pendientes

Por las reglas obtenidas en A.2:

$$\frac{dP_M}{df} = \alpha_G \gamma_G \bigl[g^M\bigr]^{\gamma_G - 1} \tilde{q}^M, \qquad \frac{dP_E}{df} = -\alpha_G \gamma_G \eta \bigl[g^E\bigr]^{\gamma_G - 1} \tilde{q}^M$$

Para las potencias $\bigl[g^M\bigr]^{\gamma_G - 1}$ y $\bigl[g^E\bigr]^{\gamma_G - 1}$, aplicando la regla de la cadena:

$$\frac{d}{df}\bigl[g^M\bigr]^{\gamma_G - 1} = (\gamma_G - 1) \bigl[g^M\bigr]^{\gamma_G - 2} \cdot \tilde{q}^M$$

$$\frac{d}{df}\bigl[g^E\bigr]^{\gamma_G - 1} = -(\gamma_G - 1) \bigl[g^E\bigr]^{\gamma_G - 2} \cdot \eta \tilde{q}^M$$

### Derivada de cada término

Sea $T_M(f) := \alpha_G \gamma_G \cdot q^M [g^M]^{\gamma_G - 1}$. Aplicando la regla del producto:

$$\frac{dT_M}{df} = \alpha_G \gamma_G \cdot \frac{dq^M}{df} \cdot \bigl[g^M\bigr]^{\gamma_G - 1} + \alpha_G \gamma_G \cdot q^M \cdot \frac{d}{df}\bigl[g^M\bigr]^{\gamma_G - 1}$$

$$= -\alpha_G \gamma_G \tilde{q}^M \bigl[g^M\bigr]^{\gamma_G - 1} + \alpha_G \gamma_G (\gamma_G - 1) \tilde{q}^M \cdot q^M \cdot \bigl[g^M\bigr]^{\gamma_G - 2}$$

$$= \alpha_G \gamma_G \tilde{q}^M \bigl[g^M\bigr]^{\gamma_G - 1} \cdot \left[ \frac{(\gamma_G - 1) q^M}{g^M} - 1 \right]$$

Análogamente, para $T_E(f) := \alpha_G \gamma_G \eta \cdot q^E [g^E]^{\gamma_G - 1}$:

$$\frac{dT_E}{df} = \alpha_G \gamma_G \eta \cdot \eta \tilde{q}^M \cdot \bigl[g^E\bigr]^{\gamma_G - 1} - \alpha_G \gamma_G \eta \cdot q^E \cdot (\gamma_G - 1) \bigl[g^E\bigr]^{\gamma_G - 2} \cdot \eta \tilde{q}^M$$

$$= \alpha_G \gamma_G \eta^2 \tilde{q}^M \bigl[g^E\bigr]^{\gamma_G - 1} \cdot \left[ 1 - \frac{(\gamma_G - 1) q^E}{g^E} \right]$$

### Combinación

Recordando que $\dfrac{d\pi}{df} = \tilde{q}^M (T_M - P_M - T_E + \eta P_E)$, se obtiene:

$$\frac{d^2 \pi}{df^2} = \tilde{q}^M \left( \frac{dT_M}{df} - \frac{dP_M}{df} - \frac{dT_E}{df} + \eta \frac{dP_E}{df} \right)$$

Sustituyendo las cuatro derivadas calculadas y agrupando los factores comunes $\alpha_G \gamma_G \bigl[g^M\bigr]^{\gamma_G - 1}$ y $\alpha_G \gamma_G \eta^2 \bigl[g^E\bigr]^{\gamma_G - 1}$:

$$\frac{d^2 \pi}{df^2} = (\tilde{q}^M)^2 \left\{ \alpha_G \gamma_G \bigl[g^M\bigr]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q^M}{g^M} - 2 \right] + \alpha_G \gamma_G \eta^2 \bigl[g^E\bigr]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q^E}{g^E} - 2 \right] \right\}$$

### Signo y concavidad

Las cantidades $\alpha_G \gamma_G [g^M]^{\gamma_G - 1}$ y $\alpha_G \gamma_G [g^E]^{\gamma_G - 1}$ son estrictamente positivas en el régimen interior. Por tanto, el signo de $d^2 \pi / df^2$ depende del signo de los corchetes:

$$\frac{(\gamma_G - 1) q^M}{g^M} - 2 < 0 \quad \Longleftrightarrow \quad \frac{q^M}{g^M} < \frac{2}{\gamma_G - 1}$$

y análogamente para el periodo de tarde. Con $\gamma_G = 1{,}3$, esto exige $q^M / g^M < 2 / 0{,}3 \approx 6{,}7$, condición que se cumple holgadamente en los escenarios considerados, donde la oferta solar es minoritaria respecto a la cobertura por gas. Bajo estas condiciones $d^2 \pi / df^2 < 0$ y la función de beneficios es estrictamente cóncava en $f$, de modo que la solución de la (CPO) caracteriza el máximo global del problema en el régimen interior.

## A.4. Best-response del agente $i$ en el juego de N=2

### A.4.1. Notación

Bajo las simplificaciones del apartado 4.6.2 (análisis determinista, separabilidad temporal y régimen interior), los dos agentes simétricos comparten la misma producción bruta:

$$\tilde{q}^M = \alpha_M \cdot c, \qquad \tilde{q}^E = \alpha_E \cdot c$$

Las cantidades vendidas dependen exclusivamente de la decisión propia del agente:

$$q_i^M(f_i) = (1 - f_i) \tilde{q}^M, \qquad q_i^E(f_i) = \tilde{q}^E + \eta f_i \tilde{q}^M, \qquad i \in \{1, 2\}$$

mientras que la oferta agregada y los precios dependen de las decisiones de ambos:

$$Q^M(f_1, f_2) = q_1^M + q_2^M, \qquad Q^E(f_1, f_2) = q_1^E + q_2^E$$

$$g^M = D_M - Q^M, \qquad g^E = D_E - Q^E$$

$$P_M = c_0 + \alpha_G [g^M]^{\gamma_G}, \qquad P_E = c_0 + \alpha_G [g^E]^{\gamma_G}$$

El beneficio del agente $i$, dado $f_j$ fijo, es:

$$\pi_i(f_i; f_j) = P_M \cdot q_i^M(f_i) + P_E \cdot q_i^E(f_i)$$

### A.4.2. Derivadas auxiliares respecto a $f_i$

Las derivadas individuales son inmediatas:

$$\frac{\partial q_i^M}{\partial f_i} = -\tilde{q}^M, \qquad \frac{\partial q_i^E}{\partial f_i} = \eta \tilde{q}^M$$

Como la cantidad del rival $q_j$ no varía con $f_i$, la oferta agregada cambia exactamente como la individual:

$$\frac{\partial Q^M}{\partial f_i} = \frac{\partial q_i^M}{\partial f_i} = -\tilde{q}^M, \qquad \frac{\partial Q^E}{\partial f_i} = \frac{\partial q_i^E}{\partial f_i} = \eta \tilde{q}^M$$

de modo que las derivadas del gas y de los precios son las mismas que en el caso del agente único:

$$\frac{\partial g^M}{\partial f_i} = \tilde{q}^M, \qquad \frac{\partial g^E}{\partial f_i} = -\eta \tilde{q}^M$$

$$\frac{\partial P_M}{\partial f_i} = \alpha_G \gamma_G [g^M]^{\gamma_G - 1} \tilde{q}^M, \qquad \frac{\partial P_E}{\partial f_i} = -\alpha_G \gamma_G \eta [g^E]^{\gamma_G - 1} \tilde{q}^M$$

### A.4.3. Derivada parcial del beneficio

Aplicando la regla del producto sobre $\pi_i = P_M \cdot q_i^M + P_E \cdot q_i^E$:

$$\frac{\partial \pi_i}{\partial f_i} = \frac{\partial P_M}{\partial f_i} \cdot q_i^M + P_M \cdot \frac{\partial q_i^M}{\partial f_i} + \frac{\partial P_E}{\partial f_i} \cdot q_i^E + P_E \cdot \frac{\partial q_i^E}{\partial f_i}$$

Sustituyendo las derivadas obtenidas en A.4.2:

$$= \alpha_G \gamma_G \tilde{q}^M [g^M]^{\gamma_G - 1} \cdot q_i^M - P_M \tilde{q}^M - \alpha_G \gamma_G \eta \tilde{q}^M [g^E]^{\gamma_G - 1} \cdot q_i^E + \eta P_E \tilde{q}^M$$

Sacando $\tilde{q}^M$ como factor común se obtiene la forma compacta utilizada en el apartado 4.6.2:

$$\boxed{\,\frac{\partial \pi_i}{\partial f_i} = \tilde{q}^M \cdot \Bigl\{ \alpha_G \gamma_G \cdot q_i^M [g^M]^{\gamma_G - 1} - P_M - \alpha_G \gamma_G \eta \cdot q_i^E [g^E]^{\gamma_G - 1} + \eta P_E \Bigr\}\,}$$

La diferencia esencial respecto al caso del agente único (sección A.2) reside en que las cantidades inframarginales que multiplican a las pendientes son las **individuales** $q_i^M$ y $q_i^E$, no las agregadas $Q^M$ y $Q^E$. Esta diferencia es la que captura la atenuación del poder de mercado al pasar del cártel al juego de Nash. La condición de primer orden $\partial \pi_i / \partial f_i = 0$ equivale a anular la expresión entre llaves; reordenada, da la (CPO$_i$) del apartado 4.6.2.

## A.5. Hessiana y unicidad del equilibrio simétrico

### A.5.1. Concavidad estricta del beneficio en $f_i$

Para garantizar que la mejor respuesta $\text{BR}_i(f_j)$ del agente $i$ es única se verifica $\partial^2 \pi_i / \partial f_i^2 < 0$. Por brevedad, definamos:

$$T_M^{(i)} := \alpha_G \gamma_G \cdot q_i^M [g^M]^{\gamma_G - 1}, \qquad T_E^{(i)} := \alpha_G \gamma_G \eta \cdot q_i^E [g^E]^{\gamma_G - 1}$$

Aplicando la regla del producto a $T_M^{(i)}$ respecto a $f_i$:

$$\frac{\partial T_M^{(i)}}{\partial f_i} = \alpha_G \gamma_G \left[ \frac{\partial q_i^M}{\partial f_i} [g^M]^{\gamma_G - 1} + q_i^M (\gamma_G - 1) [g^M]^{\gamma_G - 2} \frac{\partial g^M}{\partial f_i} \right]$$

$$= \alpha_G \gamma_G \tilde{q}^M [g^M]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q_i^M}{g^M} - 1 \right]$$

Análogamente para $T_E^{(i)}$:

$$\frac{\partial T_E^{(i)}}{\partial f_i} = \alpha_G \gamma_G \eta^2 \tilde{q}^M [g^E]^{\gamma_G - 1} \left[ 1 - \frac{(\gamma_G - 1) q_i^E}{g^E} \right]$$

Recordando que $\partial \pi_i / \partial f_i = \tilde{q}^M (T_M^{(i)} - P_M - T_E^{(i)} + \eta P_E)$, la segunda derivada es:

$$\frac{\partial^2 \pi_i}{\partial f_i^2} = \tilde{q}^M \left( \frac{\partial T_M^{(i)}}{\partial f_i} - \frac{\partial P_M}{\partial f_i} - \frac{\partial T_E^{(i)}}{\partial f_i} + \eta \frac{\partial P_E}{\partial f_i} \right)$$

Sustituyendo y agrupando los factores comunes $\alpha_G \gamma_G \tilde{q}^M [g^M]^{\gamma_G - 1}$ y $\alpha_G \gamma_G \eta^2 \tilde{q}^M [g^E]^{\gamma_G - 1}$:

$$\frac{\partial^2 \pi_i}{\partial f_i^2} = (\tilde{q}^M)^2 \alpha_G \gamma_G \left\{ [g^M]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q_i^M}{g^M} - 2 \right] + \eta^2 [g^E]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q_i^E}{g^E} - 2 \right] \right\}$$

La expresión es formalmente idéntica a la obtenida en A.3 para el agente único, con la única diferencia de que las cantidades inframarginales son las individuales $q_i^M$, $q_i^E$. La función $\pi_i$ es estrictamente cóncava en $f_i$ siempre que se cumpla:

$$\frac{q_i^M}{g^M} < \frac{2}{\gamma_G - 1}, \qquad \frac{q_i^E}{g^E} < \frac{2}{\gamma_G - 1}$$

Como $q_i = Q/2$ en el equilibrio simétrico con $N = 2$, las condiciones son aún menos restrictivas que las del cártel (donde $\kappa = Q$) y se cumplen holgadamente con los parámetros del modelo. La mejor respuesta $\text{BR}_i(f_j)$ queda así caracterizada como el único maximizador de $\pi_i(\cdot; f_j)$ en $[0, 1]$.

### A.5.2. Unicidad del equilibrio simétrico

Sea

$$\Phi(f) := \frac{\partial \pi_i}{\partial f_i} \bigg|_{f_1 = f_2 = f}$$

la pendiente del beneficio del agente $i$ a lo largo de la diagonal $f_1 = f_2 = f$. El equilibrio de Nash simétrico $f^N$ es la raíz de $\Phi$ en $[0, 1]$. Para garantizar su unicidad basta probar que $\Phi$ es estrictamente decreciente. Por la regla de la cadena:

$$\Phi'(f) = \frac{\partial^2 \pi_i}{\partial f_i^2} + \frac{\partial^2 \pi_i}{\partial f_i \partial f_j}$$

donde ambas derivadas se evalúan en el punto simétrico. La diagonal ya se calculó en A.5.1. Para la cruzada se observa que, al derivar respecto a $f_j$, las cantidades $q_i^M$ y $q_i^E$ no cambian (no dependen de $f_j$), pero sí $g^M$ y $g^E$, que lo hacen exactamente igual que cuando se deriva respecto a $f_i$:

$$\frac{\partial g^M}{\partial f_j} = \tilde{q}^M, \qquad \frac{\partial g^E}{\partial f_j} = -\eta \tilde{q}^M$$

Procediendo análogamente a A.5.1, los términos en los que cambia el cálculo son:

$$\frac{\partial T_M^{(i)}}{\partial f_j} = \alpha_G \gamma_G (\gamma_G - 1) \tilde{q}^M \cdot q_i^M [g^M]^{\gamma_G - 2}$$

$$\frac{\partial T_E^{(i)}}{\partial f_j} = -\alpha_G \gamma_G \eta^2 (\gamma_G - 1) \tilde{q}^M \cdot q_i^E [g^E]^{\gamma_G - 2}$$

mientras que las derivadas $\partial P_M / \partial f_j$ y $\partial P_E / \partial f_j$ coinciden con las de $f_i$. Reagrupando:

$$\frac{\partial^2 \pi_i}{\partial f_i \partial f_j} = (\tilde{q}^M)^2 \alpha_G \gamma_G \left\{ [g^M]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q_i^M}{g^M} - 1 \right] + \eta^2 [g^E]^{\gamma_G - 1} \left[ \frac{(\gamma_G - 1) q_i^E}{g^E} - 1 \right] \right\}$$

Sumando con la diagonal de A.5.1:

$$\Phi'(f) = (\tilde{q}^M)^2 \alpha_G \gamma_G \left\{ [g^M]^{\gamma_G - 1} \left[ \frac{2(\gamma_G - 1) q_i^M}{g^M} - 3 \right] + \eta^2 [g^E]^{\gamma_G - 1} \left[ \frac{2(\gamma_G - 1) q_i^E}{g^E} - 3 \right] \right\}$$

$\Phi'(f) < 0$ siempre que se cumpla la condición —ligeramente más restrictiva que la de la concavidad de $\pi_i$ en $f_i$—:

$$\frac{q_i^M}{g^M} < \frac{3}{2(\gamma_G - 1)}, \qquad \frac{q_i^E}{g^E} < \frac{3}{2(\gamma_G - 1)}$$

Con $\gamma_G = 1{,}3$ esto exige $q_i / g < 3 / 0{,}6 = 5$, condición que se cumple holgadamente en los escenarios considerados. Bajo ella, $\Phi$ es estrictamente decreciente en $[0, 1]$, lo que implica que admite a lo sumo una raíz. La existencia de raíz —y por tanto del equilibrio de Nash simétrico— se sigue del teorema del valor intermedio aplicado a una función continua que típicamente toma valores positivos en $f = 0$ (incentivos al arbitraje cuando no hay almacenamiento) y negativos en $f = 1$ (predominio del efecto cantidad). En consecuencia, el equilibrio de Nash simétrico $f^N$ existe y es único.

## A.6. Convergencia del equilibrio de Nash al precio-aceptante en el límite $N \to \infty$

Esta sección formaliza el resultado de convergencia presentado en el cuerpo del apartado 4.6.3: bajo una sucesión de juegos con $N$ agentes simétricos cuya capacidad agregada permanece constante, el equilibrio de Nash simétrico $f^N$ converge al óptimo del agente precio-aceptante $f^*_{\text{pa}}$ cuando $N \to \infty$.

### A.6.1. Familia de juegos y parametrización del límite

Considérese una sucesión de juegos indexada por $N \in \mathbb{N}$, en la que la capacidad individual del agente representativo se escala inversamente al número de jugadores:

$$c^{(N)} = \frac{C}{N}$$

para una capacidad agregada $C > 0$ fija. Bajo esta parametrización, las producciones brutas individuales y las cantidades vendidas en simetría se expresan en términos de las cantidades agregadas, que son **independientes de $N$**:

$$\tilde{q}^{p,(N)} = \alpha_p \cdot c^{(N)} = \frac{\alpha_p C}{N}, \qquad q_i^{p,(N)}(f) = \frac{1}{N} \cdot Q^p(f), \qquad p \in \{M, E\}$$

con

$$Q^M(f) = (1 - f) \alpha_M C, \qquad Q^E(f) = \alpha_E C + \eta f \alpha_M C$$

En consecuencia, las cantidades de gas $g^p(f) = D_p - Q^p(f)$ y los precios $P_p(f) = c_0 + \alpha_G [g^p(f)]^{\gamma_G}$ no dependen de $N$, mientras que las cantidades individuales $q_i^p(f)$ decrecen como $1/N$.

### A.6.2. Reescritura de la (CPO) con el factor $1/N$ explícito

Sustituyendo $q_i^p = Q^p / N$ en la condición de primer orden del Nash simétrico (apartado 4.6.3), el factor $1/N$ se extrae de forma natural:

$$P_M(f^N) - \eta P_E(f^N) \;=\; \frac{\alpha_G \gamma_G}{N} \cdot \Bigl\{ Q^M(f^N) \bigl[g^M(f^N)\bigr]^{\gamma_G - 1} - \eta\, Q^E(f^N) \bigl[g^E(f^N)\bigr]^{\gamma_G - 1} \Bigr\}$$

El corchete del lado derecho es continuo en $f$ y está acotado en $[0, 1]$ (las cantidades $Q^p$, $g^p$ y sus potencias son funciones continuas y estrictamente positivas en el régimen interior). Por tanto, el lado derecho de la (CPO) es del orden $\mathcal{O}(1/N)$ uniformemente en $f$.

### A.6.3. Convergencia del equilibrio

Sea $\{f^N\}_{N \in \mathbb{N}}$ la sucesión de equilibrios de Nash simétricos. Como $f^N \in [0, 1]$ para todo $N$, la sucesión está acotada y, por el teorema de Bolzano–Weierstrass, admite al menos una subsucesión convergente. Denotamos por $f^{\infty}$ cualquier punto de acumulación.

Tomando límite en la (CPO) reescrita en A.6.2 a lo largo de una tal subsucesión: el lado derecho tiende a cero (numerador acotado, $1/N \to 0$), mientras que el lado izquierdo tiende a $P_M(f^{\infty}) - \eta P_E(f^{\infty})$ por continuidad de los precios en $f$. Se concluye:

$$P_M(f^{\infty}) = \eta P_E(f^{\infty})$$

que es exactamente la condición de arbitraje puro del agente precio-aceptante presentada en el apartado 4.6.1. Bajo las condiciones del modelo, la función $\Delta(f) := P_M(f) - \eta P_E(f)$ es continua y estrictamente monótona en $f$ (se obtiene como diferencia de dos potencias estrictamente convexas con pendientes de signo opuesto), de modo que $\Delta$ admite a lo sumo una raíz en $[0, 1]$. Si dicha raíz existe —es decir, si $\Delta$ cambia de signo en el intervalo, condición que se cumple en el escenario considerado—, entonces todos los puntos de acumulación coinciden y la sucesión completa converge:

$$f^N \;\xrightarrow{\;N \to \infty\;}\; f^*_{\text{pa}}$$

donde $f^*_{\text{pa}}$ es la fracción óptima del agente precio-aceptante. Este resultado proporciona el fundamento riguroso de la afirmación del apartado 4.6.3: la hipótesis de competencia perfecta adoptada en el Capítulo 3 no es arbitraria, sino que corresponde al comportamiento asintótico del equilibrio de Nash cuando el número de agentes simétricos tiende a infinito y la capacidad agregada se mantiene constante.
