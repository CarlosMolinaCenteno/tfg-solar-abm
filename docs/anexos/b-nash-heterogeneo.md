# Anexo B. Equilibrio de Nash con jugadores heterogéneos

La sección §3.4 del Capítulo 3 extiende el equilibrio de Nash al caso en que los productores difieren en su capacidad instalada $c_i$, y relega al material complementario tanto la demostración formal de la monotonía ("el grande almacena menos") como el tratamiento de la heterogeneidad en la capacidad de almacenamiento $s_i$. Este anexo desarrolla esos contenidos. La mecánica común de derivación —regla del producto y de la cadena sobre $\pi_i = P_M q_i^M + P_E q_i^E$— **no se repite aquí**: se reutiliza la del Anexo A.4, y este anexo se centra en lo que añade la heterogeneidad.

## Mapa cuerpo ↔ anexo

| Punto del cuerpo (Capítulo 3) | Se desarrolla en |
|---|---|
| §3.4 — $(\mathrm{CPO}_i)$ heterogénea con $\tilde{q}_i^M$ dependiente de $c_i$ | B.1 |
| §3.4 — condición de igualación de los ingresos marginales individuales | B.1 |
| §3.4 (heurística de monotonía) — prueba formal "el grande almacena menos" | B.2 |
| §3.4 — reducción al caso $s$ común cuando ningún agente satura | B.3 |
| §3.4 y §3.6.4 — heterogeneidad en $s_i$ (frontera de saturación, kink, KKT) | B.4 |
| §3.6.4 — algoritmo numérico (punto inicial, solver con cotas, homotopía) | B.5 |

## B.1. Heterogeneidad en la capacidad instalada

### B.1.1. Notación y planteamiento

Considérense $N$ agentes con capacidades instaladas heterogéneas $c_1, \ldots, c_N > 0$, eficiencia común $\eta$ y capacidad de almacenamiento $s$ grande (régimen interior). Las producciones brutas son ahora **individuales**:

$$\tilde{q}_i^M = \alpha_M c_i, \qquad \tilde{q}_i^E = \alpha_E c_i$$

Las cantidades vendidas dependen de la decisión y la capacidad propias, mientras que la oferta agregada y los precios se determinan por la suma sobre todos los agentes:

$$q_i^M(f_i) = (1 - f_i)\tilde{q}_i^M, \qquad q_i^E(f_i) = \tilde{q}_i^E + \eta f_i \tilde{q}_i^M$$

$$Q^p(\mathbf{f}) = \sum_{i=1}^{N} q_i^p(f_i), \qquad g^p(\mathbf{f}) = D_p - Q^p(\mathbf{f}), \qquad P_p(\mathbf{f}) = \alpha_G \bigl[g^p(\mathbf{f})\bigr]^{\gamma_G}$$

donde $\mathbf{f} = (f_1, \ldots, f_N)$ es el vector de estrategias.

### B.1.2. Condición de primer orden del agente $i$

El cálculo de la derivada parcial $\partial \pi_i / \partial f_i$ es el del Anexo A.4.3, sin más que sustituir la producción bruta común $\alpha_M c$ por la individual $\alpha_M c_i$. En particular, las derivadas de los precios respecto a $f_i$ escalan ahora con $\tilde{q}_i^M$:

$$\frac{\partial P_M}{\partial f_i} = \alpha_G \gamma_G \bigl[g^M\bigr]^{\gamma_G - 1} \tilde{q}_i^M, \qquad \frac{\partial P_E}{\partial f_i} = -\alpha_G \gamma_G \eta \bigl[g^E\bigr]^{\gamma_G - 1} \tilde{q}_i^M$$

y, agrupando $\tilde{q}_i^M$ como factor común, la derivada parcial conserva la forma de A.4.3:

$$\frac{\partial \pi_i}{\partial f_i} = \tilde{q}_i^M \cdot \Bigl\{ \eta P_E - P_M + \alpha_G \gamma_G \bigl[\, q_i^M \bigl[g^M\bigr]^{\gamma_G - 1} - \eta\, q_i^E \bigl[g^E\bigr]^{\gamma_G - 1}\bigr] \Bigr\}$$

Como $\tilde{q}_i^M > 0$, la condición de primer orden equivale a anular la expresión entre llaves:

$$P_M(\mathbf{f}) - \eta P_E(\mathbf{f}) \;=\; \alpha_G \gamma_G \Bigl\{ q_i^M(f_i)\bigl[g^M(\mathbf{f})\bigr]^{\gamma_G - 1} - \eta\, q_i^E(f_i)\bigl[g^E(\mathbf{f})\bigr]^{\gamma_G - 1} \Bigr\} \qquad (\mathrm{CPO}_i)$$

con dos diferencias respecto al caso simétrico: (i) las cantidades inframarginales $q_i^M, q_i^E$ son individuales y dependen de la capacidad propia; (ii) los precios y el gas dependen del **vector completo** $\mathbf{f}$ a través de la oferta agregada heterogénea.

### B.1.3. Sistema de equilibrio e igualación de ingresos marginales

El equilibrio es un vector $\mathbf{f}^* \in [0, 1]^N$ que satisface las $N$ condiciones $(\mathrm{CPO}_i)$ simultáneamente. Definiendo el residuo

$$\mathcal{R}_i(\mathbf{f}) := \bigl[P_M(\mathbf{f}) - \eta P_E(\mathbf{f})\bigr] - \alpha_G \gamma_G \Bigl\{ q_i^M(f_i)\bigl[g^M(\mathbf{f})\bigr]^{\gamma_G - 1} - \eta\, q_i^E(f_i)\bigl[g^E(\mathbf{f})\bigr]^{\gamma_G - 1} \Bigr\},$$

el sistema es $\mathcal{R}_i(\mathbf{f}^*) = 0$, $i = 1, \ldots, N$: $N$ ecuaciones no lineales acopladas en $N$ incógnitas. El primer corchete $P_M - \eta P_E$ es **común a todos los agentes** (depende sólo de la oferta agregada). Restando dos condiciones cualesquiera, $(\mathrm{CPO}_i) - (\mathrm{CPO}_j)$, ese término se cancela y queda la **condición de igualación de los ingresos marginales individuales**:

$$\bigl(q_i^M - q_j^M\bigr)\bigl[g^M\bigr]^{\gamma_G - 1} \;=\; \eta\bigl(q_i^E - q_j^E\bigr)\bigl[g^E\bigr]^{\gamma_G - 1}$$

Esta relación es combinación lineal de las CPO —no reduce el sistema— pero es la base de la prueba de monotonía de la subsección siguiente.

## B.2. Demostración de la monotonía: el grande almacena menos

La heurística de §3.4 afirma que, en equilibrio, los agentes con mayor capacidad instalada almacenan **menos** que los pequeños. Aquí se demuestra formalmente. El argumento es una comparación cualitativa **a equilibrio fijo**: no se deduce de la condición de igualación por sí sola —que sólo dice que las fracciones difieren, no en qué dirección— sino de combinarla con el signo de la cuña de arbitraje en el equilibrio.

**Paso 1 — Factor inframarginal individual.** Reescríbase el lado derecho de $(\mathrm{CPO}_i)$ definiendo

$$A := \bigl[g^M(\mathbf{f}^*)\bigr]^{\gamma_G - 1}, \qquad B := \bigl[g^E(\mathbf{f}^*)\bigr]^{\gamma_G - 1}, \qquad \Phi_i := q_i^M A - \eta\, q_i^E B.$$

Conviene subrayar el estatus de $A$ y $B$: **no son constantes** —dependen del vector $\mathbf{f}$ completo a través de la oferta agregada $Q^p$— pero **sí son comunes a todos los agentes en un equilibrio dado**, porque dependen únicamente del agregado y no del índice $i$. La $(\mathrm{CPO}_i)$ se escribe entonces $P_M - \eta P_E = \alpha_G \gamma_G\, \Phi_i$.

**Paso 2 — Extracción de $c_i$.** Sustituyendo $q_i^M = (1 - f_i)\alpha_M c_i$ y $q_i^E = \alpha_E c_i + \eta f_i \alpha_M c_i$ en $\Phi_i$ y sacando $c_i$ como factor común:

$$\Phi_i = c_i\bigl[(1 - f_i)\alpha_M A - \eta(\alpha_E + \eta f_i \alpha_M)B\bigr] = c_i\bigl(K - f_i L\bigr),$$

con

$$K := \alpha_M A - \eta \alpha_E B, \qquad L := \alpha_M\bigl(A + \eta^2 B\bigr) > 0.$$

$L > 0$ porque $\alpha_M, A, B > 0$ en el régimen interior. Como $A$, $B$, $K$ y $L$ dependen del agregado, son los mismos para todos los agentes en el equilibrio.

**Paso 3 — Comparación de dos agentes a equilibrio fijo.** En equilibrio el lado izquierdo de $(\mathrm{CPO}_i)$ es común, luego todos los $\Phi_i$ valen lo mismo:

$$\Phi_i = \Phi^* := \frac{P_M - \eta P_E}{\alpha_G \gamma_G} \quad \text{para todo } i.$$

De $c_i(K - f_i L) = \Phi^*$ se despeja $f_i = K/L - \Phi^*/(L c_i)$. Restando las expresiones de dos agentes $i, j$ (con $K$, $L$, $\Phi^*$ idénticos por evaluarse en el mismo equilibrio):

$$f_i - f_j = -\frac{\Phi^*}{L}\left(\frac{1}{c_i} - \frac{1}{c_j}\right) = -\frac{\Phi^*}{L}\cdot\frac{c_j - c_i}{c_i c_j}$$

Es una relación **implícita**, no una fórmula cerrada: $K$, $L$ y $\Phi^*$ dependen del equilibrio completo. Pero para comparar dos agentes en un equilibrio dado basta con que sean comunes, que lo son.

**Paso 4 — Signo de $\Phi^*$.** Como $\alpha_G \gamma_G > 0$, el signo de $\Phi^*$ es el de $P_M - \eta P_E$. La función $\Delta(f) := P_M - \eta P_E$ es estrictamente creciente en el almacenamiento (al almacenar más sube $P_M$ —baja la oferta matutina— y baja $P_E$ —sube la vespertina—), y se anula exactamente en el óptimo del agente precio-aceptante, $P_M = \eta P_E$. Como el Nash —homogéneo o heterogéneo— almacena **menos** que el precio-aceptante, se evalúa $\Delta$ por debajo de su raíz y por tanto

$$\Phi^* < 0.$$

Esto se confirma numéricamente en §3.6: el ratio $P_M/P_E$ queda por debajo de $\eta = 0{,}9$ en todos los regímenes (cártel $0{,}628$, Nash simétrico $0{,}881$, heterogéneo $0{,}8815$), es decir, $P_M < \eta P_E$.

**Paso 5 — Conclusión.** Con $\Phi^* < 0$, $L > 0$ y $c_i, c_j > 0$, el factor $-\Phi^*/(L c_i c_j)$ es positivo, de modo que

$$f_i - f_j = \underbrace{\left(-\frac{\Phi^*}{L\, c_i c_j}\right)}_{>\,0}\,(c_j - c_i) \;\;\Longrightarrow\;\; \operatorname{sign}(f_i - f_j) = \operatorname{sign}(c_j - c_i).$$

Por tanto $c_i > c_j \Rightarrow f_i < f_j$: **el agente con mayor capacidad almacena menos**. $\blacksquare$

**Intuición económica.** Todos los agentes enfrentan la misma cuña de arbitraje del lado izquierdo de la $(\mathrm{CPO}_i)$ —el incentivo bruto a almacenar más, común porque depende sólo del agregado— y la igualan con su propia cuña de poder de mercado en el lado derecho. La descomposición $\Phi_i = c_i\,(K - f_i\, L)$ del paso 2 muestra que esa cuña individual escala linealmente con $c_i$: el agente grande tiene un freno proporcionalmente más fuerte y modera su almacenamiento, mientras que el pequeño, con freno débil, se aproxima al comportamiento precio-aceptante (en el límite $c_i / \sum_j c_j \to 0$, $\Phi_i / c_i \to 0$ y la $(\mathrm{CPO}_i)$ colapsa a $P_M = \eta P_E$). La condición de igualación de los ingresos marginales individuales (§3.4) sólo dice que las diferencias en cantidad vendida entre agentes en la mañana y en la tarde están atadas con signos opuestos —si uno vende más por la mañana, vende menos por la tarde—, pero no fija ni quién es grande ni en qué dirección almacena; la dirección la da el paso 4, $\Phi^* < 0$, combinado con la proporcionalidad a $c_i$ del paso 2.

La monotonía queda así demostrada como propiedad cualitativa del equilibrio, y se confirma cuantitativamente en §3.6.4, donde la correlación entre la capacidad instalada y la fracción óptima es $\rho(c_i, f_i^*) = -0{,}9956$ —prácticamente perfecta y negativa— con $N = 30$ agentes y $c_i \sim \mathcal{U}[2, 3]$.

## B.3. Reducción al caso de $s$ común cuando ningún agente satura

§3.4 afirma que, en condiciones de batería no saturada, el sistema heterogéneo se reduce al caso de $s$ común. La justificación es directa a partir de la estructura de $(\mathrm{CPO}_i)$.

La capacidad de almacenamiento $s_i$ no aparece en el residuo interior $\mathcal{R}_i(\mathbf{f})$ de B.1.3: este sólo involucra $c_i$, $\eta$, los coeficientes $\alpha_M, \alpha_E, \alpha_G, \gamma_G$ y las demandas. El parámetro $s_i$ entra únicamente a través de la cota de saturación $f_{\text{sat}, i} = s_i/(\eta \alpha_M c_i)$ (sección B.4), que restringe el dominio admisible a $f_i \le f_{\text{sat}, i}$.

Supóngase que en el equilibrio $\mathbf{f}^*$ del problema interior ningún agente satura, esto es, $f_i^* < f_{\text{sat}, i}$ para todo $i$. Entonces la restricción de saturación está **inactiva** en todos los agentes, las condiciones KKT colapsan a $\mathcal{R}_i(\mathbf{f}^*) = 0$, y el sistema de equilibrio es **idéntico** al que se obtendría con cualquier otra especificación de las capacidades de almacenamiento —en particular, con un valor común $s$ grande— siempre que todas sean suficientemente generosas para no activar la cota. En consecuencia, las dos parametrizaciones (heterogeneidad sólo en $c_i$ con $s$ común, o heterogeneidad también en $s_i$ con todas las $s_i$ grandes) producen exactamente el **mismo equilibrio**. Esto es lo que se observa en §3.6.4, donde $0/30$ agentes operan en frontera de saturación y permitir heterogeneidad en $s_i$ no altera el resultado.

## B.4. Heterogeneidad en la capacidad de almacenamiento

### B.4.1. Frontera de saturación individual

Cuando los agentes tienen capacidades de almacenamiento $s_i$ distintas, cada uno tiene su propia frontera de saturación, obtenida igualando la energía vespertina derivada $\eta f_i \tilde{q}_i^M$ a la capacidad $s_i$:

$$f_{\text{sat}, i} := \frac{s_i}{\eta \tilde{q}_i^M} = \frac{s_i}{\eta \alpha_M c_i}.$$

Para $f_i \le f_{\text{sat}, i}$ el agente está en régimen interior (la batería absorbe toda la energía que se le envía); para $f_i > f_{\text{sat}, i}$, la batería está llena, la energía almacenada queda fijada en $S_i = s_i$ con independencia de $f_i$, y el exceso derivado de la mañana se pierde por curtailment.

### B.4.2. Kink en la derivada parcial

La función de beneficios $\pi_i$ es continua en $f_i$, pero su derivada parcial presenta una discontinuidad (kink) en $f_{\text{sat}, i}$:

- **Para $f_i < f_{\text{sat}, i}$** (régimen interior): se aplica la $(\mathrm{CPO}_i)$ de B.1.2.
- **Para $f_i > f_{\text{sat}, i}$** (régimen saturado): $\partial q_i^E/\partial f_i = 0$ y la derivada se reduce al término matutino (análogamente a A.7.1):

$$\left.\frac{\partial \pi_i}{\partial f_i}\right|_{\text{sat}} = -\tilde{q}_i^M\Bigl\{ P_M - \alpha_G \gamma_G\, q_i^M\bigl[g^M\bigr]^{\gamma_G - 1}\Bigr\} < 0,$$

estrictamente negativa: por encima de la frontera, incrementar $f_i$ reduce las ventas matutinas sin aumentar las vespertinas. El óptimo del agente $i$ se localiza, pues, en la raíz interior de $(\mathrm{CPO}_i)$ si ésta cumple $\le f_{\text{sat}, i}$, y en $f_{\text{sat}, i}$ en caso contrario.

### B.4.3. Condiciones KKT del problema con saturación

Las condiciones de Karush–Kuhn–Tucker del agente $i$, con la cota $f_i \le f_{\text{sat}, i}$, son:

$$\mathcal{R}_i(\mathbf{f}^*) \le 0, \qquad f_i^* \le f_{\text{sat}, i}, \qquad \mathcal{R}_i(\mathbf{f}^*)\cdot\bigl(f_{\text{sat}, i} - f_i^*\bigr) = 0.$$

En el régimen interior, $f_i^* < f_{\text{sat}, i}$ fuerza $\mathcal{R}_i(\mathbf{f}^*) = 0$; en saturación, $f_i^* = f_{\text{sat}, i}$ y se admite $\mathcal{R}_i(\mathbf{f}^*) \le 0$ (el agente querría almacenar más pero no puede). Cuando ninguna cota se activa, el sistema se reduce al interior puro de B.1.3, recuperándose el resultado de B.3.

## B.5. Resolución numérica

El sistema $\mathcal{R}_i(\mathbf{f}) = 0$ ($i = 1, \ldots, N$) no admite solución cerrada y se resuelve numéricamente. La estrategia adoptada en el banco de pruebas del proyecto es:

1. **Punto inicial.** El equilibrio simétrico $f^N$, obtenido resolviendo la CPO simétrica de §3.2 con la capacidad media $\bar{c} = \frac{1}{N}\sum_i c_i$ y el resto de parámetros comunes. Bajo heterogeneidad moderada la solución heterogénea está cerca de la simétrica, y la convergencia local desde ese punto es rápida.

2. **Solver.** `scipy.optimize.least_squares` con cotas $f_i \in [0, \min(1, f_{\text{sat}, i})]$. La elección de un solver de **mínimos cuadrados con cotas**, en lugar de un buscador de raíces puro (`fsolve`), es deliberada: las cotas garantizan que las iteraciones permanezcan en el dominio admisible $[0, 1]^N$ y, simultáneamente, gestionan de forma natural las soluciones de borde por saturación (B.4). Cuando la $(\mathrm{CPO}_i)$ interior arroja un valor por encima de $f_{\text{sat}, i}$, el solver localiza $f_i^* = f_{\text{sat}, i}$ con $\mathcal{R}_i < 0$ (residuo no nulo, consistente con la condición KKT de saturación); cuando es admisible, alcanza $\mathcal{R}_i = 0$ en el interior.

3. **Homotopía** (en caso de no convergencia desde el simétrico). Se interpola gradualmente entre el problema simétrico y el heterogéneo,

   $$c_i(\lambda) = (1 - \lambda)\bar{c} + \lambda c_i, \qquad \lambda = 0,\; 0{,}1,\; 0{,}2,\; \ldots,\; 1,$$

   resolviendo cada subproblema con la solución del anterior como punto inicial.

Sobre la velocidad de convergencia conviene un matiz. El algoritmo de `least_squares` es de tipo **Gauss–Newton / Levenberg–Marquardt**: su convergencia es cuadrática **sólo si el residuo en la solución es nulo**. Esa es precisamente la situación del régimen interior, donde $\mathcal{R}_i(\mathbf{f}^*) = 0$ para todo $i$ y la convergencia es efectivamente cuadrática; en cambio, para los agentes que saturan ($\mathcal{R}_i < 0$ en el óptimo) el residuo no se anula y la convergencia local degrada a lineal. Enunciar la convergencia como "cuadrática" sin este matiz sería impreciso, motivo por el que el detalle se relega a este anexo y el cuerpo (§3.6.4) se limita a nombrar el método.

La existencia del equilibrio heterogéneo se sigue de la teoría clásica de juegos (Fudenberg y Tirole, 1991, cap. 1): bajo heterogeneidad moderada y régimen interior bien definido, la concavidad estricta de cada $\pi_i$ en $f_i$ se preserva con los mismos argumentos del Anexo A.5, y la continuidad de las mejores respuestas sobre el compacto $[0, 1]^N$ garantiza el punto fijo. La unicidad no se demuestra formalmente; se verifica numéricamente probando distintos puntos iniciales y comprobando que todos convergen al mismo vector $\mathbf{f}^*$ (con residuo $\|\mathcal{R}\| \approx 6{,}6 \times 10^{-12}$ en la parametrización de §3.6.4).
