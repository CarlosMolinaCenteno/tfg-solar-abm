# 6. Escenarios simulados

En este capítulo se presentan los resultados obtenidos a partir de la simulación del modelo descrito e implementado en los capítulos anteriores. El objetivo no es interpretar en profundidad los mecanismos económicos subyacentes ni extraer conclusiones normativas, sino describir de forma sistemática el comportamiento del modelo bajo distintos escenarios y configuraciones.

Las simulaciones se diseñan con el fin de analizar cómo la introducción del almacenamiento distribuido y del aprendizaje adaptativo por parte de los productores solares modifica los resultados del mercado eléctrico en comparación con un escenario sin almacenamiento. Para ello, se consideran distintos escenarios que comparten los mismos parámetros fundamentales (demanda, estructura de costes y número de agentes) y difieren únicamente en la disponibilidad de almacenamiento y en la forma en que los agentes toman sus decisiones.

El capítulo se organiza de la siguiente manera. En primer lugar, se presenta un escenario base sin almacenamiento que sirve como referencia para el análisis posterior. A continuación, se analiza un escenario en el que los productores solares disponen de sistemas de almacenamiento y ajustan su comportamiento mediante un proceso de aprendizaje adaptativo. Posteriormente, se realiza una comparación directa entre ambos escenarios, cuantificando las diferencias observadas en los principales indicadores del mercado. Finalmente, se estudia la sensibilidad de los resultados a variaciones en parámetros clave del modelo y se analiza la robustez del comportamiento agregado. La interpretación económica de los patrones observados y sus implicaciones se aborda de forma específica en el Capítulo 7.

## 6.1. Escenario base: mercado sin almacenamiento

En este apartado se analiza el comportamiento del mercado eléctrico en un escenario base en el que los productores solares no disponen de sistemas de almacenamiento. Este escenario sirve como referencia para evaluar posteriormente el impacto de la introducción del almacenamiento distribuido y del aprendizaje adaptativo.

En el escenario base, la fracción de energía destinada al almacenamiento se fija en cero para todos los agentes y en todos los periodos de la simulación ($f_i(t) = 0\;\forall i, t$). Como consecuencia, toda la energía producida por los productores solares se vende de forma inmediata en el periodo correspondiente, sin posibilidad de desplazamiento intertemporal. El resto de los parámetros del modelo —incluyendo la demanda, la estructura del mercado y la tecnología de generación de gas— se mantienen idénticos a los del escenario con almacenamiento, con el fin de garantizar la comparabilidad de los resultados.

### Evolución de los precios de mercado

La Figura 6.1 muestra la evolución temporal de los precios de mercado en los periodos de mañana y tarde a lo largo de la simulación en el escenario sin almacenamiento. Se observa que el precio del periodo de mañana se sitúa en torno a $P_M \approx 69{,}4$.

Por el contrario, el precio del periodo de tarde adopta valores sustancialmente más elevados ($P_E \approx 238{,}5$ de media). Esta situación es consistente con una menor disponibilidad de energía solar en el periodo de mayor demanda y con la necesidad recurrente de recurrir a generación de gas como tecnología marginal.

En conjunto, el patrón de precios observado en este escenario refleja una clara asimetría temporal entre ambos periodos, asociada a la desalineación entre generación solar y demanda eléctrica.

### Uso de generación de gas

La Figura 6.2 presenta la evolución del uso de generación de gas en los periodos de mañana y tarde. En línea con el comportamiento de los precios, el uso de gas en el periodo de mañana es limitado ($\bar{Q}_G^M \approx 39{,}4$ unidades de media).

En el periodo de tarde, el uso de gas es significativamente mayor ($\bar{Q}_G^E \approx 111{,}2$ unidades de media). La ausencia de almacenamiento implica que la energía solar producida en el periodo de mañana no puede contribuir a satisfacer la demanda del periodo de tarde, lo que incrementa de forma sistemática la dependencia de la generación térmica de respaldo.



## 6.2. Escenario con almacenamiento y aprendizaje adaptativo

En este apartado se analiza el comportamiento del mercado eléctrico cuando los productores solares disponen de sistemas de almacenamiento y ajustan de forma adaptativa su estrategia de uso a lo largo del tiempo. Este escenario incorpora el modelo completo descrito en los capítulos anteriores y permite evaluar cómo la introducción de flexibilidad intertemporal modifica los resultados observados en el escenario base.


### Evolución de la estrategia de almacenamiento

La Figura 6.3 muestra la evolución temporal de las decisiones de almacenamiento de los agentes a lo largo de la simulación. La línea central representa la fracción media, que converge gradualmente hacia un valor de aproximadamente 0,91 a lo largo de los primeros 50 días de simulación. Las bandas sombreadas muestran la dispersión entre agentes: la desviación típica se mantiene estable y el rango mínimo-máximo abarca desde 0,1 hasta 1,0.

Este patrón muestra una dinámica de aprendizaje real: los agentes exploran diversas estrategias en los primeros días y progresivamente concentran sus decisiones en las fracciones de almacenamiento más rentables. La dispersión entre agentes se reduce con el tiempo, aunque no desaparece completamente, reflejando las diferencias en los parámetros de aprendizaje ($\phi_i$, $\beta_i$) y la naturaleza estocástica de la regla de decisión logit.

### Evolución de los precios de mercado

La Figura 6.4 presenta la evolución de los precios de mercado en los periodos de mañana y tarde en el escenario con almacenamiento. En comparación con el escenario base, se observan cambios apreciables en el perfil temporal de los precios, particularmente en el periodo de tarde.

El precio medio del periodo de mañana se sitúa en $P_M \approx 108{,}0$, sensiblemente superior al del escenario base. El precio del periodo de tarde, por su parte, se reduce a $P_E \approx 195{,}1$. Estos resultados ponen de manifiesto que las decisiones de almacenamiento adoptadas por los agentes influyen de forma sistemática en la formación de precios, produciendo una convergencia parcial entre los precios de ambos periodos.

### Uso de generación de gas

La Figura 6.5 muestra la evolución del uso de generación de gas en ambos periodos del día. En el escenario con almacenamiento, el uso de gas en el periodo de tarde se reduce a $\bar{Q}_G^E \approx 94{,}6$ unidades, inferior a las 111,2 del escenario base. En el periodo de mañana, el uso de gas aumenta a $\bar{Q}_G^M \approx 58{,}0$ unidades, frente a las 39,4 del escenario base.

Este patrón es coherente con el desplazamiento de energía solar desde el periodo de mañana hacia el periodo de tarde mediante el almacenamiento: al retirar oferta solar de la mañana, se incrementa la necesidad de gas en dicho periodo, mientras que la energía trasladada a la tarde reduce la dependencia de la generación térmica de respaldo en las horas de mayor demanda.

## 6.3. Comparación directa entre escenarios

En este apartado se realiza una comparación directa entre el escenario base sin almacenamiento y el escenario con almacenamiento y aprendizaje adaptativo, con el objetivo de cuantificar las diferencias observadas en los principales indicadores del mercado eléctrico. Esta comparación permite evaluar de forma sistemática el impacto agregado del almacenamiento distribuido, manteniendo constantes el resto de elementos del modelo.

La comparación se basa en valores medios calculados a lo largo del horizonte temporal de la simulación y se apoya en representaciones gráficas y tablas resumen que facilitan la lectura conjunta de los resultados.

### Comparación de precios medios

La Tabla 6.1 recoge los principales indicadores del mercado en ambos escenarios.

**Tabla 6.1** — Comparación de indicadores entre escenarios

| Indicador | Sin almacenamiento | Con almacenamiento | Variación |
|---|---|---|---|
| Precio medio mañana ($\bar{P}_M$) | 69,35 | 108,03 | +55,8% |
| Precio medio tarde ($\bar{P}_E$) | 238,46 | 195,06 | −18,2% |
| Gas medio mañana ($\bar{Q}_G^M$) | 39,42 | 57,99 | +47,1% |
| Gas medio tarde ($\bar{Q}_G^E$) | 111,18 | 94,55 | −14,9% |
| Beneficio medio agentes ($\bar{\pi}$) | 117,67 | 172,61 | +46,7% |
| Fracción media almac. (final) | 0,00 | 0,91 | — |
| Desv. típ. precio mañana (temporal)* | 0,64 | 2,08 | +225,0% |
| Desv. típ. precio tarde (temporal)* | 0,37 | 2,38 | +543,2% |

*La desviación típica temporal mide la variabilidad del precio entre días a lo largo de la simulación, no la dispersión entre agentes.

En el escenario con almacenamiento, el precio medio del periodo de mañana aumenta un 55,8% respecto al escenario base, mientras que el precio medio del periodo de tarde se reduce un 12,5%. Esta diferencia refleja un cambio sistemático en las condiciones de oferta del mercado: el almacenamiento retira energía del periodo de mañana (encareciendo su precio) y la traslada al periodo de tarde (abaratándolo).

### Comparación del uso de generación de gas

En el periodo de mañana, el uso de gas aumenta un 47,1%, mientras que en el periodo de tarde se observa una reducción del 14,9%. La Figura 6.6 representa gráficamente esta diferencia mediante un gráfico de barras comparativo, facilitando la visualización del cambio en la dependencia del gas como tecnología de respaldo cuando se introduce almacenamiento distribuido.

### Comparación de beneficios agregados

El beneficio medio obtenido por los productores solares aumenta un 46,7% en el escenario con almacenamiento. Esta mejora indica que la posibilidad de desplazar energía entre periodos permite a los agentes capturar una mayor parte del valor generado por la diferencia de precios, lo que tiene efectos económicos agregados significativos.

Esta diferencia se observa de manera consistente a lo largo de la simulación y refuerza la idea de que el almacenamiento modifica de forma relevante los resultados del mercado, tanto a nivel de precios como de ingresos de los productores.

## 6.4. Sensibilidad a parámetros clave

En este apartado se analiza cómo los resultados del modelo responden a variaciones en tres parámetros fundamentales: la eficiencia de la batería ($\eta$), la intensidad del aprendizaje ($\phi$) y el grado de exploración frente a explotación ($\beta$). En cada caso, se fija el parámetro estudiado en un valor homogéneo para todos los agentes, manteniendo el resto de parámetros en sus valores por defecto, y se ejecutan múltiples réplicas con distintas semillas aleatorias para obtener resultados robustos.

El objetivo de este análisis no es determinar los valores óptimos de los parámetros, sino observar cómo el comportamiento del mercado varía en función de las características tecnológicas y de aprendizaje de los agentes.

Es importante señalar una diferencia metodológica respecto a los escenarios anteriores: en los análisis de sensibilidad, el parámetro estudiado se fija en un valor **homogéneo** para todos los agentes, mientras que en el escenario principal (sección 6.2) cada agente recibe valores extraídos de distribuciones heterogéneas. Por este motivo, las fracciones de almacenamiento observadas en los análisis de sensibilidad pueden diferir ligeramente de las del escenario principal (en torno a 0,91). Esta diferencia refleja el efecto de la heterogeneidad de parámetros sobre el resultado agregado y no una inconsistencia del modelo.

### 6.4.1. Sensibilidad a la eficiencia de la batería ($\eta$)

La eficiencia de la batería determina la fracción de energía que se recupera del ciclo de almacenamiento. Un valor de $\eta = 1$ corresponde a un almacenamiento sin pérdidas, mientras que valores inferiores reflejan pérdidas crecientes en el proceso de carga y descarga.

Se ejecutan simulaciones con $\eta$ homogéneo en los valores $\{0{,}70;\ 0{,}75;\ 0{,}80;\ 0{,}85;\ 0{,}90;\ 0{,}95;\ 1{,}00\}$, con 5 réplicas por configuración.

La Figura 6.7 muestra la relación entre la eficiencia de la batería y el uso total medio de gas. Se observa una relación linealmente decreciente: a medida que aumenta la eficiencia, el uso total de gas se reduce desde aproximadamente 155 unidades ($\eta = 0{,}70$) hasta 150 unidades ($\eta = 1{,}00$). Esta reducción refleja el efecto directo de una mayor eficiencia sobre la oferta efectiva de energía solar en el periodo de tarde. Cuando las baterías son más eficientes, una mayor proporción de la energía almacenada se traslada realmente al periodo de mayor demanda, reduciendo la necesidad de generación de gas.

La fracción media de almacenamiento elegida por los agentes se mantiene estable en torno a 0,91-0,93 para todos los valores de $\eta$, lo que sugiere que la decisión de almacenamiento está más condicionada por la estructura de precios del mercado que por la eficiencia tecnológica de las baterías. No obstante, la mayor eficiencia amplifica el efecto económico de cada unidad almacenada, lo que explica la reducción del uso de gas sin un cambio significativo en la estrategia de los agentes.

### 6.4.2. Sensibilidad a la intensidad del aprendizaje ($\phi$)

El parámetro $\phi$ controla la velocidad con la que los agentes incorporan nueva información en sus valoraciones. Un valor bajo de $\phi$ implica que el agente pondera de forma similar toda su historia de beneficios, mientras que un valor alto hace que la experiencia más reciente tenga un peso dominante.

Se ejecutan simulaciones con $\phi$ homogéneo en los valores $\{0{,}01;\ 0{,}05;\ 0{,}10;\ 0{,}20;\ 0{,}30;\ 0{,}50\}$.

La Figura 6.8 muestra la evolución temporal de la fracción media de almacenamiento para cada valor de $\phi$. Se observa que todas las configuraciones convergen a niveles de almacenamiento similares en torno a 0,90-0,92, lo que indica que la intensidad del aprendizaje no modifica sustancialmente el punto de convergencia del sistema. Sin embargo, sí se aprecian diferencias claras en la dinámica de transición: valores bajos de $\phi$ generan una convergencia más lenta y gradual, mientras que valores altos producen un ajuste más rápido en los primeros días de simulación.

Este resultado es relevante desde un punto de vista económico: sugiere que el equilibrio al que tiende el sistema es robusto frente a la velocidad de aprendizaje de los agentes, y que el nivel de almacenamiento agregado está determinado fundamentalmente por las condiciones estructurales del mercado (demanda, costes del gas, eficiencia) más que por las particularidades del proceso de aprendizaje.

### 6.4.3. Sensibilidad al parámetro de exploración ($\beta$)

El parámetro $\beta$ regula el equilibrio entre exploración y explotación en la regla de decisión logit. Valores bajos de $\beta$ generan decisiones prácticamente aleatorias (alta exploración), mientras que valores altos concentran la probabilidad de elección en las estrategias con mayor atracción acumulada (alta explotación).

Se ejecutan simulaciones con $\beta$ homogéneo en los valores $\{0{,}5;\ 1{,}0;\ 2{,}0;\ 3{,}0;\ 5{,}0;\ 10{,}0\}$.

La Figura 6.9 muestra la evolución temporal de la fracción media de almacenamiento para cada valor de $\beta$. A diferencia de $\phi$, el parámetro $\beta$ sí produce diferencias apreciables en el nivel de almacenamiento medio alcanzado. Para valores bajos ($\beta = 0{,}5$), la fracción se sitúa en torno a 0,69, reflejando una exploración amplia que no permite concentrar las decisiones en las fracciones más rentables. Para valores intermedios ($\beta = 2{,}0$), la fracción media se eleva a 0,89. Para valores altos ($\beta = 5{,}0$ y $\beta = 10{,}0$), la fracción media alcanza 0,96-0,97, indicando que los agentes con mayor capacidad de explotación convergen de forma casi completa hacia la fracción óptima.

El efecto sobre el precio medio del periodo de tarde es coherente con esta observación: configuraciones con mayor $\beta$ tienden a producir precios ligeramente inferiores en el periodo de tarde, reflejando un mayor desplazamiento de energía solar desde la mañana.

Este resultado pone de manifiesto que la capacidad de los agentes para explotar la información disponible afecta no solo a su comportamiento individual, sino al resultado agregado del mercado. En un sistema donde los agentes actúan de forma más determinista, el almacenamiento resultante es mayor y los precios del periodo de tarde se ven más afectados.


## 6.5. Robustez del comportamiento agregado

El objetivo de este apartado es verificar que los resultados observados en los apartados anteriores no dependen de forma crítica de realizaciones aleatorias particulares ni del número exacto de agentes en el mercado. Para ello, se analiza la estabilidad de los principales indicadores del modelo bajo variaciones en la semilla aleatoria y en el número de productores solares.

### Variación del número de agentes

Se ejecutan simulaciones para $N \in \{10,\ 20,\ 30,\ 50,\ 100\}$ agentes, con 10 réplicas por configuración (cada una con una semilla aleatoria distinta). El resto de parámetros se mantiene en sus valores por defecto.

La Figura 6.10 presenta los resultados en dos paneles. El panel izquierdo muestra el precio medio del periodo de tarde en función del número de agentes. Se observa una relación decreciente clara: el precio medio pasa de aproximadamente 239 con $N = 10$, a 85 con $N = 100$. Este comportamiento es esperado, ya que incluir un mayor número de productores solares sin repartir la capacidad total implica una mayor oferta agregada de energía renovable, lo que reduce la necesidad de recurrir a generación de gas y, por tanto, los precios.

El panel derecho muestra la fracción media de almacenamiento final. Este indicador se mantiene estable en torno a 0,90 para $N$ entre 10 y 50, con una reducción a 0,68 para $N = 100$, lo que indica que la estrategia de almacenamiento agregada es robusta frente al tamaño del mercado. 

### Estabilidad frente a semillas aleatorias

La utilización de múltiples réplicas para cada configuración permite evaluar la variabilidad asociada a la estocasticidad del modelo. En el caso de referencia con $N = 30$, la desviación típica del precio medio del periodo de tarde entre réplicas es reducida, lo que confirma la estabilidad del modelo. Este nivel de variabilidad confirma que los resultados del modelo son estables y reproducibles para el horizonte temporal considerado.

### Síntesis del análisis de sensibilidad y robustez

Los análisis realizados en los apartados 6.4 y 6.5 permiten extraer las siguientes observaciones descriptivas:

- La eficiencia de la batería ($\eta$) tiene un efecto directo y monotónico sobre el uso de gas, pero no modifica sustancialmente la estrategia de almacenamiento de los agentes.
- La intensidad del aprendizaje ($\phi$) afecta a la velocidad de convergencia, pero no al nivel de equilibrio al que tiende el sistema.
- El parámetro de exploración ($\beta$) sí influye en el nivel de almacenamiento agregado, distinguiendo configuraciones en las que los agentes actúan de forma más o menos aleatoria.
- Los resultados son robustos frente al número de agentes y a la semilla aleatoria.

En el siguiente capítulo se analizan e interpretan estos resultados desde un punto de vista económico.
