# Etapa 2 - Motor, búsqueda de vecinos y clusters

## Objetivo

Implementar un motor correcto y reutilizable. La optimización se apoya en un oráculo de fuerza bruta para tests; nunca se optimiza una regla no validada.

## Orden recomendado de implementación

1. Tipos, parámetros y estado.
2. Geometría periódica.
3. Búsqueda de vecinos por fuerza bruta como referencia.
4. Cell Index Method (CIM).
5. Regla Vicsek.
6. Regla votante.
7. Paso sincrónico/backward.
8. Polarización.
9. Componente gigante.
10. Bucle de simulación (encadenar pasos, semillas por paso).
11. Escritura de texto y CLI.

### Estado de implementación

- [x] Tipos, parámetros y estado base en `src/core/model.hpp`.
  - Evidencia: el test geométrico compila y enlaza contra la interfaz `tp2_core`.
- [x] Geometría periódica inicial en `src/core/periodic_geometry.hpp`.
  - Evidencia: `ctest --test-dir build --output-on-failure` verifica `wrap`, distancia mínima en borde y esquina, y los casos `d=rc` y `d>rc`.
- [ ] Búsqueda de vecinos, reglas, actualización, observables, salida y CLI.
  - Estado: en progreso. Se implementaron la búsqueda de vecinos por fuerza bruta (`brute_force_neighbors`) y el Cell Index Method (`cell_index_neighbors`), las reglas de orientación de Vicsek y votante (`src/core/rules.hpp`), el paso temporal sincrónico/backward completo (`src/core/time_step.hpp`, `advance_time_step`, ver sección "Paso sincrónico/backward" más abajo), los observables `va`/`S` (`src/core/observables.hpp`, ver sección "Observables: polarización y componente gigante" más abajo) y el bucle de simulación (`src/core/simulation.hpp`, `run_simulation`, ver sección "Bucle de simulación" más abajo). Faltan la escritura de texto y la CLI.

#### Búsqueda de vecinos por fuerza bruta (oráculo de referencia)

- Implementación: `src/core/neighbor_search.hpp`, función `brute_force_neighbors(particles, parameters)`.
- Complejidad `O(N^2)`: recorre todos los pares `(i,j)` con `i<j`, calcula `distance_squared_periodic` (sin `sqrt`) y agrega la arista a ambas listas si `d2 <= rc^2` (borde inclusive).
- Devuelve, para cada partícula (indexada por posición en el vector de entrada), la lista de `id` estables de sus vecinos externos, ordenada ascendentemente. No incluye a la propia partícula. Las listas son simétricas y sin duplicados por construcción (cada par se visita una sola vez).
- Es exclusivamente un oráculo de test: no es el motor productivo. El CIM implementado en esta etapa debe coincidir exactamente con este resultado (`sorted(neighbors_CIM[i]) == sorted(neighbors_bruteforce[i])`, según pide `03_validaciones.md`).
- Supuestos documentados en el propio header: los `id` de entrada deben ser únicos; el resultado se indexa por posición de vector pero los valores son `id`. Para comparar entradas con distinto orden hay que asociar cada lista con el ID de su partícula.
- Evidencia: `tests/test_neighbor_search_bruteforce.cpp`, registrado en CTest como `neighbor_search_bruteforce`. Cubre: par separado por menos de `rc`, par separado exactamente por `rc` (borde inclusive), par separado por más de `rc`, par vecino cruzando el borde periódico (eje x), par no vecino, simetría con varias partículas, ausencia de auto-vecindad, ausencia de duplicados, comparación contra una construcción manual (cadena A-B-C más D aislada) y par vecino cruzando una esquina periódica. Se agregó además un test de determinismo (misma entrada, mismo resultado en dos llamadas).
- Comando: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` — los tests de geometría, fuerza bruta y CIM pasan.

## Cell Index Method

Reutilizar el criterio válido del CIM desarrollado en TP1: la longitud de celda y la cantidad de celdas vecinas inspeccionadas deben garantizar que ningún par con `d <= rc` quede afuera. La cátedra no fija un valor de `M`; se elige, documenta y valida contra una referencia pequeña.

Procedimiento:

1. Vaciar y reconstruir las celdas desde `x(t)`.
2. Recorrer pares de celdas sin duplicar combinaciones.
3. Para cada par candidato, evaluar distancia mínima periódica.
4. Si `d2 <= rc^2`, agregar la arista a ambas listas y ejecutar `union(i,j)`.

Requisitos:

- No duplicar vecinos.
- No incluir `i` en la lista externa.
- Mantener simetría: `j in N_i` si y solo si `i in N_j`.
- Evitar `sqrt`: comparar distancias al cuadrado.

### Estado de implementación del CIM

- [x] `cell_index_neighbors(particles, parameters)` implementado en `src/core/neighbor_search.hpp`, junto a `brute_force_neighbors` (sin modificar el oráculo existente).
- [x] Integración con `union-find` para clusters: `largest_cluster_size`/`largest_cluster_fraction` (`src/core/observables.hpp`) consumen sin cambios las listas de vecinos devueltas por `cell_index_neighbors` (o por `brute_force_neighbors`); ver sección "Observables: polarización y componente gigante" más abajo.

#### Diseño de la grilla de celdas

- Número de celdas por lado: `M = floor(L / rc)`, con mínimo 1. Con los parámetros vinculantes del TP (`L=10`, `rc=1`) queda `M=10` y tamaño de celda `cell_size = L/M = 1.0`. La función es igualmente válida para otros `L`/`rc` usados en tests pequeños (por ejemplo sistemas con pocas partículas donde `M` puede colapsar a 1 o 2).
- Cota de corrección: por construcción `cell_size = L/M >= rc`. Esa cota es la que garantiza que ningún par con `d <= rc` pueda quedar fuera de la vecindad de 3x3 celdas (incluida la celda propia): si dos celdas distan 2 o más pasos en algún eje, la separación mínima posible entre cualquier par de partículas que contengan es `>= cell_size >= rc`, por lo que nunca pueden ser vecinas y no hace falta inspeccionarlas.
- Asignación partícula→celda: se repliega la coordenada con `periodic_wrap` (la misma función que usa la geometría periódica) y se toma `floor(coordenada / cell_size)`, recortado a `[0, M-1]` como salvaguarda ante redondeo de punto flotante en el borde exacto.

#### Tratamiento del borde periódico

- La periodicidad se aplica dos veces, de forma independiente: (1) al asignar partículas a celdas, replegando la coordenada antes de dividir por `cell_size`; (2) al recorrer las celdas vecinas, replegando el índice de celda módulo `M` (`(cx + delta) mod M`, con corrección de signo). Así una partícula cerca de `x=0` sí revisa la celda de `x` cercano a `L`, y viceversa.
- Para evitar procesar el mismo par de celdas dos veces (lo que produciría vecinos duplicados) o dejar pares sin procesar, cada celda solo mira los vecinos cuyo índice lineal es `>= ` el propio, y deduplica índices de celda repetidos con un `unordered_set`. Esta deduplicación es necesaria porque con `M<=2` un mismo vecino puede alcanzarse por más de un desplazamiento `{-1,0,1}` (p. ej. `M=2`: `-1` y `+1` módulo 2 dan la misma celda). La distancia final siempre se calcula con `distance_squared_periodic` (mínima imagen), así que el resultado de vecindad no depende de por qué desplazamiento se llegó a la celda.
- Dentro de la celda consigo misma se comparan todos los pares `a<b` de su bucket; entre dos celdas distintas se comparan todos los pares producto. El criterio de vecindad es idéntico al del oráculo: `distance_squared_periodic(...) <= rc^2`, sin `sqrt`, borde inclusive.

#### Complejidad esperada

- Con partículas distribuidas aproximadamente uniformes, el número esperado de partículas por celda es `rho * cell_size^2`, una constante independiente de `N` para parámetros fijos (para el TP, con `cell_size=1`, es directamente `rho`). Eso deja el costo total esperado en `O(N)`, frente al `O(N^2)` de la fuerza bruta.
- Peor caso: si todas las partículas caen en una única celda (grilla degenerada o `M=1`), el CIM recorre todos los pares igual que la fuerza bruta, es decir `O(N^2)`. Esto es aceptable porque el CIM es correcto en todos los casos, solo deja de ser más rápido que la fuerza bruta en esa situación degenerada.

#### Evidencia de los tests

- Implementación de test: `tests/test_neighbor_search_cim.cpp`, registrado en CTest como `neighbor_search_cim`.
- Casos cubiertos (comparando siempre `cell_index_neighbors` contra `brute_force_neighbors` sobre las mismas partículas, con una función de comparación que falla imprimiendo el `id` de la partícula, la posición en el vector de entrada y las listas completas de vecinos de ambos métodos si difieren, en vez de solo comparar tamaños):
  1. Muchos estados pequeños (`N=12`) con 30 semillas fijas distintas.
  2. Estados aleatorios uniformes de tamaño moderado (`N=120`) con 6 semillas.
  3. Partículas cruzando el borde periódico en `x`.
  4. Partículas cruzando el borde periódico en `y`.
  5. Partículas cruzando una esquina periódica.
  6. Pares separados exactamente por `rc` (varios ejes y ubicaciones, incluido cerca del origen de celdas).
  7. Pares separados apenas fuera de `rc` (`rc + 1e-9`).
  8. Varias partículas dentro de la misma celda (`cell_size=1`).
  9. Partículas repartidas en celdas vecinas (horizontal, vertical y diagonal).
  10. Partículas en celdas alejadas: se verifica explícitamente que el CIM no produce ningún vecino, además de coincidir con la fuerza bruta.
  11. Simetría, ausencia de auto-vecinos y ausencia de duplicados evaluadas directamente sobre la salida del CIM (no solo por comparación con el oráculo), con `N=60` partículas aleatorias.
  12. Independencia del orden de almacenamiento: se calcula el CIM y la fuerza bruta con las partículas en un orden, se permutan (orden inverso + rotación) y se vuelve a calcular; se verifica que la lista de vecinos asociada a cada `id` es idéntica en ambos órdenes, y que CIM y fuerza bruta siguen coincidiendo tras la permutación.
  13. Varios tamaños de sistema, incluidos casos degenerados: `N ∈ {0,1,2,3,5,8,13,21,50}`, con 3 semillas cada uno.
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los tres tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`) pasan.

## Reglas de orientación

Implementadas en `src/core/rules.hpp`, junto a `vicsek_update` y `voter_update`. Alcance de esta sección: solo el cálculo de la orientación nueva a partir del estado viejo y de las listas de vecinos externos ya calculadas por `neighbor_search.hpp` (fuerza bruta o CIM). El paso temporal completo (movimiento `x(t+1)`, `y(t+1)`, intercambio de buffers) que combina estas reglas con el movimiento está en `src/core/time_step.hpp` (ver sección "Paso sincrónico/backward" más abajo); acá no se documenta movimiento, clusters ni observables.

### Interfaz implementada

- `normalize_angle(theta)`: normaliza cualquier ángulo a `[0, 2*pi)`. Es la función común de normalización que usan ambas reglas al final.
- `sample_angular_noise(rng, eta)`: helper común de ruido, `xi ~ U[-eta/2, eta/2]`, implementado con `std::uniform_real_distribution` sobre un `std::mt19937&` recibido por referencia. Con `eta <= 0` devuelve `0.0` exactamente sin consumir el generador, para que los tests con `eta=0` sean deterministas independientemente de la semilla.
- `make_particle_rng(seed, id)`: deriva un `std::mt19937` local a partir de una semilla explícita y el `id` de una partícula (ver "Generador aleatorio y orden de almacenamiento" más abajo).
- `vicsek_update(particles, neighbors, eta, seed) -> std::vector<double>`
- `voter_update(particles, neighbors, eta, seed) -> std::vector<double>`

Ambas funciones reciben:

- `particles`: el vector de partículas viejo (`Particle::theta` es la orientación vieja); no se modifica.
- `neighbors`: las listas de `id` de vecinos externos por posición, con el mismo formato de salida que `brute_force_neighbors`/`cell_index_neighbors` (no se recalcula periodicidad ni vecindad acá).
- `eta`: ancho del ruido.
- `seed`: semilla explícita `std::uint64_t` (nunca sembrada con el reloj), creada y controlada por quien llama; cada partícula deriva de ella su propio sub-generador combinado con su `id` (ver más abajo).

Devuelven un `std::vector<double>` nuevo, indexado por posición igual que `particles`, con las orientaciones nuevas ya normalizadas a `[0, 2*pi)`. Ninguna de las dos funciones escribe sobre `particles`, y ninguna lee del vector de salida: ambas calculan `new_theta[i]` exclusivamente a partir de `particles` (estado viejo), lo que hace la actualización compatible con sincronía (todas las partículas se pueden actualizar "a la vez" porque ninguna depende de una orientación ya actualizada de otra).

### Diferencia exacta entre Vicsek y votante

- **Vicsek** (`vicsek_update`): promedia vectorialmente la orientación propia y la de todos los vecinos externos, incluyendo siempre a la propia partícula en la suma:

  ```text
  theta_base = atan2(sum(sin(theta_j)), sum(cos(theta_j)))   // j recorre {i} U vecinos(i)
  theta_new[i] = normalize(theta_base + xi)
  ```

  Nunca promedia ángulos directamente (`(a+b)/2`), porque eso da resultados incorrectos al cruzar `0/2*pi` (por ejemplo `1°` y `359°` promediarían mal a `180°` en vez de a `0°`). Usa `atan2(sum_sin, sum_cos)`, que es el promedio circular correcto.

- **Votante** (`voter_update`): si `neighbors[i]` no está vacío, elige exactamente un vecino al azar con `std::uniform_int_distribution` sobre el sub-generador propio de la partícula y copia literalmente su orientación vieja (no promedia nada); nunca puede elegirse a sí misma porque `neighbors[i]` nunca contiene a `i` (ya garantizado por `neighbor_search.hpp`). Si `neighbors[i]` está vacío, conserva su propia orientación vieja. En ambos casos:

  ```text
  theta_new[i] = normalize(base_theta + xi)
  ```

  Con `eta=0`, `theta_new[i]` es siempre igual a una orientación que ya existía en el estado viejo (la propia o la de un vecino), nunca un valor intermedio.

### Manejo del ruido

- Convención de cátedra: `xi ~ U[-eta/2, eta/2]`, en radianes, sumado *después* de calcular la orientación base (el promedio vectorial en Vicsek, la copia en votante).
- El ruido se genera con `sample_angular_noise`, una única función usada por ambas reglas, para no duplicar la lógica de la distribución.
- La normalización final (`normalize_angle`) se aplica siempre, tanto en Vicsek como en votante, así que el resultado de ambas reglas siempre queda en `[0, 2*pi)` independientemente de la orientación de entrada o del signo del ruido.

#### Generador aleatorio y orden de almacenamiento (decisión revisada)

La primera versión de `vicsek_update`/`voter_update` recibía un único `std::mt19937&` compartido y lo consumía secuencialmente en el orden en que las partículas aparecían en el vector de entrada. Al implementar el paso temporal completo (`time_step.hpp`) y agregar el test de invarianza al orden de almacenamiento, ese diseño falló exactamente el riesgo que ya estaba anotado en este documento ("Consumir RNG en orden de almacenamiento y romper la prueba de permutación"): con la misma semilla pero las partículas guardadas en otro orden, el `id` `k` consumía un sorteo distinto del generador compartido (el que le tocaba según su nueva posición, no según su identidad), y terminaba con una orientación nueva distinta.

La corrección fue cambiar la firma de ambas funciones: en vez de recibir `std::mt19937&`, reciben una semilla explícita `std::uint64_t seed` (sigue sin sembrarse con el reloj, la sigue controlando quien llama). Internamente, cada partícula deriva su propio sub-generador con `make_particle_rng(seed, particles[i].id)`, que combina la semilla y el `id` con un mezclado determinista (variante del finalizador de MurmurHash3/splitmix64) antes de sembrar un `std::mt19937` local. Tanto la elección de vecino en votante como el ruido de cada partícula salen de ese sub-generador propio de su `id`.

**Pendiente para la iteración temporal:** como el paso actual no recibe el número de paso, el llamador debe variar la semilla entre pasos (por ejemplo, derivándola de `(seed_base, t)`) antes de ejecutar una corrida larga. Reutilizar exactamente la misma semilla en cada llamada repetiría los sorteos de cada partícula; esto debe resolverse al implementar el bucle de simulación y la CLI.

Con este diseño, la orientación nueva de la partícula `id=k` depende únicamente de `seed`, `k`, su propio `theta` viejo y el de sus vecinos (identificados también por `id`) — nunca de en qué posición del vector quedó almacenada. Eso garantiza por construcción, y no solo empíricamente, que permutar el orden de almacenamiento con la misma `(seed, t)` da el mismo resultado por `id`. Sigue cumpliendo los dos requisitos originales: misma semilla reproduce exactamente el mismo resultado, y una semilla distinta puede dar un resultado distinto.

### Evidencia de los tests

- Implementación de test: `tests/test_rules.cpp`, registrado en CTest como `rules`.
- Casos cubiertos (14: los 13 originalmente pedidos más uno agregado al corregir el diseño del generador aleatorio, ver más abajo):
  1. Vicsek con una partícula aislada y `eta=0`: conserva su orientación.
  2. Vicsek con `1°` y `359°`: el promedio da cerca de `0°`, no de `180°`.
  3. Vicsek con tres orientaciones (`0`, `pi/2`, `pi`) y resultado analítico exacto (`atan2(1,0) = pi/2`).
  4. Vicsek con varias orientaciones iguales y `eta=0`: conserva esa orientación.
  5. Votante con un único vecino externo y `eta=0`: lo copia siempre (probado con 20 semillas distintas).
  6. Votante aislado y `eta=0`: conserva su orientación.
  7. Votante aislado y `eta>0`: el cambio queda acotado a `<= eta/2` en distancia angular (probado con 50 semillas).
  8. Votante con varios vecinos y `eta=0`: el resultado coincide exactamente con una de las orientaciones viejas de los vecinos (probado con 30 semillas).
  9. Ninguna de las dos reglas modifica el vector `particles` de entrada (se compara contra una copia guardada antes de llamar).
  10. El resultado de ambas reglas queda siempre en `[0, 2*pi)`, incluso partiendo de ángulos negativos o mayores a `2*pi`.
  11. Reproducibilidad: dos llamadas con la misma semilla (`seed` explícita) dan resultados idénticos, en ambas reglas.
  12. Semillas distintas pueden dar resultados distintos: se prueban 40 semillas y se verifica que al menos una difiere del resultado con semilla base, en ambas reglas.
  13. Promedio vectorial de Vicsek al cruzar `0/2*pi` con otro par de ángulos (`350°` y `10°`), da cerca de `0°`.
  14. Invarianza al orden de almacenamiento: con la misma `seed`, permutar el vector de partículas (y las listas de vecinos correspondientes, siempre expresadas en `id`) da, para cada `id`, exactamente la misma orientación nueva en ambas reglas. Este caso se agregó durante la tarea del paso temporal (ver más abajo), al detectar con el test de `time_step` que el diseño original (un único `std::mt19937&` compartido, consumido en orden de índice de vector) no lo garantizaba.
- La función auxiliar `angular_distance` mide distancia angular mínima (en `[0,pi]`) para comparar orientaciones sin ambigüedad de wraparound, y las comparaciones de rango usan desigualdades con tolerancia numérica (`1e-6`/`1e-9`), nunca igualdad exacta de números de punto flotante salvo cuando la semilla y la distribución están completamente controladas (por ejemplo `eta=0`, o comparación de dos corridas con la misma semilla).
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los ocho tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, `observables`, `simulation`, `mean_neighbors`) pasan.

## Paso sincrónico/backward

Implementado en `src/core/time_step.hpp`, función `advance_time_step`. Combina la búsqueda de vecinos (`neighbor_search.hpp`) y las reglas de orientación (`rules.hpp`) sin duplicar ninguna de las dos: solo las ordena en la secuencia exacta que exige la sincronía. Alcance: únicamente el paso temporal (orientación + movimiento + repliegue periódico). No incluye clusters, `va`/`S`, salida de texto ni CLI.

### Interfaz implementada

```cpp
enum class InteractionRule { kVicsek, kVoter };

using NeighborSearchFunction = std::function<std::vector<std::vector<std::size_t>>(
    const std::vector<Particle>&, const Parameters&)>;

std::vector<Particle> advance_time_step(
    const std::vector<Particle>& particles, const Parameters& parameters,
    double eta, InteractionRule rule, std::uint64_t seed,
    const NeighborSearchFunction& neighbor_search);
```

`neighbor_search` se recibe como parámetro (no se fija una sola implementación) para poder ejecutar y validar el mismo paso temporal tanto con `brute_force_neighbors` como con `cell_index_neighbors`, sin duplicar la lógica del paso. `particles` es el estado viejo y no se modifica; la función devuelve un `std::vector<Particle>` nuevo y completo. Quien llama reemplaza el estado con una asignación (`particles = advance_time_step(particles, ...)`), que es el único punto donde `x(t)`/`theta(t)` pasan a ser `x(t+1)`/`theta(t+1)`.

### Orden de ejecución (exactamente como lo pide la especificación)

1. **Vecinos desde `x(t)`**: `neighbor_search(particles, parameters)` se llama primero, sobre el `particles` de entrada, antes de calcular nada nuevo.
2. **Orientación nueva desde `theta(t)` solamente**: se delega en `vicsek_update`/`voter_update`, que ya leen únicamente `particles` (estado viejo) y no el resultado de ningún otro paso.
3. **Posición nueva con `theta(t)`, no `theta(t+1)`**: el movimiento usa `particles[i].theta` (la orientación vieja) para cada partícula, nunca el valor recién calculado en el paso 2:

   ```text
   x_new = x(t) + v * cos(theta(t)) * dt
   y_new = y(t) + v * sin(theta(t)) * dt
   ```

   Esto es lo que la guía llama movimiento "backward": la orientación nueva queda calculada y disponible, pero recién actúa sobre el movimiento del paso siguiente.
4. **Borde periódico sobre las posiciones nuevas**: `periodic_wrap` se aplica a `x_new`/`y_new` antes de guardarlas.
5. **Reemplazo del estado completo al final**: el estado nuevo se arma en un `std::vector<Particle>` separado (`next_state`); nada del vector de entrada se sobrescribe en ningún punto intermedio. La sustitución ocurre en un único lugar, al devolver `next_state` (y, del lado de quien llama, al asignarlo sobre la variable que representa el estado).

### Evidencia de los tests

- Implementación de test: `tests/test_time_step.cpp`, registrado en CTest como `time_step`.
- Casos cubiertos (13):
  1. Caso mínimo de la sección 7 de `03_validaciones.md`: partícula en `(0,0)`, `theta_old=0`, un vecino fuerza `theta_new=pi/2` (votante, `eta=0`). Con `v=0.03,dt=1` el resultado obligatorio es `x_new=0.03, y_new=0, theta_new=pi/2`; se verifica explícitamente que NO da `(0, 0.03)` (el bug de usar `theta_new` en el movimiento).
  2. Ecuación de movimiento exacta para una partícula aislada: `x_new`/`y_new` coinciden con `x + v*cos(theta)*dt` / `y + v*sin(theta)*dt`.
  3. El borde periódico se aplica a la posición nueva (partícula que cruza `x=L` reaparece en `x=0.02`).
  4. Los vecinos se construyen con `x(t)`: un par separado `1.02` (fuera de `rc=1`) que, si se recalculara con las posiciones nuevas dentro del mismo paso, pasaría a estar a `0.99` (adentro de `rc`); se verifica que ninguna ve a la otra como vecina en este paso.
  5. Invarianza al orden de almacenamiento con la misma `(seed,t)`: se permutan las partículas y se repite el paso; identificando por `id`, posiciones y ángulos coinciden.
  6. `advance_time_step` no modifica el vector de entrada.
  7. Reproducibilidad: misma `seed` da exactamente el mismo estado nuevo.
  8. Semillas distintas pueden dar resultados distintos (con ruido).
  9. El paso da el mismo resultado usando `brute_force_neighbors` o `cell_index_neighbors` como función de búsqueda de vecinos (ambas ya validadas como equivalentes en la etapa anterior).
  10. Votante aislado con `eta=0`: conserva orientación y se mueve según esa orientación conservada.
  11. Vicsek: aunque `theta_new` sea muy distinto de `theta_old`, el movimiento de ese mismo paso usa `theta_old`.
  12. Los `id` se conservan en el estado nuevo, en la misma posición del vector de entrada.
  13. Cadena de dos pasos: se verifica que el segundo paso construye sus vecinos a partir de la posición resultante del primer paso (no de la posición original), moviendo dos partículas hasta quedar vecinas recién después del primer paso.
- Al escribir el test 5 con el generador original (`std::mt19937&` compartido) se detectó que el resultado sí dependía del orden de almacenamiento, contradiciendo el requisito de sincronía/permutación de `03_validaciones.md` sección 7. Esto llevó a rediseñar `vicsek_update`/`voter_update` para derivar un sub-generador por `id` (ver `02_motor_y_algoritmos.md`, sección "Generador aleatorio y orden de almacenamiento" dentro de "Reglas de orientación", y el caso 14 agregado a `test_rules.cpp`).
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los ocho tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, `observables`, `simulation`, `mean_neighbors`) pasan.

## Observables: polarización y componente gigante

Implementados en `src/core/observables.hpp`: `polarization(particles)`, `largest_cluster_size(neighbors, particles)` y `largest_cluster_fraction(neighbors, particles)`. Alcance de esta sección: únicamente el cálculo de estos dos observables sobre un estado ya dado (`particles` + `neighbors`); no incluye el bucle de simulación, la elección de `t_eq`, promedios entre realizaciones, semillas por paso, salida de texto ni CLI.

### Interfaz implementada

```cpp
double polarization(const std::vector<Particle>& particles);

std::size_t largest_cluster_size(
    const std::vector<std::vector<std::size_t>>& neighbors,
    const std::vector<Particle>& particles);

double largest_cluster_fraction(
    const std::vector<std::vector<std::size_t>>& neighbors,
    const std::vector<Particle>& particles);
```

Ninguna de las tres funciones modifica `particles` ni `neighbors`; ambas reciben el estado por `const&` y solo leen.

### Polarización

```text
va = hypot(sum cos(theta_i), sum sin(theta_i)) / N
```

- No usa la velocidad: como todos los módulos valen `v` (constante del TP), dividir por `v` sería redundante y solo agregaría error numérico; `va` se define directamente a partir de las orientaciones.
- No promedia ángulos directamente; usa `std::hypot(sum_cos, sum_sin)` (equivalente a `sqrt(sum_cos^2 + sum_sin^2)` pero numéricamente más estable) sobre la suma de `cos`/`sin`, análogo al promedio circular ya usado en `vicsek_update`.
- **Convención para `N=0`**: se documenta en el propio header y se devuelve `0.0` (no hay bandada que alinear; evita dividir por cero).
- Resultado esperado en `[0,1]` salvo error numérico de punto flotante despreciable (no se recorta el valor artificialmente).

### Componente gigante (`S`)

Un cluster es una componente conexa de la red de vecinos: si `i` es vecino de `j` hay una arista entre ambos, y la conectividad es transitiva (si `A`-`B` y `B`-`C` son aristas, `A`, `B` y `C` están en el mismo cluster aunque `A` y `C` no sean vecinos directos). `neighbors` debe venir ya calculado con el criterio periódico `d <= rc` (de `brute_force_neighbors` o `cell_index_neighbors`); `largest_cluster_size`/`largest_cluster_fraction` no recalculan ninguna distancia, solo recorren las aristas que reciben.

```text
n_max = tamaño de la componente más grande
S = n_max/N
```

**Algoritmo elegido: Union-Find (Disjoint Set Union)**, con compresión de camino y unión por rango, en `tp2::detail::DisjointSet` (privado del header, no expuesto en la interfaz pública). Se eligió por sobre BFS/DFS porque la entrada ya llega como una lista de aristas (cada partícula con sus vecinos) en vez de como un grafo pensado para recorrer nodo por nodo con una pila/cola explícita: con DSU cada arista `(i,j)` se procesa una única vez con `unite(i,j)`, en `O(alpha(N))` amortizado por operación, sin estructuras auxiliares de recorrido. Al final se cuenta el tamaño de cada componente (`find(i)` por cada partícula, acumulado en un mapa `raíz -> tamaño`) y se toma el máximo.

**Tratamiento de IDs**: igual que en `rules.hpp`, `neighbors[i]` contiene `id` de vecinos, no índices de vector, y los `id` no tienen por qué ser consecutivos ni coincidir con la posición de almacenamiento (se probó explícitamente con `id in {7, 20, 99}`). Antes de unir componentes se construye un mapa `id -> índice` (`std::unordered_map`) recorriendo `particles` una vez, igual que hace `vicsek_update`/`voter_update`, así que `largest_cluster_size` nunca asume `id == índice`.

**Convención para `N=0`**: se documenta en el header y se devuelve `largest_cluster_size = 0` / `largest_cluster_fraction = 0.0` (no hay partículas, no hay cluster).

El mismo algoritmo se ejecuta sin cambios sobre vecinos generados por `brute_force_neighbors` o por `cell_index_neighbors`; como ambas ya están validadas como equivalentes (etapa 2, sección CIM), el tamaño del cluster más grande también coincide entre ambas (verificado por test, ver más abajo).

### Evidencia de los tests

- Implementación de test: `tests/test_observables.cpp`, registrado en CTest como `observables`.
- Casos de polarización cubiertos (8):
  1. Una sola partícula: `va=1`.
  2. Todas las orientaciones iguales (4 partículas): `va=1`.
  3. Dos partículas con orientaciones opuestas (`0` y `pi`): `va=0`.
  4. Cuatro direcciones balanceadas (`0, pi/2, pi, 3*pi/2`): `va=0`.
  5. Resultado analítico conocido: `theta = 0` y `pi/2` en dos partículas da `va = sqrt(2)/2` exacto.
  6. Estado aleatorio de 100 partículas: `va` queda en `[0,1]`.
  7. El cálculo no modifica `x`, `y` ni `theta` de las partículas de entrada.
  8. `N=0`: `va=0`, según la convención documentada.
- Casos de clusters cubiertos (10), todos con resultados esperados derivados a mano de la definición de componente conexa, no por comparación entre dos implementaciones:
  1. Todas las partículas aisladas (sin vecinos): `S = 1/N`.
  2. Clique completo (todas conectadas entre sí): `S = 1`.
  3. Cadena `A-B-C` donde `A` y `C` no son vecinos directos: `S = 1` (verifica transitividad).
  4. Componentes de tamaños 3, 2 y 1 (`N=6`): `S = 3/6`.
  5. Vecinos que cruzan el borde periódico: partículas en `x=9.9` y `x=0.1` (separadas `0.2` a través del borde, con `L=10`), vecinos obtenidos con `cell_index_neighbors`; se verifica que quedan en el mismo cluster de tamaño 2, sin incluir a una tercera partícula lejana.
  6. La misma configuración aleatoria (`N=60`) da el mismo cluster más grande usando `brute_force_neighbors` y `cell_index_neighbors`.
  7. `N=0`: `largest_cluster_size=0`, `largest_cluster_fraction=0`, según la convención documentada.
  8. IDs no consecutivos (`7, 20, 99`): se verifica que el algoritmo usa `id` y no la posición en el vector para resolver la vecindad.
  9. `largest_cluster_size` no modifica la lista de vecinos de entrada.
  10. Transitividad verificada explícitamente y no solo la cantidad de vecinos directos: cadena `A-B`, `B-C`, `C-D` (cada partícula con a lo sumo 2 vecinos directos) debe dar un único cluster de tamaño 4.
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los ocho tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, `observables`, `simulation`, `mean_neighbors`) pasan.

## Bucle de simulación

Implementado en `src/core/simulation.hpp`, función `run_simulation`, junto a `derive_step_seed` y el alias `StateObserver`. Alcance: únicamente la iteración en memoria que encadena muchos pasos de `advance_time_step` manteniendo sincronía, movimiento backward, reproducibilidad, invariancia al orden de almacenamiento y aleatoriedad distinta entre pasos. No incluye escritura de texto, CLI, promedios estacionarios, `t_eq` ni realizaciones independientes; el formato de salida y la CLI siguen siendo decisiones abiertas y no se congelan acá.

### Interfaz implementada

```cpp
using StateObserver = std::function<void(std::size_t step, const std::vector<Particle>& state)>;

std::uint64_t derive_step_seed(std::uint64_t base_seed, std::size_t step);

std::vector<Particle> run_simulation(
    const std::vector<Particle>& initial_state, const Parameters& parameters,
    double eta, InteractionRule rule, std::size_t steps, std::uint64_t base_seed,
    const NeighborSearchFunction& neighbor_search,
    const StateObserver& observer = {});
```

`initial_state` no se modifica (se copia internamente a una variable local `state` que se va reemplazando). `rule` y `neighbor_search` se usan sin cambios en todos los pasos de la corrida: el mismo modelo (Vicsek o votante) y la misma búsqueda de vecinos (fuerza bruta o CIM) durante toda la simulación. `run_simulation` no duplica lógica de `advance_time_step`: se limita a llamarlo `steps` veces con una semilla de paso distinta cada vez y a encadenar su salida como entrada del siguiente.

### Ciclo de vida de los estados y definición de los pasos observados

- **`step=0`** es `initial_state`, tal cual, antes de cualquier avance. No corresponde a ningún sorteo aleatorio: es el punto de partida, no el resultado de una regla de orientación. Si se pasa `observer`, se lo llama una única vez con `(0, initial_state)` antes de ejecutar el primer paso.
- Para cada `t` de `1` a `steps`: se deriva `step_seed = derive_step_seed(base_seed, t)` y se llama `advance_time_step(state, parameters, eta, rule, step_seed, neighbor_search)` sobre el `state` que dejó el paso anterior (nunca sobre `initial_state`, salvo en `t=1`, donde coinciden). El resultado reemplaza `state`. Si se pasa `observer`, se lo llama inmediatamente después con `(t, state)`.
- **`steps=0`** es un caso válido y explícitamente soportado: no se ejecuta ningún avance, `observer` (si existe) se llama solo con `step=0`, y la función devuelve `initial_state` sin cambios.
- El valor de retorno es siempre el estado después de `steps` avances (o `initial_state` si `steps=0`); es el mismo estado que se le pasó al observador en la última llamada, cuando hay observador.
- El observador recibe el estado por `const std::vector<Particle>&`; no tiene forma de modificar el estado interno de la simulación (no se le entrega ninguna referencia no-const ni un puntero al buffer interno).

### Estrategia de derivación de semillas: `(base_seed, step, id)`

El requisito es que el sorteo de cada partícula en cada paso dependa de la terna completa `(base_seed, step, id)`, nunca de la posición de almacenamiento ni de una semilla repetida entre pasos. Esto se resuelve en dos niveles, sin volver a tocar `rules.hpp`:

1. **`derive_step_seed(base_seed, step)`** (nuevo, en `simulation.hpp`): combina `base_seed` y `step` con un mezclado determinista (variante del finalizador de MurmurHash3/splitmix64, con constantes distintas de las de `make_particle_rng` en `rules.hpp` para que ambos mezclados no queden correlacionados entre sí) y devuelve una `step_seed` de tipo `std::uint64_t`.
2. **`make_particle_rng(step_seed, id)`** (ya existente en `rules.hpp`, sin cambios): combina esa `step_seed` con el `id` de cada partícula dentro de `vicsek_update`/`voter_update`, exactamente como ya hacía para un único paso.

El resultado neto es que el sub-generador de la partícula `id` en el paso `t` queda determinado por `make_particle_rng(derive_step_seed(base_seed, t), id)`, es decir, por la terna completa `(base_seed, t, id)`. No hizo falta cambiar la firma de `vicsek_update`/`voter_update` ni de `advance_time_step`: alcanzó con que el bucle nunca reutilice la misma `seed` en dos llamadas a `advance_time_step`.

Consecuencias verificadas por test (ver más abajo):

- Misma `base_seed` y misma configuración ⇒ misma corrida exacta, en cualquier cantidad de pasos.
- Dos pasos consecutivos de la misma corrida no repiten el mismo sorteo (se usan `step_seed` distintas).
- Una `base_seed` distinta puede cambiar la corrida completa (con `eta>0`).
- Permutar el orden de almacenamiento de las partículas iniciales, con la misma `base_seed`, da exactamente el mismo resultado por `id` después de varios pasos (se hereda de la invariancia al orden ya garantizada en `rules.hpp`/`time_step.hpp`, y se vuelve a comprobar explícitamente a nivel del bucle completo).

**Nota documentada explícitamente**: `step=0` corresponde al estado inicial observado (sin sorteo asociado); el primer avance real (el que produce el estado de `step=1`) usa `derive_step_seed(base_seed, 1)`, no `base_seed` directamente ni una semilla de "paso 0".

### Evidencia de los tests

- Implementación de test: `tests/test_simulation.cpp`, registrado en CTest como `simulation`.
- Casos cubiertos (10):
  1. `steps=0`: devuelve exactamente `initial_state`; el observador recibe una única llamada, con `step=0`.
  2. `steps=1` coincide exactamente con una llamada directa a `advance_time_step` usando `derive_step_seed(base_seed, 1)`; probado para Vicsek y para votante.
  3. Varios pasos (`N=30`, 8 pasos, Vicsek): se conserva el tamaño del estado, los `id` (en la misma posición), las posiciones quedan en `[0,L)` y las orientaciones en `[0,2*pi)`.
  4. Observador: recibe `steps+1` llamadas en orden creciente de `step`; el estado observado en cada `step=t` coincide exactamente con reconstruir la corrida a mano llamando `advance_time_step` `t` veces con las `step_seed` correspondientes; el estado devuelto coincide con la última llamada observada; el vector de estado inicial de entrada no se modifica.
  5. Reproducibilidad: dos corridas con la misma configuración y `base_seed` son bit a bit idénticas; se prueban 39 `base_seed` distintas con `eta>0` y se verifica que al menos una produce una corrida distinta.
  6. Semillas por paso: partícula aislada con votante (para que la diferencia entre pasos consecutivos aísle directamente el sorteo de ruido de ese paso) y `eta=0.6`; se verifica que el incremento angular del paso 1 y el del paso 2 no coinciden exactamente, sin asumir valores concretos.
  7. Invariancia al orden: se permutan 4 partículas iniciales, se corren 5 pasos con la misma `base_seed`, y se compara por `id` (no por posición) que posiciones y orientaciones finales coinciden; probado para Vicsek y para votante.
  8. Búsqueda de vecinos: la misma corrida (`N=35`, 6 pasos, Vicsek) con `brute_force_neighbors` y con `cell_index_neighbors` da el mismo estado final y los mismos estados observados en cada paso.
  9. Partícula aislada con `eta=0` (votante): conserva exactamente su orientación en todos los pasos, y su posición en cada paso sigue la ecuación `x0 + v*cos(theta)*dt*step` (verificado paso a paso, no solo al final).
  10. Cadena de pasos: dos partículas separadas `1.02` en `x` (fuera de `rc=1`) que se acercan; en el primer paso todavía no son vecinas (conservan su `theta` propia, votante con `eta=0`) y quedan separadas por `0.96` (dentro de `rc`); en el segundo paso, calculado ya con las posiciones actualizadas del primero, sí se ven como vecinas y cada una copia la orientación de la otra. Prueba que el paso `t` usa las posiciones de `t-1`, no las iniciales.
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los ocho tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, `observables`, `simulation`, `mean_neighbors`) pasan.
- Alcance exacto de este cierre: cubre la iteración en memoria del bucle completo (sincronía, backward, reproducibilidad, invariancia al orden, semillas por paso, compatibilidad Vicsek/votante y fuerza bruta/CIM). No incluye escritura de texto, CLI, promedios estacionarios, `t_eq` ni realizaciones independientes, que siguen pendientes.

## Validación estadística: número medio inicial de vecinos

Implementado como validación (no como pieza del motor) en `tests/test_mean_neighbors.cpp`, registrado en CTest como `mean_neighbors`. No modifica `cell_index_neighbors` ni ninguna otra pieza de `neighbor_search.hpp`: solo genera posiciones uniformes iniciales con semillas explícitas y mide el promedio de vecinos externos con el CIM, para las tres densidades obligatorias (`rho=2,4,8` -> `N=200,400,800`, `L=10`, `rc=1`), 40 realizaciones independientes por densidad. Los valores medidos quedan dentro de un 5% del valor teórico `rho*pi*rc^2` y respetan el orden estricto `mean_k(2)<mean_k(4)<mean_k(8)`. Detalle completo (semillas, criterio de aceptación y justificación de la tolerancia) en `03_validaciones.md`, sección "3. Número medio inicial de vecinos". No se modificó el algoritmo de vecinos: no fue necesario, ya que no se encontró ningún error de geometría, periodicidad o radio en esta validación.

`03_validaciones.md` distingue además, para esta misma validación, entre la aproximación asintótica que usa la cátedra (`rho*pi*rc^2`) y la expectativa finita exacta para vecinos externos en una caja periódica (`(N-1)*pi*rc^2/L^2`); ambas están documentadas ahí junto con la explicación de por qué difieren (una partícula nunca se cuenta a sí misma como vecina). El criterio de aceptación del test no cambió: sigue comparando contra `rho*pi*rc^2`.

## Regresión diagnóstica: consenso del votante sin ruido

Herramienta nueva: `tests/voter_consensus_regression.cpp`, compilada como el ejecutable `voter_consensus_regression` (target de CMake, **no** registrado con `add_test`). Verifica, como control de regresión (pedido explícitamente por `AGENTS.md` y por la sección "Caso de validación: votante sin ruido" de `bibliografia/teoria_tp2_automatas_off_lattice.md`), que el modelo votante con `eta=0` puede alcanzar consenso polar exacto en un sistema finito.

- **Escenario elegido**: sistema pequeño (`N=20`) con una búsqueda de vecinos **completa** controlada — una función de vecinos (compatible con `NeighborSearchFunction`, ver `simulation.hpp`) que devuelve a todas las demás partículas como vecinas de cada partícula, sin usar `rc` ni posición. Esto aísla la dinámica de la regla de votante de la conectividad espacial: se descartó deliberadamente usar los parámetros físicos completos del TP (`v=0.03`, `L=10`, vecinos geométricos) con un horizonte largo, porque mezclaría la propiedad de convergencia de la regla con la velocidad de difusión espacial, algo que el TP no pide afirmar como resultado. Reutiliza `tp2::run_simulation` sin modificar `rules.hpp`, `time_step.hpp` ni `simulation.hpp`.
- **Semillas y horizonte**: 10 semillas explícitas (`700001` a `700010`), 3000 pasos por corrida. Son parámetros de esta regresión puntual, no un protocolo experimental (no se reutilizan como grilla de `eta`, `t_eq` ni cantidad de realizaciones del barrido).
- **Criterio de consenso**: con `eta=0`, `voter_update` nunca crea una orientación nueva (solo copia una existente), así que el conjunto de orientaciones distintas del sistema nunca puede crecer. Se define consenso exacto como que ese conjunto llegue a tener un único valor (comparación exacta con tolerancia `1e-12`, que solo absorbe redondeo de `normalize_angle`). La herramienta reporta, por semilla: `va` inicial y final, cantidad de orientaciones distintas inicial y final, si hubo consenso exacto y en qué paso ocurrió por primera vez.
- **Resultado obtenido** (ver también `03_validaciones.md`, sección "6. Votante"): 10/10 semillas alcanzaron consenso exacto, entre el paso 17 y el paso 64 (muy por debajo del horizonte de 3000). No hizo falta ejercitar la rama diagnóstica para semillas sin consenso.
- **Por qué no es un test de CTest**: la herramienta no tiene ningún assert rígido sobre alcanzar consenso (solo sobre invariantes que sí serían un bug real: `va` fuera de `[0,1]`, o un aumento en la cantidad de orientaciones distintas). Eso la hace, por diseño, no apta para el pase/fallo automático de CTest sin depender de una casualidad estadística; se ejecuta explícitamente con `./build/voter_consensus_regression` y su salida se documenta como evidencia.
- **Alcance**: cubre únicamente la propiedad de convergencia de la regla de votante sin ruido en un grafo completo. No valida consenso con los parámetros físicos completos del TP (densidad, `rc`, movimiento real), que sigue pendiente y no se marca como cerrado (ver checklist en `03_validaciones.md`).

## Paso del motor

Mantener buffers separados:

```text
x_old, y_old, theta_old
x_new, y_new, theta_new
```

La fase de orientación no escribe el estado viejo. La fase de movimiento usa únicamente `theta_old`. Recién al final se intercambian buffers.

Un diseño válido puede guardar un solo vector de partículas y buffers auxiliares, siempre que ningún campo viejo se sobrescriba antes de haber calculado todas las salidas que dependen de él.

**Nota sobre sincronía de la medición** (todavía no implementada, queda para el bucle de simulación): calcular `va(t)` y `S(t)` sobre el mismo estado temporal. Si el paso reconstruye vecinos desde `x(t)` pero ya confirmó `x(t+1)`, no reutilizar una lista desfasada para rotular `S(t+1)`. La opción más clara es medir antes de avanzar o exponer una operación `measure_current_state()` que garantice sincronía; esta decisión se toma cuando se implemente el bucle completo, no en esta tarea.

## Salidas y costo

- El escritor de trayectoria se puede apagar por completo.
- El log escalar puede escribirse cada paso o con *stride*; para justificar estacionariedad conviene cada paso en pilotos.
- Comprobar errores de apertura/escritura.
- El motor no crea gráficos ni depende de Matplotlib.

## Riesgos específicos

- Usar `theta_new` al mover.
- Incluir a `i` en la lista externa y volver a incluirla en Vicsek.
- Permitir autoelección en votante.
- Aplicar borde periódico a posiciones pero no a vecinos/clusters.
- Medir `S` con la vecindad del paso anterior.
- Consumir RNG en orden de almacenamiento y romper la prueba de permutación.
- Construir mal las componentes por confundir vecinos directos con conectividad transitiva.
- Usar `< rc` cuando la especificación dice `<= rc`.

## Criterio de cierre

- [x] Ambos modelos comparten el mismo motor y solo bifurcan en la regla de orientación.
  - Evidencia: `advance_time_step` (`src/core/time_step.hpp`) es una única función que ejecuta el paso completo (vecinos, movimiento, borde periódico) para ambos modelos; el único punto donde se bifurca es la elección entre `vicsek_update`/`voter_update` según el parámetro `InteractionRule rule`. `tests/test_time_step.cpp` ejercita ambas ramas sobre el mismo `advance_time_step`.
- [x] El CIM coincide exactamente con fuerza bruta en configuraciones pequeñas.
  - Evidencia: `tests/test_neighbor_search_cim.cpp` compara listas completas de IDs en 13 familias de casos; `ctest --test-dir build --output-on-failure` pasa los ocho tests registrados.
- [x] `S` usa las mismas aristas periódicas que la interacción.
  - Evidencia: `largest_cluster_size`/`largest_cluster_fraction` (`src/core/observables.hpp`) reciben las listas de vecinos ya calculadas por `brute_force_neighbors`/`cell_index_neighbors` (que ya aplican `d <= rc` con distancia mínima periódica) y no recalculan ninguna distancia; `tests/test_observables.cpp` incluye un caso explícito de vecinos cruzando el borde periódico (`x=9.9`/`x=0.1`) y otro que compara el resultado usando fuerza bruta y CIM sobre el mismo estado.
- [ ] Se puede ejecutar sin trayectoria y con log escalar.
- [ ] Todas las salidas incluyen parámetros y semilla.
- [ ] El código queda listo para la suite de la etapa 3, pero todavía no se autoriza producción.
