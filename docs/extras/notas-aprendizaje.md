# Anexo. Diseño y diagnóstico de la regla de aprendizaje

Este anexo documenta el proceso real —con sus callejones sin salida, correcciones y la
correspondencia con el tutor— por el que se llegó a la regla de aprendizaje adoptada en el
Capítulo 4. El cuerpo del capítulo expone el resultado en un orden lógico (los dos ejes de
diseño, la regla elegida); este anexo recoge cómo se llegó hasta ahí, y conviene leerlo en **dos
registros distintos**:

- **Antes del banco (Partes I–II)**: el recorrido cronológico de pruebas sueltas —los callejones
  de la esquina, el bug de semilla, una conclusión que luego se invierte—. Su lección de fondo no
  fue una regla concreta, sino *metodológica*: con ensayos ad-hoc no se podía decidir entre
  reglas, y eso reveló la necesidad de construir un banco de pruebas.
- **Con el banco (Partes III–IV)**: el análisis sistemático hecho **ya con ese banco**, en el
  régimen final del TFG —el marco de los dos ejes, los barridos, la comparativa entre reglas y la
  reconciliación de métricas—. Es donde se tomaron las decisiones y lo que respalda el capítulo;
  aquí caen también análisis que apoyan el cuerpo (initraw §14, atracción media §16), no
  descubrimientos del camino.

El código ejecutable de todas las comprobaciones vive en el cuaderno `banco_pruebas.ipynb`
(§§5–12) y en el script `generate_figures_cap4.py`; este anexo se centra en la narrativa y los
resultados, y remite a ellos para la reproducción.

## Aviso sobre los parámetros

El proceso atravesó **tres regímenes de parámetros**, y conviene no confundir sus cifras:

| Régimen | Cuándo | Parámetros | Equilibrio |
|---|---|---|---|
| **Esquina** | exploración inicial (Partes I) | $D_M=60$, $c\in[0{,}8;1{,}2]$ | $f^*=1{,}0$ (trivial) |
| **Interior intermedio** | reparametrización (Parte II) | $D_M=80$, $\bar c=2{,}0$ | $f^*\approx0{,}72$ (numérico) |
| **Interior final** | TFG (Partes III–IV) | $D_M=80$, $c=2{,}5$, $s=10$, $\eta=0{,}9$ | cártel $0{,}475$, Nash $f^N=0{,}639$ |

**Solo las cifras del régimen final (Partes III–IV) son las del cuerpo del TFG.** Las de los
regímenes de esquina e intermedio se conservan como registro del proceso, no como resultados
publicables.

---

# Parte I — Antes del banco: los callejones del régimen de esquina

Toda la exploración inicial de reglas se hizo con los parámetros originales del modelo, que dan
una solución de esquina ($f^*=1{,}0$: a esos precios siempre conviene almacenar al máximo). Que
el óptimo fuera trivial ocultó durante un tiempo el verdadero problema, como se verá en la
Parte II.

## 1. El punto de partida: fijación el día uno

El modelo original fijaba a los 30 agentes en una fracción **aleatoria** el primer día, que ya
no cambiaban (verificado: 30 de 30 agentes con una sola elección en toda la simulación; 26 de
30 en una fracción subóptima). La causa es un **desajuste de escala**: las atracciones se
inicializan en $A_i(f,0)\sim\mathcal U(-0{,}1;0{,}1)$, pero el beneficio diario es $\pi\approx180$.
Tras un día, la atracción de la fracción jugada salta a $\approx13$ mientras el resto sigue en
$\approx0$; con $\beta\approx3{,}8$ la softmax da $\Pr[f\text{ jugada}]\approx1$. El agente queda
"fijado" sin haber comparado con nada.

Este es el **problema de escala** del cuerpo (§4.2.1). La señal cruda, demasiado grande frente
a las atracciones, colapsa la decisión.

## 2. Primer intento: normalizar por el máximo contrafactual ($\pi/\pi^{\max}$)

Aprovechando que los precios son públicos, el agente calcula el beneficio que habría dado cada
fracción y normaliza su realizado por el máximo: $\pi^{\text{norm}}=\pi/\pi^{\max}\in[0,1]$.
Esto **resuelve la fijación** (la señal vuelve a una escala comparable a las atracciones y los
agentes exploran), pero **no converge**: tras 500–2000 días, 23 de 30 agentes siguen en
fracciones subóptimas (gap medio $\approx16\%$). La razón: $\pi/\pi^{\max}$ es **siempre
positiva**, así que hasta una mala elección recibe refuerzo positivo. La señal dice "esto fue
regular", nunca "esto fue malo, cámbialo".

## 3. Centrar en cero: el *regret* ($(\pi-\pi^{\max})/\pi^{\max}$)

Para que la señal pueda castigar, se centra en el máximo: $\pi^{\text{norm}}=(\pi-\pi^{\max})/\pi^{\max}\in[-1,0]$
—cero si se acertó la óptima del día, negativo si no—. Es el *coste de oportunidad* o *regret*.
Pero, aplicado **solo a la fracción jugada**, sigue sin converger (23/30 subóptimos): castiga lo
malo pero no informa de las alternativas. El agente sabe "esto fue malo", no "aquello habría
sido mejor". El castigo produce exploración aleatoria, no dirigida.

## 4. Aprender de todas las fracciones (estructura EWA)

La extensión natural: usar el contrafactual no solo para normalizar, sino para **actualizar
todas las fracciones** a la vez. Es un caso particular del modelo *Experience-Weighted
Attraction* de Camerer y Ho (1999), tratando todas las acciones simétricamente. Se probaron
tres normalizaciones (con actualización contrafactual completa, régimen de esquina):

| Normalización | Subóptimos | Gap medio |
|---|---:|---:|
| Min-max $[0,1]$ | 14/30 | 7,0 % |
| $z$-score $(\pi-\bar\pi)/\sigma$ | 4/30 | 2,2 % |
| Regret/std $(\pi-\pi^{\max})/\sigma$ | 4/30 | 2,2 % |

Dos lecturas que serán claves después:

- **$z$-score y regret/std son la misma regla bajo actualización completa.** Ambas señales
  difieren en una constante aditiva —la diferencia media−máximo del día—, **idéntica para todas
  las fracciones**. Al actualizar **todas**, esa constante desplaza por igual el vector entero de
  atracciones, y la softmax, invariante ante desplazamientos uniformes, no la ve: las elecciones
  son idénticas. La equivalencia depende, pues, críticamente de que se actualicen *todas*; en
  cuanto se actualice solo la jugada (§6), la constante recae sobre una sola atracción, deja de
  ser un desplazamiento uniforme, y las dos reglas divergen.
- **Min-max es inferior** porque sus señales, siempre positivas, refuerzan todas las fracciones
  y ralentizan la diferenciación.

En este punto se creyó —**conclusión precipitada**, corregida en §8— que el aprendizaje
contrafactual (actualizar todas) era *necesario*: la normalización por std sobre solo la jugada
daba 22/30 subóptimos.

## 5. Un bug de reproducibilidad

Se descubrió que el argumento `seed` de Mesa **no controla** el módulo `random` de Python, que
es el que el modelo usa para shocks, atracciones iniciales y elecciones: dos ejecuciones con la
misma semilla daban resultados distintos. Se corrigió fijando explícitamente `random.seed` y
`np.random.seed` en el constructor de `MarketModel`. Sin esto, ninguna de las comparaciones
anteriores sería reproducible.

## 6. La regla candidata: $z$-score, solo la jugada, sin decaimiento

La variante que acabaría siendo la elegida combina actualizar **solo la fracción jugada** (como
el modelo original), **sin decaimiento** en las demás (conservan intacta su atracción), y con
señal **$z$-score** del beneficio realizado, $z=(\pi-\bar\pi)/\sigma$. La normalización por
$z$-score —la pieza que la hace funcionar— la puso sobre la mesa el estudiante como la regla a
elegir; no surgió de los tutores. Frente a la actualización completa del §4 (donde $z$-score y
regret/std eran equivalentes, $\approx4$–$5/30$ subóptimos), restringir el alcance a la sola
fracción jugada no empeora el resultado, pero **rompe esa equivalencia** (esquina, 10 semillas):

| Configuración | Subóptimos | Gap |
|---|---:|---:|
| **Solo elegida, sin decay, $z$-score** | **4,9/30** | **2,5 %** |
| Solo elegida, sin decay, regret/std | 6,2/30 | 2,9 % |

Aquí aparece la primera grieta importante: **con actualización parcial, $z$-score y regret/std
dejan de ser equivalentes**. La constante aditiva que los separa ya no se aplica a todas las
atracciones, sino a una sola, y la softmax no la cancela. Con regret/std (siempre $\le0$) la
atracción de la jugada solo puede bajar: castiga toda exploración y nunca premia. Con $z$-score
puede ser positiva o negativa: premia y castiga. Por eso el $z$-score es el pertinente cuando se
actualiza solo la elegida. (Es el argumento del cuerpo, §4.2.3.)

La virtud del **sin decaimiento** es la *memoria persistente*: lo aprendido de una fracción se
conserva hasta volver a probarla, sin diluirse por el paso del tiempo.

## 7. La variante "bandit" sin normalizar: vuelve la fijación

El tutor propuso después una variante más austera: solo la jugada, sin decay, pero con
**beneficio bruto sin normalizar** y atracciones iniciales nulas $A(f,0)=0$. En esencia ya la
habíamos probado —es la regla cruda solo-jugada del §1 con otra inicialización—, pero se
**reensayó por petición expresa del tutor**, por si acaso, dada la elegancia de su intuición
teórica: la actualización $A\leftarrow A+\phi(\pi-A)$ tiene punto fijo $A=\pi$, así que la
atracción converge al beneficio esperado, y $A=0$ es un anclaje natural. Pero **reproduce la
fijación** (gap 17,5 %, $\bar f=0{,}505$): tras el día 1 la jugada salta a
$A\approx18$ y el resto se queda en 0, la softmax colapsa, y el agente no vuelve a explorar. La
regla es *teóricamente correcta* (la atracción de la jugada sí converge a $\pi$) pero
*numéricamente inviable* a la escala del beneficio bruto. Es, de nuevo, el problema de escala
del §1.

## 8. Corrección: "todas las fracciones, sin normalizar" sí funciona

Al comparar rigurosamente la propuesta bandit con todo lo anterior se detectó un **error de
caracterización previo**: se había afirmado (§4) que el beneficio bruto sobre *todas* las
fracciones colapsaba al instante. No es así. Bajo actualización completa con decay, beneficio
bruto y regret sin normalizar son **matemáticamente equivalentes** (su diferencia es una
constante aditiva idéntica para todas las fracciones; verificado: la diferencia de atracciones
es la misma para todo $f$), y la softmax los iguala. Ambos convergen al óptimo de esquina
(28–30/30). El error venía de haber confundido esa prueba con otra de solo-elegida.

La conclusión de esta Parte —**en el régimen de esquina**— fue que el diferenciador entre
reglas que funcionan y que fallan parecía ser el *alcance* (actualizar todas vs solo la jugada),
no la normalización. La Parte II mostró que esa conclusión, ligada a la trivialidad del óptimo
de esquina, **se invierte** en cuanto el óptimo es interior.

---

# Parte II — Antes del banco: la reparametrización y la necesidad de un banco de pruebas

## 9. Por qué la esquina es un mal banco de pruebas

Con los parámetros originales la producción solar es insuficiente en ambos periodos (mañana
35 % de $D_M$, tarde 7,5 % de $D_E$): el gas domina, la convexidad de su coste dispara el precio
vespertino y el ratio $P_M/P_E\approx0{,}58$ queda muy por debajo de $\eta\approx0{,}90$.
Almacenar es *siempre* rentable, el óptimo de todos es $f=1{,}0$, y se verificó que ni siquiera
relajar la batería ($s=10$) lo cambia: la causa es la falta de producción solar, no la
restricción de almacenamiento. Un óptimo trivial no discrimina entre reglas.

Se buscó por barrido una parametrización con **solución interior** —que exista $f^*\in(0,1)$ con
$P_M(f^*)=\eta\,P_E(f^*)$—, manteniendo $\alpha_M=0{,}7$, $\alpha_E=0{,}3$ y $N=30$. Régimen
intermedio elegido entonces: $\bar c=2{,}0$, $D_M=80$, $D_E=120$, con $f^*\approx0{,}72$
(numérico, agente representativo). El régimen **final** del TFG refinó esto a $c=2{,}5$
(cártel $0{,}475$, Nash $f^N=0{,}639$); la derivación analítica de esos equilibrios es del
Capítulo 3.

> **Una trampa de medición.** En las primeras corridas interiores se midió el $f$ óptimo
> contrafactual **del último día**, que depende de los precios de esa jornada concreta, y se
> concluyó por error "0 agentes interiores". El óptimo *puntual* de un día puede ser $0$ o $1$
> aunque la media temporal esté en $0{,}70$. La métrica correcta es la media sobre un bloque
> largo de días, no un día aislado.

## 10. El hallazgo decisivo: la contrafactual *raw* entra en ciclo

Al medir bien, la regla contrafactual *raw* (actualiza todas, sin normalizar) daba
$\bar f\approx0{,}68$ por bloques de 100 días —engañosamente cerca del $f^*$—. Pero el examen
**día a día** reveló que esa media es un **artefacto de una distribución bimodal**, no una
convergencia:

```
Día  2: f_mean=0.98 | f=1: 26/30 | P_M/P_E=1.30   (todos almacenan -> arbitraje invertido)
Día  3: f_mean=0.15 | f=0: 14/30 | P_M/P_E=0.40   (nadie almacena  -> arbitraje restaurado)
Día  4: f_mean=0.99 | f=1: 28/30 | P_M/P_E=1.36
Día  5: f_mean=0.73 |          | P_M/P_E=0.94   (pasa por el equilibrio, pero no se queda)
```

El sistema **oscila** entre "todos almacenan" (retiran la oferta matutina → $P_M$ se dispara,
$P_E$ se hunde, $P_M/P_E>1$, almacenar pasa a ser mal negocio) y "nadie almacena" (lo contrario).
Pasa por el equilibrio (día 5: $\bar f=0{,}73$, $P_M/P_E=0{,}94$) pero no puede quedarse: las
decisiones casi deterministas ($P(f^*)\approx0{,}99$) hacen que todos los agentes salten **en
bloque y en la misma dirección**, sin amortiguación. El ciclo es permanente (no es un
transitorio de arranque: persiste 1000 días sin atenuarse).

La regla **$z$-score solo elegida**, con la misma parametrización, **no entra en el ciclo**:
$\bar f$ unimodal, dispersión que se reduce con el tiempo (std temporal $0{,}044$), rango
$0{,}49$–$0{,}80$. El mecanismo: la señal normalizada da $P(f^*)\approx0{,}57$ (no $0{,}99$), de
modo que cada día unos agentes eligen una fracción y otros otra; al no saltar al unísono, la
retroalimentación precios→decisiones se amortigua.

**Esto invierte la conclusión de la Parte I.** El diferenciador no era el alcance, sino que **la
contrafactual raw solo "funcionaba" porque la esquina era estable**; en cuanto el óptimo es
interior, su falta de amortiguación la hace ciclar. Lo robusto es la combinación
*escala controlada* + *alcance exclusivo*. Esto se comunicó al tutor (correo del 21 de abril de
2026) junto con la condición de equilibrio $P_M=\eta\,P_E$ y las variantes pendientes de probar.

## El giro: del tanteo al banco de pruebas

El recorrido de las Partes I y II se hizo en buena medida a base de **pruebas sueltas**, y su
lección de fondo no fue una regla concreta sino **metodológica**: con ensayos ad-hoc era fácil
medir mal (la trampa del último día, §9) y confundir una media engañosa con una convergencia (el
ciclo bimodal, §10). Para decidir con criterio qué regla elegir hacían falta dos cosas: (a) una
parametrización con **óptimo interior**, para que la elección no fuera trivial como en la esquina,
y (b) un **banco de pruebas** que corriera todas las reglas con la misma semilla y las contrastara
con un cuadro de métricas consistentes (gap de beneficio, dispersión temporal e intradía,
entropía, perfil de elección y ratio de precios; definidas y reconciliadas en §17).

Ese banco (`banco_pruebas.ipynb`) es el que tomó las decisiones. **Todo lo que sigue —Partes III y
IV— se apoya en él**, ya en el régimen final del TFG; las Partes I–II quedan como el registro de
lo aprendido por el camino que llevó hasta aquí.

---

# Parte III — Con el banco: el marco de los dos ejes

Ya con el banco, la síntesis del proceso anterior es que las reglas varían en **dos ejes
independientes**, y cada uno gobierna un problema distinto (es la organización del cuerpo, §4.2):

- **Escala** de la señal (cruda vs normalizada): determina si la softmax conserva capacidad de
  discriminar o **colapsa**.
- **Alcance** de la actualización (todas las fracciones vs solo la jugada): determina si el
  agente forma una **preferencia propia** o persigue la esquina.

|  | actualiza **todas** | actualiza **solo la jugada** |
|---|---|---|
| **cruda** | ciclo $f=0\leftrightarrow1$ (escala) | fijación día 1 (escala) |
| **$z$-score** | converge, pero persigue la esquina (alcance) | **regla elegida**: preferencia interior |

Los experimentos siguientes (régimen final, $\beta\in[2,3]$, seed=0; reproducibles en
`banco_pruebas.ipynb` §12 y `generate_figures_cap4.py`) sostienen las afirmaciones del cuerpo.

## 11. La señal apunta siempre a una esquina

El beneficio contrafactual a precios fijos, $\pi(f)=P_M(1-f)\tilde q^M+P_E(\tilde q^E+\min\{s,\eta f\tilde q^M\})$,
es **lineal en $f$** mientras la batería no satura ($s=10$ nunca satura), así que su máximo
diario cae en $f=0$ o $f=1$ según el signo de $\eta P_E-P_M$. Medido sobre la población:

| Regla | argmax $f=1$ | argmax interior |
|---|---:|---:|
| cf_raw (ciclo) | 49,8 % | **0 %** |
| $z$-score (todas) | 58,0 % | **0 %** |
| $z$-score (elegida) | 63,5 % | **0 %** |

En **cero** días el óptimo diario es interior. Todas las reglas reciben la misma "tentación de
esquina"; la cuestión es si ceden a ella. El reparto entre esquinas lo fija la dispersión del
agregado diario (cf_raw, muy dispersa, reparte $\approx50/50$; la elegida, concentrada, $\approx64\%$
en $f=1$).

## 12. Quién cede a la esquina y quién no (el perfil de elección)

La diferencia está entre la **señal** (siempre de esquina) y la **preferencia** que se acaba
formando. Perfil de probabilidad poblacional en régimen estacionario:

- **$z$-score (todas)**: perfil monótonamente creciente, **moda en la esquina $f=1$**. El
  agregado interior ($\bar f\approx0{,}62$) es un promedio de elecciones sesgadas al extremo, no
  una preferencia.
- **$z$-score (elegida)**: **joroba interior** con moda en $f\approx0{,}7$ (junto al Nash) y
  $P(f=1)=0{,}086$, **por debajo** de la uniforme ($0{,}091$): la regla *penaliza* la esquina.

La elegida resiste la tentación por la conjunción de sus dos rasgos: **actualizar solo la
jugada** da estabilidad (no reimporta a diario la señal de esquina → no se desata el ciclo), y
el **centrado del $z$-score sobre una atracción que no decae** da la preferencia interior (la
esquina rinde por debajo de la media los días en que el arbitraje se invierte → señal neta
mediocre; una fracción intermedia queda consistentemente algo por encima).

## 13. El centrado y el no-decaimiento son ambos necesarios (no solo el alcance)

Dos experimentos aíslan cada ingrediente, retirándolo y observando el colapso a la esquina:

- **Quitar el no-decaimiento.** Añadir decay $(1-\phi)$ a las fracciones no jugadas —dejando la
  regla por lo demás idéntica— desplaza la moda de $0{,}7$ a la esquina $f=1$. Lo mismo le ocurre
  a la EWA con $\delta=0$ (señal $z$-score, solo la jugada, pero con la depreciación propia de la
  EWA): converge en agregado pero persigue la esquina. Sin decaimiento, la atracción tiende al
  $z$ medio de la fracción cuando se juega, y gana la intermedia (modesta pero constante) sobre
  la esquina (espectacular pero intermitente); con decaimiento, ese promedio se corrompe.

- **Quitar el centrado.** Sustituir el $z$-score por la señal cruda (controlando la escala con
  $\beta$ bajo) no recupera la preferencia interior (Parte III §14).

| Regla | moda | $f$ media | entropía |
|---|---:|---:|---:|
| $z$-score elegida (sin decay) | **0,7** | 0,63 | 0,86 |
| $z$-score elegida **+ decay** | 1,0 | 0,57 | — |
| EWA $z$-score, $\delta=0$ | 1,0 | 0,60 | — |

## 14. Por qué no se rescata la regla cruda rebajando $\beta$ (ni inicializando en el Nash)

Cabe preguntar por qué no controlar la escala de la regla cruda solo-elegida **rebajando
$\beta$** —la otra palanca de §1— en vez de normalizar. Tres barridos (banco §12.4, semilla 0)
lo responden, y de paso muestran por qué hay que mirar la **moda** de la elección y no solo la
$f$ media: la media puede rozar el Nash mientras la distribución cuenta otra historia.

**(a) Desde la inicialización natural, ningún $\beta$ funciona** (§12.4a). Con la init natural
$\mathcal U(-0{,}1;0{,}1)$, no hay $\beta$ que lleve a la cruda solo-elegida a una preferencia
interior:

| $\beta$ | $f$ media | moda | entropía |
|---:|---:|---:|---:|
| 0,01 | 0,54 | 1,0 | 0,98 |
| 0,02 | 0,55 | 1,0 | 0,65 |
| 0,05 | 0,42 | 1,0 | 0,00 |
| 0,1 | 0,40 | 0,1 | 0,00 |
| 0,2 | 0,41 | 0,1 | 0,00 |
| 0,5 | 0,41 | 0,1 | 0,00 |

Con $\beta$ minúsculo ($\approx0{,}01$) la softmax es casi plana (entropía $\approx1$): el agente
explora al azar, no forma preferencia —la moda nominal $1{,}0$ no significa nada con esa
entropía— y $\bar f\approx0{,}54$ es el promedio de una elección difusa. En cuanto $\beta$ sube
lo justo para que explote lo aprendido ($\geq0{,}05$), la señal —de la magnitud del beneficio—
colapsa la softmax (entropía $0$) sobre la primera fracción que la suerte refuerza: la moda se
congela en un extremo arbitrario (1,0 o 0,1 según la semilla) y $\bar f$ cae a $\approx0{,}4$.
No hay $\beta$ intermedio fuerte-sin-colapso: es el problema de escala de §1, que rebajar
$\beta$ no cura, solo desplaza.

**(b) Con init en escala-beneficio se esquiva la fijación, pero el perfil queda sesgado a la
esquina** (§12.4b). Inicializando las atracciones en la escala del beneficio ($\approx230$,
uniforme) se evita el colapso del día 1, y aparece una ventana estrecha ($\beta\approx0{,}1$–$0{,}15$)
donde $\bar f\approx$ Nash conservando exploración:

| $\beta$ | $f$ media | moda | entropía | $P(f=1)$ |
|---:|---:|---:|---:|---:|
| 0,05 | 0,60 | 1,0 | 0,94 | 0,140 |
| 0,1 | 0,62 | 0,7 | 0,72 | 0,114 |
| 0,15 | 0,63 | 0,6 | 0,35 | 0,127 |
| 0,2 | 0,64 | 0,8 | 0,11 | 0,132 |
| 0,3 | 0,60 | 0,6 | 0,01 | 0,133 |

Aquí está lo que la $f$ media esconde: a **todo** $\beta$, la probabilidad de la esquina
$P(f=1)$ se mantiene **por encima de la uniforme** ($0{,}091$) —entre $0{,}11$ y $0{,}14$—,
mientras que la regla elegida ($z$-score) la deja en $0{,}086$, por debajo. Aunque la moda pueda
caer en el interior (0,6–0,8) y $\bar f$ ronde el Nash, la cruda arrastra una cola persistente
hacia la esquina, porque sin centrar nunca *penaliza* $f=1$; solo deja de reforzarla. El
centrado del $z$-score sí la penaliza los días en que el arbitraje se invierte.

**(c) No aprende desde cualquier punto** (§12.4c, el experimento decisivo). Inicializada con un
sesgo, la cruda ($\beta=0{,}1$) se queda anclada en él; la $z$-score ($\beta$ operativo) converge
al Nash desde cualquier sitio:

| init | cruda $\bar f$ | cruda moda | $z$-score $\bar f$ | $z$-score moda |
|---|---:|---:|---:|---:|
| sesgo $f=0{,}2$ | 0,30 | 0,3 | 0,62 | 0,8 |
| sesgo $f=0{,}9$ | 0,77 | 0,7 | 0,62 | 0,8 |
| uniforme | 0,62 | 0,7 | 0,62 | 0,9 |
| neutra | 0,40 | 0,1 | 0,64 | 0,7 |

La cruda **hereda dónde se la pone**: con un pico inicial en $f=0{,}2$ acaba con moda $0{,}3$ y
$\bar f=0{,}30$; con un pico en $f=0{,}9$, moda $0{,}7$ y $\bar f=0{,}77$. Su señal, siempre
positiva, refuerza la fracción preferida y nunca la abandona. La $z$-score lleva $\bar f$ a
$\approx0{,}62$ desde las cuatro inicializaciones —sesgada arriba, abajo, uniforme o neutra—,
porque su señal centrada da valor negativo a las fracciones que rinden por debajo de la media
del día y las abandona. (Su moda oscila entre $0{,}7$ y $0{,}9$ bajo estas inits extremas, pero
$\bar f$ es invariante: lo robusto es a dónde converge, no el detalle del pico.)

**Conclusión.** La regla cruda solo-elegida se descarta no porque no pueda asentarse cerca del
Nash —con la init y el $\beta$ adecuados lo hace—, sino porque para ello habría que decirle de
antemano dónde empezar, y aun así deja una cola hacia la esquina que el $z$-score no deja. El
$z$-score controla la escala de forma robusta (en todo el rango operativo, desde una init
neutra) y además centra, lo que le da la preferencia interior genuina.

---

# Parte IV — Con el banco: verificación final y reconciliación de métricas

## 15. La regla elegida con los parámetros finales

`model.py` implementa por defecto la regla elegida ($z$-score del beneficio realizado, solo la
fracción jugada, sin decay), y `DEFAULT_PARAMS` está alineado a INTERIOR ($D_M=80$, $c=2{,}5$,
$s=10$, $\eta=0{,}9$, $\phi\in[0{,}05;0{,}3]$, $\beta\in[2,3]$). $\beta\in[2,3]$ introduce
heterogeneidad realista sin degradar la convergencia ($\beta\in[1,5]$ la empeora levemente).

Verificación built-in sobre 6 semillas (Nash $f^N=0{,}639$, beneficio/agente $275{,}1$):
$\bar f$ media $=0{,}631$, std temporal $\approx0{,}045$, **0 % de días en extremos** en todas, gap
de beneficio $\approx0$. La regla converge a la banda del Nash con dispersión residual estable.

## 16. Comparativa cross-rule (régimen final)

Cinco configuraciones, misma semilla, agrupadas por alcance (las cuatro primeras actualizan
todas; la última, solo la jugada):

| Regla | $\bar f$ | std temp. | std intradía | gap benef. | $P_M/P_E$ | extremos | entropía |
|---|---:|---:|---:|---:|---:|---:|---:|
| Contrafactual *raw*, $\beta\in[2,3]$ | 0,627 | 0,380 | 0,186 | 17,6 % | 1,105 | 61 % | 0,22 |
| Contrafactual *raw*, $\beta=0{,}2$ | 0,630 | 0,077 | 0,292 | 0,36 % | 0,875 | 0 % | 0,95 |
| $z$-score, todas | 0,622 | 0,099 | 0,290 | 0,52 % | 0,867 | 0 % | 0,95 |
| EWA, $z$-score (todas) | 0,638 | 0,061 | 0,288 | 0,41 % | 0,887 | 0 % | 0,95 |
| **$z$-score, solo elegida** | **0,633** | **0,044** | **0,236** | **≈0 %** | **0,874** | **0 %** | **0,86** |

Lecturas: (1) **la $f$ media engaña** —cf_raw da $\bar f\approx$ Nash pero cicla (std temporal
enorme, 61 % de días en extremos, ratio invertido) y pierde 17,6 % de beneficio—; (2) controlada
la escala (rebajar $\beta$ **o** normalizar), las cuatro restantes convergen en agregado, y
cf_raw a $\beta=0{,}2$ es casi idéntica a la $z$-score sobre todas (dos vías para la misma
palanca de escala); (3) entre las que convergen, solo la elegida combina el menor gap con la
menor dispersión y la entropía algo más baja ($0{,}86$ vs $0{,}95$) que delata una preferencia
interior concentrada, no una elección difusa hacia el extremo.

**Atracción media de la fracción jugada** (medida de calidad desde el estado interno):

- Reglas normalizadas (atracción $\approx$ un $z$-score centrado en 0): la elegida es la más
  próxima a cero — $0{,}014$, frente a $0{,}066$ de la $z$-score sobre todas y $0{,}073$ de la EWA
  $z$-score—. Cercana a cero no significa "mayor precisión" en abstracto, sino que la fracción
  escogida rinde apenas por encima de la media de sus alternativas: el paisaje plano del Nash
  (§3.6.2). Que la elegida sea la **más** próxima a cero delata que es la única que se asienta de
  veras en ese régimen plano; las que persiguen la esquina escogen un extremo cuyo $z$ es algo
  positivo los días en que lo juegan, y por eso su atracción media queda más alta.
- Contrafactual *raw* (atracción en escala de beneficio): $\approx286$ (medida en el momento de
  decidir) frente a un beneficio realizado de $227$ — el agente "cree" que su elección vale más
  de lo que le reporta; la firma del ciclo.

## 17. Reconciliación de definiciones de métrica

Las simulaciones son **bit-reproducibles** (misma semilla → misma trayectoria). Las
discrepancias que aparecieron entre el script y el banco fueron siempre de **definición de
métrica**, no de la simulación. Quedan fijadas así (banco §11 y `generate_figures_cap4.py`
alineados):

- **Entropía**: media sobre los agentes de la entropía normalizada de su softmax (no la del
  agente representativo). Da $0{,}86$ para la elegida, no $0{,}92$.
- **Desviaciones típicas**: con `ddof=0` (poblacional), para coincidir con el script. La
  "std temporal" del cuerpo es la de la media diaria $\bar f(t)$; la "std intradía" es la
  dispersión entre agentes dentro de cada día.
- **Ratio $P_M/P_E$**: media de los cocientes diarios (no cociente de medias). Para las reglas
  que convergen ambas coinciden; en el ciclo de cf_raw no ($1{,}105$ vs $\approx0{,}87$), y se
  reporta la primera por reflejar la inversión del arbitraje.
- **$f$ media**: sobre los últimos 100 días (no toda la serie).
- **Atracción de cf_raw**: $286$ es la atracción en el momento de decidir (pre-refuerzo, la que
  usa el banco); leída tras el refuerzo del día da $\approx275$. Ambas son correctas; difieren
  por el instante de lectura.

## 18. Resumen del recorrido

| # | Variante (régimen) | Veredicto |
|---|---|---|
| 1 | Cruda, solo jugada, init pequeña (esquina) | Fijación día 1 |
| 2 | $\pi/\pi^{\max}$, solo jugada | No converge (señal siempre positiva) |
| 3 | Regret, solo jugada | No converge (castiga sin dirección) |
| 4 | Contrafactual (todas) + min-max / $z$ / regret-std | Converge a la esquina (trivial) |
| 6 | $z$-score, solo jugada, sin decay (**regla elegida**) | Funciona; $z\ne$ regret aquí |
| 7 | Cruda, solo jugada, sin decay, init 0 (bandit) | Fijación (escala) |
| 8 | Cruda, todas, sin normalizar | $\equiv$ regret bajo softmax; converge (esquina) |
| 10 | Contrafactual *raw* (interior) | **Ciclo $f=0\leftrightarrow1$** |
| 10 | $z$-score solo elegida (interior) | **Converge al equilibrio** |
| — | **Regla elegida (final, $c=2{,}5$)** | Converge al Nash desde cualquier init, con exploración residual |

La lección de fondo: en el régimen de esquina casi todo "funciona" porque el óptimo es trivial y
estable; es el régimen interior el que separa las reglas, y allí solo la combinación
**escala normalizada + alcance exclusivo + sin decaimiento** produce un aprendizaje genuino —que
descubre el equilibrio desde cualquier punto y mantiene exploración— en lugar de un ciclo, una
fijación o una preferencia heredada de la inicialización.
