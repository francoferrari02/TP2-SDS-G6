# Etapa 6 - Barrido definitivo

## Objetivo

Ejecutar todas las combinaciones pedidas con el protocolo fijado en la etapa anterior y producir tablas reproducibles para las figuras.

## Matriz principal obligatoria

Para cada valor de la grilla final:

```text
model in {vicsek,voter}
rho in {2,4,8}
eta in {eta_1,...,eta_K}
realization in {1,...,R}
```

La grilla final común aprobada es:

```text
eta={0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}.
```

No sustituirla por grillas distintas por modelo: los gráficos pueden incluir
un zoom de `eta<=0.5`, pero la tabla de producción conserva los mismos 14
puntos para Vicsek y votante.

El protocolo temporal y estadístico de la matriz base queda fijado como:

```text
steps=3000
R=20
t_eq=1500
ventana estacionaria=t=1500..3000
barras=desvío estándar entre realizaciones
```

Esta convención aplica a Vicsek y votante para `rho=2,4,8`. Para Vicsek, la
decisión formal se tomó el 2026-08-30 a partir de las corridas
`vicsek_eta0_6_deta0p5_steps3000_R20_v1`; esas corridas validan el corte y
la duración, pero no cubren todos los puntos finos de la grilla común final.
El barrido de producción debe completar o regenerar las combinaciones
faltantes antes de producir figuras comparativas definitivas.

De cada corrida guardar las series `va(t)` y `S(t)`. Para los pocos casos animados, guardar además posiciones y velocidades por instante en texto.

## Extensión del punto de clusters

Para `S(t)` y `<S>` vs. `eta`, agregar en ambos modelos:

```text
rho nominal in {1/pi,1/(2pi),1/(3pi)}
```

Con `L=10` se debe convertir cada densidad a un `N` entero y registrar tanto el valor nominal como el realmente simulado. La decisión registrada el 2026-08-30 es redondear `N=rho_nominal L^2` al entero más cercano:

| rho nominal | N | rho efectiva |
|---:|---:|---:|
| `1/pi` | 32 | 0.32 |
| `1/(2pi)` | 16 | 0.16 |
| `1/(3pi)` | 11 | 0.11 |

Estas densidades adicionales no se incorporan a `<va>` vs. `eta` ni a `<va>` vs. `<S>` sin una confirmación explícita de la cátedra. El mínimo obligatorio de esos gráficos sigue usando `rho=2,4,8`.

Esta convención ya no bloquea el bloque de clusters bajos: la tabla de cada corrida debe conservar `rho_nominal`, `N` y `rho_effective`.

El formato escalar puede seguir escribiendo `va(t)` junto con `S(t)` porque el motor mide ambos observables; conservar ese dato no crea una figura ni un estudio adicional.

## Control de combinaciones

Antes de ejecutar, generar una tabla con una fila por corrida:

```text
run_id,protocol_id,code_id,model,rho_nominal,rho_effective,N,
eta,realization,seed,steps,t_eq,output_path,status
```

Esto es una herramienta interna para verificar el pedido “hacer todas las combinaciones”. No es un experimento adicional.

`run_id` debe cambiar si cambia cualquier entrada capaz de modificar los datos. `protocol_id` identifica la grilla, duraciones, realizaciones, ventanas y definición estadística; `code_id` identifica la versión del motor. No reutilizar un archivo solo porque su nombre contiene `rho`, `eta` y semilla: antes de aceptarlo, comprobar que coincide también en duración, parámetros fijos, protocolo y código.

Durante la ejecución:

- registrar fallos y repetir únicamente las corridas fallidas con la misma semilla;
- comprobar que `0 <= va <= 1` y `1/N <= S <= 1`;
- comprobar que cada archivo tenga exactamente los instantes/campos esperados y una terminación válida;
- no descartar realizaciones por producir resultados atípicos.

El resumen definitivo se genera solo si la matriz esperada está completa. Registrar fallos y continuar puede ser útil durante la ejecución, pero la agregación final debe fallar si falta una combinación, si un punto tiene menos de `R` realizaciones o si mezcla identificadores de protocolo/código. No producir silenciosamente barras con un `n_realizations` menor al acordado.

## Agregación

Para cada `(model,rho,eta)`:

1. promediar `va(t)` y `S(t)` en la ventana estacionaria de cada realización;
2. promediar esos resultados entre realizaciones;
3. calcular la barra según la definición fijada;
4. guardar `R`, `t_eq` y semillas junto al resumen.

Tablas mínimas:

```text
per_realization.csv
summary.csv
```

## Progreso parcial (2026-08-30): Vicsek, clusters bajos

Se agregó y ejecutó `python/vicsek_lowrho_cluster_study_run.py` para cubrir el bloque faltante de Vicsek con las tres densidades bajas usando la conversión aprobada:

```text
rho_nominal={1/pi,1/(2pi),1/(3pi)}
N={32,16,11}
eta={0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}
R=20
steps=3000
t_eq=1500 en el analisis
observables_stride=1
```

Evidencia:

- `PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/vicsek_lowrho_cluster_study_run.py --run-name vicsek_lowrho_cluster_study_1 --steps 3000 --realizations 20 --jobs 8` -> `840` corridas, `0` fallos.
- `PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/pilot_analyze.py --run-name vicsek_lowrho_cluster_study_1 --sample-stride 50 --t-eq 1500` -> `840` observables leídos, `840` válidos, `0` problemas.
- Control independiente de matriz: `42` combinaciones `(model,rho,eta)`, todas con `20` realizaciones; etas exactos de la grilla final común; modelo `vicsek`; `N=32,16,11`.
- Tablas generadas: `data/summary/vicsek_lowrho_cluster_study_1_manifest.csv`, `data/summary/vicsek_lowrho_cluster_study_1_by_realization.csv`, `data/summary/vicsek_lowrho_cluster_study_1_by_combo.csv`, `data/summary/vicsek_lowrho_cluster_study_1_series_sampled.csv`.

## Fuera de alcance

No se agrega un barrido continuo de densidad, percolación estática, susceptibilidad ni estimación de transición crítica. La extensión de densidad se limita al estudio de cluster solicitado.

## Progreso parcial (2026-08-30): grilla fina común `eta<=0.4` para ambos modelos

Se ejecutó y validó el bloque `final_fine_grid_steps3000_R20_v1`, un subconjunto de la
grilla final de 14 puntos ya aprobada (`DECISIONES_PENDIENTES.md`), necesario para las
figuras finales que comparan Vicsek y votante en la zona `eta<=0.4` con la misma
densidad de puntos:

```text
model in {vicsek, voter}
rho in {2, 4, 8}  (N = 200, 400, 800)
eta in {0.05, 0.10, 0.15, 0.20, 0.30, 0.40}
realization in {0,...,19}  (R=20)
steps=3000, t_eq=1500, observables_stride=1, sin trayectoria
```

Antes de correr se verificó que no había `observables.csv` crudos reutilizables para
esta grilla exacta: `data/pilots/pilot_grid_1` usa `steps=600`/`R=3`;
`vicsek_eta0_6_deta0p5_steps3000_R20_v1` usa paso `0.5` (no incluye `0.05,0.10,...`);
`voter_eta_fine_lowrange_1` usa `steps=5000` (protocolo distinto, no sirve para esta
grilla de `steps=3000`); `voter_eta_study_1`/`voter_eta_refine_run.py` usan otra
grilla de `eta`. Por lo tanto se regeneraron las 720 corridas desde cero.

Comandos ejecutados:

```text
cmake --build build
ctest --test-dir build --output-on-failure   # 11/11 OK
python3 python/final_fine_grid_run.py --jobs 10
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/pilot_analyze.py \
    --run-name final_fine_grid_steps3000_R20_v1 --sample-stride 50 --t-eq 1500
```

Script nuevo: `python/final_fine_grid_run.py` (generaliza
`python/voter_eta_study_run.py`/`voter_eta_refine_run.py` a ambos modelos en un único
lanzamiento). Semillas deterministas sin colisión:
`seed = 1100000 + model_offset + rho_offset + 100*eta_index + realization`
(`model_offset`: vicsek=0, voter=100000; `rho_offset`: rho_2=0, rho_4=30000, rho_8=60000).

Evidencia:

- `find data/pilots/final_fine_grid_steps3000_R20_v1 -name observables.csv | wc -l` → `720`.
- Manifiesto `data/summary/final_fine_grid_steps3000_R20_v1_manifest.csv`: `720` filas, `0` fallos (`returncode=0` en todas).
- `pilot_analyze.py`: `720/720` `observables.csv` válidos, `0` problemas de formato.
- Validación programática independiente (script ad hoc, no versionado): `by_realization.csv` tiene exactamente `720` filas; `by_combo.csv` tiene exactamente `36` filas (`2 modelos x 3 rho x 6 eta`); cada combinación `(model, rho_label, eta)` tiene exactamente `20` realizaciones; `steps=3000` en todas las filas; `va_mean`/`S_mean` en `[0,1]`; columnas `va_stdev_between_realizations`/`S_stdev_between_realizations` presentes.
- No se escribió ningún `trajectory.csv` (`find ... -name trajectory.csv | wc -l` → `0`), conforme al pedido de este lote.
- No se descartó ninguna realización por outliers; no hubo corridas fallidas que repetir.

Archivos generados:

```text
data/summary/final_fine_grid_steps3000_R20_v1_manifest.csv
data/summary/final_fine_grid_steps3000_R20_v1_by_realization.csv
data/summary/final_fine_grid_steps3000_R20_v1_by_combo.csv
data/summary/final_fine_grid_steps3000_R20_v1_series_sampled.csv
```

Alcance de esta evidencia: cubre solo el subconjunto fino `eta<=0.4` de la grilla común
de 14 puntos, para las tres densidades obligatorias, ambos modelos. No cierra el
criterio de cierre de la etapa (que exige la grilla completa de 14 puntos y, para el
bloque de clusters, las tres densidades adicionales) porque:

- Vicsek con `R=20`/`steps=3000` para el resto de la grilla de 14 puntos (`eta>=0.5`) ya
  existe pero con un protocolo de grilla distinto (`vicsek_eta0_6_deta0p5_steps3000_R20_v1`,
  paso `0.5`, no los mismos puntos discretos que la grilla de 14 aprobada) — falta
  reconciliar o completar esos puntos exactos.
- El votante para `eta>=0.5` de la grilla de 14 puntos tiene datos de estudios previos
  (`voter_eta_study_1`, etc.) bajo grillas/protocolos distintos entre sí — falta
  verificar cuáles son directamente reutilizables bajo el mismo `protocol_id`/`code_id`
  y cuáles deben regenerarse.
- Las tres densidades bajas del bloque de clusters (`1/pi,1/(2pi),1/(3pi)`) no fueron
  tocadas por esta tarea.

## Progreso parcial (2026-08-30): puntos faltantes del votante en la grilla común base

Se ejecutaron y validaron los dos lotes que faltaban del votante para completar la
grilla común de 14 puntos en `rho=2,4,8` y en las densidades bajas de clusters,
recordando que `voter_eta_study_1`, `voter_lowrho_cluster_study_1` y
`voter_eta_fine_lowrange_1` **no** son reutilizables como datos finales (`t_eq=2250`
los dos primeros, `steps=5000` el tercero; ver `DECISIONES_PENDIENTES.md`).

**A. `final_voter_base_coarse_v1`** (script nuevo `python/final_voter_base_coarse_run.py`):

```text
model=voter
rho in {2, 4, 8}  (N = 200, 400, 800)
eta in {0, 0.5, 1, 2, 3, 4, 5, 6}   (los 8 puntos de la grilla común que
                                     final_fine_grid_steps3000_R20_v1 no cubre)
realization in {0,...,19}  (R=20)
steps=3000, t_eq=1500 (en el análisis), observables_stride=1, sin trayectoria
```

Comando ejecutado: `python3 python/final_voter_base_coarse_run.py --run-name
final_voter_base_coarse_v1 --jobs 10` → **480/480 corridas exitosas, 0 fallos**
(`3 rho x 8 eta x 20 realizaciones = 480`), `571.8s` de cómputo total. Semillas
deterministas nuevas (`seed = 1400000 + rho_offset + 100*eta_index + realization`,
sin colisión con ningún estudio previo: el máximo de semilla usado hasta ahora era
`1291319`, en `vicsek_lowrho_cluster_study_run.py`).

**B. `final_voter_lowrho_grid_v1`** (script nuevo `python/final_voter_lowrho_grid_run.py`):

```text
model=voter
rho_nominal in {1/pi, 1/(2pi), 1/(3pi)}  (N = 32, 16, 11, redondeo al entero más cercano)
eta in {0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}  (grilla común
                                                                          completa de 14 puntos)
realization in {0,...,19}  (R=20)
steps=3000, t_eq=1500 (en el análisis), observables_stride=1, sin trayectoria
```

Comando ejecutado: `python3 python/final_voter_lowrho_grid_run.py --run-name
final_voter_lowrho_grid_v1 --jobs 10` → **840/840 corridas exitosas, 0 fallos**
(`3 rho bajas x 14 eta x 20 realizaciones = 840`), `13.9s` de cómputo total (estos
`N` son mucho más chicos que `200-800`). Semillas nuevas (`seed = 1500000 + N_offset +
100*eta_index + realization`), sin solapar con el rango reservado por el lote A.

**Análisis y validación de ambos lotes:**

```text
python3 python/pilot_analyze.py --run-name final_voter_base_coarse_v1 --sample-stride 50 --t-eq 1500
python3 python/pilot_analyze.py --run-name final_voter_lowrho_grid_v1 --sample-stride 50 --t-eq 1500
```

→ `480/480` y `840/840` `observables.csv` válidos respectivamente, `0` problemas de
formato en ambos. Se agregó `python/validate_final_voter_matrix.py`, una validación
programática independiente (no confía en los manifiestos de los lanzadores: relee
`*_by_realization.csv`/`*_by_combo.csv`) que confirma para cada lote: cantidad exacta
de corridas, `R=20` realizaciones por combinación, `steps=3000`, `t_window_start=1500`,
etas exactos de la grilla declarada, `rho_label`/`N` correctos, `0<=va,S<=1`, cero
fallos en el manifiesto, y presencia de las columnas de desvío estándar entre
realizaciones. Ambos lotes pasaron sin problemas:

```text
python3 python/validate_final_voter_matrix.py --run-name final_voter_base_coarse_v1 \
    --expected-eta 0,0.5,1,2,3,4,5,6 --expected-rho rho_2:200,rho_4:400,rho_8:800 \
    --expected-realizations 20 --expected-steps 3000 --expected-t-eq 1500
python3 python/validate_final_voter_matrix.py --run-name final_voter_lowrho_grid_v1 \
    --expected-eta 0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6 \
    --expected-rho rho_1_over_pi:32,rho_1_over_2pi:16,rho_1_over_3pi:11 \
    --expected-realizations 20 --expected-steps 3000 --expected-t-eq 1500
```

Archivos generados: `data/summary/final_voter_base_coarse_v1_{manifest,by_realization,
by_combo,series_sampled}.csv` y `data/summary/final_voter_lowrho_grid_v1_{manifest,
by_realization,by_combo,series_sampled}.csv`.

Con esto, el votante ya tiene datos finales (protocolo `steps=3000`, `R=20`,
`t_eq=1500`, sin colisión de semillas) para **toda** la grilla común de 14 puntos en
`rho=2,4,8` (repartidos entre `final_fine_grid_steps3000_R20_v1` para
`eta<=0.4` y `final_voter_base_coarse_v1` para el resto) y en las tres densidades
bajas de clusters (`final_voter_lowrho_grid_v1`, los 14 puntos completos en un solo
lote). **No se generó ninguna tabla consolidada del votante en esta tarea** (a
diferencia de Vicsek, ver más abajo): eso queda pendiente como "consolidación final
del votante".

## Progreso parcial (2026-08-30): tabla base final consolidada de Vicsek

Se agregó `python/build_final_vicsek_base_table.py`, que combina, sin volver a correr
nada, `final_fine_grid_steps3000_R20_v1` (filtrado a `model=vicsek`, puntos
`eta={0.05,0.10,0.15,0.20,0.30,0.40}`) con `vicsek_eta0_6_deta0p5_steps3000_R20_v1`
(filtrado a `eta={0,0.5,1,2,3,4,5,6}`), cuya unión cubre exactamente los 14 puntos de
la grilla común aprobada para las tres densidades obligatorias, sin superposición. El
script valida explícitamente, antes de escribir nada: que la unión de ambos conjuntos
de `eta` da exactamente 14 puntos sin solapamiento entre los dos lotes de origen, que
no falta ninguna combinación `(rho,eta)` de las `42` esperadas (`3 rho x 14 eta`), que
cada combinación tiene exactamente `R=20` realizaciones (ni de más ni de menos), que
`steps=3000` y `t_window_start=1500` en todas las filas, que `rho_label`/`N` son
consistentes y que `0<=va,S<=1`. Cada fila de las cuatro tablas de salida lleva una
columna `source_run` con el lote de origen.

Comando ejecutado: `python3 python/build_final_vicsek_base_table.py` →

```text
Validacion OK: 840 filas by_realization (3 rho x 14 eta x R=20), 42 combinaciones, todas con R=20.
Escrito: data/summary/final_vicsek_base_grid_steps3000_R20_v1_manifest.csv (840 filas)
Escrito: data/summary/final_vicsek_base_grid_steps3000_R20_v1_by_realization.csv (840 filas)
Escrito: data/summary/final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv (42 filas)
Escrito: data/summary/final_vicsek_base_grid_steps3000_R20_v1_series_sampled.csv (2562 filas)
```

`vicsek_eta0_6_deta0p5_steps3000_R20_v1` no tenía un manifiesto de lanzador
versionado; el manifiesto consolidado reconstruye sus filas a partir de
`*_by_realization.csv` (que ya trae modelo, densidad, `N`, `eta`, semilla,
realización y `steps`), con `returncode=0` (esas filas ya pasaron la validación de
formato de `pilot_analyze.py`) y `elapsed_s` vacío (no se registró para ese lote
histórico).

Esta tarea **no generó ni modificó ninguna figura**: solo produjo y validó las cuatro
tablas consolidadas. Sigue pendiente regenerar las figuras finales de Vicsek a partir
de esta tabla (con desvío estándar entre realizaciones, no error estándar) y la
consolidación equivalente para el votante.

## Criterio de cierre

- [ ] Están todas las combinaciones de dos modelos, tres densidades base y todos los `eta`.
  - Estado: en progreso. Vicsek ya tiene una tabla consolidada con los 14 puntos de la
    grilla común para `rho=2,4,8` (`final_vicsek_base_grid_steps3000_R20_v1`, ver
    arriba). El votante ya tiene datos finales para los 14 puntos y las tres
    densidades base (repartidos entre `final_fine_grid_steps3000_R20_v1` y
    `final_voter_base_coarse_v1`), pero todavía sin una tabla consolidada equivalente
    a la de Vicsek.
- [ ] El bloque de clusters incluye las tres densidades adicionales.
  - Estado: en progreso. Vicsek ya cubre las tres densidades bajas con la grilla común
    completa (`vicsek_lowrho_cluster_study_1`). El votante también, con protocolo
    final (`final_voter_lowrho_grid_v1`, `840/840` corridas, `0` fallos, `R=20`,
    `steps=3000`, `t_eq=1500`), pero sin consolidar en una única tabla todavía.
- [ ] Cada punto tiene la cantidad `R` acordada de realizaciones válidas.
  - Estado: en progreso. Cumplido y verificado programáticamente para
    `final_fine_grid_steps3000_R20_v1`, `vicsek_lowrho_cluster_study_1`,
    `final_voter_base_coarse_v1`, `final_voter_lowrho_grid_v1` y la tabla consolidada
    `final_vicsek_base_grid_steps3000_R20_v1`; falta la consolidación final del
    votante para verificarlo en un único lugar.
- [ ] No hay corridas fallidas o incompletas sin resolver.
  - Estado: cumplido para todos los lotes ejecutados hasta ahora (`0` fallos en cada
    uno: `720` de la grilla fina, `840` de clusters bajos de Vicsek, `480` del votante
    base, `840` del votante en densidades bajas).
- [ ] Las tablas se obtienen aplicando el promedio temporal y entre realizaciones definido.
- [ ] Se pueden rastrear parámetros y semilla de cualquier resultado.
  - Estado: cumplido para todos los lotes vía sus manifiestos (o, en el caso de la
    tabla consolidada de Vicsek, la columna `source_run` que apunta al lote original).
- [ ] Ningún dato de piloto o de un protocolo/código anterior fue reutilizado como producción.
  - Estado: cumplido. Se verificó explícitamente que `voter_eta_study_1`,
    `voter_lowrho_cluster_study_1` (ambos `t_eq=2250`) y `voter_eta_fine_lowrange_1`
    (`steps=5000`) no se usaron como datos finales; los lotes A y B de esta tarea se
    regeneraron desde cero con protocolo `t_eq=1500`/`steps=3000`.
- [ ] La agregación verifica el producto cartesiano y exige exactamente `R` realizaciones por punto.
  - Estado: en progreso. Cumplido con scripts de validación versionados
    (`python/validate_final_voter_matrix.py` para los lotes del votante,
    validación interna de `python/build_final_vicsek_base_table.py` para la tabla
    consolidada de Vicsek); falta un chequeo equivalente sobre una tabla consolidada
    única del votante.

## Pendientes explícitos que quedan fuera de esta tarea

No se generaron ni modificaron: figuras (PNG), animaciones, comparación de
rendimiento (etapa 8), ni una tabla consolidada final del votante análoga a
`final_vicsek_base_grid_steps3000_R20_v1`. Tampoco se marcan como completas la
etapa 6 ni la etapa 7.
