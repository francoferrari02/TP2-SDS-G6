# Hoja de ruta maestra - TP2 de bandadas off-lattice

## Objetivo

Desarrollar desde cero un motor reproducible para los modelos de Vicsek y votante ruidoso, validarlo antes de producir datos, ejecutar los barridos requeridos y generar las figuras, animaciones, comparación de rendimiento e informe del TP2.

Esta carpeta es el punto de entrada operativo para humanos y agentes. Cada etapa tiene entradas, tareas, pruebas y un criterio de cierre. Una etapa no se considera terminada porque el código compile: debe satisfacer su evidencia de aceptación.

## Fuentes vinculantes

Leer, en este orden, antes de implementar:

1. [`../bibliografia/enunciado_tp2_guia_de_trabajo.md`](../bibliografia/enunciado_tp2_guia_de_trabajo.md)
2. [`../bibliografia/teoria_tp2_automatas_off_lattice.md`](../bibliografia/teoria_tp2_automatas_off_lattice.md)
3. [`../bibliografia/fuentes_recomendadas_tp2.md`](../bibliografia/fuentes_recomendadas_tp2.md)

El repositorio externo auditado sirve para detectar aciertos y errores, no como especificación ni como fuente de resultados. La auditoría está en [`00_auditoria_referencia_y_notas.md`](00_auditoria_referencia_y_notas.md).

La comprobación requisito por requisito está en [`REVISION_FINAL_DE_ALCANCE.md`](REVISION_FINAL_DE_ALCANCE.md).

Las elecciones que todavía no pueden asumirse están centralizadas en [`DECISIONES_PENDIENTES.md`](DECISIONES_PENDIENTES.md).

Mapa rápido del contexto teórico:

| Tema de desarrollo | Sección de la guía teórica |
|---|---|
| estado, parámetros y condición inicial | secciones 1-2 |
| distancia mínima y vecinos periódicos | sección 3 |
| Vicsek y actualización sincrónica/backward | sección 4 |
| votante y conversión de la convención de ruido | secciones 5-5.1 |
| polarización | sección 6 |
| transitorio, realizaciones y barras | sección 7 |
| clusters/componente gigante | sección 8 |
| controles físicos esperables | sección 9 |

## Reglas que no se negocian

- Espacio continuo, caja periódica cuadrada: `L=10`.
- `rc=1`, `dt=1`, `v=0.03`.
- Densidades obligatorias: `rho=2,4,8`, por lo que `N=200,400,800`.
- Ruido de cátedra: `xi ~ U[-eta/2, eta/2]`; `eta` se expresa en radianes.
- Actualización sincrónica.
- Movimiento *backward*: `x(t+1)=x(t)+v(t) dt`; la orientación nueva afecta el desplazamiento siguiente.
- Vicsek incluye a la propia partícula en el promedio vectorial.
- Votante elige otra partícula dentro de `rc`; si no existe, conserva su orientación y solo suma ruido.
- Vecindad y clusters usan distancia mínima periódica y el criterio `d <= rc`.
- El motor escribe texto; análisis y animación son consumidores independientes.
- Ningún barrido definitivo comienza mientras fallen las validaciones de la etapa 3.

## Alcance de densidades

La matriz principal es:

```text
{vicsek, voter} x {2, 4, 8} x {todos los eta finales} x {R realizaciones}
```

Solo para el estudio de clusters se agregan:

```text
rho nominal = {1/pi, 1/(2pi), 1/(3pi)}
```

Con `L=10`, esas densidades producen un `N` no entero. La decisión registrada el 2026-08-30 es redondear al entero más cercano:

| rho nominal | N redondeado | rho efectiva N/L^2 |
|---:|---:|---:|
| `1/pi = 0.31831...` | 32 | 0.32 |
| `1/(2pi) = 0.15915...` | 16 | 0.16 |
| `1/(3pi) = 0.10610...` | 11 | 0.11 |

En todos los casos se guardan `rho_nominal`, `N` y `rho_efectiva`; no se presenta `N=32` como densidad exactamente igual a `1/pi`.

La extensión se aplica al punto D del enunciado: `S(t)` y `<S>` vs. `eta`. La curva `<va>` vs. `eta` y el gráfico `<va>` vs. `<S>` conservan las tres densidades explícitamente indicadas por el enunciado: `rho=2,4,8`. Si la cátedra confirma que “estudio de clusters” también amplía el punto E, ese gráfico puede reutilizar las corridas de densidad baja, pero no se lo incluye como obligación en este plan.

## Etapas y puertas de calidad

| Etapa | Estado | Documento | Producto que habilita avanzar |
|---:|:---:|---|---|
| 0 | [x] | [`00_auditoria_referencia_y_notas.md`](00_auditoria_referencia_y_notas.md) | Auditoría y seguimiento externo actualizados hasta `413dcef` (29/08) |
| 1 | [ ] | [`01_especificacion_y_arquitectura.md`](01_especificacion_y_arquitectura.md) | Contrato del modelo, interfaz y formatos de salida acordados |
| 2 | [ ] | [`02_motor_y_algoritmos.md`](02_motor_y_algoritmos.md) | Motor de ambos modelos y búsqueda de vecinos implementados |
| 3 | [ ] | [`03_validaciones.md`](03_validaciones.md) | Suite mínima completa en verde; permiso para hacer pilotos |
| 4 | [ ] | [`04_observables_y_estadistica.md`](04_observables_y_estadistica.md) | Estimadores, `t_eq`, realizaciones y barras de error definidos |
| 5 | [ ] | [`05_pilotos_y_grilla_eta.md`](05_pilotos_y_grilla_eta.md) | Grilla final de ruido y duraciones justificadas con series temporales |
| 6 | [ ] | [`06_barrido_de_produccion.md`](06_barrido_de_produccion.md) | Matriz completa, trazable y sin combinaciones faltantes |
| 7 | [ ] | [`07_figuras_y_animaciones.md`](07_figuras_y_animaciones.md) | Todas las figuras obligatorias y animaciones verificadas |
| 8 | [x] | [`08_rendimiento_cim.md`](08_rendimiento_cim.md) | Comparación TP1/TP2 metodológicamente interpretable |
| 9 | [ ] | [`09_informe_presentacion_entrega.md`](09_informe_presentacion_entrega.md) | Informe, exposición, enlaces y ZIP final listos |
| 10 | [x] | [`10_protocolo_para_agentes.md`](10_protocolo_para_agentes.md) | Reglas de delegación, handoff y definición de terminado establecidas |

### Progreso parcial dentro de etapas todavía abiertas

- **Etapa 2:** en progreso. Están implementadas y probadas la búsqueda de vecinos por fuerza bruta (`src/core/neighbor_search.hpp`, `brute_force_neighbors`, oráculo de referencia), el Cell Index Method (`cell_index_neighbors`, validado exhaustivamente contra el oráculo), las reglas de orientación de Vicsek y votante (`src/core/rules.hpp`, `vicsek_update`/`voter_update`), el paso temporal sincrónico/backward completo (`src/core/time_step.hpp`, `advance_time_step`, que combina vecinos + orientación + movimiento + borde periódico para ambos modelos), los observables `va`/`S` (`src/core/observables.hpp`, `polarization`/`largest_cluster_size`/`largest_cluster_fraction`, esta última con `union-find`), el bucle de simulación (`src/core/simulation.hpp`, `run_simulation`/`derive_step_seed`, que encadena muchos pasos derivando una semilla distinta por paso a partir de `(base_seed, step)`, combinada luego con el `id` de cada partícula) y el inicializador productivo del estado (`src/core/initialization.hpp`, `initialize_particles`/`initialize_particles_from_density`, posiciones y orientaciones uniformes con `mt19937_64` y semilla explícita, reutilizado tanto por la validación de vecinos medios como directamente compatible con `run_simulation`). También están implementados el escritor de salida (`src/core/text_output.hpp`, dos archivos CSV por corrida -- `observables.csv` siempre, `trajectory.csv` opcional -- con cabecera de metadatos autocontenida) y la CLI productiva (`src/cli/simulate_cli.hpp`/`src/cli/simulate.cpp`, ejecutable `simulate`, con directorio propio por corrida, no sobrescritura por defecto y `--overwrite` explícito), siguiendo el contrato aprobado en [`DECISIONES_PENDIENTES.md`](DECISIONES_PENDIENTES.md); una revisión posterior reforzó la validación de entradas (rechazo de `NaN`/`inf` en `--rho-nominal`/`--eta`, `--rho-label` restringida a una lista blanca de caracteres seguros) y la publicación atómica de archivos (escritura y verificación de ambos temporales antes de publicar, limpieza ante error, sin dejar mezcla de archivos viejos/nuevos), documentando también el límite real de atomicidad entre dos archivos que queda sin resolver en C++17 portable. Evidencia: `ctest --test-dir build --output-on-failure` (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, `observables`, `simulation`, `mean_neighbors`, `initialization`, `text_output`, `cli_simulate`, los once en verde). El formato de salida ya está congelado e implementado; lo que sigue sin decidirse son los valores productivos de stride, no el mecanismo. Detalle completo en [`02_motor_y_algoritmos.md`](02_motor_y_algoritmos.md).
- **Etapa 5:** en progreso (arrancada antes de que la etapa 3 cierre por completo, porque las piezas que bloqueaban los pilotos -- motor, observables, escritor de salida y CLI -- ya están implementadas y probadas; lo que falta de la etapa 3 es la validación de consenso del votante con parámetros físicos reales, que no bloquea poder pilotar). Se ejecutó un primer piloto de 108 corridas (2 modelos x 3 densidades obligatorias x 6 valores exploratorios de `eta` x 3 realizaciones, `steps=600`, CIM, sin trayectoria salvo una corrida de inspección puntual), lanzado y analizado con `python/pilot_run.py`/`python/pilot_analyze.py` (solo biblioteca estándar). Los 108 `observables.csv` pasaron la verificación independiente de formato; se observó la caída esperada de `<va>` con `eta` en ambos modelos y las tres densidades, y evidencia de que el votante con `eta=0` necesita sustancialmente más de 600 pasos para estabilizarse con los parámetros físicos reales (a diferencia de Vicsek, que se estabiliza dentro de los primeros 100-200 pasos para `eta<=2`). Ninguna decisión del protocolo estadístico (grilla final de `eta`, `t_eq`, realizaciones, semillas, barras de error) quedó cerrada: cada una tiene ahora evidencia preliminar registrada en `DECISIONES_PENDIENTES.md`. Detalle completo en [`05_pilotos_y_grilla_eta.md`](05_pilotos_y_grilla_eta.md). Los datos crudos del piloto quedan fuera de git (`data/pilots/`); las tablas de resumen livianas sí se versionan (`data/summary/pilot_grid_1_*.csv`).
- **Etapa 7:** en progreso. Se agregó `python/vicsek_eta_study_plot.py` y se generaron figuras diagnósticas de Vicsek para `vicsek_eta0_6_deta0p5_steps3000_R20_v1` (`rho=2,4,8`, `eta=0..6` con paso `0.5`, `R=20`, `steps=3000`): curvas estacionarias `<va>` vs. `eta`, `<S>` vs. `eta`, zooms `eta<=1.5`, series `va(t)`/`S(t)` con `t_eq=1500`, y `<va>` vs. `<S>`. El 30/08 se formalizó para Vicsek el protocolo ya usado de hecho: `steps=3000`, `R=20`, `t_eq=1500`, ventana estacionaria `t=1500..3000`, por ser un corte conservador y comparable con votante. También se actualizó `python/pilot_analyze.py` para que `*_series_sampled.csv` incluya `S(t)`, desvío entre realizaciones y error estándar, permitiendo regenerar las figuras de clusters desde datos livianos versionados. Evidencia: `780/780` observables de Vicsek válidos, `0` problemas; PNG en `figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/`. Las PNG actuales usan error estándar y son diagnósticas: la decisión posterior de usar desvío estándar entre realizaciones obliga a regenerarlas antes de la entrega. El mismo 30/08 se completaron los puntos finos `eta={0.05,0.10,0.15,0.20,0.30,0.40}` de la grilla común final para ambos modelos (ver progreso de la etapa 6 más abajo), por lo que ese faltante quedó resuelto; sigue pendiente regenerar las figuras finales con desvío entre realizaciones y usando esos datos. Para clusters bajos de Vicsek ya se resolvió la conversión `1/pi,1/(2pi),1/(3pi) -> N=32,16,11`, se ejecutó `vicsek_lowrho_cluster_study_1` con la grilla final común (`840/840` corridas, `0` fallos, `R=20`, `steps=3000`, `t_eq=1500`) y se generaron tablas `data/summary/vicsek_lowrho_cluster_study_1_*` y PNG en `figures/vicsek_lowrho_cluster_study_1/`; la matriz agregada tiene `42` combinaciones y todas tienen `20` realizaciones. El 30/08 se generaron, además, **todas las figuras finales** de los puntos B-F en una carpeta nueva y separada, `figures/final_production_v1/`, con un único script reproducible `python/generate_final_figures.py` que lee exclusivamente las tres tablas consolidadas finales (`final_vicsek_base_grid_steps3000_R20_v1`, `final_voter_base_grid_steps3000_R20_v1`, `final_lowrho_cluster_grid_steps3000_R20_v1`), no ejecuta simulaciones y rechaza escribir fuera de `figures/`. Son `36` PNG a `220` dpi: curvas `<va>` vs. `eta` y `<S>` vs. `eta` con sus zooms `eta<=0.5` y `<va>` vs. `<S>` para cada modelo en `rho=2,4,8`; `12` series temporales `va(t)`/`S(t)` de la matriz base con `eta={0,0.40,6}` y `t_eq=1500` marcado; `<S>` vs. `eta` y `S(t)` en las tres densidades bajas para ambos modelos; y `4` figuras de comparación Vicsek-votante en paneles por densidad. Todas usan desvío estándar entre realizaciones como barra (`va_stdev_between_realizations`/`S_stdev_between_realizations`) y `va_stdev`/`S_stdev` como banda en series, sin título interno, sin grilla de fondo, con `va` y `S` separados, eje `y` en `[0,1]`, fuente >= 20 pt y color por densidad consistente entre figuras. La carpeta incluye su propio `README.md` con la tabla archivo -> punto A-F del enunciado, tablas fuente, protocolo, definición de barras, significado de colores y comandos de regeneración. Las carpetas diagnósticas previas se conservan intactas y quedan fuera de la entrega. Sigue abierta la etapa: faltan las animaciones (punto A) y la integración/revisión del formato final de diapositivas. El mismo 30/08 se agregaron los **fotogramas estáticos de referencia** para la presentación: `python/render_reference_snapshots.py` (script nuevo que lee exclusivamente `trajectory.csv`, no ejecuta el motor y no produce animaciones) genera `figures/reference_snapshots_v1/{vicsek_rho2_snapshot,voter_rho2_snapshot,rho2_model_comparison_snapshot}.png` a `220` dpi, con una flecha por partícula, color por `theta` con mapa cíclico HSV y barra angular `0..2pi`, caja `[0,10]x[0,10]` de aspecto igual, sin grilla, sin título ni caption. Los casos se eligieron a partir de nuestras tablas finales en `rho=2` (`N=200`, `steps=3000`, `t=2000`): Vicsek `eta=3.00` (`<va>=0.4627`, `base_seed=9100000`) y votante `eta=0.40` (`<va>=0.4625`, `base_seed=9200000`), ambos con realización `0`; las trayectorias quedan en `data/illustrations/` (ignorado por git) escritas con `--trajectory-stride 10`. Verificado: `200` IDs únicos en `t=2000` en cada trayectoria, `theta` en `[0,2pi)`, `py_compile` sin errores y revisión visual de las tres PNG. La longitud de flecha está amplificada por un factor común `15.0` **solo por legibilidad** (`v=0.03` es idéntica para todas las partículas), documentado en `figures/reference_snapshots_v1/README.md` junto con las rutas fuente y los comandos exactos de regeneración. Esto **no cierra el punto A**: no hay video, GIF ni módulo animador todavía.
- **Etapa 6:** en progreso. El 30/08 se ejecutó y validó la grilla fina de producción `final_fine_grid_steps3000_R20_v1`: `{vicsek,voter} x {rho=2,4,8} x {eta=0.05,0.10,0.15,0.20,0.30,0.40} x R=20`, `steps=3000`, `t_eq=1500`, `observables_stride=1`, sin trayectoria, `720` corridas nuevas (`0` fallos) lanzadas con `python/final_fine_grid_run.py` (nuevo, generaliza `voter_eta_study_run.py`/`voter_eta_refine_run.py` a ambos modelos, semillas deterministas `1100000 + model_offset + rho_offset + 100*eta_index + realization`, sin colisión entre modelos/densidades/eta/realizaciones). Analizado con `python/pilot_analyze.py --run-name final_fine_grid_steps3000_R20_v1 --sample-stride 50 --t-eq 1500`: `720/720` `observables.csv` válidos, `0` problemas de formato. Validación programática independiente confirmó `720` filas en `*_by_realization.csv`, `36` filas en `*_by_combo.csv` (2 modelos x 3 densidades x 6 eta), exactamente `20` realizaciones por combinación, `steps=3000` en todas las filas, `va_mean`/`S_mean` en `[0,1]`, y presencia de `va_stdev_between_realizations`/`S_stdev_between_realizations`. Esta grilla fina es un subconjunto de la grilla final de 14 puntos de `eta` ya aprobada (no la reemplaza): cubre la zona `eta<=0.4` con la misma densidad de puntos para ambos modelos, necesaria para comparar Vicsek y votante en la región donde el votante cambia rápido. Además, la conversión de densidades bajas quedó resuelta como redondeo al entero más cercano y se ejecutó el bloque de clusters bajos de Vicsek `vicsek_lowrho_cluster_study_1`: `840/840` corridas, `0` fallos, `42` combinaciones, todas con `R=20`, `steps=3000`, `t_eq=1500`, tablas `data/summary/vicsek_lowrho_cluster_study_1_*`.

  El mismo día se completaron los puntos faltantes del votante en la grilla común
  final con protocolo `steps=3000`/`R=20`/`t_eq=1500` (recordando que
  `voter_eta_study_1`, `voter_lowrho_cluster_study_1` y `voter_eta_fine_lowrange_1`
  no son reutilizables como datos finales: usan `t_eq=2250` o `steps=5000`). Lote A,
  `final_voter_base_coarse_v1` (script nuevo `python/final_voter_base_coarse_run.py`,
  `voter x rho={2,4,8} x eta={0,0.5,1,2,3,4,5,6} x R=20`): `480/480` corridas, `0`
  fallos. Lote B, `final_voter_lowrho_grid_v1` (script nuevo
  `python/final_voter_lowrho_grid_run.py`, `voter x rho_nominal={1/pi,1/(2pi),1/(3pi)}
  (N=32,16,11) x los 14 eta de la grilla común x R=20`): `840/840` corridas, `0`
  fallos. Ambos con semillas nuevas sin colisión con ningún estudio previo (bases
  `1400000` y `1500000`, por encima del máximo usado hasta entonces, `1291319`).
  Analizados con `pilot_analyze.py --sample-stride 50 --t-eq 1500` (`480/480` y
  `840/840` observables válidos, `0` problemas) y verificados con el script nuevo
  `python/validate_final_voter_matrix.py` (cantidad exacta de corridas, `R=20` por
  combinación, `steps=3000`, `t_window_start=1500`, etas exactos, `rho`/`N`
  correctos, `va`/`S` en `[0,1]`, cero fallos, columnas de desvío presentes): ambos
  lotes sin problemas. Con esto el votante ya tiene datos finales para toda la
  grilla común en `rho=2,4,8` y en las tres densidades bajas de clusters, aunque
  todavía sin consolidar en una única tabla (a diferencia de Vicsek, ver abajo).

  También el 30/08 se agregó `python/build_final_vicsek_base_table.py`, que combina
  `final_fine_grid_steps3000_R20_v1` (filtrado a `model=vicsek`) con
  `vicsek_eta0_6_deta0p5_steps3000_R20_v1` (filtrado a `eta={0,0.5,1,2,3,4,5,6}`) en
  una única tabla de producción final de Vicsek,
  `final_vicsek_base_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,
  series_sampled}.csv`, con columna `source_run` para trazabilidad. El script valida
  antes de escribir que la unión da exactamente los 14 puntos de la grilla común sin
  solapamiento entre los dos lotes de origen, que las `42` combinaciones (`3 rho x 14
  eta`) están completas con `R=20` cada una, y que `steps=3000`/`t_eq=1500` en todas
  las filas: `840` filas por realización, `42` combinaciones, todas con `R=20`, sin
  problemas.

  El mismo 30/08 se cerró la consolidación equivalente del votante y la de clusters
  bajos, con dos scripts nuevos que solo combinan lotes ya validados (no recomputan
  ni alteran ningún valor) y validan antes de escribir:
  `python/build_final_voter_base_table.py` produce
  `final_voter_base_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv`
  uniendo `final_fine_grid_steps3000_R20_v1` (filtrado a `model=voter`) con
  `final_voter_base_coarse_v1` (`840` filas, `42` combinaciones, `R=20` cada una,
  `rho={2,4,8}`, los 14 eta exactos, `steps=3000`, `t_window_start=1500`, sin eta
  duplicado ni combinaciones faltantes); `python/build_final_lowrho_cluster_table.py`
  produce `final_lowrho_cluster_grid_steps3000_R20_v1_*` uniendo
  `vicsek_lowrho_cluster_study_1` con `final_voter_lowrho_grid_v1` (`1680` filas,
  `84` combinaciones, ambos modelos, tres densidades bajas `N=32,16,11`, 14 eta,
  `R=20` cada una, `steps=3000`, `t_window_start=1500`). Ambas tablas llevan
  `source_run` por fila. Con esto existen las tres tablas finales de producción del
  TP2 y ninguna combinación de la matriz de datos queda faltante.

  Sigue abierta la etapa 6 en su parte de trayectorias para animación (punto A) y de
  las corridas de rendimiento (etapa 8): esos datos todavía no se generaron. No se
  marcan las etapas 6, 7 ni 8 como completas.
- **Etapa 3:** en progreso. Quedaron cerrados (`[x]`): "CIM contra fuerza bruta" (13 casos), "Número medio inicial de vecinos" (40 realizaciones independientes por densidad para `rho=2,4,8`, ahora generadas con el inicializador productivo en vez de una función propia del test, comparadas contra la aproximación asintótica `rho*pi*rc^2` con tolerancia empírica del 5% y orden estricto entre densidades; documentada también la expectativa finita exacta `(N-1)*pi*rc^2/L^2` sin cambiar el criterio de aceptación), "Vicsek y votante satisfacen reglas distintas" (14 casos sobre el cálculo de orientación, incluyendo invarianza al orden de almacenamiento), "Sincronía y movimiento backward" (13 casos sobre el paso temporal completo, incluyendo el caso mínimo obligatorio `x_new=0.03, y_new=0, theta_new=pi/2` y la permutación de partículas con ruido no nulo), "Polarización `va`" (8 casos, incluyendo un resultado analítico exacto), "Componente gigante `S`" (10 casos, incluyendo transitividad explícita, borde periódico e IDs no consecutivos) y "Bucle de simulación, semillas por paso y reproducibilidad en memoria" (10 casos, incluyendo reproducibilidad exacta con la misma `base_seed`, semillas distintas entre pasos consecutivos e invarianza al orden a lo largo de varios pasos). También quedó validado el inicializador productivo (`tests/test_initialization.cpp`, 11 casos: IDs, rangos, reproducibilidad, densidades obligatorias, `N=0`, integración directa con `run_simulation`, ausencia de siembra por reloj). Hay evidencia diagnóstica nueva sobre el consenso del votante sin ruido (`tests/voter_consensus_regression.cpp`, ejecutable separado no registrado en CTest: 10/10 semillas alcanzaron consenso exacto -- ahora por igualdad exacta de punto flotante, no por tolerancia -- en un grafo completo controlado, `N=20`, 3000 pasos), pero ese punto sigue en `[ ]` porque falta repetirlo con los parámetros físicos completos del TP. También quedó cerrada la validación del escritor de salida y la CLI (`tests/test_text_output.cpp`, formato puro; `tests/test_cli_simulate.cpp`, 17 casos: filas de observables/trayectoria, trayectoria desactivada por defecto, reproducibilidad byte a byte de archivos, reconstrucción de `vx,vy` desde `theta`, metadatos, no sobrescritura por defecto y `--overwrite` coherente, strides con `t=0`/`t=T` garantizados, ruta que diferencia modelo/densidad/eta/pasos/realización/semilla, casos inválidos de CLI incluyendo valores no finitos y etiquetas inseguras, ausencia de colisión en nombres de `eta`, ausencia de temporales tras una corrida exitosa, y publicación segura ante un error real de escritura). El resto de las validaciones de la etapa (consenso del votante con parámetros físicos del TP) sigue sin implementarse porque depende de corridas todavía no ejecutadas ni de un protocolo estadístico decidido. Detalle en [`03_validaciones.md`](03_validaciones.md).
- **Etapa 9:** en progreso documental. El 30/08 se generó `output/pdf/estado_actual_tp2_explicado.pdf`, una síntesis para el grupo que relaciona cada consigna con el estado del motor, validaciones, piloto y decisiones abiertas. Se verificó su renderizado A4 de cinco páginas y se volvió a ejecutar `ctest --test-dir build --output-on-failure`: 11/11 pruebas en verde. Este PDF es una ayuda de seguimiento, no el informe ni la presentación final; no cierra ningún criterio de la etapa 9.
- **Etapa 9:** además, se creó `PLAN_PPT_TP2.md` en la raíz: guion de 21 diapositivas, con división por secciones, tiempos orientativos, activos finales ya disponibles y placeholders explícitos para animaciones, benchmark y datos administrativos. Es una planificación de la PPT, no la entrega final.
- **Etapa 9:** se creó y verificó `output/presentation/TP2_Bandadas_Borrador_Presentacion.pptx`, un borrador avanzado 16:9 con 21 diapositivas para la exposición y 12 de apéndice. Integra 29 PNG exclusivamente de `figures/final_production_v1/` y `figures/reference_snapshots_v1/`, todos embebidos y sin deformación, y contiene notas del orador en sus 33 diapositivas. Evidencia: render e inspección individual de las 33 diapositivas, montage y `slides_test.py` sin overflow; el paquete contiene 33 slides, 33 notes slides y 29 recursos de imagen. Esto cierra la creación/QA del borrador, no la etapa: siguen pendientes animaciones y links, benchmark, grupo/comisión, PDF, informe y ZIP final.
- **Etapa 9:** el 31/08 se preservó el borrador anterior y se exportó `output/presentation/TP2_Bandadas_Borrador_Presentacion_clarificada.pptx`. La diapositiva 12 ahora explicita la comparación a polarización instantánea casi idéntica (`va≈0.515`), identifica Vicsek/`eta=3` a la izquierda y votante/`eta=0.4` a la derecha, y separa los parámetros comunes. Las otras 32 diapositivas y el fotograma científico no cambiaron. Evidencia: render completo, inspección visual de la diapositiva 12, `slides_test.py` sin overflow y fidelidad de plantilla con `0` problemas. Esto no cierra las animaciones ni los demás pendientes de la etapa.
- **Etapa 9:** el 31/08 se auditó esa copia contra la guía oficial `GuiaPresentaciones.pdf` y se exportó `output/presentation/TP2_Bandadas_Presentacion_reestructurada_guia_catedra.pptx` (22 diapositivas de exposición y 11 de apéndice). Se eliminaron los números de los separadores, se llevó la arquitectura de salida/visualización a Simulaciones, se agregó un separador exclusivo de Conclusiones y se retiró el texto de pendientes de la conclusión. Evidencia: render completo de 33 diapositivas, inspección visual de las afectadas, `slides_test.py` sin overflow y fidelidad de plantilla con `0` problemas. La auditoría dejó abiertos la integración de animaciones/enlaces, la ubicación estrictamente lateral de parámetros, el esquema explícito de simulación y el reparto de expositores; por eso no cierra la etapa.

- **Etapa 8 (cerrada, 03/09):** benchmark comparable TP1 (Python, `cell-index-method`)
  vs. TP2 (C++), aislando únicamente la llamada al CIM. Tres condiciones para separar
  causas: TP1 real (radio, sin superposición, `M_max=13`), TP1 ablacionado a partículas
  puntuales (`r=0`, mismo código, `M_max=20`) y TP2 (puntual, `M_max=20`); mismos
  `L=20`, `rc=1`, borde periódico, `N∈{10,...,800}`, `R=100` repeticiones. TP2 resultó
  más rápido en todo el rango (~90x en `N=10`, ~4.8x en `N=800`, brecha que se achica
  porque el CIM de TP1 ya está vectorizado con numpy); dentro de TP1, tener radio es
  ~26% más lento que no tenerlo a `N=800`, con causa medida (`M_max` menor y más
  vecinos reales por el criterio borde-borde, no solo conjeturada). Herramientas:
  `src/cli/benchmark_cim.cpp`, `python/benchmark_tp1_vs_tp2.py`,
  `python/benchmark_tp1_vs_tp2_plot.py`. Detalle completo, tabla y gráfico en
  [`08_rendimiento_cim.md`](08_rendimiento_cim.md).

## Decisiones experimentales que la cátedra deja abiertas

El plan no fija números que no aparecen en el material. Antes del barrido definitivo el grupo debe elegir, registrar y mantener constantes:

- grilla de valores de `eta` (resuelta el 2026-08-30: `{0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}` para ambos modelos);
- cantidad de pasos de transitorio y de medición (resuelta para la matriz base de ambos modelos: `steps=3000`, `t_eq=1500`);
- cantidad de realizaciones independientes y lista de semillas (`R=20` resuelto para la matriz base; semillas trazadas por los scripts/manifiestos de cada estudio);
- definición de las barras de error: desvío entre realizaciones (resuelta el 2026-08-30);
- conversión de densidades bajas de clusters: redondeo al entero más cercano (`N=32,16,11`) con `rho_nominal` y `rho_efectiva` reportadas (resuelta el 2026-08-30);
- frecuencia/formato de escritura;
- entorno y tramo cronometrado en la comparación con TP1.

Estas decisiones se toman con corridas preliminares y series temporales, tal como pide la guía. No se presentan como valores impuestos por la cátedra.

## Fuera de alcance del camino principal

No se planifican susceptibilidad, estimación de `eta_c`, exponentes críticos, histéresis, distribución de tamaños de cluster, barrido de percolación estática, interacción topológica ni estudios de tamaño finito. Pueden mencionarse como contexto bibliográfico, pero no se implementan ni sustituyen los gráficos A-G solicitados.

## Estructura objetivo del repositorio

```text
src/                 motor C++
tests/               pruebas unitarias, integración y regresión
python/              barrido, análisis y animación
config/              protocolo y grillas versionadas
data/raw/            salidas por realización (ignorado por git)
data/summary/        tablas agregadas reproducibles
figures/             gráficos finales
animations/          productos de visualización
docs/                bitácora de decisiones y entregables
```

## Registro interno de decisiones

Antes de ejecutar producción debe existir una tabla interna con los parámetros fijos, grilla de `eta`, `t_eq`, pasos medidos, cantidad de realizaciones, semillas, definición de barras, frecuencia de muestreo y formato de salida. Es una forma de conservar las decisiones que el enunciado pide elegir; no es un entregable adicional de la cátedra.
