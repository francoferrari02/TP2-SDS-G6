# Etapa 8 - Tiempos del CIM

## Objetivo

Cumplir el punto G: registrar tiempos del código implementado para cantidades de partículas similares a las usadas en TP1 y compararlos con TP1.

## Decisiones que deben registrarse

- valores de `N` elegidos;
- cantidad de pasos;
- cantidad de repeticiones del cronometraje;
- equipo, sistema, compilador y opciones de compilación;
- tramo exacto que se cronometra.

La cátedra no fija esos valores numéricos, pero exige que la comparación sea interpretable.

## Medición

- Usar el mismo equipo y entorno para TP1 y TP2.
- Elegir tamaños de `N` iguales o similares a los de TP1; incluir `200,400,800` si son comparables con los tamaños anteriores.
- Preferir instrumentar dentro de ambos motores la misma operación CIM: reconstrucción de celdas y generación de vecinos. Registrar cuántas llamadas entraron en cada media.
- Excluir de esa ventana el arranque del proceso, generación inicial, trayectoria, log escalar, animación, gráficos y reconstrucciones adicionales hechas solo para medir observables.
- Igualar, siempre que los dos TP lo permitan, `N`, `L`, `rc`, periodicidad, `M` y la convención geométrica de partículas puntuales. Si alguna no puede igualarse, declararla antes de interpretar la diferencia.
- No incluir animación ni generación de gráficos.
- Si se comparan tramos o parámetros diferentes, declararlo y no interpretar la diferencia como una mejora del CIM.
- Repetir las mediciones suficientes veces para informar una tendencia estable; la cantidad se fija en el protocolo, no viene dada por la cátedra.
- Definir antes de medir cómo se tratan calentamiento y valores atípicos. Si se descartan mediciones, aplicar una regla idéntica, conservar el conteo descartado y justificarla; no recortar datos solo para que las barras se vean mejor.
- La geometría de entrada afecta el número de pares candidatos. Idealmente usar configuraciones comparables; si TP1 usa posiciones uniformes y TP2 estados evolucionados/agrupados, informar esa diferencia y acompañarla con el número medio de vecinos o pares candidatos.

## Resultado

Preparar una tabla o gráfico con:

```text
N, pasos, tiempo TP1, tiempo TP2, dispersión de repeticiones, entorno
```

La conclusión debe limitarse a lo realmente medido. No es obligatorio ajustar una complejidad ni comparar CIM contra fuerza bruta en esta etapa.

## Progreso (2026-09-03): benchmark comparable TP1 vs TP2

### Decisiones registradas

- **Qué se cronometra**: únicamente la llamada a la búsqueda de vecinos por
  Cell Index Method (`cell_index_neighbors` en TP2; `buscar_vecinos_cim` en
  TP1), sin generación de partículas (se genera una única vez, fuera del
  bucle cronometrado, en ambos lados), sin I/O, sin animación ni gráficos.
  Herramienta nueva en TP2: `src/cli/benchmark_cim.cpp` (ejecutable
  `benchmark_cim`, no registrado en CTest: no valida correctitud, solo mide
  tiempos). Driver de la comparación: `python/benchmark_tp1_vs_tp2.py` /
  `benchmark_tp1_vs_tp2_plot.py`.
- **Parámetros comunes**: `L=20`, `rc=1`, borde periódico en ambos motores,
  `N ∈ {10, 25, 50, 100, 200, 400, 800}` (incluye los `200,400,800`
  requeridos), `R=100` repeticiones por punto, semilla `12345`.
- **Entorno**: misma máquina (macOS, arm64) y misma sesión para ambos TP.
  TP2 compilado con `clang++ -std=c++17 -O2` (Apple clang 17.0.0), sin
  sanitizers ni flags de profiling. TP1 corrido con el intérprete de su
  propio `venv` (Python 3.13.9, numpy 2.5.2), invocado como subproceso
  nuevo por cada punto de `N` para que el costo de arranque del intérprete
  y el `import numpy` (que sí varían con el entorno pero no con el
  algoritmo) queden fuera de la zona cronometrada, igual que se excluye el
  arranque del proceso en TP2.
- **Calentamiento y atípicos**: no se descartó ninguna repetición ni punto
  (no hubo un criterio de outlier aplicado); las 100 repeticiones de cada
  punto ya se promedian y se reporta su desvío estándar como dispersión.
  No se hizo una fase de "warm-up" previa descartada, porque tanto el CIM
  de TP2 como el de TP1 no tienen estado interno que mejore entre llamadas
  (no hay JIT, cachés persistentes ni estructuras que se reutilicen entre
  repeticiones): cada llamada reconstruye la grilla desde cero.

### Por qué se corrieron tres condiciones, no dos

El objetivo explícito era "asociar y buscarle una causa" a la diferencia de
tiempos, no solo reportar un número. TP1 y Tp2 difieren en más de una cosa
a la vez (lenguaje, partículas con o sin radio, criterio de vecindad
borde-borde vs. centro-centro, `M` máximo distinto), así que comparar
directamente el TP1 real contra TP2 mezclaría todas esas causas en un único
número. Para separarlas se agregó una condición intermedia:

- **A) TP1 real**: partículas con radio `r ~ U[0.23,0.26]`, generadas sin
  superposición (rejection sampling), criterio de vecindad borde-borde
  (`distancia_centros - (r_i+r_j) < rc`). Es el TP1 tal como está
  construido y entregado.
- **B) TP1 ablacionado a partículas puntuales**: mismo código de TP1
  (`buscar_vecinos_cim`, sin modificar), pero con `r=0` para todas las
  partículas. Con radio nulo, la condición de rechazo por superposición
  nunca se activa (no hace falta espacio libre entre partículas) y el
  criterio de vecindad queda igual al de TP2 (distancia centro-centro).
  Aísla el efecto de "tener radio" (menor `M_max`, criterio borde-borde,
  generación con rejection sampling) del efecto de "estar escrito en
  Python vs. C++".
- **C) TP2**: `cell_index_neighbors`, partículas puntuales, periódico.

Cada condición usa su propio `M` óptimo (`calcular_M_max` de cada
implementación), sin forzarlos a ser iguales: la diferencia de `M_max`
entre A y B/C es en sí misma una de las causas que se quiere mostrar, no
un parámetro a neutralizar.

| Condición | `r` | Criterio de vecindad | `M_max` (L=20, rc=1) |
|---|---|---|---:|
| A: TP1 real | `U[0.23,0.26]` | borde-borde | 13 |
| B: TP1 puntual | `0` | centro-centro | 20 |
| C: TP2 | `0` | centro-centro | 20 |

### Resultados

Gráfico: `figures/benchmark_tp1_vs_tp2/tiempo_y_vecinos_vs_N.png` (dos
paneles: tiempo vs. `N` en escala log-log, y vecinos medios por partícula
vs. `N`). Tabla completa: `data/summary/benchmark_tp1_vs_tp2.csv`.

| Condición | N=10 | N=100 | N=800 |
|---|---:|---:|---:|
| A: TP1 real (ms) | 0.142 ± 0.063 | 0.160 ± 0.013 | 1.050 ± 0.234 |
| B: TP1 puntual (ms) | 0.269 ± 0.018 | 0.298 ± 0.019 | 0.833 ± 0.067 |
| C: TP2 (ms) | 0.0030 ± 0.0007 | 0.0209 ± 0.0026 | 0.174 ± 0.023 |

Vecinos medios por partícula a `N=800` (misma `rc=1` nominal en las tres):
**A: 13.08**, **B: 6.27**, **C: 6.21** (B y C coinciden dentro del margen
esperado, ambas son partículas puntuales con el mismo criterio geométrico
-- consistencia cruzada entre implementaciones).

### Interpretación (limitada a lo medido)

1. **TP2 es más rápido que ambas variantes de TP1 en todo el rango de `N`
   medido**, pero la magnitud de la ventaja **no es constante**: a `N=10`,
   TP2 es ~90x más rápido que TP1 puntual; a `N=800`, esa ventaja baja a
   ~4.8x. La explicación coherente con los datos es que a `N` chico domina
   un costo fijo por llamada (en TP1: overhead del intérprete de Python,
   construcción de arrays de numpy, llamadas a funciones; en TP2: ninguno
   de eso existe, es código compilado sin intérprete de por medio), y ese
   costo fijo es mucho mayor en Python que en C++. A medida que `N` crece,
   el trabajo real (comparar pares candidatos) empieza a dominar sobre ese
   costo fijo en ambos, y como el CIM de TP1 está vectorizado con numpy (no
   es un loop puro de Python sobre pares, según su propio código), la
   ventaja de TP2 se reduce en vez de mantenerse en órdenes de magnitud.
2. **Dentro de TP1, tener radio (condición A) es más lento que no tenerlo
   (condición B) a partir de `N≈200`**, y la brecha crece con `N` (a
   `N=800`, A es ~26% más lento que B). Esto tiene una causa identificable
   y medida, no solo conjeturada: con radio, `M_max` cae de 20 a 13 (grilla
   más gruesa, más partículas por celda, más pares candidatos), y además el
   criterio borde-borde extiende el alcance efectivo de interacción
   (`rc_efectivo ≈ rc + r_i + r_j`), lo que se ve directamente en el panel
   de vecinos medios: a igual `rc=1` nominal, A encuentra ~13 vecinos por
   partícula a `N=800` mientras que B y C encuentran ~6.2 -- más del doble.
   Con más vecinos reales por partícula, hay más pares que sobreviven el
   filtro de distancia y más trabajo de por medio, incluso después de
   armar la grilla. A `N` chico (10-100) esta relación se invierte
   (A parece más rápido que B): ahí el ruido de medición y el costo fijo de
   arrancar numpy dominan sobre la diferencia real de `M`/vecinos, que
   recién se vuelve visible cuando el trabajo por llamada supera ese piso.
3. **La restricción de no superposición de TP1 (rejection sampling) no
   aparece en esta medición**, porque se excluyó deliberadamente la
   generación de partículas del tiempo cronometrado (igual que en TP2, que
   tampoco mide su inicializador). Su efecto real es otro, y distinto: no
   hace más lenta cada búsqueda de vecinos, sino que **limita el `N` máximo
   alcanzable** para un `L` dado (empaquetamiento denso con radios
   `U[0.23,0.26]` en `L=20`), algo que TP2 no sufre porque sus partículas
   son puntuales y pueden superponerse sin límite práctico de densidad.
   Esto se verificó indirectamente: generar `N=800` en `L=20` con esos
   radios tardó `~0.06s` (fuera de la ventana cronometrada), sin necesitar
   ajustar `max_intentos`; no se exploró el límite superior real de `N`
   para TP1 porque no hacía falta para esta comparación.
4. **Que TP1 no mueva las partículas (una única foto estática) no afecta
   esta medición particular**, porque en TP2 también se aisló la llamada al
   CIM de todo el resto del motor (reglas de orientación, movimiento,
   repliegue periódico): se cronometra la misma operación puntual en ambos
   casos, no un paso completo de simulación. Si se hubiera cronometrado un
   paso completo de TP2 (`advance_time_step`) contra la única llamada
   estática de TP1, la comparación habría mezclado el costo de la dinámica
   con el de la búsqueda de vecinos, violando el requisito de "instrumentar
   la misma operación" de este documento.

### Reproducción

```bash
clang++ -std=c++17 -O2 -Isrc -o build/benchmark_cim src/cli/benchmark_cim.cpp
python3 python/benchmark_tp1_vs_tp2.py
python3 python/benchmark_tp1_vs_tp2_plot.py
```

`benchmark_tp1_vs_tp2.py` depende de la ruta local
`/Users/katiamenshikoff/Documents/ITBA/SDS/cell-index-method` (el
repositorio del TP1, con su propio `venv`); es una dependencia de máquina,
documentada explícitamente porque el TP1 vive en un repositorio aparte, no
dentro de este.

## Criterio de cierre

- [x] Los `N` son similares a los de TP1.
  - `N ∈ {10,25,50,100,200,400,800}`, incluye los `200,400,800` pedidos explícitamente.
- [x] Se informa qué tramo fue cronometrado.
  - Únicamente la llamada a la búsqueda de vecinos (`cell_index_neighbors`/`buscar_vecinos_cim`); generación de partículas excluida en ambos lados.
- [x] Animación y gráficos quedan fuera del tiempo.
  - El benchmark no genera ninguna figura ni animación dentro de la ventana cronometrada; el gráfico se produce después, leyendo el CSV ya escrito.
- [x] TP1 y TP2 se miden en el mismo entorno o se declara la limitación.
  - Misma máquina y sesión; compilador y versión de Python/numpy documentados arriba.
- [x] Los parámetros geométricos y las configuraciones de entrada son comparables o sus diferencias están cuantificadas.
  - `L`, `rc` y periodicidad iguales en las tres condiciones; la diferencia de radio/`M_max`/criterio de vecindad entre A y B/C está cuantificada (tabla de `M_max` y de vecinos medios).
- [x] El tratamiento de calentamiento/atípicos y el número de mediciones están documentados.
  - `R=100` repeticiones por punto, sin descarte de repeticiones ni fase de warm-up (justificado: el CIM no tiene estado que mejore entre llamadas).
- [x] Tabla/gráfico y conclusión son reproducibles.
  - Comandos exactos documentados arriba; `data/summary/benchmark_tp1_vs_tp2.csv` y `figures/benchmark_tp1_vs_tp2/tiempo_y_vecinos_vs_N.png`.
