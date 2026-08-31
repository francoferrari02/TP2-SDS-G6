# Decisiones pendientes del TP2

## Cómo usar este archivo

Este es el registro único de decisiones que no pueden resolverse suponiendo. Todo agente debe revisarlo antes de comenzar una etapa y actualizarlo cuando una decisión se abre o se cierra.

Estados:

- `[ ]` pendiente: todavía requiere evidencia, aclaración de cátedra o elección del usuario.
- `[x]` resuelta: registrar decisión, fecha, fundamento y archivos/etapas afectados.

Una recomendación del agente no equivale a una decisión. Mientras el checkbox siga abierto, no ejecutar trabajo definitivo que dependa de ella.

## Ambigüedades de alcance y parámetros

- [ ] **Alcance de las densidades bajas en el punto E (`<va>` vs. `<S>`).**
  - Contexto: la aclaración dice extender densidades “solo para el estudio de Cluster”, mientras el punto E original pide distinguir tres densidades.
  - Camino mínimo actual: usar las densidades bajas en el punto D y mantener `rho=2,4,8` en el punto E.
  - Bloquea: únicamente una posible ampliación del gráfico E, no el motor ni el barrido principal.
  - Decisión del usuario/cátedra: pendiente.

## Protocolo experimental

Estas decisiones deben proponerse después de las corridas preliminares de la etapa 5 y ser aceptadas antes del barrido definitivo:

- [ ] **Frecuencia productiva de muestreo (valores concretos de `--observables-stride`/`--trajectory-stride`).**
  - Contexto: el *formato* de salida y el *mecanismo* de stride ya están implementados y aprobados (ver "Decisiones resueltas" más abajo). Lo que sigue abierto es qué valores concretos de stride se van a usar en el barrido definitivo (por ejemplo, escribir observables en cada paso pero trayectoria cada 10 o 50 pasos).
  - Evidencia necesaria: corridas piloto que muestren cuánto puede espaciarse el muestreo sin perder resolución en `va(t)`/`S(t)` ni en las animaciones.
  - Bloquea: el barrido de producción de las etapas 5-6, no el escritor ni la CLI (que ya aceptan cualquier stride válido).
  - Decisión del usuario/cátedra: pendiente.

  ### Formato público de salida: implementado y aprobado (referencia histórica de la propuesta)

  El contenido de esta subsección documenta la propuesta original que llevó a la decisión aprobada; el registro formal de la decisión (fecha, fundamento, alcance) está en "Decisiones resueltas". Se conserva aquí como contexto de diseño, no como un ítem pendiente.

  **Alcance de la propuesta.** Cubre únicamente el *formato de archivo* y su organización; no fija todavía frecuencia de muestreo, `t_eq`, cantidad de realizaciones ni la grilla de `eta` (esas decisiones siguen en sus propios ítems de este documento). Tampoco se traduce todavía en un escritor de archivos (`text_output` en `01_especificacion_y_arquitectura.md`) ni en la CLI: es solo el contrato que ese código futuro debería cumplir.

  **Qué debe distinguir cada corrida.** Cada archivo corresponde a exactamente una combinación `(modelo, rho_nominal, eta, base_seed, realización)`. Nunca se agregan filas de dos corridas distintas al mismo archivo (evita mezclar datos, uno de los requisitos explícitos). Esa quíntupla, junto con `N`, `rho_efectiva` (`N/L^2`, para distinguirla de `rho_nominal` como ya exige `REVISION_FINAL_DE_ALCANCE.md` para las densidades bajas) y los parámetros fijos (`L, rc, dt, v`), se registra dentro del propio archivo, no solo en su nombre, para que sea interpretable de forma aislada.

  **Dos archivos por corrida, no uno.** Se proponen archivos separados para observables y para trayectoria:

  - `..._obs.csv`: una fila por paso `t`, columnas `t,va,S`. Liviano (unos pocos KB incluso con miles de pasos); es lo único que hace falta para las figuras B, C, D y E del enunciado (series temporales, `<va>` vs. `eta`, `<S>` vs. `eta`, `<va>` vs. `<S>`).
  - `..._traj.csv`: una fila por `(t, id)`, columnas `t,id,x,y,theta`. Es lo único que necesita el módulo de animación (punto A). Puede pesar mucho (`N x steps` filas), así que su escritura debe poder desactivarse sin afectar al archivo de observables: son dos archivos independientes, no dos secciones de uno solo, precisamente para que "no escribir trayectoria" sea "no crear ese archivo" y nada más.

  Se descarta mezclar ambos en un único archivo ancho (una fila por paso con las `N` filas de partículas repitiendo `va(t)` y `S(t)`): desperdicia espacio (`va`/`S` se repetirían `N` veces por paso), obliga a quien solo quiere las curvas escalares a leer y descartar la trayectoria completa, y mezcla dos granularidades (una fila por paso vs. una fila por partícula-paso) en el mismo parser, una fuente típica de errores de lectura aguas abajo.

  **Por qué no vx,vy.** La trayectoria guarda `theta`, no `vx,vy`: como `v` es constante y ya queda registrado en la cabecera del archivo, `vx=v cos(theta)` y `vy=v sin(theta)` se reconstruyen sin ambigüedad. El enunciado permite explícitamente "velocidades o información equivalente para reconstruirlas" (sección 2); guardar `theta` es esa información equivalente, con un número menos por fila y sin el riesgo de que `vx,vy` almacenados no sean exactamente consistentes con `theta` por redondeo independiente de cada uno.

  **Separador, comentarios y encabezado.** Se propone CSV (separador `,`) en vez de espacios: es inequívoco para herramientas (`pandas.read_csv`, `numpy.genfromtxt`, cualquier parser de C++ que separe por `,`) y no depende de cuántos espacios haya entre campos. Las primeras líneas son comentarios de metadatos con prefijo `#` (convención que tanto `pandas` como `numpy` reconocen con `comment='#'`, y que un parser propio en C++ puede saltear con una comparación de un carácter), seguidas de una línea de encabezado con los nombres de columna, y luego los datos:

  ```text
  # tp2_observables v1
  # model=vicsek
  # L=10 rc=1 dt=1 v=0.03
  # rho_nominal=2 N=200 rho_effective=2.0
  # eta=0.50
  # base_seed=12345 realization=0
  t,va,S
  0,0.0123,0.0512
  1,0.0140,0.0498
  ```

  ```text
  # tp2_trajectory v1
  # model=vicsek
  # L=10 rc=1 dt=1 v=0.03
  # rho_nominal=2 N=200 rho_effective=2.0
  # eta=0.50
  # base_seed=12345 realization=0
  t,id,x,y,theta
  0,0,3.281,7.933,1.204
  0,1,8.002,0.114,4.910
  ```

  El campo `v1` etiqueta la versión del esquema, para poder distinguir a futuro un archivo de una versión anterior si el formato cambia; hoy no hay más de una versión.

  **Unidades.** `x,y` en las mismas unidades de longitud que `L` (adimensional, tamaño de caja); `theta` en radianes, `[0,2pi)`; `va,S` adimensionales en `[0,1]`; `t` es el número de paso entero (no tiempo físico), y el tiempo físico, si hiciera falta, se reconstruye como `t*dt` a partir del `dt` de la cabecera. Todo esto debe quedar explícito en la cabecera de cada archivo, no solo en la documentación externa.

  **Nombres de archivo (sugeridos, no fijados).**

  ```text
  data/raw/{model}_rho{rho_nominal}_N{N}_eta{eta}_seed{seed}_rea{realization}_obs.csv
  data/raw/{model}_rho{rho_nominal}_N{N}_eta{eta}_seed{seed}_rea{realization}_traj.csv
  ```

  El nombre es una conveniencia para ubicar archivos a simple vista; no reemplaza la cabecera interna, que es la fuente de verdad si alguna vez un archivo se copia o renombra fuera de esta convención.

  **Lectura por un programa externo.** Un lector en Python puede abrir directamente con `pandas.read_csv(path, comment='#')`; un lector en C++ o cualquier otro lenguaje solo necesita: saltear líneas que empiecen con `#`, tomar la siguiente línea como encabezado de columnas, y parsear el resto como CSV. Ningún archivo depende de leer otro archivo primero: cada uno es autocontenido.

  **Desactivar trayectoria sin perder observables.** El escritor (todavía no implementado) debería aceptar un flag explícito (por ejemplo `--trajectory-out none`, ya sugerido en `01_especificacion_y_arquitectura.md`) que simplemente omite la creación de `..._traj.csv`; `..._obs.csv` se escribe siempre. Así el barrido de producción (muchas combinaciones, muchas realizaciones) puede evitar generar datos pesados de trayectoria y reservarla solo para los pocos casos elegidos para animar (punto A del enunciado).

  **Información mínima que debe quedar registrada en cada archivo.** Modelo (`vicsek`/`voter`), `L,rc,dt,v`, `rho_nominal`, `N`, `rho_efectiva`, `eta`, `base_seed`, índice de realización, y el nombre/versión del esquema. Sin esos campos, un archivo aislado no alcanza para saber qué corrida lo produjo, y "reproducibilidad" perdería sentido con solo el nombre de archivo como referencia.

  **Alternativas comparadas.**

  1. **Un solo archivo ancho por corrida** (observables y trayectoria mezclados, una fila por paso con `N` sub-filas de partículas repitiendo `va`,`S`). Descartada: desperdicia espacio, mezcla dos granularidades distintas en un mismo parser y obliga a leer la trayectoria completa para obtener solo las curvas escalares.
  2. **Un archivo por paso** (`step_000001.csv` con `N` filas `id,x,y,theta`, al estilo de algunos simuladores de partículas), más un archivo aparte de observables. Descartada como formato por defecto: para `N` hasta 800 y miles de pasos, multiplicado por todas las combinaciones del barrido y sus realizaciones, generaría una cantidad de archivos difícil de manejar en el sistema de archivos (aunque cada uno sea chico), contradiciendo "no generes datos pesados" en su forma de cantidad de archivos más que de bytes. No se descarta por completo como opción interna para casos de animación puntuales, pero no se propone como formato general.
  3. **Dos archivos por corrida, observables y trayectoria separados, en CSV con cabecera de metadatos** (la propuesta de arriba). Recomendada: mantiene el formato simple de texto, es trivial de leer desde Python y C++, separa lo liviano (observables, siempre necesario) de lo pesado y opcional (trayectoria), no mezcla corridas distintas (una quíntupla por archivo) y cada archivo es autocontenido para reproducibilidad.

  No se copió el formato de ningún repositorio externo auditado: el seguimiento hasta `413dcef` (ver `00_auditoria_referencia_y_notas.md`) no fue revisado como fuente de formato de salida en esta propuesta; la comparación de arriba se construyó únicamente a partir de los requisitos del enunciado y la teórica citados en la cabecera de este documento.

  **Decisión finalmente aprobada (con una diferencia respecto de esta propuesta).** El usuario aprobó (a) dos archivos por corrida en vez de uno o de un archivo por paso, (b) CSV con separador `,` y comentarios `#`, (c) guardar `theta` en vez de `vx,vy`, y (e) que la trayectoria sea siempre opcional y los observables siempre obligatorios. La única diferencia con lo propuesto aquí es (d): en vez de la convención de nombre de archivo plano sugerida (`data/raw/{model}_..._obs.csv`), el contrato aprobado usa un **directorio independiente por corrida** con archivos de nombre fijo dentro (`observables.csv`, `trajectory.csv`), ver el registro completo en "Decisiones resueltas".

## Rendimiento y entrega

- [ ] **Protocolo de comparación de tiempos con TP1.**
  - Falta elegir `N`, pasos/repeticiones, entorno y tramo cronometrado.
  - Bloquea: etapa 8.

- [ ] **Datos administrativos y enlaces finales.**
  - Falta confirmar grupo, comisión, integrantes/números requeridos y destino de las animaciones.
  - Bloquea: cierre de etapa 9.

- [ ] **Indicaciones visuales atribuidas a la consulta de clase.**
  - Contexto: el repositorio de referencia actualizado afirma que la cátedra pidió gráficos sin grilla de fondo, `va` y `S` en figuras separadas y resultados de cada modelo por separado antes de la comparación.
  - Verificado directamente el 2026-08-31 en `/Users/francoferrari/Downloads/GuiaPresentaciones.pdf`: sí aparecen la fuente mínima 20, ausencia de título/*caption* dentro de figuras de presentación, parámetros al costado, puntos visibles y animación integrada en vivo/fotograma con link en PDF. La guía también exige separadores sin numerar, Implementación limitada al motor y una conclusión sin trabajo pendiente. Las otras tres indicaciones (sin grilla, `va` y `S` separados y cada modelo individual antes de comparar) no aparecen en ese PDF y solo constan como comentario del repositorio externo.
  - Bloquea: congelar el diseño visual final de etapas 7 y 9; no bloquea motor, pilotos ni producción de datos.
  - Decisión del usuario/cátedra: pendiente.

## Evidencia externa que no resuelve decisiones

El seguimiento del repositorio de referencia hasta `413dcef` muestra que ese grupo usa `N=32,16,11`, amplía el punto E a densidades bajas, adopta 39 valores de `eta`, 10 semillas, 2000/10000 pasos y un corte del 50%. Ninguna de esas elecciones prueba una indicación de cátedra ni reemplaza nuestros pilotos. Además, su regla de votante sigue permitiendo autoelección, por lo que sus tiempos de relajación y resultados del votante no son transferibles. Todos los checkboxes correspondientes permanecen abiertos.

## Decisiones resueltas

Mover aquí los ítems cerrados conservando su texto, y agregar:

```text
Decisión:
Fecha:
Fundamento/evidencia:
Etapas y archivos afectados:
Usuario que aprobó:
```

- [x] **Conversión de densidades bajas a `N` entero.**
  - Contexto original: con `L=10`, `N=rho L^2` no es entero para `rho=1/pi,1/(2pi),1/(3pi)`.

```text
Decisión:
Para la extension de clusters se redondea `N=rho_nominal*L^2` al entero mas
cercano y se reportan siempre `rho_nominal`, `N` y `rho_effective=N/L^2`.
La tabla queda:
1/pi -> N=32 -> rho_effective=0.32
1/(2pi) -> N=16 -> rho_effective=0.16
1/(3pi) -> N=11 -> rho_effective=0.11
No se presenta `N=32,16,11` como densidad nominal exacta: son los tamanos
enteros simulados que aproximan las tres densidades pedidas.
Fecha: 2026-08-30
Fundamento/evidencia: el usuario pidio resolver esta conversion antes de
cerrar los graficos de clusters bajos e indico que ya se venia usando
`32,16,11`; esa es exactamente la regla de redondeo al entero mas cercano
que estaba documentada provisionalmente en README/REVISION_FINAL_DE_ALCANCE.
El motor ya acepta `--rho-nominal`, `--rho-label` y `--N` explicitos, por lo
que la densidad nominal y la efectiva quedan trazadas sin ambiguedad.
Etapas y archivos afectados: desbloquea el bloque de clusters bajos de la
etapa 6 y las figuras del punto D de la etapa 7. Se aplico a
python/vicsek_lowrho_cluster_study_run.py y a los estudios existentes del
votante. No resuelve el alcance del punto E, que sigue pendiente por
aclaracion docente.
Usuario que aprobó: usuario del proyecto (francoferrari).
```

- [x] **Grilla final común de valores de `eta`.**
  - Contexto original: la grilla era una decisión pendiente; los pilotos mostraron que el votante cambia principalmente para `eta<=0.5`, mientras que Vicsek requiere ruido mayor para recorrer su pérdida de orden.

```text
Decisión:
Ambos modelos, las tres densidades obligatorias y sus figuras comparativas
usan la misma grilla no uniforme de ruido, en radianes:
eta={0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}.
La zona eta<=0.5 se densifica para resolver la caída rápida del votante; los
puntos eta>=1 verifican su régimen desordenado y cubren la región de cambio
de Vicsek. En la presentación se permite mostrar un zoom eta<=0.5, pero las
tablas y la comparación conservan los 14 puntos de la grilla completa.
Fecha: 2026-08-30
Fundamento/evidencia: el barrido amplio del votante muestra polarización baja
para eta>0.5, y la grilla fina existente confirma que el cambio de interés se
concentra por debajo de ese valor. Las figuras diagnósticas de Vicsek muestran
que su polarización aún es alta cerca de eta=0.5 y cae a valores mayores de
ruido. Una grilla común permite comparar los modelos punto a punto sin perder
resolución donde el votante cambia.
Etapas y archivos afectados: cierra la decisión de grilla de la etapa 5 y
define la matriz base de la etapa 6 y las figuras B-E de la etapa 7. No vuelve
definitivas las corridas ya existentes que no cubran exactamente la grilla o
no compartan el protocolo final; se deben completar y reagrupar antes de
generar figuras finales.
Usuario que aprobó: usuario del proyecto (francoferrari).
```

- [x] **Cantidad de realizaciones independientes, semillas y duración (`steps`) para el votante.**
  - Contexto original: "Cantidad de realizaciones independientes y semillas" y "Cantidad de pasos de transitorio y de medición".

```text
Decisión:
Para el modelo votante (unico foco del equipo a partir de este punto):
R=20 realizaciones independientes, steps=3000, para las tres densidades
obligatorias (rho=2,4,8) y las tres densidades bajas del estudio de
clusters (1/pi,1/(2pi),1/(3pi) -> N=32,16,11, redondeo al entero mas
cercano). Semillas explicitas y deterministas por estudio (ver esquemas en
python/voter_eta_study_run.py, voter_lowrho_cluster_study_run.py,
voter_eta_refine_run.py, voter_eta_fine_lowrange_run.py).
Fecha: 2026-08-30
Fundamento/evidencia: con R=3 (piloto exploratorio inicial) el desvio entre
realizaciones cerca de la transicion era ±0.18, comparable al propio valor
medio; con R=20 el error estandar del peor caso observado bajo a un orden
de 0.01-0.05 (data/summary/voter_eta_study_1_by_combo.csv). La duracion de
3000 pasos se verifico como suficiente (no supuesta) comparando contra
corridas de 5000 y 6000 pasos en tres estudios independientes: (1)
voter_lowrho_cluster_study_2 (steps=6000, densidades bajas): <va> a 3000 y
6000 pasos coincide dentro del margen de error en todo el barrido de eta;
(2) voter_eta_fine_lowrange_1 (steps=5000, rho=2,4,8, eta=0..0.2, semillas
independientes): <va> en eta=0.2 coincide con la corrida de 3000 pasos
(0.708 vs 0.723 en rho=2, 0.663 vs 0.650 en rho=4, 0.514 vs 0.517 en
rho=8), y ademas explico que el pico-y-caida visto antes en esa serie era
ruido estadistico, no un transitorio sin terminar. Detalle completo en
plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md.
Etapas y archivos afectados: cierra el criterio de duracion/realizaciones
para el barrido definitivo del votante (etapa 6). Esta decisión particular
corresponde al votante; Vicsek queda cubierto por una decisión separada más
abajo. Las tablas de resumen ya generadas
(data/summary/voter_eta_study_1_*.csv, voter_lowrho_cluster_study_1_*.csv,
voter_eta_fine_lowrange_1_*.csv) son la base de datos vigente para figuras;
no hace falta volver a correrlas si se usa el mismo protocolo.
Usuario que aprobó: usuario del proyecto (kmenshikoff@balanz.com).
```

- [x] **Cantidad de realizaciones independientes, duración (`steps`) y ventana estacionaria para Vicsek.**
  - Contexto original: Vicsek ya tenía corridas y figuras diagnósticas con `steps=3000`, `R=20` y `t_eq=1500`, pero ese protocolo todavía no estaba registrado como decisión formal.

```text
Decisión:
Para el modelo Vicsek se adopta formalmente el protocolo ya usado en las
corridas diagnósticas: R=20 realizaciones independientes, steps=3000 y
t_eq=1500. La ventana estacionaria usada para promediar es t=1500..3000,
con la misma ventana para va(t) y S(t). Esta decisión aplica a las tres
densidades obligatorias rho=2,4,8 y a la comparación con el modelo votante.
Fecha: 2026-08-30
Fundamento/evidencia: el piloto exploratorio de ambos modelos con steps=600
mostró que Vicsek relaja mucho antes que el votante (en ruido bajo/moderado,
del orden de 100-200 pasos para eta<=2), mientras que las corridas
diagnósticas posteriores de Vicsek con R=20 y steps=3000 fueron reanalizadas
con t_eq=1500 y 780/780 archivos de observables válidos, 0 problemas. Las
series va(t) y S(t) en
figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/ marcan t_eq=1500 y no
muestran una tendencia sistemática posterior incompatible con régimen
estacionario. Además, el corte es conservador para Vicsek y mantiene la
comparabilidad directa con el votante, que también usa steps=3000 y
t_eq=1500.
Etapas y archivos afectados: cierra la decisión de duración, R y t_eq para
Vicsek en las etapas 4, 5, 6 y 7. No convierte en finales las figuras ya
exportadas si usan error estándar: deben regenerarse con desvío estándar
entre realizaciones. Tampoco completa por sí sola los puntos de eta finos
faltantes de la grilla común aprobada
{0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}; las
corridas existentes de Vicsek con paso 0.5 siguen siendo evidencia válida
del corte, pero la comparación final requiere cubrir la grilla común.
Usuario que aprobó: usuario del proyecto (francoferrari), mensaje
"bueno hacelo asi".
```

- [x] **Definición de la ventana estacionaria (`t_eq`).**
  - Contexto original: "Cantidad de pasos de transitorio y de medición / criterio de `t_eq`"; la guía pide justificarlo con series temporales, no fijarlo a ciegas.

```text
Decisión:
t_eq=1500 (la segunda mitad de los steps=3000 usados en el estudio del
votante), como ventana estacionaria unica para todas las combinaciones de
densidad y eta (tanto rho=2,4,8 como las densidades bajas de clusters).
Fecha: 2026-08-30
Fundamento/evidencia: series va(t) en figures/voter_eta_study_1/va_t_rho_2.png,
va_t_rho_4.png, va_t_rho_8.png (densidades obligatorias) y
figures/voter_lowrho_cluster_study_1/va_t_rho_1_over_*.png (densidades
bajas) muestran que, para la enorme mayoria de las combinaciones, el nivel
medio ya se estabiliza bien antes de t=1500 (eta=0 converge entre
t~650-1200 segun densidad; eta>=1.5 se estabiliza casi de inmediato). La
zona mas lenta (eta bajo pero distinto de cero, ~0.2-1) sigue fluctuando
con amplitud considerable incluso despues de t=1500, pero alrededor de un
nivel medio ya establecido, no con una tendencia sistematica: esto se
confirmo cuantitativamente con tres comparativas de duracion distinta (ver
decision anterior de R/steps), que descartaron que ese nivel medio fuera un
transitorio a mitad de camino. t_eq=1500 es por lo tanto un corte
conservador (deja 1500 pasos de ventana estacionaria, la mitad de la
corrida) y justificado visualmente, no un numero elegido a ciegas. Detalle
completo, con la lista exacta de figuras y comparativas, en INFORME.md
(seccion "Definición de barras de error y de `t_eq`").
Etapas y archivos afectados: cierra el criterio de t_eq para el barrido
definitivo del votante (etapa 6) y las figuras B/D (etapa 7). Esta decisión
particular corresponde al votante; Vicsek queda cubierto por una decisión
separada más arriba. Se reconoce como limitacion documentada que la
heuristica automatica de t_eq (en *_analyze.py) no es confiable para las
densidades bajas por ruido de tamano finito (ver
05_pilotos_y_grilla_eta.md); t_eq=1500 se adopta por inspeccion visual, no
por ese numero automatico.
Usuario que aprobó: usuario del proyecto (kmenshikoff@balanz.com).
```

- [x] **Definición de barras de error.**
  - Contexto original: la guía admite desvío entre realizaciones o error estándar; no elegía entre ambas.

```text
Decisión:
Se usa el desvío estándar entre las medias estacionarias de las realizaciones
(s_va, s_S) como definición de barra de error en todas las figuras del TP,
para ambos observables (va, S), todas las densidades y todo el barrido de
eta. El error estándar se sigue calculando y guardando en las tablas de
resumen, pero no se usa como barra de la presentación ni del informe.
Fecha: 2026-08-30
Fundamento/evidencia: el desvío estándar comunica directamente la
variabilidad observada entre realizaciones independientes, que es la
incertidumbre empírica relevante para la dinámica ruidosa del TP. Ambas
cantidades ya están calculadas en las tablas *_by_combo.csv de data/summary/
(columnas va_stderr/S_stderr y
va_stdev_between_realizations/S_stdev_between_realizations), por lo que el
cambio no exige repetir las simulaciones, sino regenerar sus figuras usando
las columnas de desvío.
Etapas y archivos afectados: aplica a todas las figuras B-E de la etapa 7 y
a la agregación de la etapa 6 (columna a usar como barra:
*_stdev_between_realizations, no *_stderr). No modifica ningún dato ya
generado, pero invalida como versiones finales las figuras diagnósticas que
usan error estándar hasta que se regeneren.
Usuario que aprobó: usuario del proyecto (francoferrari).
```

- [x] **Formato público de salida de texto y CLI productiva.**
  - Contexto original: "Frecuencia y formato final de salida de texto", ver la propuesta comparada contra alternativas más arriba en este documento.

```text
Decisión:
Cada corrida escribe un directorio propio
output/<modelo>/<rho_label>/eta_<eta>/steps_<T>/realization_<R>_seed_<SEED>/
con dos archivos: observables.csv (siempre) y trajectory.csv (solo si se pide
--write-trajectory). Ambos son CSV UTF-8, separador ',', punto decimal,
locale C, con un bloque de metadatos "# clave=valor" (18 claves fijas,
incluyendo schema_version, model, L, rc, dt, v, periodic, rho_label,
rho_nominal, N, rho_effective, eta, noise_convention, base_seed,
realization, steps, observables_stride, trajectory_stride) seguido de una
línea de encabezado CSV ("t,va,S" o "t,id,x,y,theta") y los datos. `theta`
se guarda en vez de vx,vy (se reconstruye con v, ya documentado en la
cabecera). t=0 y t=steps se guardan siempre, independientemente del stride.
Los valores double se escriben con std::setprecision(max_digits10) para
permitir round-trip exacto. Cada archivo se publica mediante un temporal
verificado y `rename`; el par de archivos no es una transacción atómica
portable
y no sobrescribe por defecto: si el directorio de la corrida ya existe, la
CLI falla sin modificar nada, salvo que se pida --overwrite (que además
elimina un trajectory.csv viejo si la corrida nueva no pide trayectoria).
N se recibe explícitamente por CLI (--N), nunca se recalcula a partir de
rho_nominal, salvo una verificación opcional de consistencia para las
densidades obligatorias rho=2,4,8.
Fecha: 2026-08-29
Fundamento/evidencia: tests/test_text_output.cpp (formato de los dos
archivos: metadatos, encabezados, cantidad de filas, precisión, separador
decimal) y tests/test_cli_simulate.cpp (17 casos en la versión actual: filas de observables y
trayectoria, trayectoria desactivada por defecto, reproducibilidad byte a
byte, reconstrucción de vx/vy desde theta, N ids distintos por paso,
metadatos coincidentes, error sin --overwrite y sin modificar archivos
existentes, --overwrite reemplaza coherentemente, strides guardan t=0 y
t=T, la ruta diferencia modelo/densidad/eta/pasos/realización/semilla,
nombres sin coma ni punto decimal, casos inválidos de CLI). Ambos
registrados en CTest: 100% tests passed, 0 failed, out of 11 (incluyendo
los 9 tests previos a esta tarea).
Etapas y archivos afectados: src/core/text_output.hpp, src/cli/simulate_cli.hpp,
src/cli/simulate.cpp, tests/test_text_output.cpp, tests/test_cli_simulate.cpp,
CMakeLists.txt. No modifica el motor (rules.hpp, time_step.hpp,
neighbor_search.hpp, simulation.hpp, observables.hpp, initialization.hpp).
Etapa 2 (motor): sigue en progreso, no se marca completa. Etapa 1
(especificación): el ítem de formato de salida queda cerrado en
01_especificacion_y_arquitectura.md; el resto de la etapa 1 sigue abierto.
Usuario que aprobó: usuario del proyecto (francoferrari123111@gmail.com),
mensaje "Implementá ahora el escritor de salida y la CLI del TP2 siguiendo
exactamente el contrato aprobado debajo."
```

Lo que este ítem **no** resuelve (siguen `[ ]` en este documento): los valores concretos de stride que se usarán en producción, la grilla de `eta`, `t_eq`, la cantidad de realizaciones y semillas, la definición de barras de error, y la conversión de las densidades bajas a `N` entero.

- [x] **Revisión de robustez del escritor de salida y la CLI (validación de entradas y publicación de archivos).**
  - Contexto: revisión posterior al ítem anterior, sobre los mismos archivos, sin cambiar el formato público ni agregar funcionalidades nuevas.

```text
Decisión:
Se corrigieron cuatro problemas de robustez detectados por revisión, sin
cambiar el formato público de observables.csv/trajectory.csv ni el
protocolo estadístico:
1. --rho-nominal y --eta ahora se validan con std::isfinite (rechazan NaN,
   inf, -inf) además de las validaciones de signo ya existentes;
   --rho-nominal debe ser estrictamente mayor que cero.
2. --rho-label pasó de una lista negra (rechazar '/', '\\', espacios) a una
   lista blanca (aceptar solo letras, dígitos, '_' y '-'); esto excluye por
   construcción '.', '..' y cualquier secuencia de escape de directorio
   ('../algo'), sin necesitar casos especiales.
3. format_eta_for_path (uso interno, para el segmento "eta_..." de la ruta)
   pasó de una precisión fija arbitraria (10 dígitos) a
   std::numeric_limits<double>::max_digits10 (17 dígitos, la misma garantía
   de round-trip que ya usaban los metadatos), para que dos valores de eta
   distintos no puedan colisionar en el mismo nombre de directorio.
4. execute_run ahora escribe y verifica ambos archivos requeridos completos
   como temporales (abrir, escribir, flush, close, cada paso chequeado)
   antes de publicar nada; recién publica con rename, trayectoria primero y
   observables.csv al final (la señal de que la corrida terminó), así que
   nunca se publica observables.csv si la escritura de la trayectoria
   requerida falló. Cualquier error limpia los .tmp que hayan llegado a
   crearse. Eliminar una trayectoria vieja (--overwrite sin
   --write-trajectory) ahora comprueba el resultado del borrado: si falla,
   se devuelve error sin publicar nada nuevo, en vez de ignorar el error de
   filesystem.
Fecha: 2026-08-30
Fundamento/evidencia: tests/test_cli_simulate.cpp, casos 12 (extendido:
--rho-nominal nan/inf/-1/0, --eta nan/inf/-inf), 13 (--rho-label inválido:
".", "..", "../escape", "rho/2", "rho 2", "rho\\2", vacío; válido: "rho_2",
"rho_1_over_pi", "rho_1_over_2pi", "rho-2", "RHO2"), 14 (format_eta_for_path
no colisiona para eta y std::nextafter(eta,1.0), y es determinístico), 15
(no queda ningún .tmp y el directorio tiene exactamente los 2 archivos
esperados tras una corrida exitosa), 16 (--overwrite sin trayectoria borra
la vieja; repetirlo cuando ya no hay trayectoria que borrar no falla), 17
(un error real de escritura -- directorio sin permiso de escritura -- no
publica observables.csv ni deja un .tmp, y se omite la aseveración estricta
si el entorno de ejecución ignora permisos, por ejemplo root en CI). Suite
completa: 100% tests passed, 0 failed, out of 11 (mismos 11 tests que
antes, sin agregar ni quitar targets de CMake).
Limitación de atomicidad documentada (no resuelta, es un límite real de
C++17 portable): std::filesystem::rename no ofrece una transacción atómica
entre dos archivos. Si el proceso se interrumpe exactamente entre publicar
trajectory.csv y publicar observables.csv, el directorio puede quedar con
una trayectoria nueva pero sin observables.csv actualizado; la función
nunca informa éxito en ese caso, y la recuperación es volver a correr con
--overwrite. Documentado en el comentario de execute_run
(src/cli/simulate_cli.hpp) y en 02_motor_y_algoritmos.md.
Etapas y archivos afectados: src/cli/simulate_cli.hpp,
tests/test_cli_simulate.cpp. text_output.hpp, model.hpp y el resto del
motor no se modificaron. No cambia el formato público de archivo ni marca
ninguna etapa (2, 3, 4, 5, 6) como completa; el protocolo estadístico sigue
sin decidirse.
Usuario que aprobó: usuario del proyecto (francoferrari123111@gmail.com),
mensaje "Corregí únicamente los problemas detectados en la revisión de la
salida y la CLI."
```
