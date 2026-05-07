# 8. Discusión y conclusiones

## 8.1. Principales hallazgos

El presente trabajo ha desarrollado, implementado y analizado un modelo basado en agentes que simula el comportamiento de un mercado eléctrico con productores solares heterogéneos capaces de almacenar energía y aprender de forma adaptativa su estrategia de almacenamiento. Los principales hallazgos del análisis pueden sintetizarse en los siguientes puntos.

**El almacenamiento distribuido reduce la brecha de precios entre periodos.** La introducción de sistemas de almacenamiento por parte de los productores solares produce una convergencia parcial de los precios de mercado entre los periodos de mañana y tarde. El precio medio del periodo de mañana aumenta un 55,8%, mientras que el del periodo de tarde se reduce un 18,2%. Este resultado refleja el traslado efectivo de energía solar desde las horas de exceso de producción hacia las horas de mayor demanda.

**Los agentes aprenden estrategias de almacenamiento estables.** El mecanismo de aprendizaje por refuerzo permite a los agentes identificar de forma descentralizada una fracción de almacenamiento que converge hacia aproximadamente 0,91. Esta convergencia se produce en las primeras decenas de días de simulación y es robusta frente a variaciones en los parámetros de aprendizaje, el número de agentes y la semilla aleatoria. La estrategia emergente es cualitativamente consistente con la condición de equilibrio teórico que iguala el beneficio marginal de almacenar con el coste de oportunidad de vender inmediatamente.

**Los agentes convergen de forma heterogénea.** Aunque la fracción media de almacenamiento converge hacia un nivel alto, los agentes individuales mantienen cierta dispersión en sus decisiones, reflejando las diferencias en los parámetros de aprendizaje y en la naturaleza estocástica de la regla de decisión logit. Esta dispersión se reduce con el tiempo pero no desaparece completamente, lo que constituye un resultado relevante: el equilibrio del sistema no requiere unanimidad entre agentes, sino solo estabilidad estadística a nivel agregado.

**El almacenamiento redistribuye, más que reduce, el uso de gas.** El gas total utilizado en el sistema no disminuye de forma sustancial con la introducción del almacenamiento. Lo que se produce es una redistribución: menos gas en el periodo de tarde (donde es más costoso) y más en el periodo de mañana (donde es más barato). No obstante, gracias a la convexidad de la función de costes del gas, esta redistribución sí reduce el coste total de generación térmica en un 14,5%, generando una ganancia de eficiencia en el sistema.

**Los productores solares se benefician del almacenamiento.** El beneficio medio de los agentes aumenta un 46,7% respecto al escenario sin almacenamiento, lo que confirma que la posibilidad de desplazar energía hacia el periodo de mayor valor genera una mejora económica significativa para los productores.

## 8.2. Relevancia para mercados reales

Aunque el modelo opera en un entorno altamente estilizado, los mecanismos identificados tienen correspondencia con dinámicas observadas o anticipadas en mercados eléctricos reales.

La convergencia de precios entre periodos como consecuencia del almacenamiento es un fenómeno documentado en mercados con alta penetración de baterías. En mercados como el australiano o el californiano, la expansión del almacenamiento ha comenzado a suavizar los picos de precios vespertinos, un efecto que el modelo reproduce de forma cualitativa.

La persistencia de heterogeneidad entre productores, incluso en un equilibrio estacionario, es también un rasgo realista: los operadores de almacenamiento real adoptan estrategias diversas en función de su tecnología, su posición en el mercado y su tolerancia al riesgo.

Finalmente, la observación de que el almacenamiento redistribuye el uso de gas más que eliminarlo tiene implicaciones relevantes para la política energética: los incentivos al almacenamiento distribuido no deben evaluarse únicamente por su capacidad de reducir emisiones totales, sino también por su contribución a la eficiencia del sistema y a la reducción de los costes de generación pico.

## 8.3. Trabajo futuro

El análisis realizado sugiere varias líneas de extensión que podrían profundizar los resultados obtenidos.

**Equilibrio teórico formal.** El desarrollo completo de la sección 4.6, con la derivación del equilibrio de Nash para los casos de agente único, dos agentes simétricos y $N$ agentes, permitiría cuantificar la distancia entre el resultado del ABM y las predicciones teóricas, cerrando el análisis de convergencia iniciado en el Capítulo 7.

**Demanda flexible.** La introducción de elasticidad en la demanda permitiría estudiar cómo el almacenamiento interactúa con la respuesta de los consumidores a los precios, generando potencialmente efectos de retroalimentación adicionales.

**Costes de degradación de baterías.** Incorporar un coste asociado al uso de la batería (proporcional a los ciclos de carga y descarga) permitiría analizar si los agentes aprenden a moderar el uso del almacenamiento cuando este tiene un coste operativo, y cómo esto modifica el equilibrio del sistema.

**Mercados multi-periodo.** La extensión del modelo a más de dos periodos diarios (por ejemplo, un esquema horario) permitiría representar de forma más realista la dinámica intradiaria de la generación solar y la demanda eléctrica.

**Aprendizaje más sofisticado.** La implementación de esquemas de aprendizaje que consideren beneficios contrafactuales (como el EWA) o que incorporen anticipación de precios podría acelerar la convergencia y modificar las propiedades del equilibrio.

**Heterogeneidad tecnológica realista.** La calibración del modelo con datos reales de plantas solares y sistemas de almacenamiento permitiría evaluar cuantitativamente los efectos del almacenamiento distribuido en mercados específicos.

Estas extensiones representan un programa de investigación que parte de la base establecida en este trabajo y que permitiría avanzar hacia un análisis más completo del papel del almacenamiento distribuido en la transición energética.
