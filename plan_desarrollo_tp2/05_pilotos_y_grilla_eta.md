# Etapa 5 - Corridas preliminares y elección del barrido de ruido

## Objetivo

Tomar las decisiones numéricas que la cátedra deja abiertas: valores de `eta`, duración, inicio estacionario, cantidad de realizaciones y casos característicos.

## Qué no está fijado

El enunciado no establece:

- rango ni paso de `eta`;
- cantidad de puntos del barrido;
- cantidad de pasos;
- cantidad de realizaciones;
- semillas;
- definición de las barras.

Por eso no se congela ahora una grilla numérica ni una duración arbitraria.

## Procedimiento mínimo

1. Elegir una grilla inicial gruesa de varios valores de `eta`, expresados con la convención `U[-eta/2,eta/2]`.
2. Ejecutar corridas preliminares para ambos modelos y las densidades `2,4,8`.
3. Inspeccionar `va(t)` y `S(t)` para distinguir transitorio y estacionario.
4. Confirmar que la grilla contiene situaciones cualitativamente diferentes de ruido bajo y alto.
5. Si el cambio de los observables queda mal resuelto, agregar puntos en esa zona.
6. Fijar una grilla final y ejecutarla completa para ambos modelos y las tres densidades.
7. Repetir el procedimiento de `S` para las densidades adicionales del estudio de clusters.

Las densidades adicionales deben pilotarse por separado: con `L=10` tienen solamente `N=32,16,11`, por lo que su tiempo de relajación y variabilidad pueden ser muy distintos de los casos `N=200,400,800`. No extrapolarles automáticamente el mismo `t_eq` ni la misma duración. Si se eligen duraciones distintas por bloque de densidad, documentarlas antes de producción y conservar una ventana estacionaria comparable en significado.

Esta exploración es parte del diseño experimental requerido; no es un estudio adicional.

## Comparabilidad

Para comparar modelos y densidades, conviene usar la misma grilla final de `eta`, la misma cantidad de realizaciones y el mismo criterio estadístico. Si una decisión difiere, debe justificarse y declararse antes del barrido definitivo.

Los pilotos pueden usar una grilla gruesa o duraciones cortas, pero sus archivos deben vivir en rutas o identificadores distintos de la producción. La identidad de una corrida debe incluir, como mínimo, protocolo/versión, modelo, densidad o `N`, `eta`, semilla y cantidad de pasos. Una corrida exploratoria nunca puede sobrescribir ni ser confundida con una definitiva.

## Casos característicos

Las notas del profesor sugieren quedarse con dos casos claramente distintos para series y animaciones:

- un caso de ruido bajo;
- un caso de ruido alto.

Los valores se eligen después de las corridas preliminares. No hace falta animar cada punto del barrido.

## Resultado que debe quedar registrado

Una tabla de protocolo con:

```text
eta_values, transient_steps, measurement_steps,
realizations, seeds, error_definition,
scalar_output_frequency, animation_output_frequency
```

Cada valor debe estar acompañado por una breve justificación basada en las series preliminares o en reproducibilidad/costo.

## Piloto ejecutado (2026-08-30): grilla exploratoria, resultados y propuestas preliminares

> Estado: propuesta preliminar. Ninguna decisión de esta sección está cerrada; ver "Qué sigue sin poder cerrarse" al final.

### Grilla y protocolo del piloto

- **Densidades**: únicamente las obligatorias, `rho=2,4,8` (`N=200,400,800`). No se incluyeron las densidades bajas (`1/pi, 1/(2pi), 1/(3pi)`): su conversión a `N` entero sigue sin resolverse.
- **Modelos**: Vicsek y votante, ambos con el mismo protocolo.
- **Grilla exploratoria de `eta`** (explícitamente de piloto, no la grilla final): `{0.0, 1.0, 2.0, 3.0, 4.0, 6.0}`. Justificación: con la convención de cátedra `xi~U[-eta/2,eta/2]`, el ruido cubre todo el círculo cuando `eta>=2*pi≈6.283`; valores mayores no agregan un régimen distinto porque el `U` ya es uniforme sobre `[0,2pi)`. Se eligieron 6 puntos razonablemente espaciados en `[0, ~2pi]` para separar cualitativamente ruido nulo, bajo, intermedio y cercano al máximo, sin comprometerse todavía con una grilla fina en ninguna zona particular (eso requeriría ya haber visto esta evidencia, que es justamente el objetivo de este piloto). No se copió ninguna grilla de otro grupo ni de la bibliografía (el artículo de votante usa otra convención de `eta`, ver `teoria_tp2_automatas_off_lattice.md` sección 5.1).
- **Realizaciones**: 3 por combinación (rango sugerido por la consigna: 3 a 5). Semillas explícitas y deterministas: `seed = 800000 + offset(modelo) + offset(rho) + 100*indice_eta + realizacion`, con `offset(vicsek)=0`, `offset(voter)=50000`, `offset(rho=2)=0`, `offset(rho=4)=10000`, `offset(rho=8)=20000` (ver `python/pilot_run.py`, función `seed_for`). El esquema es una función pura de la combinación: cualquier corrida del piloto se puede reproducir exactamente a partir de su fila en el manifiesto, sin tener que volver a correr el lote completo.
- **Duración**: `steps=600`, con `--observables-stride 1` (una fila por paso) y sin `--write-trajectory` (trayectoria desactivada, salvo en una corrida de inspección puntual separada, ver más abajo).
- **Búsqueda de vecinos**: únicamente CIM (`cell_index_neighbors`), vía la CLI productiva `simulate`. No se usó fuerza bruta como motor de estas corridas.
- **Combinaciones totales**: `2 modelos x 3 densidades x 6 etas x 3 realizaciones = 108 corridas`.

### Corrida de prueba previa (smoke test)

Antes de lanzar el lote completo se corrió una sola combinación pequeña (`vicsek, rho=2, eta=1.0, steps=200`) para comprobar tiempos, estructura de directorios y formato del CSV, y otra con `rho=8, N=800` para medir el caso más pesado. Resultado: `~0.07s` (N=200, 200 pasos) y `~0.48s` (N=800, 200 pasos) de tiempo de usuario. Con esa medición se decidió que 108 corridas de 600 pasos eran perfectamente viables en un piloto (estimado <2 minutos), y así fue: el lote completo tardó **65.7s**, sin fallos.

### Comandos ejecutados

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure          # 11/11 antes del piloto

python3 python/pilot_run.py --run-name pilot_grid_1 --steps 600
python3 python/pilot_analyze.py --run-name pilot_grid_1
```

`pilot_run.py` invoca `build/simulate` 108 veces (una por combinación) escribiendo en `data/pilots/pilot_grid_1/` (fuera de control de versiones, ver `.gitignore`) y deja un manifiesto liviano en `data/summary/pilot_grid_1_manifest.csv`. `pilot_analyze.py` relee **de forma independiente** cada `observables.csv` generado (sin confiar en el manifiesto: parsea la cabecera `# clave=valor` y los datos igual que lo haría un lector externo), verifica invariantes de formato, y escribe tres tablas resumen livianas en `data/summary/`:

- `pilot_grid_1_by_realization.csv`: una fila por corrida (109 filas incluyendo cabecera).
- `pilot_grid_1_by_combo.csv`: agregado entre las 3 realizaciones por `(modelo, rho, eta)` (37 filas incluyendo cabecera).
- `pilot_grid_1_series_sampled.csv`: evolución temporal de `va(t)` promediada entre realizaciones, muestreada cada 25 pasos, por combinación.

### Verificación de formato e invariantes

`pilot_analyze.py` verificó automáticamente, sobre los 108 `observables.csv` reales (no sobre el manifiesto): `t` ordenado, `va` y `S` en `[0,1]`, presencia de `t=0` y del paso final `t=600`, y presencia de las claves de metadatos requeridas. Resultado: **108/108 archivos válidos, 0 problemas encontrados**.

Verificaciones manuales adicionales:

- Reproducibilidad byte a byte: dos corridas con exactamente la misma configuración y semilla producen el mismo `observables.csv` (`diff` sin diferencias).
- Semillas/realizaciones diferenciadas: cambiar `--realization`/`--base-seed` cambia el archivo resultante.
- Sin `--write-trajectory`, no se crea ningún `trajectory.csv` (confirmado con `find`).
- Con `--write-trajectory --trajectory-stride 10` en una corrida de inspección puntual (`vicsek, rho=4, eta=1.0, steps=100`), se generó `trajectory.csv` con las filas esperadas (`(steps/stride + 1) * N` más el primer y último paso garantizados) y el formato `t,id,x,y,theta` documentado.

### Resultados: `<va>` estacionario aproximado por densidad y modelo

Promedio entre 3 realizaciones del promedio temporal en el último 25% de los 600 pasos (`t>=450`), **no** el valor final puntual. Tabla completa con desvío entre realizaciones y error estándar en `data/summary/pilot_grid_1_by_combo.csv`; acá una versión condensada:

| modelo | rho | eta=0.0 | eta=1.0 | eta=2.0 | eta=3.0 | eta=4.0 | eta=6.0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| vicsek | 2 | 1.000 | 0.914 ± 0.047 | 0.666 ± 0.102 | 0.402 ± 0.183 | 0.159 ± 0.018 | 0.065 ± 0.001 |
| vicsek | 4 | 1.000 | 0.947 ± 0.002 | 0.791 ± 0.019 | 0.547 ± 0.037 | 0.190 ± 0.028 | 0.045 ± 0.001 |
| vicsek | 8 | 1.000 | 0.954 ± 0.001 | 0.811 ± 0.017 | 0.601 ± 0.020 | 0.341 ± 0.013 | 0.032 ± 0.001 |
| votante | 2 | 0.887 ± 0.179 (*) | 0.241 ± 0.053 | 0.106 ± 0.014 | 0.083 ± 0.002 | 0.067 ± 0.004 | 0.062 ± 0.001 |
| votante | 4 | 0.883 ± 0.103 (*) | 0.136 ± 0.045 | 0.080 ± 0.012 | 0.058 ± 0.004 | 0.048 ± 0.001 | 0.043 ± 0.002 |
| votante | 8 | 0.521 ± 0.189 (*) | 0.100 ± 0.015 | 0.052 ± 0.008 | 0.042 ± 0.002 | 0.035 ± 0.001 | 0.030 ± 0.001 |

`(±)` es el desvío entre las 3 realizaciones (no error estándar), solo para esta tabla condensada. `(*)` marca los casos donde la serie temporal (ver abajo) muestra que la corrida **todavía no llegó** a un régimen estable dentro de los 600 pasos: no deben leerse como el `<va>` estacionario real de esos casos.

El patrón cualitativo esperado por la teoría aparece con claridad: `<va>` decrece monótonamente al aumentar `eta` en ambos modelos y las tres densidades, y a igual `eta` una densidad mayor sostiene más orden (más vecinos por partícula). `S` (fracción del cluster más grande) se mantiene cerca de 1 en casi todos los casos con estas densidades (`rho=2,4,8` ya están bien por encima del umbral de percolación de un disco de radio `rc=1`), así que en este piloto `S` no resulta tan informativo como `va` para distinguir regímenes; puede ser distinto para las densidades bajas, que quedan fuera de este piloto.

### Evolución temporal: qué sí y qué no alcanza a verse en 600 pasos

Se inspeccionó la serie completa muestreada cada 25 pasos (`data/summary/pilot_grid_1_series_sampled.csv`), no solo el promedio final, para las combinaciones más relevantes:

- **Vicsek, cualquier densidad, `eta<=2`**: `va(t)` sube rápido desde el estado inicial desordenado (`va(0)~0.03-0.15`, consistente con el residual `O(N^-1/2)` esperado de un estado aleatorio) y se estabiliza dentro de los primeros 100-200 pasos, con fluctuaciones pequeñas alrededor de un valor estable el resto de la corrida. Ejemplo (`vicsek, rho=8, eta=0`): ya en `t=125` el promedio entre realizaciones está indistinguible de 1.
- **Vicsek, ruido intermedio (`eta=3,4`), densidad baja (`rho=2`)**: la serie **no** se estabiliza limpiamente dentro de los 600 pasos: sigue oscilando con amplitud comparable a su propio valor medio (ejemplo `vicsek, rho=2, eta=3`: valores muestreados entre 0.13 y 0.52 después de `t=100`, sin una tendencia clara de asentarse). Es evidencia de estar cerca de la zona de transición orden/desorden para esa densidad, donde las fluctuaciones finitas son grandes y 3 realizaciones no alcanzan para promediarlas.
- **Votante, `eta=0` (las tres densidades)**: la serie sigue **creciendo** de forma sostenida durante toda la corrida, sin aplanarse. Ejemplo (`voter, rho=2, eta=0`): el promedio entre realizaciones pasa de `0.07` (`t=0`) a `0.63` (`t=125`) a `0.92` (`t=600`), todavía subiendo al final de la ventana observada, con un desvío entre realizaciones grande y no decreciente (`~0.11-0.16` en la segunda mitad de la corrida). Para `rho=8` la situación es más marcada: el promedio llega solo a `~0.46-0.56` hacia el final y con oscilaciones grandes, lejos del consenso (`va=1`) que sí se observó en la regresión diagnóstica de grafo completo (`tests/voter_consensus_regression.cpp`, consenso en 17-64 pasos, pero con conectividad total, no con el CIM y `rc=1` reales).
- **Votante, `eta>=1`**: a diferencia de `eta=0`, sí se estabiliza dentro de la ventana observada (valores de `<va>` pequeños y con desvío chico entre realizaciones desde aproximadamente `t=400-600`, según la densidad).

### Comparación Vicsek vs. votante en tiempo de relajación

Con el mismo protocolo (misma duración, misma cantidad de realizaciones, mismas densidades), la evidencia de este piloto indica que **el votante necesita sustancialmente más pasos que Vicsek para estabilizarse**, al menos en el régimen de ruido bajo (`eta=0`) con los parámetros físicos reales del TP (`v=0.03`, `rc=1`, densidades finitas, búsqueda de vecinos por CIM, sin conectividad total). Esto es consistente con la naturaleza de cada regla: Vicsek promedia toda la vecindad en cada paso (una sola actualización ya "resume" mucha información), mientras que el votante solo copia un vecino a la vez, así que la información tarda más pasos en propagarse por todo el sistema, y esa propagación además depende de que las partículas se muevan lo suficiente como para encontrarse (a diferencia del escenario de grafo completo de la regresión diagnóstica, donde todos son vecinos de todos desde el primer paso).

### Estimación heurística (preliminar) de `t_eq` por combinación

`pilot_analyze.py` calcula, además de las tablas anteriores, una estimación **puramente informativa** de `t_eq`: el primer punto muestreado (cada 25 pasos) tal que todos los puntos posteriores quedan a menos de `0.03` del promedio de la ventana final. Es una regla simple y documentada, no un criterio de cierre: cuando la serie no se estabiliza dentro de los 600 pasos, la función devuelve explícitamente `sin_evidencia` en vez de forzar un número (ver columna `t_eq_heuristic_estimate` en `data/summary/pilot_grid_1_by_combo.csv`). Aparece `sin_evidencia` en: `vicsek rho=2 eta={3,4}`, `vicsek rho=4 eta=3`, `vicsek rho=8 eta=4`, y **todos** los `voter eta=0` (las tres densidades) y `voter rho=4 eta=1`. Estos son exactamente los casos señalados arriba como "no estabilizados en 600 pasos": la heurística no inventa un `t_eq` donde la evidencia no lo sostiene.

Donde sí hay una estimación (por ejemplo `vicsek rho=8 eta=0`: `t_eq≈125`; `vicsek rho=4 eta=1`: `t_eq≈200`), los valores son consistentes con la inspección visual de la serie: la relajación de Vicsek en ruido bajo/moderado ocurre dentro del primer tercio de los 600 pasos usados en este piloto.

### Propuesta inicial que surge de esta evidencia (preliminar, no decisión de cierre)

- **Grilla de `eta`**: la grilla piloto `{0,1,2,3,4,6}` ya separa regímenes cualitativamente distintos (orden casi perfecto, transición, desorden) en ambos modelos. Antes de fijar la grilla definitiva conviene **agregar puntos entre `eta=2` y `eta=4`** (donde `<va>` cae más rápido, sobre todo en `rho=2`) para resolver mejor la curva `<va>` vs. `eta` en esa zona, y quizás un punto más entre `4` y `6` para confirmar el aplanamiento cerca del máximo. No se propone todavía un valor de espaciado fijo.
- **`t_eq` y duración**: para Vicsek con `eta<=2`, `t_eq` del orden de 100-200 pasos parece razonable según esta evidencia, con `steps` de producción bastante mayor que eso para tener una ventana estacionaria amplia. Para el votante en `eta=0` (y posiblemente `eta` bajo en general) la evidencia indica que **600 pasos no alcanzan**: haría falta una corrida piloto específica y más larga (por ejemplo 2000-5000 pasos) antes de proponer un `t_eq` para ese caso, y probablemente una duración distinta por modelo en vez de una única duración común (la guía de la etapa 5 ya anticipa esta posibilidad para las densidades bajas; este piloto muestra que también aplica entre modelos a igual densidad).
- **Realizaciones**: con solo 3 realizaciones, el desvío entre ellas es grande en la zona de transición (por ejemplo `vicsek rho=2 eta=3`: desvío `±0.18`, más grande que muchos de los propios valores medios de la tabla). Para el barrido definitivo, sobre todo cerca de la transición, va a hacer falta más de 3 realizaciones para que el error estándar sea razonablemente chico; este piloto no alcanza para proponer un número concreto, pero sí para descartar que 3 realizaciones sean suficientes en esa zona.
- **Stride**: `--observables-stride 1` (usado en todo el piloto) generó archivos de pocos KB incluso con 600 pasos y `N` hasta 800 (los observables no dependen de `N`, solo de `steps`); no hay evidencia todavía de que haga falta espaciar el muestreo de observables para producción. La trayectoria (probada aparte, con `--trajectory-stride 10`) sí crece con `N`, como se esperaba, y confirma que conviene mantenerla desactivada por defecto en el barrido y activarla solo para los pocos casos que se vayan a animar.
- **Barras de error**: no se decide en este piloto (la guía admite desvío entre realizaciones o error estándar); ambas quedan calculadas en `data/summary/pilot_grid_1_by_combo.csv` para cuando se tome esa decisión.

### Datos livianos guardados en el repositorio

- `data/summary/pilot_grid_1_manifest.csv`: 108 filas, comando/semilla/tiempo de cada corrida.
- `data/summary/pilot_grid_1_by_realization.csv`: 108 filas, resumen por corrida.
- `data/summary/pilot_grid_1_by_combo.csv`: 36 filas, agregado entre realizaciones por combinación.
- `data/summary/pilot_grid_1_series_sampled.csv`: series `va(t)` muestreadas cada 25 pasos, promediadas entre realizaciones, por combinación.
- `python/pilot_run.py` y `python/pilot_analyze.py`: herramientas auxiliares (solo biblioteca estándar de Python, sin dependencias externas) para reproducir el lanzamiento y el análisis.

Los 108 `observables.csv` crudos (y cualquier archivo bajo `data/pilots/`) **no** se versionan (`.gitignore` agregó `/data/pilots/` y `/data/raw/`); se pueden regenerar en menos de dos minutos con los comandos de la sección "Comandos ejecutados".

### Qué sigue sin poder cerrarse con este piloto

- La grilla final de `eta`, el valor o criterio final de `t_eq` (en particular para el votante), la cantidad definitiva de realizaciones, las semillas de producción y la definición de barras de error: todo sigue en `[ ]` en `DECISIONES_PENDIENTES.md`.
- El votante en `eta=0` (y posiblemente otros `eta` bajos) requiere un piloto dedicado con más pasos antes de proponer su `t_eq`: la evidencia de este piloto alcanza para decir "600 pasos no bastan", no para decir cuántos bastarían.
- Las densidades bajas (`1/pi,1/(2pi),1/(3pi)`) no se pilotaron todavía (conversión a `N` sin resolver).
- Los valores productivos de stride para el barrido definitivo (más allá de confirmar que `stride=1` en observables es liviano) siguen sin decidirse.

## Estudio dedicado del votante (2026-08-30): grilla refinada, R=20, 3000 pasos

> Estado: protocolo acordado con el usuario para el votante (el grupo decidió enfocarse únicamente en este modelo). Grilla de `eta`, `R` y `steps` ya fijados para esta línea de trabajo; sigue pendiente la definición de barra de error (desvío vs. error estándar) y la elección explícita de `t_eq` por combinación.

### Grilla y protocolo

- **Grilla de `eta` refinada** (reemplaza a la exploratoria `{0,1,2,3,4,6}` del piloto anterior, densificada entre `eta=2` y `eta=4` por la caída rápida observada ahí): `{0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6}` (11 puntos).
- **Realizaciones**: `R=20`, elegido a partir de la varianza observada en el piloto anterior (con `R=3`, desvío `±0.18` cerca de la transición, comparable al propio valor medio). Con `R=20` el error estándar del peor caso observado bajó a un orden de `0.01-0.05` (ver `voter_eta_study_1_by_combo.csv`).
- **Duración**: `steps=3000` (frente a los `600` del piloto exploratorio), porque el votante con `eta` bajo no se estabilizaba en 600 pasos con los parámetros físicos reales del TP.
- **Densidades obligatorias** (`rho=2,4,8`): herramienta `python/voter_eta_study_run.py` / `python/voter_eta_study_analyze.py` / `python/voter_eta_study_plot.py`. 660 corridas (3 densidades x 11 etas x 20 realizaciones), 0 fallos, ~305s de cómputo total (paralelizado). Resultados en `data/summary/voter_eta_study_1_*.csv` y `figures/voter_eta_study_1/*.png`.
- **Densidades bajas del estudio de clusters** (`1/pi,1/(2pi),1/(3pi)` -> `N=32,16,11`, redondeo al entero más cercano, ver README): herramienta `python/voter_lowrho_cluster_study_run.py` (mismo protocolo: misma grilla de `eta`, mismo `R=20`). Se corrieron dos duraciones para decidir `steps`:
  - `voter_lowrho_cluster_study_1` (steps=3000): 660 corridas, 0 fallos, ~9s.
  - `voter_lowrho_cluster_study_2` (steps=6000): 660 corridas, 0 fallos, ~18s.

### Por qué 3000 pasos alcanzan para las densidades bajas (evidencia, no solo criterio automático)

El motivo por el que se corrió también a 6000 pasos fue descartar que el sistema siguiera en transitorio a los 3000. La comparación directa de `<va>` estacionario entre ambas duraciones, para `rho=1/pi` (N=32), da:

| eta | `<va>` (steps=3000) | `<va>` (steps=6000) |
|---:|---:|---:|
| 0 | 1.0000 | 1.0000 |
| 0.5 | 0.5737 | 0.6252 |
| 1 | 0.4092 | 0.3977 |
| 1.5 | 0.2858 | 0.2909 |
| 2 | 0.2357 | 0.2386 |
| 2.5 | 0.2050 | 0.2053 |
| 3 | 0.1842 | 0.1878 |
| 3.5 | 0.1712 | 0.1729 |
| 4 | 0.1645 | 0.1652 |
| 5 | 0.1591 | 0.1585 |
| 6 | 0.1565 | 0.1570 |

Duplicar la duración no desplazó la estimación (la mayor diferencia, en `eta=0.5`, es `0.057`, del orden del propio desvío entre realizaciones en ese punto). Si el sistema hubiera seguido relajando entre `t=3000` y `t=6000`, el valor medido a 6000 pasos tendría que haberse corrido sistemáticamente respecto del de 3000 pasos; no lo hizo. Esto es evidencia directa (no una suposición) de que **el régimen ya era estacionario a los 3000 pasos**, y de que no hace falta correr más para esta línea de trabajo.

### Por qué la heurística automática de `t_eq` no es confiable para estas densidades, y qué hacer en su lugar

`pilot_analyze.py`/`voter_eta_study_analyze.py` calculan una estimación automática de `t_eq`: recorren la serie temporal muestreada y devuelven el primer `t` tal que, desde ahí en adelante, **todos** los puntos siguientes quedan a menos de `0.03` del promedio de la ventana final; si ningún punto cumple eso, informan `sin_evidencia`.

Para las densidades bajas, esa heurística marcó `sin_evidencia` (o un `t_eq` pegado al último paso, es decir, "recién se cumplió al final por casualidad") en varias combinaciones, incluso después de duplicar la duración a 6000 pasos, mientras que la tabla de arriba muestra que el valor medio ya era estable desde los 3000. La razón es puramente de **tamaño finito**, no de falta de equilibración:

- Con `N=11,16,32`, cada partícula pesa una fracción grande del sistema (`1/N` entre `0.03` y `0.09`). En el modelo de votante, cada paso puede cambiar la orientación de una fracción no despreciable de partículas de una sola vez (copian a un vecino), así que la polarización `va` de una corrida individual fluctúa con una amplitud que no se achica con más pasos: es una propiedad de la dinámica en un sistema chico, no un transitorio que "todavía falta terminar".
- El promedio entre las `R=20` realizaciones reduce esa fluctuación, pero no la elimina: el error estándar de ese promedio, en varios puntos, queda en el mismo orden que la tolerancia fija de `0.03` que usa la heurística. Como la heurística exige que **todos** los puntos muestreados posteriores queden dentro de esa tolerancia, alcanza con que una sola fluctuación estadística la exceda (algo casi garantizado cuando hay muchos puntos muestreados, como con `steps=6000`) para que el criterio automático informe "no hay evidencia de estacionario", aunque el promedio real ya esté establecido.
- Esto explica también por qué correr más pasos no mejoró el diagnóstico automático: más pasos muestreados significa más oportunidades de que una fluctuación puntual rompa la condición estricta de la heurística, no una serie que realmente siga sin asentarse.

**Consecuencia para el informe**: para las densidades bajas del estudio de clusters, `t_eq` no se puede justificar citando el número que devuelve el script automático (fue calibrado pensando en la escala de ruido de `rho=2,4,8`, donde las fluctuaciones de tamaño finito son mucho menores). Hay que justificarlo por **inspección visual de la serie temporal completa** (los gráficos `va_t_rho_1_over_*.png` en `figures/voter_lowrho_cluster_study_1/` y `_2/`): mostrar que, salvo por el ruido esperable de un sistema chico, el nivel medio de la curva ya se estabiliza tempranamente (para la mayoría de los `eta`, dentro de los primeros 500-1000 pasos; el caso `eta=0`, que converge a consenso exacto, se estabiliza incluso antes, entre `t≈650` y `t≈1600` según la densidad), y acompañarlo con la evidencia cuantitativa de la tabla de arriba (comparación 3000 vs. 6000 pasos) como respaldo de que la ventana estacionaria elegida no depende de dónde se corte la corrida.

### Resultado físico del estudio de clusters con densidades bajas

`S` (fracción del cluster más grande) cae de forma monótona con `eta`, desde `~0.86-0.98` en `eta=0` hasta `~0.17-0.22` en `eta=6`, muy por debajo de 1 en todo el barrido y con las tres densidades bajas casi superpuestas entre sí. Esto contrasta con `rho=2,4,8`, donde `S` se mantiene siempre cerca de 1: es la evidencia de que estas densidades bajas (`rho*pi*rc^2` del orden de `1, 0.5, 0.33` vecinos medios) están por debajo del umbral de percolación de un disco de radio `rc=1`, así que la red de vecinos queda fragmentada en varios clusters chicos en vez de formar una única componente gigante. Detalle completo en `data/summary/voter_lowrho_cluster_study_1_by_combo.csv` y `figures/voter_lowrho_cluster_study_1/S_vs_eta.png`.

## Criterio de cierre

- [ ] Hay varios valores de `eta` y situaciones de bajo/alto ruido.
  - Estado: propuesta preliminar. El piloto de 2026-08-30 (grilla `{0,1,2,3,4,6}`, ambos modelos, `rho=2,4,8`) ya muestra situaciones cualitativamente distintas; falta decidir si esa grilla es la definitiva o necesita más puntos (ver "Propuesta inicial" arriba).
- [ ] La grilla resuelve el cambio observado sin imponer un `eta_c` no solicitado.
  - Estado: propuesta preliminar. La caída de `<va>` vs. `eta` está bien resuelta en los extremos; la zona `eta=2..4` (donde cae más rápido, sobre todo en `rho=2`) probablemente necesite más puntos antes de considerarse resuelta.
- [ ] `t_eq` y duración se justifican con series temporales.
  - Estado: propuesta preliminar, y con una limitación explícita: para Vicsek con `eta` bajo/moderado hay evidencia razonable (`t_eq` del orden de 100-200 pasos); para el votante en `eta=0` la evidencia muestra que 600 pasos no alcanzan a estabilizar la serie, así que ese caso queda sin propuesta de `t_eq` (ver "Qué sigue sin poder cerrarse").
- [ ] Cantidad de realizaciones, semillas y barras quedaron definidas.
  - Estado: propuesta preliminar. El piloto usó 3 realizaciones con semillas explícitas y deterministas (documentadas arriba), pero mostró que 3 no alcanzan para un error chico cerca de la transición; no se fija todavía un número definitivo. La definición de barras (desvío vs. error estándar) sigue sin elegirse.
- [ ] El mismo protocolo permite comparar Vicsek y votante.
  - Estado: propuesta preliminar. El piloto ya corrió ambos modelos con exactamente el mismo protocolo (misma grilla, misma duración, mismas realizaciones, mismas densidades), lo que permitió justamente detectar que sus tiempos de relajación difieren (ver "Comparación Vicsek vs. votante").
- [ ] La grilla final está registrada antes de producción.
  - Sigue sin registrarse: lo de arriba es la grilla del piloto, no la definitiva.
- [ ] Las densidades bajas fueron pilotadas por separado antes de fijar su `t_eq` y duración.
  - Sigue pendiente: no se incluyeron en este piloto.
- [ ] Los artefactos de pilotos y producción tienen identidades/rutas incompatibles entre sí.
  - Estado: propuesta preliminar cumplida en la práctica. Los pilotos viven bajo `data/pilots/<run_name>/...` (ignorado por git), con la misma estructura de directorio por corrida que usaría producción pero bajo una raíz distinta (`--output-dir data/pilots/pilot_grid_1` en vez de, por ejemplo, `data/raw/...`), así que no hay forma de que una corrida de piloto sobrescriba o se confunda con una corrida de producción real.
