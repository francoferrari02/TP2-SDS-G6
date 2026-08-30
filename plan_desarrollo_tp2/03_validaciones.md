# Etapa 3 - Validaciones que habilitan el barrido

## Regla de avance

No ejecutar el barrido definitivo si alguna validación crítica falla. Un test que solo reproduce la implementación no es evidencia: los resultados esperados deben derivarse de la ecuación, de una construcción manual o de un oráculo independiente.

## 1. Geometría periódica

Casos deterministas:

- Partículas en `x=0.1` y `x=9.9`, igual `y`, deben estar separadas por 0.2.
- Repetir cruzando `y` y una esquina.
- Una separación exactamente `rc` debe contar como vecina.
- Una separación `rc+epsilon` no debe contar.
- `periodic_wrap` siempre deja coordenadas en `[0,L)` incluso para desplazamientos negativos.

## 2. CIM contra fuerza bruta

Para muchos estados pequeños y semillas:

```text
sorted(neighbors_CIM[i]) == sorted(neighbors_bruteforce[i]) para todo i
```

Probar posiciones aleatorias y construcciones adversarias: bordes, esquinas, varias partículas en una celda y pares justo en el radio. Verificar listas simétricas, sin duplicados ni autoaristas.

Fuerza bruta queda únicamente como oráculo interno de test, no como motor productivo ni como estudio adicional.

- [x] **Comparación CIM vs. fuerza bruta.**
  - Implementación: `tp2::cell_index_neighbors` en `src/core/neighbor_search.hpp`, validada contra `tp2::brute_force_neighbors` (sin modificar el oráculo existente) en `tests/test_neighbor_search_cim.cpp`, registrado en CTest como `neighbor_search_cim`.
  - Evidencia (13 casos, todos comparando listas completas de `id`, no solo tamaños): muchos estados pequeños con semillas fijas (`N=12`, 30 semillas), posiciones aleatorias uniformes de tamaño moderado (`N=120`, 6 semillas), cruce de borde en `x`, cruce de borde en `y`, cruce de esquina periódica, pares exactamente a `rc`, pares apenas fuera de `rc`, varias partículas en la misma celda, partículas en celdas vecinas (horizontal/vertical/diagonal), partículas en celdas alejadas (con verificación explícita de listas vacías), simetría/ausencia de autovecinos/ausencia de duplicados evaluadas directamente sobre la salida del CIM, independencia del orden de almacenamiento (comparando por `id`, no por posición), y varios tamaños de sistema incluidos casos degenerados `N ∈ {0,1,2,3,5,8,13,21,50}`.
  - La función de comparación falla con un mensaje explícito (partícula, posición, listas completas de ambos métodos) si detecta una diferencia, en vez de solo comparar cantidades de vecinos.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: solo cubre la comparación de listas de vecinos entre CIM y fuerza bruta pedida por este punto. La integración del CIM con `union-find`/clusters ya está implementada (`tp2::largest_cluster_size`/`largest_cluster_fraction` en `src/core/observables.hpp`, consumen sin cambios las listas de `cell_index_neighbors`) y validada por separado en la sección "8. Clusters" de este mismo documento; ese es un punto distinto del criterio de cierre general de la etapa, no algo que falte aquí.

## 3. Número medio inicial de vecinos

Promediar muchas inicializaciones uniformes. Para las densidades base, el número medio de otros vecinos debe aproximar el valor asintótico que usa la cátedra, `rho*pi*rc^2`.

Conviene distinguir dos cantidades, porque no son la misma expresión y difieren en una cantidad conocida y explicable:

- **Aproximación de la cátedra (asintótica en `N`):** `rho*pi*rc^2 = (N/L^2)*pi*rc^2`. Es la que aparece en `AGENTS.md` y en el enunciado, y la que se usa como criterio de validación.
- **Expectativa finita exacta para vecinos *externos*:** en una caja periódica (torus), cada una de las otras `N-1` partículas es independiente y uniforme sobre el área `L^2`, y cae dentro del disco de radio `rc` alrededor de una partícula dada con probabilidad exacta `pi*rc^2/L^2` (sin efecto de borde, porque el torus no tiene borde). Por linealidad de la esperanza, el valor esperado *exacto* del número de vecinos externos de una partícula es `(N-1)*pi*rc^2/L^2`, no `N*pi*rc^2/L^2`.

La diferencia entre ambas expresiones es exactamente `pi*rc^2/L^2` (una partícula menos en el numerador): con `L=10`, `rc=1`, eso es `pi/100 ≈ 0.0314`, y se debe pura y simplemente a que una partícula **nunca puede contarse a sí misma como vecina** (`cell_index_neighbors`/`brute_force_neighbors` excluyen explícitamente la autoarista). No es un error de la aproximación de la cátedra ni de la medición: es la diferencia esperada entre una fórmula asintótica en `N` y la cuenta exacta de "otros" en un sistema finito.

| rho | N | aproximada `rho*pi*rc^2` | finita exacta `(N-1)*pi*rc^2/L^2` |
|---:|---:|---:|---:|
| 2 | 200 | 6.283 | 6.252 |
| 4 | 400 | 12.566 | 12.535 |
| 8 | 800 | 25.133 | 25.101 |

No exigir igualdad exacta a una sola inicialización: la guía pide verificar que el promedio de varias condiciones iniciales se aproxime a esos valores. El criterio de aceptación de este punto sigue comparando contra la aproximación de la cátedra (`rho*pi*rc^2`, ver evidencia abajo); la expectativa finita exacta se documenta como una explicación más precisa de por qué el valor medido cae sistemáticamente un poco por debajo de la aproximación asintótica, no como un cambio del criterio de aceptación (los resultados ya medidos siguen siendo válidos bajo cualquiera de las dos referencias, porque `6.355`, `12.502` y `25.123` quedan cerca de ambas).

- [x] **Vecinos medios compatibles con teoría.**
  - Implementación: `tests/test_mean_neighbors.cpp`, registrado en CTest como `mean_neighbors`. No modifica `tp2::cell_index_neighbors` ni ninguna otra pieza del motor: genera el estado inicial con el inicializador productivo `tp2::initialize_particles` (`src/core/initialization.hpp`, ver sección "Validación del inicializador" más abajo) y mide con el CIM. Antes de esta tarea el test tenía su propia función de generación de posiciones (`uniform_random_particles`, fijando `theta=0.0`); ahora usa la misma pieza que usará la simulación, y `theta` sale aleatorio uniforme (irrelevante para este test, que solo mide vecindad geométrica).
  - Método: para cada densidad obligatoria (`rho=2,4,8` -> `N=200,400,800`, `L=10`, `rc=1`), se ejecutan **40 realizaciones independientes** con semillas explícitas `seed = seed_base + i` (`i=0..39`), `seed_base=100000` para `rho=2`, `200000` para `rho=4`, `300000` para `rho=8` (offsets separados para que ninguna realización de una densidad reutilice la secuencia de otra). Se cuentan únicamente vecinos externos (`cell_index_neighbors` nunca incluye a la propia partícula) y se promedia sobre el total de partículas de las 40 realizaciones.
  - Valores medidos (corrida posterior a cambiar la generación de posiciones al inicializador productivo, `cmake --build build && ./build/test_mean_neighbors`; el valor cambia levemente frente a la corrida anterior porque el orden de consumo del generador ya no es el mismo -- ahora también sortea `theta` por partícula -- pero sigue dentro de la tolerancia y conserva el orden estricto):

    | rho | N | aproximada `rho*pi*rc^2` | finita exacta `(N-1)*pi*rc^2/L^2` | medido | realizaciones | semilla base |
    |---:|---:|---:|---:|---:|---:|---:|
    | 2 | 200 | 6.283 | 6.252 | 6.338 | 40 | 100000 |
    | 4 | 400 | 12.566 | 12.535 | 12.498 | 40 | 200000 |
    | 8 | 800 | 25.133 | 25.101 | 25.162 | 40 | 300000 |

  - Los tres valores medidos caen entre ambas referencias (aproximada y finita exacta), y más cerca todavía de la finita exacta en dos de las tres densidades, lo cual es consistente con que la medición cuenta vecinos *externos* (sin autoarista), tal como predice la expectativa finita.
  - Criterio de aceptación (sin cambios respecto de la evidencia anterior): (1) el valor medido de cada densidad debe estar dentro de un 5% relativo del valor **aproximado** `rho*pi*rc^2` (no de la expectativa finita exacta, para no introducir un segundo criterio); (2) `mean_k(rho=2) < mean_k(rho=4) < mean_k(rho=8)` estrictamente. El 5% es una **tolerancia de validación empírica**, no un requisito de la cátedra: con 40 realizaciones y `N` partículas por realización, el error estándar esperado del promedio (`~sqrt(<k>/(N*realizaciones))`) es de un orden de magnitud menor a esa banda para las tres densidades, así que la tolerancia deja margen tanto para la fluctuación estadística normal de una muestra finita como para el corrimiento sistemático y ya explicado hacia la expectativa finita exacta (`~0.03` vecinos), sin dejar pasar errores reales de geometría, periodicidad, radio o asignación de vecinos (que típicamente producen desvíos de orden 1 o mayores, o rompen el orden entre densidades). El test también imprime una línea legible por densidad (`rho=... N=... expected=... measured=... realizations=... seed_base=...`).
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: valida únicamente la inicialización uniforme y la búsqueda de vecinos (CIM) en el estado inicial, para las tres densidades obligatorias. No valida el comportamiento dinámico (no ejecuta ningún paso de simulación), no fija ni congela `eta`, `t_eq`, cantidad de realizaciones o semillas para el barrido definitivo, y no compara contra fuerza bruta en esta suite (esa comparación ya está cubierta por separado en la sección "2. CIM contra fuerza bruta" de este mismo documento).

### Validación del inicializador

- [x] **Inicializador productivo del estado.**
  - Implementación: `tp2::initialize_particles`/`tp2::initialize_particles_from_density` en `src/core/initialization.hpp`, validadas en `tests/test_initialization.cpp`, registrado en CTest como `initialization`. Detalle de interfaz, generador y distribuciones en `02_motor_y_algoritmos.md`, sección "Inicializador productivo del estado".
  - Evidencia (11 casos): IDs consecutivos y únicos (`0..N-1`); cantidad correcta de partículas; posiciones en `[0,L)`; orientaciones en `[0,2*pi)`; misma semilla produce estados idénticos bit a bit; semillas distintas pueden producir estados distintos (verificado sobre 20 semillas); las tres densidades obligatorias (`rho=2,4,8`) producen `N=200,400,800`; la inicialización no modifica `Parameters`; `N=0` (con ambas funciones) devuelve un vector vacío sin error; el estado generado se pasa directamente a `run_simulation` (5 pasos de Vicsek con CIM) sin ninguna adaptación y el resultado queda en rango; el resultado no depende de ninguna semilla del reloj (dos llamadas con la misma semilla explícita, separadas por trabajo intermedio no trivial, dan el mismo resultado bit a bit).
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 9`.
  - Alcance de este cierre: cubre únicamente la construcción del estado inicial en memoria (posiciones/orientaciones uniformes, reproducibilidad, integración directa con `run_simulation`). No incluye la conversión de las densidades bajas (`1/pi`, `1/(2*pi)`, `1/(3*pi)`) a `N` entero, que sigue como decisión abierta en `DECISIONES_PENDIENTES.md`, ni ningún formato de salida a disco.

## 4. Polarización

- Todas las orientaciones iguales: `va=1` dentro de tolerancia numérica.
- Pares opuestos balanceados: `va=0` dentro de tolerancia.
- Para estados aleatorios: `0 <= va <= 1`.

- [x] **Polarización `va`.**
  - Implementación: `tp2::polarization` en `src/core/observables.hpp`, validada en `tests/test_observables.cpp`, registrado en CTest como `observables`.
  - Evidencia (8 casos, todos con resultado esperado derivado de la definición, no de la propia implementación): una sola partícula (`va=1`); todas las orientaciones iguales, 4 partículas (`va=1`); dos orientaciones opuestas `0`/`pi` (`va=0`); cuatro direcciones balanceadas `0, pi/2, pi, 3*pi/2` (`va=0`); resultado analítico exacto para `theta=0` y `pi/2` (`va=sqrt(2)/2`); estado aleatorio de 100 partículas con `0<=va<=1`; el cálculo no modifica `particles`; `N=0` da `va=0` según la convención documentada en el header.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: cubre el cálculo de `va` sobre un estado fijado a mano o generado aleatoriamente en el propio test. No incluye medir `va(t)` dentro de un bucle de simulación, ni promedios entre realizaciones ni la elección de `t_eq`, que dependen de piezas todavía no implementadas.

## 5. Promedio circular de Vicsek

- Dos ángulos `1 grado` y `359 grados` deben promediar cerca de `0`, no de `180`.
- Una partícula aislada con `eta=0` conserva su ángulo porque el promedio incluye a sí misma.
- Construcción manual de tres partículas con resultado analítico conocido.

- [x] **Regla de Vicsek (cálculo de orientación nueva).**
  - Implementación: `tp2::vicsek_update` en `src/core/rules.hpp`, validada en `tests/test_rules.cpp`, registrado en CTest como `rules`.
  - Evidencia: partícula aislada con `eta=0` conserva su orientación; `1°`/`359°` promedian cerca de `0°` (no de `180°`); tres orientaciones (`0`, `pi/2`, `pi`) dan el resultado analítico exacto `atan2(1,0)=pi/2`; varias orientaciones iguales con `eta=0` se conservan; cruce adicional de `0/2*pi` con `350°`/`10°`. Todos estos casos comparan contra un valor esperado derivado de la ecuación (promedio vectorial con `atan2`), no contra la propia implementación.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: cubre el cálculo de la orientación nueva a partir de un estado viejo y listas de vecinos fijadas a mano en el test. La integración con el movimiento y la sincronía punto por punto sobre `x(t)` (paso temporal completo, "backward") se valida por separado en la sección 7, ahora ya implementada y cerrada.

## 6. Votante

- Con un único vecino externo y `eta=0`, debe copiarlo con probabilidad 1; nunca conservarse por autoelección.
- Aislada y `eta=0`: conserva ángulo.
- Aislada y `eta>0`: cambia solo por un ruido dentro de `[-eta/2,eta/2]`.
- Todas las direcciones producidas a `eta=0` deben pertenecer al conjunto de direcciones viejas.
- En sistema finito, `eta=0` debe poder alcanzar consenso polar; usar varias semillas y un horizonte largo como regresión, sin convertirlo en requisito temporal del barrido.

- [x] **Regla de votante (cálculo de orientación nueva).**
  - Implementación: `tp2::voter_update` en `src/core/rules.hpp`, validada en `tests/test_rules.cpp`, registrado en CTest como `rules`.
  - Evidencia: con un único vecino externo y `eta=0`, lo copia siempre (20 semillas); aislada y `eta=0`, conserva su orientación; aislada y `eta>0`, el cambio queda acotado a `<= eta/2` en distancia angular (50 semillas); con varios vecinos y `eta=0`, el resultado coincide exactamente con una orientación vieja de algún vecino (30 semillas); nunca se elige a sí misma porque `neighbors[i]` nunca contiene a `i` (garantizado por `neighbor_search.hpp`, reutilizado sin duplicar lógica).
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: cubre el cálculo de orientación con vecinos fijados a mano, y también (ver sección 7 más abajo) integrado en el paso temporal completo. El caso de "consenso polar en sistema finito con horizonte largo" se cubre por separado, como regresión diagnóstica, más abajo en esta misma sección.

### Regresión diagnóstica: consenso del votante sin ruido

- Herramienta: `tests/voter_consensus_regression.cpp`, compilada como el ejecutable `voter_consensus_regression` (`cmake --build build`). **No** está registrada con `add_test`: no tiene un assert rígido sobre alcanzar consenso (solo sobre invariantes que sí serían un bug real, ver más abajo), así que no corresponde volverla parte del pase/fallo automático de CTest, tal como pide la tarea que la introdujo. Se ejecuta explícitamente con `./build/voter_consensus_regression`.
- Escenario elegido (de las tres alternativas consideradas): sistema pequeño (`N=20`) con una búsqueda de vecinos **completa** controlada (cada partícula ve a todas las demás como vecinas, sin usar `rc` ni geometría) — la alternativa 1 de las sugeridas. Se descartó explícitamente la alternativa de usar los parámetros físicos del TP con un horizonte largo, porque mezclaría la propiedad de consenso de la regla de votante con la velocidad de difusión espacial (`v=0.03` sobre `L=10`), algo que el TP no pide afirmar. El grafo completo aísla la dinámica de la regla en sí, sin introducir una afirmación física sobre bandadas reales.
- Reutiliza el bucle de simulación existente (`tp2::run_simulation`), con `eta=0`, `InteractionRule::kVoter`, y **10 semillas explícitas** (`700001`-`700010`), cada una con su propio estado inicial aleatorio (posiciones y orientaciones uniformes), y un horizonte de **3000 pasos** por corrida (parámetros de esta regresión puntual, no un protocolo experimental final).
- Criterio de consenso: con `eta=0`, `voter_update` nunca crea una orientación nueva, solo copia una ya existente (de la propia partícula o de un vecino). Por lo tanto el conjunto de orientaciones distintas presentes en el sistema nunca puede crecer. Se define **consenso exacto** como que ese conjunto se haya reducido a un único valor bajo **igualdad exacta de punto flotante** (`==`, sin ninguna tolerancia). Esto es coherente con `eta=0`, no una aproximación: `sample_angular_noise` devuelve `0.0` exactamente sin perturbar la suma, y `normalize_angle` (`std::fmod`) es una operación exacta -- sin redondeo -- cuando el argumento ya está en `[0,2*pi)`, que es siempre el caso en esta corrida (el estado inicial ya sale normalizado del inicializador, y toda copia posterior preserva ese valor bit a bit). No hay entonces ninguna fuente de error numérico que una tolerancia debiera absorber. (Revisión de nomenclatura: la primera versión de esta herramienta usaba una tolerancia `1e-12` "por las dudas"; se reemplazó por igualdad exacta al confirmar que, con esta regla y `eta=0`, la comparación exacta es la correcta y no produce falsos negativos.) Esto es más fuerte y más verificable que pedir `va` cercano a 1: `va=1` puede acercarse por redondeo de punto flotante en la suma de senos/cosenos sin que las orientaciones sean exactamente iguales entre sí, mientras que "una única orientación distinta bajo igualdad exacta" es una propiedad exacta y discreta del propio proceso de copia. La herramienta también informa, por separado, la polarización `va` inicial y final de cada corrida, para distinguir explícitamente entre consenso exacto de orientaciones, polarización cercana a 1 y mera finalización de la corrida.
- **Resultado observado** (corrida ejecutada en esta tarea, `./build/voter_consensus_regression`): las **10 de 10** semillas alcanzaron consenso exacto, en un rango de **17 a 64 pasos** (muy por debajo del horizonte de 3000), con `va` inicial entre `0.089` y `0.334` y `va` final `1.000000` en todos los casos. No hubo ninguna semilla sin consenso en esta corrida, así que no aplicó la rama diagnóstica de "no fuerces un assert" (el programa la tiene implementada y documentada por si una corrida futura con otra configuración la necesita).
- La única verificación con `assert`/`abort` real de la herramienta es de sanidad, no de consenso: que `va` quede en `[0,1]` y que la cantidad de orientaciones distintas nunca aumente entre el estado inicial y el final. Una violación de eso sería un bug real (por ejemplo, la regla creando una orientación nueva), no una simple falta de horizonte.
- **Resultado observado vs. criterio de cierre**: este resultado es evidencia de regresión puntual sobre un escenario deliberadamente simplificado (grafo completo, `N=20`), no un requisito temporal del barrido ni una prueba sobre los parámetros físicos completos del TP (`rc=1`, `L=10`, `N=200/400/800`, movimiento real). No se marca ningún punto de "consenso del votante con los parámetros del TP" como cerrado a partir de esta corrida: ver el ítem correspondiente, todavía en `[ ]`, en "Evidencia requerida para cerrar" al final de este documento.
- Comando ejecutado: `cmake --build build && ./build/voter_consensus_regression` (por separado de `ctest`, que sigue en `100% tests passed, 0 tests failed out of 8` sin cambios).

Nota general para ambas reglas: se verificó además, como parte del mismo test, que ninguna de las dos modifica el vector de orientaciones viejo (`particles`), que el resultado siempre queda normalizado a `[0, 2*pi)`, que el ruido es reproducible con la misma semilla explícita y que semillas distintas pueden producir resultados distintos. También se agregó un caso adicional (invarianza al orden de almacenamiento) al detectar, durante la validación del paso temporal en la sección 7, que el diseño original del generador aleatorio no lo garantizaba (ver `02_motor_y_algoritmos.md`). Estos puntos no estaban en la lista original de "Promedio circular de Vicsek"/"Votante" del enunciado de esta etapa, pero son prerrequisitos directos de la sección 7 (sincronía) y de la sección 9 (reproducibilidad).

## 7. Sincronía y movimiento backward

Caso mínimo: una partícula en `(0,0)` con `theta_old=0` cuya interacción produce `theta_new=pi/2`, `v=0.03`, `dt=1`.

Resultado obligatorio:

```text
x_new=0.03, y_new=0, theta_new=pi/2
```

El resultado `(0,0.03)` prueba que se usó por error la orientación nueva.

Permutar el almacenamiento de partículas, conservar `id` y repetir un paso con el mismo `(seed,t)`. Al ordenar por `id`, posiciones y ángulos deben coincidir. Probar ambos modelos con ruido distinto de cero.

- [x] **Sincronía y movimiento backward.**
  - Implementación: `tp2::advance_time_step` en `src/core/time_step.hpp`, validada en `tests/test_time_step.cpp`, registrado en CTest como `time_step`.
  - Evidencia (13 casos): el caso mínimo obligatorio de esta sección se verifica exactamente como está escrito arriba (partícula en `(0,0)`, `theta_old=0`, votante sin ruido con un vecino a `pi/2`, `v=0.03`, `dt=1` → `x_new=0.03, y_new=0, theta_new=pi/2`, comprobando explícitamente que NO da `(0,0.03)`). Además: ecuación de movimiento exacta para una partícula aislada; repliegue periódico aplicado a la posición nueva; los vecinos se construyen con `x(t)` y no con la posición ya movida (caso adversarial donde recalcular con `x(t+1)` cambiaría el resultado); invarianza al orden de almacenamiento con la misma `(seed,t)` con `eta=0.4` (ruido distinto de cero) para Vicsek, y con `eta=0.5` para ambos modelos a nivel de `rules.hpp` (`test_rules.cpp`, caso 14); `advance_time_step` no modifica el estado de entrada; reproducibilidad con la misma semilla; semillas distintas pueden diferir; el paso da el mismo resultado con `brute_force_neighbors` o `cell_index_neighbors`; votante aislado conserva orientación y se mueve en consecuencia; Vicsek usa `theta_old` para moverse aunque `theta_new` sea muy distinto; los `id` se conservan; una cadena de dos pasos usa la posición actualizada del primer paso para calcular los vecinos del segundo.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Decisión de diseño registrada: el generador aleatorio de `vicsek_update`/`voter_update` se rediseñó durante esta tarea (de un `std::mt19937&` compartido y consumido en orden de índice, a un sub-generador derivado de `(seed, id)`) porque el diseño original no garantizaba la invarianza al orden de almacenamiento que pide este punto. Ver detalle en `02_motor_y_algoritmos.md`.
  - Alcance de este cierre: cubre el paso temporal completo (orientación + movimiento + borde periódico) para ambos modelos, con vecinos por fuerza bruta y por CIM. No incluye clusters, `va`/`S`, salida de texto ni CLI, que son puntos distintos de esta misma etapa y siguen pendientes.

## 8. Clusters

- Cadena `A-B-C` con `A` no vecina directa de `C`: `S=1` para tres partículas; prueba transitividad.
- Componentes de tamaños 3, 2 y 1: `S=3/6`.
- Partículas conectadas solo a través de borde periódico: misma componente.
- Todas aisladas: `S=1/N`.
- Todas conectadas: `S=1`.
- El algoritmo elegido (BFS/DFS o `union-find`) debe coincidir con casos de componentes construidos manualmente.

- [x] **Componente gigante `S`.**
  - Implementación: `tp2::largest_cluster_size`/`tp2::largest_cluster_fraction` en `src/core/observables.hpp` (union-find con compresión de camino y unión por rango), validadas en `tests/test_observables.cpp`, registrado en CTest como `observables`.
  - Evidencia (10 casos, todos con resultado esperado derivado a mano de la definición de componente conexa, no por comparación entre implementaciones): todas aisladas (`S=1/N`); todas conectadas, clique completo (`S=1`); cadena `A-B-C` con `A` y `C` no vecinas directas (`S=1`, prueba transitividad); componentes de tamaños 3, 2 y 1 (`S=3/6`); vecinos cruzando el borde periódico (`x=9.9`/`x=0.1`, vecinos por CIM, mismo cluster); mismo resultado con fuerza bruta y CIM sobre un estado aleatorio de `N=60`; `N=0` da tamaño 0 y `S=0` según la convención documentada; IDs no consecutivos (`7, 20, 99`); la lista de vecinos de entrada no se modifica; transitividad verificada explícitamente con una cadena `A-B-C-D` (cada partícula con a lo sumo 2 vecinos directos) que debe dar un único cluster de tamaño 4.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: cubre el cálculo de `S` sobre listas de vecinos ya calculadas (fuerza bruta o CIM) y fijadas a mano o generadas en el propio test. No incluye medir `S(t)` dentro de un bucle de simulación, la sincronía entre `S(t)` y el estado que se está midiendo (nota ya registrada en `02_motor_y_algoritmos.md`), ni el estudio de clusters con las densidades extendidas (`rho nominal = 1/pi, 1/(2pi), 1/(3pi)`), que dependen de piezas todavía no implementadas.

## 9. Bucle de simulación, semillas por paso y reproducibilidad en memoria

- Encadenar muchos pasos de `advance_time_step` manteniendo sincronía y movimiento backward en cada uno.
- Misma configuración y `base_seed`: la corrida completa en memoria (todos los estados intermedios y el final) debe ser idéntica.
- `base_seed` distinta: la corrida puede diferir (con `eta>0`).
- Dos pasos consecutivos de la misma corrida no deben repetir exactamente el mismo sorteo (semilla derivada de `(base_seed, step)`, no la misma semilla reutilizada en cada paso).
- Permutar el orden de almacenamiento de las partículas iniciales, con la misma `base_seed`, no debe cambiar el resultado por `id` después de varios pasos.
- El bucle debe funcionar igual con Vicsek y con votante, y con fuerza bruta y con CIM.

- [x] **Bucle de simulación (`run_simulation`) y semillas por paso.**
  - Implementación: `tp2::run_simulation` y `tp2::derive_step_seed` en `src/core/simulation.hpp`, validadas en `tests/test_simulation.cpp`, registrado en CTest como `simulation`.
  - Evidencia (10 casos): `steps=0` devuelve el estado inicial sin avanzar y el observador recibe solo `step=0`; `steps=1` coincide exactamente con una llamada directa a `advance_time_step` usando `derive_step_seed(base_seed, 1)`, para Vicsek y votante; varios pasos conservan tamaño, `id`, `x`/`y` en `[0,L)` y `theta` en `[0,2*pi)`; el observador recibe `steps+1` llamadas en orden, y el estado de cada `step=t` coincide con reconstruir la corrida a mano `t` veces (el estado inicial de entrada no se modifica); misma configuración y `base_seed` dan corridas bit a bit idénticas, y alguna de 39 `base_seed` distintas (con `eta>0`) produce una corrida distinta; en una partícula aislada con votante y `eta=0.6`, el incremento angular del paso 1 y el del paso 2 no coinciden exactamente (semillas de paso distintas); permutar 4 partículas iniciales y correr 5 pasos con la misma `base_seed` da, por `id`, el mismo resultado, para Vicsek y votante; la misma corrida con `brute_force_neighbors` y con `cell_index_neighbors` da el mismo estado final y los mismos estados observados en cada paso; una partícula aislada con `eta=0` conserva su orientación en todos los pasos y su posición sigue exactamente `x0 + v*cos(theta)*dt*step`; una cadena de dos pasos muestra que el paso 2 usa las posiciones actualizadas por el paso 1 (dos partículas que no son vecinas en el paso 1 pasan a serlo recién en el paso 2, tras haberse acercado).
  - Estrategia de semillas: `derive_step_seed(base_seed, step)` combina la semilla base y el número de paso; dentro de `advance_time_step`, esa `step_seed` se combina con el `id` de cada partícula (`make_particle_rng`, sin cambios en `rules.hpp`). El sorteo final depende de la terna completa `(base_seed, step, id)`, nunca de la posición de almacenamiento ni de una semilla repetida entre pasos. Detalle completo en `02_motor_y_algoritmos.md`, sección "Bucle de simulación".
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 8`.
  - Alcance de este cierre: cubre exclusivamente la reproducibilidad **en memoria** de la iteración (misma corrida, mismo `base_seed`, sin pasar por disco). No cubre la reproducibilidad de **archivos** (ver más abajo, todavía pendiente porque la escritura de texto no está implementada), ni corridas largas para observar consenso del votante o estacionariedad, ni realizaciones independientes ni barras de error.

### Reproducibilidad de archivos (pendiente)

- Misma configuración y semilla: archivos escalares idénticos.
- Semilla distinta: al menos la condición inicial o la dinámica difiere.
- La animación puede leer el formato de texto documentado sin llamar al motor.
- `va` y `S` rotulados con el mismo `t` pertenecen al mismo estado.
- Deshabilitar trayectoria no cambia la serie escalar.

Ninguno de estos puntos se puede validar todavía: dependen de la escritura de texto y del formato de salida, que siguen sin implementarse ni congelarse (ver `DECISIONES_PENDIENTES.md`).

## 10. Pruebas de humo físicas

No son asserts rígidos sobre una transición:

- Vicsek, bajo ruido: tendencia a aumentar polarización.
- Un caso de ruido alto elegido en el barrido debe diferenciarse del caso de ruido bajo.
- Densidad inicial alta: más vecinos medios que densidad baja.
- Votante sin ruido: coarsening/consenso eventual en corridas suficientemente largas.

Si una tendencia no aparece, investigar; no “arreglar” el test forzando un umbral arbitrario.

## Evidencia requerida para cerrar

- [x] Geometría periódica y `d=rc` correctos.
  - Evidencia: `tests/test_periodic_geometry.cpp` y `tests/test_neighbor_search_bruteforce.cpp` cubren `wrap`, distancia mínima en borde/esquina y los casos `d=rc` y `d>rc`.
- [x] CIM igual a fuerza bruta.
  - Evidencia: ver detalle y comando en la sección "2. CIM contra fuerza bruta" arriba.
- [x] Vecinos medios compatibles con teoría.
  - Evidencia: ver detalle y comando en la sección "3. Número medio inicial de vecinos" arriba (`tests/test_mean_neighbors.cpp`, 40 realizaciones por densidad, `rho=2,4,8`, tolerancia empírica del 5% y orden estricto `mean_k(2)<mean_k(4)<mean_k(8)`). Cubre solo la inicialización uniforme y el CIM; no el comportamiento dinámico.
- [x] `va` y `S` dentro de límites y casos manuales correctos.
  - Evidencia: ver detalle y comando en las secciones "4. Polarización" y "8. Clusters" arriba. Cubre el cálculo puntual de ambos observables sobre estados fijados a mano o aleatorios; no cubre medirlos dentro de un bucle de simulación en marcha (pendiente, ver alcance de cada sección).
- [x] Vicsek y votante satisfacen reglas distintas.
  - Evidencia: ver detalle y comando en las secciones "5. Promedio circular de Vicsek" y "6. Votante" arriba.
- [x] Movimiento backward demostrado.
  - Evidencia: ver detalle y comando en la sección "7. Sincronía y movimiento backward" arriba (caso mínimo obligatorio con resultado exacto `x_new=0.03, y_new=0, theta_new=pi/2`).
- [x] Invarianza al orden demostrada con ruido.
  - Evidencia: sección "7. Sincronía y movimiento backward" (permutación con `eta=0.4` en `test_time_step.cpp`), caso 14 de `test_rules.cpp` (permutación con `eta=0.5` para Vicsek y votante), y sección "9. Bucle de simulación..." (permutación de 4 partículas con `eta=0.4` a lo largo de 5 pasos encadenados, para Vicsek y votante).
- [x] Bucle de simulación e iteración en memoria reproducibles.
  - Evidencia: ver detalle y comando en la sección "9. Bucle de simulación, semillas por paso y reproducibilidad en memoria" arriba: misma configuración/`base_seed` da corridas idénticas, `base_seed` distinta puede diferir, semillas distintas entre pasos consecutivos, compatible con Vicsek/votante y fuerza bruta/CIM.
- [ ] Reproducibilidad y lectura independiente de la salida verificadas.
  - Nota: la reproducibilidad de la *iteración en memoria* (un paso o una corrida de muchos pasos, con la misma semilla) ya está demostrada (secciones 7 y 9). Lo que falta es específicamente la salida a disco (archivos de texto) y su lectura independiente por la animación, que dependen de la escritura de texto (todavía no implementada, ver `plan_desarrollo_tp2/02_motor_y_algoritmos.md` y `DECISIONES_PENDIENTES.md`).
- [ ] Corridas largas y consenso del votante sin ruido validados como regresión.
  - Nota: sigue en `[ ]` a propósito. Existe evidencia diagnóstica nueva (ver "Regresión diagnóstica: consenso del votante sin ruido" en la sección "6. Votante" arriba): 10/10 semillas alcanzaron consenso exacto en un escenario deliberadamente simplificado (grafo completo, `N=20`, `eta=0`, horizonte de 3000 pasos). Eso demuestra que la regla de votante en sí converge, pero **no** es todavía la validación de "corridas largas" que pide este ítem general de la etapa: falta repetir el control con los parámetros físicos completos del TP (`rc=1`, `L=10`, `N=200/400/800`, movimiento real con `v=0.03`, búsqueda de vecinos geométrica), donde la conectividad espacial sí puede volverse un factor limitante y el horizonte necesario puede ser mucho mayor. No se marca este punto como cerrado hasta tener esa evidencia.

Al completar esta lista queda habilitada la etapa de pilotos, no todavía la producción definitiva.
