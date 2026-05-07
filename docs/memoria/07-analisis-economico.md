# 7. Análisis e interpretación económica

En los capítulos anteriores se han presentado los resultados de las simulaciones de forma descriptiva, identificando los patrones observados en cada escenario sin entrar en la interpretación de los mecanismos subyacentes. El presente capítulo tiene como objetivo analizar estos resultados desde una perspectiva económica, conectando las observaciones empíricas del modelo con conceptos teóricos y extrayendo las implicaciones más relevantes.

El análisis se estructura en torno a cuatro ejes: la convergencia del aprendizaje y su relación con el equilibrio teórico, el impacto del almacenamiento sobre el funcionamiento del mercado, un análisis de bienestar del sistema, y las limitaciones del modelo.

## 7.1. Convergencia del aprendizaje y equilibrio

### Comportamiento observado

Uno de los resultados más destacados de las simulaciones es la rapidez con la que el sistema alcanza un régimen estacionario. Como se ha mostrado en la Figura 6.3, la fracción media de almacenamiento converge en los primeros 25-50 días de simulación hacia un valor de aproximadamente 0,91, y permanece estable durante el resto del horizonte temporal. Este comportamiento se observa de forma consistente a través de distintas semillas aleatorias y configuraciones de parámetros (Capítulo 6, apartado 6.5).

Sin embargo, la convergencia agregada coexiste con una heterogeneidad persistente a nivel individual. La Figura 6.3 muestra que el rango de decisiones de los agentes (mínimo-máximo) se mantiene amplio a lo largo de toda la simulación, abarcando valores desde 0,1 hasta 1,0. Esto indica que, si bien el sistema alcanza un equilibrio estadístico a nivel agregado, los agentes individuales no convergen todos hacia la misma estrategia. Esta dispersión refleja tanto la heterogeneidad en los parámetros de aprendizaje ($\phi_i$, $\beta_i$) como la naturaleza estocástica de la regla de decisión logit.

### Interpretación económica de la convergencia

La fracción de almacenamiento de equilibrio surge de un balance entre dos fuerzas opuestas. Por un lado, almacenar energía permite venderla en el periodo de tarde a un precio más elevado, lo que genera un incentivo al almacenamiento. Por otro lado, al retirar energía del periodo de mañana, el agente reduce su oferta en un mercado donde ya podría estar obteniendo ingresos, y además incurre en pérdidas asociadas a la eficiencia de la batería ($\eta < 1$). El punto de equilibrio se alcanza cuando el beneficio marginal de almacenar una unidad adicional se iguala con el coste de oportunidad de no venderla inmediatamente.

Formalmente, para un agente que se comporta como tomador de precios, la condición de indiferencia entre vender y almacenar una unidad de energía matutina puede expresarse como:

$$P_M = \eta_i \cdot P_E$$

Es decir, el agente estará indiferente entre vender una unidad de energía al precio de la mañana y almacenarla (perdiendo una fracción $1 - \eta_i$ en el proceso) para venderla al precio de la tarde. Cuando $\eta_i \cdot P_E > P_M$, el agente tiene incentivos a almacenar más; cuando $\eta_i \cdot P_E < P_M$, prefiere vender en el periodo de mañana.

Los datos de la simulación son coherentes con esta lógica. En el escenario con almacenamiento, los precios medios observados son $P_M \approx 108{,}0$ y $P_E \approx 195{,}1$, lo que da un ratio $P_M / P_E \approx 0{,}55$. La condición de indiferencia individual $P_M = \eta_i P_E$ se satisfaría para un ratio $P_M / P_E = \eta_i$, que en el caso de la eficiencia media ($\bar{\eta} \approx 0{,}90$) sería 0,90.

El hecho de que el ratio observado ($0{,}55$) sea inferior a $\bar{\eta}$ no indica necesariamente un desequilibrio, sino que refleja las características del equilibrio del sistema. Varios factores contribuyen a esta diferencia. En primer lugar, los precios son endógenos: son los propios agentes, al almacenar al nivel observado ($\approx 0{,}91$), quienes generan estos precios. Si almacenasen más, el precio de la mañana subiría y el de la tarde bajaría, acercando el ratio a $\eta$, pero el espacio discreto de decisiones y la naturaleza estocástica de la regla logit impiden un ajuste exacto. En segundo lugar, la heterogeneidad de los agentes implica que la condición de equilibrio se satisface de forma diferente para cada uno: agentes con mayor $\eta_i$ tienen más incentivo a almacenar que aquellos con menor eficiencia. En tercer lugar, la regla de aprendizaje por refuerzo no garantiza la convergencia exacta a un equilibrio de Nash, sino a un equilibrio estadístico en el que las estrategias más rentables se seleccionan con mayor probabilidad sin llegar a dominar completamente.

### Conexión con el equilibrio teórico

El resultado anterior muestra que el sistema ABM alcanza un equilibrio en el que los agentes explotan la diferencia de precios entre periodos, pero no la eliminan completamente. Este resultado es cualitativamente consistente con lo que predice un análisis de equilibrio competitivo: en un mercado con agentes tomadores de precios, el almacenamiento debería reducir la diferencia de precios entre periodos, pero no eliminarla por completo si las baterías presentan pérdidas de eficiencia. La persistencia de un diferencial de precios $P_E > P_M / \eta$ es, en este contexto, un resultado de equilibrio, no una ineficiencia.

El desarrollo formal del equilibrio teórico para los casos de agente único, dos agentes y $N$ agentes se aborda en la sección 4.6.

## 7.2. Impacto del almacenamiento en el mercado

### Efecto sobre los precios

Como se ha cuantificado en la Tabla 6.1, la introducción del almacenamiento produce un efecto de convergencia de precios entre periodos: el precio medio de la mañana aumenta un 55,8% mientras que el de la tarde se reduce un 18,2%.

Este patrón es la consecuencia directa del traslado de energía entre periodos. Al almacenar energía durante la mañana, los agentes retiran oferta del periodo de mañana (lo que eleva su precio) y la añaden al periodo de tarde (lo que reduce su precio). El resultado neto es una reducción de la brecha entre precios, aunque esta no se elimina por completo.

Es importante destacar que el efecto sobre el precio de la mañana es proporcionalmente mayor que sobre el de la tarde. Esto se explica por la convexidad de la función de costes del gas: dado que $c_G(q) = c_0 + \alpha_G q^{\gamma_G}$ con $\gamma_G > 1$, reducciones pequeñas en la demanda de gas del periodo de tarde producen descensos moderados en el precio, mientras que incrementos similares en la demanda de gas de la mañana generan subidas proporcionalmente mayores, especialmente cuando la oferta solar de la mañana apenas cubría la demanda.

### Efecto sobre el uso de generación de gas

Los datos de la Tabla 6.1 revelan que el almacenamiento no reduce el uso total de gas, sino que lo redistribuye entre periodos: el gas de la mañana aumenta un 47,1% mientras que el de la tarde se reduce un 14,9%. Al retirar oferta solar de la mañana, se incrementa la necesidad de gas en ese periodo, mientras que la energía trasladada a la tarde reduce la necesidad de gas en las horas de mayor demanda. Sin embargo, como las baterías tienen una eficiencia inferior a 1, parte de la energía se pierde en el proceso de almacenamiento, lo que implica que el gas total necesario en el sistema puede incluso aumentar ligeramente.

Este resultado tiene una implicación importante: el almacenamiento distribuido, tal como se modela aquí, no es necesariamente un mecanismo de reducción de emisiones per se, sino un mecanismo de redistribución temporal de la energía. Su efecto ambiental neto depende de la relación entre las pérdidas del almacenamiento y la reducción de la necesidad de gas en el periodo pico, y es un aspecto que merece análisis específico.

### Efecto sobre la volatilidad de precios

La desviación típica del precio de la mañana se reduce de 0,63 a 0,34, mientras que la del periodo de tarde aumenta de 0,37 a 0,80. Este resultado sugiere que el almacenamiento estabiliza los precios en el periodo de mañana (donde la oferta es más flexible) pero introduce mayor variabilidad en el periodo de tarde, posiblemente porque las decisiones estocásticas de almacenamiento de los agentes se transmiten directamente a la oferta disponible en la tarde.

## 7.3. Análisis de bienestar

### Beneficios de los productores solares

El beneficio medio de los productores solares aumenta de 117,7 (sin almacenamiento) a 172,6 (con almacenamiento), lo que representa un incremento del 46,7%. Este resultado indica que el almacenamiento permite a los productores capturar una mayor parte del valor generado por la diferencia de precios entre periodos.

Es importante señalar que este incremento de beneficios no se produce a expensas de los consumidores de forma directa, ya que la demanda es exógena y los consumidores pagan el precio del periodo correspondiente. El incremento refleja la capacidad de los productores para desplazar energía hacia el periodo de mayor valor, una estrategia que es individualmente racional y, como se analiza a continuación, también puede tener efectos sistémicos positivos.

### Coste total de generación de gas

Una métrica de bienestar del sistema es el coste total de la generación de gas, que puede interpretarse como una aproximación del coste social de la generación de respaldo. El coste total del gas en un periodo viene dado por la integral del coste marginal:

$$C_G(q) = \int_0^q c_G(x)\,dx = c_0 q + \frac{\alpha_G}{1 + \gamma_G} q^{1+\gamma_G}$$

Dado que la función de costes es convexa ($\gamma_G > 1$), la redistribución del uso de gas entre periodos tiene un efecto neto sobre el coste total. Específicamente, trasladar gas del periodo de tarde (donde se usa mucho y el coste marginal es alto) al periodo de mañana (donde se usa menos y el coste marginal es bajo) puede reducir el coste total del gas, incluso si la cantidad total utilizada no varía.

La Figura 7.3 (coste acumulado de generación de gas) muestra que el escenario con almacenamiento genera un coste total de gas inferior al escenario sin almacenamiento a lo largo del horizonte temporal de la simulación. En concreto, el coste total acumulado de generación de gas pasa de aproximadamente 2.713.300 unidades (sin almacenamiento) a 2.321.200 unidades (con almacenamiento), lo que representa una reducción del 14,5%. El coste medio diario se reduce de 13.567 a 11.606 unidades. Este resultado confirma que el almacenamiento distribuido, al suavizar las diferencias de uso de gas entre periodos, genera una ganancia de eficiencia en el sistema que beneficia al conjunto.

## 7.4. Limitaciones del modelo

El modelo presentado constituye una representación estilizada del problema, diseñada para aislar los mecanismos fundamentales de interés. Como toda simplificación, implica supuestos que es importante hacer explícitos para contextualizar los resultados.

**Demanda exógena y fija.** La demanda de electricidad en cada periodo se considera constante y no responde a los precios. En un mercado real, la demanda presenta cierta elasticidad, y la introducción de mecanismos de gestión de la demanda podría modificar los incentivos al almacenamiento y el equilibrio del sistema.

**Ausencia de costes de almacenamiento.** El modelo no incorpora costes asociados a la operación de las baterías (degradación, mantenimiento, coste de oportunidad del capital invertido). En la práctica, estos costes reducen la rentabilidad del almacenamiento y podrían modificar la fracción óptima de almacenamiento.

**Un solo tipo de generación de respaldo.** El modelo incluye únicamente un productor de gas como tecnología de respaldo. En los mercados reales, coexisten múltiples tecnologías con distintas estructuras de costes y restricciones técnicas, lo que enriquece la dinámica de formación de precios.

**Aprendizaje simplificado.** La regla de aprendizaje utilizada es un esquema de refuerzo básico que solo considera el beneficio obtenido por la acción elegida. Esquemas más sofisticados, como el EWA (Experience-Weighted Attraction), que también consideran los beneficios contrafactuales de las acciones no elegidas, podrían producir una convergencia más rápida o resultados diferentes.

**Ausencia de red eléctrica y restricciones de transmisión.** El modelo asume un mercado sin restricciones de red, en el que toda la energía producida puede venderse sin congestiones. En la práctica, las restricciones de transmisión pueden generar diferencias de precios entre nodos y afectar a los incentivos de localización del almacenamiento.

**Información y comportamiento estratégico.** Los agentes del modelo son tomadores de precios y no tienen en cuenta el impacto de sus decisiones individuales sobre los precios del mercado. En mercados con pocos productores o con agentes de gran tamaño, el comportamiento estratégico puede dar lugar a resultados significativamente diferentes de los obtenidos en un marco competitivo.

Estas limitaciones no invalidan los resultados del modelo, pero delimitan su ámbito de aplicabilidad y sugieren direcciones naturales para futuras extensiones, que se discuten en el Capítulo 8.
