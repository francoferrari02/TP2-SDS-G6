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
10. Escritura de texto y CLI.

### Estado de implementación

- [x] Tipos, parámetros y estado base en `src/core/model.hpp`.
  - Evidencia: el test geométrico compila y enlaza contra la interfaz `tp2_core`.
- [x] Geometría periódica inicial en `src/core/periodic_geometry.hpp`.
  - Evidencia: `ctest --test-dir build --output-on-failure` verifica `wrap`, distancia mínima en borde y esquina, y los casos `d=rc` y `d>rc`.
- [ ] Búsqueda de vecinos, reglas, actualización, observables, salida y CLI.
  - Estado: en progreso. Se implementaron la búsqueda de vecinos por fuerza bruta (`brute_force_neighbors`) y el Cell Index Method (`cell_index_neighbors`), las reglas de orientación de Vicsek y votante (`src/core/rules.hpp`) y el paso temporal sincrónico/backward completo (`src/core/time_step.hpp`, `advance_time_step`, ver sección "Paso sincrónico/backward" más abajo). Faltan los observables `va`/`S`, la construcción de clusters, la escritura de texto y la CLI.

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
- [ ] Integración con `union(i,j)` para clusters: todavía no corresponde a esta tarea; el CIM por ahora solo devuelve listas de vecinos, igual que el oráculo. La construcción de componentes conexas queda para cuando se implemente el punto "Clusters" de esta misma etapa.

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
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los cinco tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`) pasan.

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
- Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → los cinco tests (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`) pasan.

## Clusters

El cluster es conectividad transitiva, no “todas las partículas dentro de un mismo disco”. A partir de las aristas de vecinos se obtienen las componentes conexas y luego:

```text
n_max = tamaño de la componente más grande
S = n_max/N
```

La guía teórica admite BFS/DFS sobre la lista de vecinos o `union-find`. El plan no impone una de esas alternativas; se elige la más simple de integrar y se valida con casos conocidos. El borde periódico debe estar resuelto al generar las aristas.

## Paso del motor

Mantener buffers separados:

```text
x_old, y_old, theta_old
x_new, y_new, theta_new
```

La fase de orientación no escribe el estado viejo. La fase de movimiento usa únicamente `theta_old`. Recién al final se intercambian buffers.

Un diseño válido puede guardar un solo vector de partículas y buffers auxiliares, siempre que ningún campo viejo se sobrescriba antes de haber calculado todas las salidas que dependen de él.

## Observables en el motor

Polarización:

```text
va = hypot(sum cos(theta_i), sum sin(theta_i)) / N
```

Componente gigante:

```text
S = n_max/N
```

Calcular `va(t)` y `S(t)` sobre el mismo estado temporal. Si el paso reconstruye vecinos desde `x(t)` pero ya confirmó `x(t+1)`, no reutilizar una lista desfasada para rotular `S(t+1)`. La opción más clara es medir antes de avanzar o exponer una operación `measure_current_state()` que garantice sincronía.

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
  - Evidencia: `tests/test_neighbor_search_cim.cpp` compara listas completas de IDs en 13 familias de casos; `ctest --test-dir build --output-on-failure` pasa los cinco tests registrados.
- [ ] `S` usa las mismas aristas periódicas que la interacción.
- [ ] Se puede ejecutar sin trayectoria y con log escalar.
- [ ] Todas las salidas incluyen parámetros y semilla.
- [ ] El código queda listo para la suite de la etapa 3, pero todavía no se autoriza producción.
