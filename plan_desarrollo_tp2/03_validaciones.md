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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 3`.
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

## 5. Promedio circular de Vicsek

- Dos ángulos `1 grado` y `359 grados` deben promediar cerca de `0`, no de `180`.
- Una partícula aislada con `eta=0` conserva su ángulo porque el promedio incluye a sí misma.
- Construcción manual de tres partículas con resultado analítico conocido.

- [x] **Regla de Vicsek (cálculo de orientación nueva).**
  - Implementación: `tp2::vicsek_update` en `src/core/rules.hpp`, validada en `tests/test_rules.cpp`, registrado en CTest como `rules`.
  - Evidencia: partícula aislada con `eta=0` conserva su orientación; `1°`/`359°` promedian cerca de `0°` (no de `180°`); tres orientaciones (`0`, `pi/2`, `pi`) dan el resultado analítico exacto `atan2(1,0)=pi/2`; varias orientaciones iguales con `eta=0` se conservan; cruce adicional de `0/2*pi` con `350°`/`10°`. Todos estos casos comparan contra un valor esperado derivado de la ecuación (promedio vectorial con `atan2`), no contra la propia implementación.
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 5`.
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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 5`.
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
  - Comando ejecutado: `cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure` → `100% tests passed, 0 tests failed out of 5`.
  - Decisión de diseño registrada: el generador aleatorio de `vicsek_update`/`voter_update` se rediseñó durante esta tarea (de un `std::mt19937&` compartido y consumido en orden de índice, a un sub-generador derivado de `(seed, id)`) porque el diseño original no garantizaba la invarianza al orden de almacenamiento que pide este punto. Ver detalle en `02_motor_y_algoritmos.md`.
  - Alcance de este cierre: cubre el paso temporal completo (orientación + movimiento + borde periódico) para ambos modelos, con vecinos por fuerza bruta y por CIM. No incluye clusters, `va`/`S`, salida de texto ni CLI, que son puntos distintos de esta misma etapa y siguen pendientes.

## 8. Clusters

- Cadena `A-B-C` con `A` no vecina directa de `C`: `S=1` para tres partículas; prueba transitividad.
- Componentes de tamaños 3, 2 y 1: `S=3/6`.
- Partículas conectadas solo a través de borde periódico: misma componente.
- Todas aisladas: `S=1/N`.
- Todas conectadas: `S=1`.
- El algoritmo elegido (BFS/DFS o `union-find`) debe coincidir con casos de componentes construidos manualmente.

## 9. Salida y reproducibilidad

- Misma configuración y semilla: archivos escalares idénticos.
- Semilla distinta: al menos la condición inicial o la dinámica difiere.
- La animación puede leer el formato de texto documentado sin llamar al motor.
- `va` y `S` rotulados con el mismo `t` pertenecen al mismo estado.
- Deshabilitar trayectoria no cambia la serie escalar.

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
- [ ] `va` y `S` dentro de límites y casos manuales correctos.
- [x] Vicsek y votante satisfacen reglas distintas.
  - Evidencia: ver detalle y comando en las secciones "5. Promedio circular de Vicsek" y "6. Votante" arriba.
- [x] Movimiento backward demostrado.
  - Evidencia: ver detalle y comando en la sección "7. Sincronía y movimiento backward" arriba (caso mínimo obligatorio con resultado exacto `x_new=0.03, y_new=0, theta_new=pi/2`).
- [x] Invarianza al orden demostrada con ruido.
  - Evidencia: sección "7. Sincronía y movimiento backward" (permutación con `eta=0.4` en `test_time_step.cpp`) y caso 14 de `test_rules.cpp` (permutación con `eta=0.5` para Vicsek y votante).
- [ ] Reproducibilidad y lectura independiente de la salida verificadas.
  - Nota: la reproducibilidad del *paso temporal* con la misma semilla ya está demostrada (sección 7). Lo que falta es específicamente la salida a disco (archivos de texto) y su lectura independiente por la animación, que dependen de la escritura de texto (todavía no implementada).

Al completar esta lista queda habilitada la etapa de pilotos, no todavía la producción definitiva.
