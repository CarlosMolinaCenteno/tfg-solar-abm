# 5. Implementación del modelo en Mesa

En este capítulo se describe la implementación computacional del modelo basado en agentes desarrollado en los capítulos anteriores. El objetivo no es detallar exhaustivamente el código, sino explicar cómo las relaciones teóricas y las decisiones de modelización se traducen en una simulación operativa utilizando la librería Mesa en Python.

La implementación permite simular la interacción de múltiples productores solares que toman decisiones descentralizadas de almacenamiento, así como analizar la evolución del mercado eléctrico resultante en distintos escenarios. En particular, se busca que la estructura del código refleje de manera fiel la secuencia temporal del modelo, el proceso de toma de decisiones de los agentes y la formación de precios en cada periodo.

La elección de Mesa como entorno de desarrollo responde a su adecuación para modelos basados en agentes, ya que proporciona una arquitectura clara para definir agentes, modelos y mecanismos de actualización temporal, facilitando tanto la experimentación como la reproducibilidad de los resultados.

## 5.1. Arquitectura general del modelo

La implementación del modelo sigue la estructura estándar propuesta por la librería Mesa, que distingue claramente entre tres componentes principales: el modelo global, los agentes individuales y el planificador temporal (*scheduler*).

El modelo global se implementa mediante una clase que hereda de `Model` y que contiene los parámetros comunes del mercado eléctrico, la creación de los agentes y el control de la evolución temporal de la simulación. Esta clase centraliza la información agregada necesaria para el funcionamiento del mercado, como los niveles de demanda, los parámetros del productor de gas y las reglas de formación de precios.

Los agentes solares se implementan como instancias de una clase que hereda de `Agent`. Cada agente encapsula sus propios parámetros tecnológicos y de aprendizaje, así como las variables internas necesarias para tomar decisiones y actualizar su comportamiento a lo largo del tiempo. Esta separación permite representar de forma natural la heterogeneidad entre productores solares y facilita la extensión del modelo a configuraciones más complejas.

En cuanto a la gestión temporal, el modelo no emplea un planificador secuencial estándar como `BaseScheduler`. En su lugar, la activación de los agentes se realiza mediante una llamada explícita al método `shuffle_do`, que ejecuta de forma aleatoria un mismo método de decisión para todos los agentes en cada paso temporal. Esta elección permite representar de manera más fiel la toma de decisiones simultánea de los productores solares al inicio de cada día, evitando posibles efectos artificiales derivados del orden de activación de los agentes. En nuestro caso, las decisiones de un agente no condicionan las de otros, por lo que no debería suponer ningún cambio, pero este método es más robusto frente a posibles variaciones del modelo.

Cada iteración del método `step_day()` del modelo representa un día completo y sigue una secuencia bien definida: en primer lugar, los agentes solares toman sus decisiones de almacenamiento y determinan su oferta en cada periodo; a continuación, el modelo calcula la oferta agregada, despeja los mercados de mañana y tarde y determina los precios correspondientes; finalmente, los agentes observan los resultados y actualizan su comportamiento mediante la regla de aprendizaje descrita en el Capítulo 4.

## 5.2. Descripción del flujo de simulación

En este apartado se describe el funcionamiento del modelo a lo largo de una iteración temporal completa, que en la simulación representa un día. El objetivo es mostrar cómo la lógica económica y el modelo teórico descritos en los capítulos anteriores se traducen en una secuencia concreta de operaciones computacionales.

Cada día de simulación se implementa mediante una llamada al método `step_day()` del modelo, que coordina las decisiones de los agentes, la formación de precios, la actualización del aprendizaje y la recolección de datos. A continuación, se describen estas etapas en el orden en que se ejecutan.

### 5.2.1. Inicialización del modelo y de los agentes

La simulación comienza con la creación de una instancia del modelo de mercado, implementado en la clase `MarketModel`. Esta fase de inicialización establece el entorno global en el que interactuarán los agentes y fija los parámetros comunes del mercado eléctrico que permanecerán constantes a lo largo de la simulación.

En el constructor de la clase `MarketModel`, se crea un número fijo de productores solares, cada uno de ellos representado por una instancia de la clase `SolarAgent`. El número de agentes es un parámetro exógeno del modelo y determina el tamaño del mercado simulado. Durante esta fase, el modelo no ejecuta todavía ninguna interacción estratégica, sino que se limita a configurar el sistema y a preparar las estructuras necesarias para la evolución temporal posterior.

Cada agente solar se inicializa de forma independiente en el constructor de la clase `SolarAgent`. En este proceso se asignan los parámetros tecnológicos y de comportamiento que caracterizan al agente, tales como la capacidad productiva, la capacidad de almacenamiento, la eficiencia del sistema de baterías y los parámetros asociados al aprendizaje adaptativo. Estos valores se extraen de distribuciones comunes, lo que introduce heterogeneidad entre agentes y permite representar diferencias realistas entre productores solares sin imponer comportamientos estratégicos diferenciados de manera exógena.

Además de los parámetros tecnológicos, cada agente inicializa su estado interno de aprendizaje. En particular, se define el conjunto discreto de fracciones de almacenamiento disponibles y se asocia a cada una de ellas un valor inicial de atracción. Estas atracciones representan la valoración inicial de cada estrategia y se inicializan con pequeños valores aleatorios, evitando así que el comportamiento de los agentes esté sesgado hacia una decisión concreta en los primeros días de simulación.

Una vez creados los agentes, el modelo inicializa un recolector de datos (`DataCollector`), que se encargará de almacenar información relevante tanto a nivel agregado del mercado como a nivel individual de los agentes. En esta fase se definen explícitamente las variables que se registrarán en cada periodo, preparando la simulación para el análisis posterior de resultados.

Tras completar esta etapa de inicialización, el modelo queda preparado para comenzar la simulación dinámica. A partir de este punto, cada llamada al método que representa un día de simulación activará el proceso de decisiones, interacción de mercado y aprendizaje descrito en los apartados siguientes.

### 5.2.2. Producción y decisión de almacenamiento

La primera etapa de cada día de simulación corresponde a la producción de energía solar y a la decisión de almacenamiento de los agentes. Esta etapa se implementa en la clase `SolarAgent`, concretamente en el método `produce_and_decide`, que encapsula el comportamiento individual de los productores solares al inicio de cada periodo temporal.

Desde el punto de vista del flujo diario del modelo, esta fase se ejecuta de forma simultánea para todos los agentes mediante una activación aleatoria coordinada por el modelo. Conceptualmente, esto representa que todos los productores toman su decisión de almacenamiento sin observar las decisiones de los demás en ese mismo día, coherentemente con la formulación teórica del modelo.

En el método `produce_and_decide`, cada agente comienza determinando su producción solar diaria introduciendo un shock meteorológico idiosincrático. Este shock afecta de manera multiplicativa tanto a la producción del periodo de mañana como a la del periodo de tarde, reflejando la variabilidad inherente a la generación solar. A partir de este shock y de la capacidad instalada del agente, se calculan las cantidades potenciales de energía disponibles en cada periodo.

Una vez determinada la producción, el agente elige la fracción de energía del periodo de mañana que destina al almacenamiento. Esta elección se realiza a partir de las atracciones internas asociadas a cada fracción posible de almacenamiento, que el agente mantiene como parte de su estado interno. En la implementación, estas atracciones se almacenan como un diccionario que asigna un valor a cada fracción discreta del conjunto de decisiones permitido.

La probabilidad de seleccionar cada fracción se calcula mediante una regla logit, implementada a través de una función *softmax* numéricamente estable. El parámetro de sensibilidad del agente controla el grado de exploración o explotación en la elección, de modo que fracciones con mayor atracción acumulada tienen una mayor probabilidad de ser seleccionadas, sin que la decisión sea completamente determinista.

Una vez seleccionada la fracción de almacenamiento, el agente determina la cantidad de energía que se vende de forma inmediata en el periodo de mañana y la cantidad de energía que se almacena para su uso posterior. Las pérdidas de eficiencia de la batería ($\eta_i$) se aplican en el momento del almacenamiento: la energía efectivamente almacenada es $\eta_i \cdot f_i \cdot \tilde{q}_i^M$, sujeta al límite de capacidad $s_i$. La energía almacenada se incorpora a la oferta del periodo de tarde, estableciendo así un vínculo intertemporal entre ambos mercados dentro del mismo día de simulación.

Al finalizar este método, el agente ha fijado completamente su contribución a la oferta agregada del sistema en ambos periodos. Estas decisiones individuales no producen todavía efectos directos sobre los precios, que se determinan únicamente en la siguiente etapa del flujo diario, una vez que el modelo ha agregado las decisiones de todos los agentes.

### 5.2.3. Agregación de la oferta y *clearing* del mercado

Una vez que todos los agentes han producido energía y han tomado su decisión de almacenamiento al inicio del día, el modelo procede a determinar el resultado del mercado en cada uno de los periodos. Esta etapa se implementa en el método `step_day` de la clase `MarketModel` y constituye el mecanismo mediante el cual las decisiones individuales se traducen en precios de mercado y uso de generación de respaldo.

En primer lugar, el modelo calcula la oferta agregada de energía solar en el periodo de mañana. Para ello, se suman las cantidades de energía que cada agente ha decidido vender de forma inmediata tras su producción matutina. Esta agregación se realiza una vez que todos los agentes han ejecutado el método `produce_and_decide`, garantizando que la oferta considerada refleja un conjunto completo de decisiones simultáneas.

La oferta solar agregada se compara a continuación con la demanda exógena del periodo de mañana. Si la producción solar es suficiente para cubrir la demanda, el mercado se despeja sin necesidad de recurrir a generación de gas y el precio del periodo se fija en cero. Este resultado representa una situación de abundancia de energía renovable, en la que la tecnología marginal no entra en operación.

En caso contrario, cuando la oferta solar es insuficiente para satisfacer la demanda, el modelo introduce generación de gas para cubrir la demanda residual. La cantidad de energía producida mediante gas se calcula como la diferencia entre la demanda y la oferta solar agregada, y el precio del mercado se determina a partir del coste marginal asociado a dicha producción. Este coste marginal se modeliza como una función creciente de la cantidad producida, reflejando el encarecimiento progresivo de la generación térmica conforme aumenta su utilización.

Una vez despejado el mercado de mañana, el modelo repite el mismo procedimiento para el periodo de tarde. En este caso, la oferta solar agregada incluye tanto la producción directa de los agentes en el periodo de tarde como la energía previamente almacenada durante el periodo de mañana. De este modo, las decisiones de almacenamiento tomadas al inicio del día influyen de forma directa en la oferta disponible y en la necesidad de recurrir a generación de gas en el periodo de mayor demanda.

Al finalizar esta etapa, el modelo ha determinado los precios de mercado y el uso de generación de gas en ambos periodos del día. Estos resultados constituyen el vínculo fundamental entre las decisiones individuales de los agentes y los incentivos económicos que guiarán su aprendizaje en etapas posteriores. Es importante destacar que, hasta este punto, los agentes no han actualizado aún su comportamiento: los precios se forman exclusivamente a partir de la agregación de decisiones ya tomadas, de acuerdo con la lógica de mercado definida en el Capítulo 3.

### 5.2.4. Cálculo de beneficios y actualización del aprendizaje

Una vez que el modelo ha determinado los precios de mercado en los periodos de mañana y tarde, se procede al cálculo de los beneficios individuales de los agentes y a la actualización de su comportamiento. Esta etapa cierra el ciclo diario de la simulación y constituye el mecanismo fundamental mediante el cual los agentes adaptan progresivamente sus decisiones.

El cálculo de beneficios se realiza dentro del método `step_day` de la clase `MarketModel`, una vez que los mercados de ambos periodos han sido despejados. Para cada agente solar, el beneficio diario se calcula como el ingreso obtenido por la venta de energía en cada periodo, es decir, como la suma del producto entre el precio de cada periodo y la cantidad de energía vendida en dicho periodo. De este modo, los beneficios reflejan directamente el resultado económico de la decisión de almacenamiento tomada al inicio del día.

Una vez calculado el beneficio, el modelo delega en cada agente la actualización de su estado interno de aprendizaje. Esta actualización se implementa en el método `update_learning` de la clase `SolarAgent`, siguiendo la formulación desarrollada en el Capítulo 4.

En primer lugar, el método calcula el beneficio contrafactual que el agente habría obtenido con cada una de las fracciones posibles del espacio de decisiones, utilizando los precios ya fijados por el mercado y la producción bruta del día. Dado que los precios de mercado son públicos, esta información está disponible para cualquier agente sin necesidad de observar las decisiones de los demás. A partir de este vector de beneficios contrafactuales se obtienen el máximo contrafactual y su desviación típica, que permiten construir la señal normalizada $r_i(f, t) = (\pi_i(f, t) - \pi_i^{\max}(t)) / \sigma_i(t)$.

A continuación, el agente actualiza las atracciones de todas las fracciones aplicando la regla $(1 - \phi_i) \cdot A_i(f, t) + \phi_i \cdot r_i(f, t)$. La fracción que resultó óptima ex-post recibe una señal nula (no se refuerza ni se deprecia relativamente), mientras que las fracciones subóptimas reciben señales negativas proporcionales a su coste de oportunidad estandarizado.

Este esquema de aprendizaje por refuerzo contrafactual permite a los agentes extraer información sobre todas las estrategias posibles a partir de los precios observados, sin necesidad de haberlas probado efectivamente. De este modo, las estrategias que habrían generado mayores beneficios tienden a ser seleccionadas con mayor probabilidad en los días siguientes, dando lugar a una dinámica de adaptación progresiva sin que los agentes resuelvan problemas de optimización intertemporal ni anticipen el comportamiento de los demás.

Es importante destacar que la actualización del aprendizaje se produce después de la formación de precios y del cálculo de beneficios, y que no afecta a las decisiones tomadas dentro del mismo día. De este modo, el modelo respeta una estructura temporal clara en la que las decisiones influyen en los precios, los precios determinan los beneficios y los beneficios condicionan las decisiones futuras, pero nunca de forma simultánea dentro de un mismo periodo.

### 5.2.5. Recolección de datos y transición al siguiente periodo

Una vez que los agentes han actualizado su estado interno de aprendizaje al final del día, el modelo procede a la recolección sistemática de información sobre el estado del sistema y de los agentes. Esta etapa final del flujo diario se implementa mediante el uso del objeto `DataCollector`, inicializado en la clase `MarketModel`, y tiene como objetivo facilitar el análisis posterior de los resultados de la simulación.

El `DataCollector` registra, en cada día de simulación, un conjunto de variables agregadas del mercado. Entre estas variables se incluyen los precios de mercado en los periodos de mañana y tarde, el uso de generación de gas en cada periodo, la producción solar total y estadísticas resumidas del comportamiento de los agentes, como la fracción media de almacenamiento elegida y el beneficio medio diario. Estas variables permiten caracterizar la evolución temporal del sistema y analizar cómo las decisiones individuales afectan al funcionamiento agregado del mercado.

De forma complementaria, el recolector de datos almacena información a nivel individual de los agentes. En particular, se registran variables como la cantidad de energía vendida en cada periodo, la fracción de almacenamiento seleccionada, la energía almacenada y el beneficio obtenido por cada agente en cada día. Este nivel de detalle permite estudiar la heterogeneidad entre agentes, la convergencia del aprendizaje y la posible aparición de patrones diferenciados de comportamiento.

La recolección de datos se realiza al final de cada día, una vez que todas las decisiones, interacciones de mercado y actualizaciones de aprendizaje han tenido lugar. De este modo, los valores registrados reflejan el estado completo del sistema tras una iteración temporal y pueden interpretarse directamente como resultados diarios de la simulación.

Tras completar la recolección de datos, el modelo queda preparado para iniciar el siguiente día de simulación. El flujo descrito en los apartados anteriores se repite de manera idéntica en cada iteración, permitiendo observar la evolución dinámica del mercado y del comportamiento de los agentes a lo largo de horizontes temporales prolongados.

## 5.3. Validación del modelo

Este apartado tiene como objetivo verificar que la implementación computacional del modelo reproduce correctamente la lógica económica descrita en los capítulos anteriores y que su comportamiento es consistente con los supuestos teóricos planteados. La validación no persigue contrastar el modelo con datos reales, sino comprobar que el código ejecuta de forma adecuada los mecanismos definidos y que los resultados obtenidos son razonables desde un punto de vista económico.

La validación se estructura en torno a varios aspectos clave del modelo: la formación de precios, el funcionamiento del almacenamiento, el proceso de aprendizaje de los agentes y la coherencia de la dinámica temporal.

### 5.3.1. Validación de la formación de precios

En primer lugar, se verifica el correcto funcionamiento del mecanismo de vaciado del mercado en ambos periodos del día. De acuerdo con la formulación teórica, el precio de mercado debe fijarse en cero cuando la oferta agregada de energía solar es suficiente para cubrir la demanda, y debe coincidir con el coste marginal de la generación de gas cuando esta entra como tecnología de respaldo.

Para validar este comportamiento, se comprueba que en aquellos días en los que la producción solar agregada supera la demanda exógena, el precio registrado por el modelo es nulo y no se utiliza generación de gas. De forma análoga, cuando la producción solar es insuficiente, el modelo introduce generación de gas y fija el precio de acuerdo con la función de coste marginal definida.

La Figura 5.1 muestra la evolución de los precios de mercado en los periodos de mañana y tarde a lo largo de la simulación. Se observa que el precio del periodo de mañana presenta valores nulos en un número significativo de días, coherentemente con situaciones de abundancia de generación solar. Por el contrario, el precio del periodo de tarde refleja una mayor dependencia de la generación de gas, adoptando valores positivos de forma más frecuente. Este comportamiento confirma el correcto funcionamiento del mecanismo de formación de precios implementado.

### 5.3.2. Validación del mecanismo de almacenamiento

El segundo elemento validado es el funcionamiento del almacenamiento distribuido. En el modelo, la energía almacenada por los agentes debe cumplir dos propiedades fundamentales: por un lado, reducir la oferta de energía en el periodo de mañana y, por otro, aumentar la oferta disponible en el periodo de tarde.

Para comprobar este comportamiento, se analiza la relación entre la fracción media de almacenamiento elegida por los agentes y la producción solar agregada en cada periodo. En particular, se observa que aumentos en la fracción de almacenamiento reducen la energía vendida en el periodo de mañana y elevan la energía ofertada en el periodo de tarde, confirmando el efecto intertemporal esperado.

Asimismo, se verifica que la energía almacenada está sujeta a las restricciones técnicas implementadas en el código, de modo que no se supera la capacidad de almacenamiento individual ni la energía disponible tras considerar la eficiencia del sistema de baterías.

### 5.3.3. Validación del proceso de aprendizaje

Un aspecto central del modelo es la capacidad de los agentes para adaptar su comportamiento a partir de la experiencia. Para validar el proceso de aprendizaje, se analiza la evolución temporal de las decisiones de almacenamiento y de las atracciones asociadas a cada estrategia.

La Figura 5.2 representa la evolución de la fracción media de almacenamiento elegida por los agentes. Se verifica que las atracciones se actualizan correctamente: la fracción elegida recibe refuerzo proporcional al beneficio obtenido, mientras que las restantes se deprecian. La fracción media tiende a estabilizarse a lo largo de la simulación, confirmando que el mecanismo de aprendizaje genera adaptación progresiva. El análisis detallado de la dinámica de convergencia y sus implicaciones económicas se desarrolla en los Capítulos 6 y 7.

### 5.3.4. Coherencia de la dinámica temporal

Finalmente, se valida la coherencia temporal del modelo, comprobando que las distintas etapas del flujo diario se ejecutan en el orden correcto y que no existen retroalimentaciones simultáneas no deseadas.

En particular, se verifica que las decisiones de almacenamiento se toman antes de la formación de precios, que los precios determinan los beneficios y que estos beneficios solo afectan a las decisiones futuras de los agentes a través del aprendizaje. Esta separación temporal garantiza que el modelo respeta la causalidad económica implícita en su formulación teórica.

La repetición consistente de este flujo a lo largo de la simulación permite interpretar cada iteración como un día independiente, conectado con los anteriores únicamente a través del estado interno de aprendizaje de los agentes.
