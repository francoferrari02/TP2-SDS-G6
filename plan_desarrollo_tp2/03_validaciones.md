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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
  - Alcance de este cierre: solo cubre la comparación de listas de vecinos entre CIM y fuerza bruta pedida por este punto. No incluye la integración del CIM con `union-find`/clusters (todavía no implementada, ver `02_motor_y_algoritmos.md`), que es un punto distinto del criterio de cierre general de la etapa.

## 3. Número medio inicial de vecinos

Promediar muchas inicializaciones uniformes. Para las densidades base, el número medio de otros vecinos debe aproximar:

| rho | valor asintótico `rho*pi*rc^2` |
|---:|---:|
| 2 | 6.283 |
| 4 | 12.566 |
| 8 | 25.133 |

No exigir igualdad exacta a una sola inicialización: la guía pide verificar que el promedio de varias condiciones iniciales se aproxime a esos valores.

## 4. Polarización

- Todas las orientaciones iguales: `va=1` dentro de tolerancia numérica.
- Pares opuestos balanceados: `va=0` dentro de tolerancia.
- Para estados aleatorios: `0 <= va <= 1`.

- [x] **Polarización `va`.**
  - Implementación: `tp2::polarization` en `src/core/observables.hpp`, validada en `tests/test_observables.cpp`, registrado en CTest como `observables`.
  - Evidencia (8 casos, todos con resultado esperado derivado de la definición, no de la propia implementación): una sola partícula (`va=1`); todas las orientaciones iguales, 4 partículas (`va=1`); dos orientaciones opuestas `0`/`pi` (`va=0`); cuatro direcciones balanceadas `0, pi/2, pi, 3*pi/2` (`va=0`); resultado analítico exacto para `theta=0` y `pi/2` (`va=sqrt(2)/2`); estado aleatorio de 100 partículas con `0<=va<=1`; el cálculo no modifica `particles`; `N=0` da `va=0` según la convención documentada en el header.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
  - Alcance de este cierre: cubre el cálculo de `va` sobre un estado fijado a mano o generado aleatoriamente en el propio test. No incluye medir `va(t)` dentro de un bucle de simulación, ni promedios entre realizaciones ni la elección de `t_eq`, que dependen de piezas todavía no implementadas.

## 5. Promedio circular de Vicsek

- Dos ángulos `1 grado` y `359 grados` deben promediar cerca de `0`, no de `180`.
- Una partícula aislada con `eta=0` conserva su ángulo porque el promedio incluye a sí misma.
- Construcción manual de tres partículas con resultado analítico conocido.

- [x] **Regla de Vicsek (cálculo de orientación nueva).**
  - Implementación: `tp2::vicsek_update` en `src/core/rules.hpp`, validada en `tests/test_rules.cpp`, registrado en CTest como `rules`.
  - Evidencia: partícula aislada con `eta=0` conserva su orientación; `1°`/`359°` promedian cerca de `0°` (no de `180°`); tres orientaciones (`0`, `pi/2`, `pi`) dan el resultado analítico exacto `atan2(1,0)=pi/2`; varias orientaciones iguales con `eta=0` se conservan; cruce adicional de `0/2*pi` con `350°`/`10°`. Todos estos casos comparan contra un valor esperado derivado de la ecuación (promedio vectorial con `atan2`), no contra la propia implementación.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
  - Alcance de este cierre: cubre el cálculo de orientación con vecinos fijados a mano, y también (ver sección 7 más abajo) integrado en el paso temporal completo. El caso de "consenso polar en sistema finito con horizonte largo" sigue pendiente porque requiere iterar muchos pasos y varias semillas como regresión, algo que no corresponde a esta tarea de validación puntual.

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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 7`.
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
- [ ] Vecinos medios compatibles con teoría.
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
  - Nota: sigue pendiente (ver sección "6. Votante" arriba); requiere iterar muchos pasos con varias semillas, algo que ahora ya es posible ejecutar con `run_simulation`, pero que todavía no se corrió ni se validó como caso de regresión en esta tarea.

Al completar esta lista queda habilitada la etapa de pilotos, no todavía la producción definitiva.
