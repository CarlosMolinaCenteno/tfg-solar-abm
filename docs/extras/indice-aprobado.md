# Indice aprobado del TFG - Modelo de almacenamiento solar adaptativo
## Aprobado: 2026-04-08

### 1. Introduccion
- Contexto energetico global
- Problema: intermitencia solar
- Propuesta: ABM con aprendizaje adaptativo
- Contribucion del TFG
- Estructura del documento

### 2. Motivacion y antecedentes
- 2.1. Mercado electrico y flexibilidad
- 2.2. Almacenamiento distribuido
- 2.3. Modelos existentes en la literatura
- 2.4. Justificacion del uso de un ABM

### 3. Descripcion del mercado electrico y actores
- 3.1. Estructura temporal del mercado
- 3.2. Productores solares
- 3.3. Productor de gas
- 3.4. Mercado y formacion de precios
- 3.5. Parametrizacion del modelo **[NUEVO]**

### 4. Modelo basado en agentes: fundamentos teoricos
- 4.1. Representacion del agente solar
- 4.2. Mecanismo de almacenamiento
- 4.3. Regla de aprendizaje adaptativo
- 4.4. Dinamica del sistema
- 4.5. Escenario sin baterias
- 4.6. Analisis teorico del equilibrio **[NUEVO]**
  - Agente unico: fraccion optima de almacenamiento
  - Dos agentes simetricos: equilibrio de Nash
  - Extension a N agentes

### 5. Implementacion del modelo en Mesa
- 5.1. Arquitectura general del modelo
- 5.2. Descripcion del flujo de simulacion
- 5.3. Validacion del modelo
  - 5.3.1. Validacion de la formacion de precios (Figura 5.1)
  - 5.3.2. Validacion del mecanismo de almacenamiento
  - 5.3.3. Validacion del proceso de aprendizaje (Figura 5.2)
  - 5.3.4. Coherencia de la dinamica temporal

### 6. Escenarios simulados
- 6.1. Escenario base: mercado sin almacenamiento
  - Figura 6.1: Evolucion temporal de precios
  - Figura 6.2: Uso de generacion de gas
- 6.2. Escenario con almacenamiento y aprendizaje adaptativo
  - Figura 6.3: Evolucion de la fraccion media de almacenamiento
  - Figura 6.4: Evolucion de precios
  - Figura 6.5: Uso de generacion de gas
- 6.3. Comparacion directa entre escenarios
  - Tabla 6.1: Comparacion de medias
  - Figura 6.6: Grafico de barras comparativo
- 6.4. Sensibilidad a parametros clave
  - 6.4.1. Sensibilidad a la eficiencia (eta)
    - Figura 6.7: Uso total de gas vs eta
  - 6.4.2. Sensibilidad a la intensidad del aprendizaje (phi)
    - Figura 6.8: Evolucion de fraccion media vs phi
  - 6.4.3. Sensibilidad al parametro de exploracion (beta) **[NUEVO]**
- 6.5. Robustez del comportamiento agregado

### 7. Analisis e interpretacion economica **[REESTRUCTURADO]**
- 7.1. Convergencia del aprendizaje y equilibrio
  - Conexion ABM <-> equilibrio teorico de 4.6
- 7.2. Impacto del almacenamiento en el mercado
  - Precios, volatilidad, uso de gas
- 7.3. Analisis de bienestar **[NUEVO]**
  - Coste total del sistema, beneficios de agentes
- 7.4. Limitaciones del modelo

### 8. Discusion y conclusiones
- 8.1. Principales hallazgos
- 8.2. Relevancia para mercados reales
- 8.3. Trabajo futuro

### Bibliografia

---
## Notas
- Cap. 5 detalle de codigo puede ir a apendice/GitHub si es necesario
- Figuras y tablas se numeran segun capitulo
- No preocuparse por limite de palabras de momento
