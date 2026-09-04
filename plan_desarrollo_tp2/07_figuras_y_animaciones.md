# Etapa 7 - Figuras y animaciones obligatorias

## Objetivo

Generar únicamente los estudios A-E para ambos modelos y la comparación F indicados por el enunciado.

## A. Animaciones características

- Un vector por partícula, ubicado en su posición.
- Dirección y módulo dados por su velocidad.
- Color asociado al ángulo.
- Módulo de animación independiente que lee la salida de texto.
- Pocos casos representativos; las notas del profesor sugieren dos casos bien distintos, de ruido bajo y alto.

Las animaciones deben abrir cada estudio en la presentación. El PDF lleva links explícitos y no las embebe.

## B. Evolución temporal de polarización

Para cada densidad `rho=2,4,8` y situaciones características de `eta`:

- graficar `va(t)`;
- comparar Vicsek y votante bajo el mismo protocolo;
- marcar `t_eq` con una línea vertical;
- explicar la ventana usada para el promedio estacionario.

## C. Polarización estacionaria vs. ruido

```text
x = eta
y = <va>_est
densidades = {2,4,8}
modelos = {vicsek,voter}
barras = definición declarada del protocolo
```

Las tres densidades deben distinguirse claramente mediante curvas o paneles comparables.

## D. Estudio de clusters

Para ambos modelos:

1. graficar `S(t)` en situaciones características;
2. marcar la misma ventana estacionaria usada para `va`;
3. graficar `<S>_est` vs. `eta` con barras de error.

Este punto incluye:

```text
rho = {2,4,8,1/pi,1/(2pi),1/(3pi)}
```

Se recomienda separar densidades base y adicionales en paneles para mantener legibilidad, sin agregar otro estudio.

## E. Relación entre orden y conectividad

El enunciado pide polarización en función de componente gigante:

```text
x = <S>_est
y = <va>_est
cada punto = un eta del barrido
densidades = {2,4,8}
```

Distinguir densidades y modelos. `eta` no es un eje. Este gráfico estudia si conectividad espacial y alineamiento global se relacionan, pero no presupone el resultado.

La ampliación a las tres densidades bajas no se incluye como obligación porque el punto E dice explícitamente “distinguir las tres densidades”. Solo se hará si la cátedra confirma que la aclaración de clusters también abarca este punto.

## F. Comparación entre modelos

Repetir A-E para el votante y comparar contra Vicsek usando:

- mismos parámetros;
- misma grilla de ruido;
- mismo criterio de estacionario;
- misma cantidad de realizaciones;
- misma definición de barras.

La grilla común aprobada para estas comparaciones es
`eta={0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}`.
Se permite un panel o figura de zoom para `eta<=0.5`, pero no reemplaza la
curva completa ni autoriza puntos distintos por modelo.

## Convenciones de presentación

- `va` y `S` se muestran en su rango `[0,1]`.
- Colores, líneas y marcadores identifican siempre de la misma forma modelo y densidad.
- Cada epígrafe declara `rho`, `eta` cuando corresponda, `R` y significado de barras.
- No se suavizan datos ni se agregan ajustes no solicitados.

La copia de la Guía de Presentaciones incluida en el repositorio de referencia agrega controles de formato que sí son coherentes con la documentación citada por el enunciado:

- en la presentación, la figura no lleva título interno ni *caption*; los parámetros se escriben al costado de la figura;
- los ejes se rotulan preferentemente con palabras y unidades cuando correspondan;
- letras y números dentro de la figura deben tener tamaño legible, al menos 20 para las diapositivas;
- cada dato promedio debe distinguirse con un símbolo o su barra; una línea recta puede usarse como guía visual, pero no una interpolación arbitraria;
- para el PDF se usa un fotograma representativo y un enlace explícito; durante la exposición en vivo la animación debe quedar integrada en la diapositiva, sin salir a otro programa.

El repositorio externo afirma además que la cátedra pidió figuras sin grilla de fondo, `va` y `S` separados y cada modelo individual antes de la superposición comparativa. Mantener estas indicaciones como pendientes de confirmación: no cambian el barrido ni bloquean la generación de tablas, pero sí el diseño visual final.

## Fuera de alcance

No generar susceptibilidad, `eta_c`, histéresis, distribución de tamaños de cluster ni curva de percolación. Ninguna reemplaza los gráficos A-E.

## Progreso parcial (2026-08-30): figuras diagnósticas de Vicsek

Se agregó `python/vicsek_eta_study_plot.py`, siguiendo la estructura de los scripts del votante. El protocolo de estas corridas queda formalizado para Vicsek como `steps=3000`, `R=20`, `t_eq=1500` y ventana estacionaria `t=1500..3000`. Sus exportaciones actuales usan error estándar (`va_stderr`, `S_stderr`) y bandas de error estándar; tras la decisión del 2026-08-30 de informar desvío estándar entre realizaciones, son diagnósticas y deben regenerarse con las columnas `va_stdev_between_realizations`/`S_stdev_between_realizations` (y `va_stdev`/`S_stdev` en series) antes de incluirse en la presentación. La dependencia externa es `matplotlib`; en esta máquina se instaló con:

```text
python3 -m pip install --user matplotlib==3.8.4
```

Entrada usada:

```text
data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_by_combo.csv
data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_series_sampled.csv
```

Comandos verificados:

```text
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/pilot_analyze.py python/vicsek_eta_study_plot.py
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/pilot_analyze.py --run-name vicsek_eta0_6_deta0p5_steps3000_R20_v1 --sample-stride 50 --t-eq 1500
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/vicsek_eta_study_plot.py --run-name vicsek_eta0_6_deta0p5_steps3000_R20_v1 --t-eq 1500
```

Evidencia:

- `pilot_analyze.py` releyó `780` observables, `780` válidos, `0` problemas.
- `data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_series_sampled.csv` ahora guarda `va(t)` y `S(t)`, con desvío y error estándar, por lo que las series de clusters se pueden regenerar desde datos livianos versionados.
- Se generaron `11` PNG en `figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/`: `va_vs_eta.png`, `S_vs_eta.png`, sus zooms `eta<=1.5`, `va_vs_S.png`, y `va_t_*/S_t_*` para `rho=2,4,8`.
- Se revisaron visualmente `va_vs_eta.png`, `S_t_rho_2.png` y `va_vs_S.png`: los archivos renderizan, los ejes cubren `[0,1]`, aparecen las barras/bandas y las series marcan `t_eq=1500`.

Alcance: esto no cierra la etapa 7. Falta integrar el votante bajo el mismo estilo estadístico, completar la comparación Vicsek-votante, decidir el formato final de diapositivas y generar/validar animaciones.

## Progreso parcial (2026-08-30): datos crudos de la grilla fina común listos, figuras aún no regeneradas

Se completó y validó (ver `06_barrido_de_produccion.md`) el bloque de producción
`final_fine_grid_steps3000_R20_v1`: `{vicsek,voter} x {rho=2,4,8} x
{eta=0.05,0.10,0.15,0.20,0.30,0.40} x R=20`, `steps=3000`, `t_eq=1500`, sin
trayectoria. Las tablas resumen quedaron en:

```text
data/summary/final_fine_grid_steps3000_R20_v1_by_realization.csv
data/summary/final_fine_grid_steps3000_R20_v1_by_combo.csv
data/summary/final_fine_grid_steps3000_R20_v1_series_sampled.csv
```

Esto habilita, en cuanto a datos, regenerar con `va_stdev_between_realizations`/
`S_stdev_between_realizations` (la convención de barras ya decidida) las figuras C y D
en la zona fina `eta<=0.4` comparando ambos modelos. Esta tarea **no generó** ninguna
figura (PNG) todavía: solo produjo y validó los datos crudos y resumidos. Sigue
pendiente:

- escribir/adaptar un script de graficado que combine `final_fine_grid_steps3000_R20_v1`
  con el resto de la grilla de 14 puntos (`eta>=0.5`) para Vicsek y votante, una vez
  reconciliados esos protocolos (ver pendiente en `06_barrido_de_produccion.md`);
- regenerar las figuras diagnósticas de Vicsek (`figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/`)
  con desvío entre realizaciones en vez de error estándar;
- producir la comparación Vicsek-votante (punto F) con la grilla común completa, no solo
  el tramo fino.

Además, la grilla de esa corrida (`eta=0..6` con paso `0.5`) no cubre todos
los puntos finos de la grilla común aprobada para la comparación
(`0.05, 0.10, 0.15, 0.20, 0.30, 0.40`). Por eso sirve como evidencia del
protocolo temporal de Vicsek, pero no como tabla final completa de
comparación.

## Progreso parcial (2026-08-30): clusters bajos de Vicsek

Se resolvió la conversión de densidades bajas a `N` entero como redondeo al entero más cercano y se agregó el bloque faltante de Vicsek para el punto D:

```text
run_name=vicsek_lowrho_cluster_study_1
rho_nominal={1/pi,1/(2pi),1/(3pi)}
N={32,16,11}
eta={0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}
R=20
steps=3000
t_eq=1500
```

Comandos verificados:

```text
cmake --build build
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/pilot_analyze.py python/vicsek_lowrho_cluster_study_run.py python/vicsek_lowrho_cluster_study_plot.py
ctest --test-dir build --output-on-failure
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/vicsek_lowrho_cluster_study_run.py --run-name vicsek_lowrho_cluster_study_1 --steps 3000 --realizations 20 --jobs 8
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/pilot_analyze.py --run-name vicsek_lowrho_cluster_study_1 --sample-stride 50 --t-eq 1500
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache .venv-mpl311/bin/python python/vicsek_lowrho_cluster_study_plot.py --run-name vicsek_lowrho_cluster_study_1
```

Evidencia:

- `ctest` pasó `11/11`.
- El lanzador produjo `840/840` corridas exitosas, sin fallos.
- `pilot_analyze.py` releyó `840` observables, todos válidos, y generó las tablas `data/summary/vicsek_lowrho_cluster_study_1_*`.
- La matriz agregada tiene `42` combinaciones y todas tienen `R=20`.
- Se generaron `10` PNG en `figures/vicsek_lowrho_cluster_study_1/`: `<S>` vs. `eta`, zoom de `<S>`, `<va>` vs. `eta`, zoom de `<va>`, y series `va(t)`/`S(t)` para cada densidad baja.
- Se revisó visualmente `figures/vicsek_lowrho_cluster_study_1/S_vs_eta.png`: renderiza correctamente, con eje `S` en `[0,1]`, tres densidades distinguibles y barras de desvío estándar.

## Progreso parcial (2026-08-30): figuras finales de produccion en `figures/final_production_v1/`

Se consolidaron las dos tablas finales que faltaban y se generaron **todas** las figuras
finales de los puntos B-F en una carpeta nueva y separada de las diagnosticas.

Tablas consolidadas nuevas (ningun valor recomputado; solo union con `source_run`):

```text
python/build_final_voter_base_table.py
  -> data/summary/final_voter_base_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv
     (final_fine_grid_steps3000_R20_v1 filtrado a voter + final_voter_base_coarse_v1)

python/build_final_lowrho_cluster_table.py
  -> data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv
     (vicsek_lowrho_cluster_study_1 + final_voter_lowrho_grid_v1)
```

Script unico de figuras: `python/generate_final_figures.py`. Lee exclusivamente las tres
tablas consolidadas finales (`final_vicsek_base_grid_steps3000_R20_v1`,
`final_voter_base_grid_steps3000_R20_v1`, `final_lowrho_cluster_grid_steps3000_R20_v1`),
no ejecuta simulaciones y rechaza cualquier `--out-dir` fuera de `figures/`.

Comandos verificados:

```text
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/build_final_voter_base_table.py python/build_final_lowrho_cluster_table.py python/generate_final_figures.py
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/build_final_voter_base_table.py
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/build_final_lowrho_cluster_table.py
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache .venv-mpl311/bin/python python/generate_final_figures.py
```

Evidencia:

- Votante base: `840` filas `by_realization`, `42` combinaciones, `20` realizaciones cada
  una, `rho={2,4,8}`, los 14 eta exactos, `steps=3000`, `t_window_start=1500`, sin eta
  duplicado entre lotes ni combinaciones faltantes. Validacion OK, `0` problemas.
- Clusters bajos: `1680` filas `by_realization`, `84` combinaciones, ambos modelos, tres
  densidades bajas (`N=32,16,11`), 14 eta, `20` realizaciones cada una, `steps=3000`,
  `t_window_start=1500`. Validacion OK, `0` problemas.
- Se generaron `36` PNG en `figures/final_production_v1/`, mas su `README.md` con la
  tabla archivo -> punto A-F, tablas fuente, protocolo, definicion de barras, significado
  de colores y comandos de regeneracion.
- Barras: `va_stdev_between_realizations`/`S_stdev_between_realizations` en curvas
  estacionarias; bandas `va_stdev`/`S_stdev` en series temporales. Ninguna figura usa
  `*_stderr` (verificado por inspeccion del script: no aparece la cadena `stderr`).
- Sin titulo interno ni `suptitle` (verificado: el script no llama `set_title`), sin
  grilla de fondo (`axes.grid=False` y `ax.grid(False)` explicito), `va` y `S` separados,
  eje `y` en `[0,1]` con margen `[-0.04,1.04]`, fuente >= 20 pt, PNG a `220` dpi, color
  por densidad constante en todas las figuras.
- En `va` vs. `S` la linea recorre los puntos en el orden del barrido de `eta` (no en
  orden de `S`): es guia visual del camino del barrido, no un ajuste.
- Revision visual: `vicsek_va_vs_eta.png`, `voter_S_vs_eta_lowrho.png`,
  `vicsek_va_vs_S.png`, `vicsek_va_t_rho_2.png`, `voter_S_t_rho_2.png` y
  `comparison_va_vs_eta.png` renderizan correctamente, con puntos visibles, barras/bandas,
  `t_eq=1500` marcado en las series y paneles legibles en la comparacion.

Las carpetas diagnosticas previas (`figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/`,
`figures/vicsek_lowrho_cluster_study_1/`) se conservan sin tocar como evidencia
historica; no se usan en la presentacion.

Alcance: **esto no cierra la etapa 7**. Siguen faltando las animaciones (punto A) y la
integracion final en diapositivas; el benchmark del CIM (etapa 8) tampoco esta hecho.

## Progreso parcial (2026-08-30): fotogramas estaticos de referencia listos

Se generaron **fotogramas estaticos de referencia** para la presentacion: imagenes
fijas de las particulas con su vector de direccion. Esto **no cierra el punto A**:
no hay video, GIF ni animador todavia; son cuadros de referencia para las
diapositivas y para fijar la convencion visual (vector por particula, color por
angulo) que despues debera reusar la animacion.

Script nuevo: `python/render_reference_snapshots.py`. Lee **exclusivamente**
`trajectory.csv`; no ejecuta el motor, no depende de su tiempo de computo, no
produce animaciones y rechaza cualquier `--out-dir` fuera de `figures/`.

Casos elegidos a partir de nuestras tablas finales (no copiados de ninguna otra
fuente), ambos con `rho=2`, `N=200`, `L=10`, `steps=3000`, `t=2000` (ventana
estacionaria, `t_eq=1500`), una realizacion determinista por caso:

| Modelo | `eta` | `<va>` tabla final (`rho=2`, `R=20`) | `base_seed` | realizacion |
|---|---:|---:|---:|---:|
| Vicsek | `3.00` | `0.4627` | `9100000` | `0` |
| Votante | `0.40` | `0.4625` | `9200000` | `0` |

`eta=3` es el punto de polarizacion intermedia de Vicsek en `rho=2`
(`0.9284 -> 0.7336 -> 0.4627 -> 0.1897` para `eta=1,2,3,4`), dentro de la zona
donde cae el orden. `eta=0.40` es el punto de la zona fina `eta<=0.5` del votante
donde el ruido ya es evidente (`1.0000 -> 0.7318 -> 0.4625` para
`eta=0, 0.20, 0.40`) y ademas iguala el `<va>` de Vicsek en `eta=3`, lo que hace
directamente comparable la figura lado a lado.

Trayectorias en un directorio separado (`data/illustrations/`, agregado a
`.gitignore` como el resto de las salidas crudas), escritas con
`--write-trajectory --trajectory-stride 10`.

PNG generadas en `figures/reference_snapshots_v1/` (`220` dpi, fondo blanco):

```text
figures/reference_snapshots_v1/vicsek_rho2_snapshot.png
figures/reference_snapshots_v1/voter_rho2_snapshot.png
figures/reference_snapshots_v1/rho2_model_comparison_snapshot.png
figures/reference_snapshots_v1/README.md
```

La comparativa pone Vicsek y votante lado a lado con la misma escala espacial
(`[0,10]x[0,10]`, aspecto igual) y el mismo mapeo de color angular.

Convenciones: una flecha por particula en su posicion, direccion dada por `theta`,
color por `theta` con mapa ciclico HSV y barra de color angular de `0` a `2pi`,
caja cuadrada con aspecto igual, sin grilla de fondo, sin titulo ni caption ni
links dentro del PNG, fuente `20` pt. **La longitud de las flechas esta amplificada
por un unico factor comun `15.0` (`v*15 = 0.45` unidades de caja) solo por
legibilidad**: la rapidez fisica es `v=0.03` e identica para todas las particulas,
y la longitud dibujada no codifica ninguna diferencia entre ellas. Esto queda
documentado tambien en `figures/reference_snapshots_v1/README.md`, junto con las
rutas de `trajectory.csv` usadas y los comandos exactos de regeneracion.

Comandos verificados:

```text
./build/simulate --model vicsek --rho-nominal 2 --rho-label rho_2 --N 200 --eta 3 --steps 3000 --base-seed 9100000 --realization 0 --output-dir data/illustrations/reference_snapshots_v1 --observables-stride 100 --write-trajectory --trajectory-stride 10
./build/simulate --model voter --rho-nominal 2 --rho-label rho_2 --N 200 --eta 0.40 --steps 3000 --base-seed 9200000 --realization 0 --output-dir data/illustrations/reference_snapshots_v1 --observables-stride 100 --write-trajectory --trajectory-stride 10
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/render_reference_snapshots.py
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache .venv-mpl311/bin/python python/render_reference_snapshots.py
```

Evidencia:

- Cada `trajectory.csv` contiene exactamente `200` IDs unicos en `t=2000`
  (`60200` filas totales con stride `10`), `theta` en `[0,2pi)` y posiciones
  dentro de `[0,10]x[0,10]`, en ambos casos.
- `va` de la realizacion mostrada en `t=2000`: `0.5144` (Vicsek) y `0.5153`
  (votante), consistentes con los `<va>` de ensamble de las tablas finales.
- `py_compile` sobre `python/render_reference_snapshots.py` sin errores.
- Las tres PNG se inspeccionaron visualmente: renderizan, la caja es cuadrada y
  cubre `[0,10]`, las flechas son legibles, la barra de color angular va de `0` a
  `2pi` y los dos paneles de la comparativa comparten escala y color.

Alcance: **esto no cierra la etapa 7 ni el punto A**. Sigue faltando la animacion
propiamente dicha (video/GIF con su modulo animador), la integracion en las
diapositivas y el benchmark de la etapa 8.

## Progreso parcial (2026-08-30): integración y QA del borrador PPTX

Se integraron las figuras finales y el fotograma comparativo en
`output/presentation/TP2_Bandadas_Borrador_Presentacion.pptx`. El cuerpo principal
usa una o dos figuras por diapositiva, deja los parámetros fuera de los PNG y conserva
su proporción; el apéndice reúne las series restantes, comparaciones y zooms sin
reutilizar imágenes del cuerpo. El archivo tiene 33 diapositivas (21 de exposición y 12
de respaldo), 29 PNG embebidos y notas del orador en todas las diapositivas.

Evidencia: render independiente de las 33 diapositivas, inspección individual a tamaño
completo y montage; `slides_test.py` pasó sin overflow. Se corrigieron durante la QA
las imágenes inicialmente referenciadas por ruta para que quedaran embebidas por bytes,
y se acortaron títulos hasta eliminar wrapping/clipping. Esto cierra la maquetación de
figuras para el borrador, pero no el punto A: siguen sin existir video/GIF, módulo
animador ni links públicos probados.

## Progreso parcial (2026-08-31): comparación a igual polarización clarificada

Se preservó el borrador original y se exportó
`output/presentation/TP2_Bandadas_Borrador_Presentacion_clarificada.pptx`. En la
diapositiva 12 se mantuvo el mismo fotograma comparativo porque los dos estados ya
habían sido seleccionados con polarización instantánea prácticamente idéntica
(`va(t=2000)=0.5144` para Vicsek con `eta=3` y `0.5153` para votante con `eta=0.4`).
Se reescribieron únicamente el título y el bloque lateral para explicitar el criterio,
identificar los paneles izquierdo/derecho y separar los parámetros comunes. No se
regeneraron ni alteraron las trayectorias o figuras científicas.

Evidencia: se renderizaron las 33 diapositivas de la copia, se inspeccionó la
diapositiva 12 a tamaño completo, `slides_test.py` informó `Test passed. No overflow
detected.` y `check_template_fidelity.mjs` pasó con `0` problemas. El original
`TP2_Bandadas_Borrador_Presentacion.pptx` permanece intacto.

Alcance: mejora la interpretación del fotograma estático, pero no cierra el punto A:
siguen faltando las animaciones y sus links probados.

## Progreso parcial (2026-08-31): relación exploratoria `va`--`S` con seis densidades

Se agregó `python/plot_cluster_order_relationship.py`, que lee exclusivamente las
tres tablas finales consolidadas y genera
`figures/cluster_order_relationship_v1/comparison_va_vs_S_six_densities.png`.
La figura reproduce la orientación de la referencia externa (`x=<va>`, `y=<S>`),
combina ambos modelos y las seis densidades disponibles y, desde la revisión del
31/08 pedida por el usuario, muestra solo los promedios sin barras de desvío para
reducir la superposición visual. El script
valida antes de graficar las `168` combinaciones esperadas (`2 modelos x 6 rho x
14 eta`), sin duplicados, con `R=20` y observables en `[0,1]`; además escribe
`correlation_summary.csv` con coeficientes de Pearson y rangos por serie.

Alcance: es una figura exploratoria pedida para comprender los datos y no reemplaza
`figures/final_production_v1/comparison_va_vs_S.png`, que conserva la convención
obligatoria `x=<S>`, `y=<va>` y `rho={2,4,8}`. La ampliación formal del punto E a
densidades bajas sigue pendiente de aclaración docente.

## Progreso parcial (2026-08-31): guía oficial auditada y estructura de la PPT corregida

Se auditó `output/presentation/TP2_Bandadas_Borrador_Presentacion_clarificada.pptx`
contra `/Users/francoferrari/Downloads/GuiaPresentaciones.pdf` y se generó
`output/presentation/TP2_Bandadas_Presentacion_reestructurada_guia_catedra.pptx`.
La guía confirma como requisitos: figuras sin título ni *caption* interno, parámetros
al costado, fuente interna mínima de 20, marcadores visibles, animaciones integradas en
la versión de exposición y fotograma con enlace explícito en el PDF.

La primera reestructuración no regeneró datos ni PNG: corrigió separadores, orden de
secciones y conclusiones, y preservó las 29 imágenes embebidas. El render completo de
33 diapositivas pasó `slides_test.py` sin overflow y el control de fidelidad de plantilla
sin problemas. La revisión también detectó que varios bloques metodológicos de resultados
siguen debajo de las figuras y no estrictamente al costado; por eso el cumplimiento visual
de este criterio vuelve a quedar abierto hasta una segunda pasada de maquetación.

Alcance: esto no cierra la etapa 7 ni el punto A. Siguen faltando el módulo animador,
los archivos de animación, sus enlaces públicos probados y la adecuación lateral de
parámetros en todas las diapositivas de resultados.

## Progreso parcial (2026-09-03): grilla de `eta` ampliada a 37 puntos y figuras finales regeneradas

El usuario notó que `vicsek_va_vs_eta.png` (14 puntos de `eta`, paso entero entre
`eta=1` y `eta=6`) se veía notoriamente menos preciso que una figura de referencia
externa aceptada por la cátedra en otro grupo, y que la cátedra exige gráficos
"precisos". Ver la corrida y consolidación de datos en
`06_barrido_de_produccion.md` ("Progreso parcial (2026-09-03): ampliación de la
grilla de `eta` a 37 puntos") y la decisión formal en `DECISIONES_PENDIENTES.md`.

Con las tablas `final_vicsek_base_grid_steps3000_R20_v1_*` y
`final_voter_base_grid_steps3000_R20_v1_*` ya ampliadas a 37 puntos de `eta` (mismo
nombre de archivo, mismo protocolo, sin cambios de código en los scripts de figuras),
se re-ejecutó `python/generate_final_figures.py` y se regeneraron las `36` PNG de
`figures/final_production_v1/` sin modificar el script. Revisión visual: las curvas
`<va>` vs. `eta` y `<S>` vs. `eta` de ambos modelos, antes poligonales entre `eta=1` y
`eta=6`, ahora son sigmoides/decaimientos suaves, con las tres densidades bien
separadas y sin cruces salvo en la cola de ruido alto (`eta>=5`), zona de polarización
residual ya documentada como ruido estadístico.

Además se agregó `python/plot_vicsek_va_vs_eta_paper_style.py`, que grafica
`<va>` vs. `eta` de Vicsek (`rho=2,4,8`) replicando el estilo visual (colores,
marcador por densidad, leyenda sin marco) de una figura de referencia que el usuario
compartió como ejemplo de forma deseada; usa `va_stderr` como barra (en vez de
`va_stdev_between_realizations`) solo para esta figura de estilo, para igualar la
apariencia de barras finas de la referencia. Escribe
`figures/vicsek_va_vs_eta_paper_style_v1/vicsek_va_vs_eta_paper_style.png`.

Alcance: esta tarea cubre solo `rho=2,4,8` (matriz base) para ambos modelos; no tocó
el bloque de densidades bajas de clusters ni las series temporales `va(t)`/`S(t)`
(que usan `eta={0,0.40,6}`, puntos ya presentes en la grilla ampliada). No cierra el
punto A (animaciones) ni la maquetación lateral de parámetros en la PPT, que siguen
abiertos de tareas anteriores.

## Progreso parcial (2026-09-03): fotograma Vicsek `rho=2`, `eta=1` vs `eta=5`

A pedido del usuario se generó una figura estática lado a lado para comparar dos
estados avanzados del modelo Vicsek con `rho=2`: bajo ruido (`eta=1`) y alto ruido
(`eta=5`). Como las corridas de producción no guardaban trayectorias, se re-ejecutaron
solo esas dos realizaciones con `--write-trajectory`, usando semillas ya presentes en
la tabla final de producción:

```text
./build/simulate --model vicsek --rho-nominal 2 --rho-label rho_2 --N 200 --eta 1 --steps 3000 --base-seed 922000 --realization 0 --output-dir data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1 --observables-stride 100 --write-trajectory --trajectory-stride 10 --overwrite
./build/simulate --model vicsek --rho-nominal 2 --rho-label rho_2 --N 200 --eta 5 --steps 3000 --base-seed 930000 --realization 0 --output-dir data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1 --observables-stride 100 --write-trajectory --trajectory-stride 10 --overwrite
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/render_vicsek_rho2_eta1_eta5_snapshots.py
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache .venv-mpl311/bin/python python/render_vicsek_rho2_eta1_eta5_snapshots.py
```

Artefactos:

```text
python/render_vicsek_rho2_eta1_eta5_snapshots.py
figures/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek_rho2_eta1_eta5_t2000_side_by_side.png
figures/vicsek_rho2_eta1_eta5_snapshots_v1/README.md
```

Evidencia: cada `trajectory.csv` tiene `60200` filas (`N=200`, pasos `0..3000` cada
10 pasos), el renderizador validó `200` IDs únicos en `t=2000`, `theta` en `[0,2pi)`
y posiciones en la caja. La polarización instantánea del fotograma es
`va(t=2000)=0.927548` para `eta=1` y `0.088270` para `eta=5`, coherente con el
contraste esperado entre régimen ordenado y desordenado. Se inspeccionó visualmente el
PNG: ambos paneles comparten escala espacial, mapa de color angular y longitud visual
de flecha.

Alcance: este fotograma no cierra el punto A ni reemplaza las animaciones requeridas;
solo agrega una figura estática útil para la presentación o el informe.

## Criterio de cierre

- [ ] Hay animaciones independientes con vectores coloreados por ángulo.
  - Estado: **abierto**. El 2026-08-30 quedaron listos los *fotogramas estáticos de referencia* (`figures/reference_snapshots_v1/`, script `python/render_reference_snapshots.py`), que fijan la convención visual (un vector por partícula, color por ángulo con mapa cíclico). No hay video, GIF ni módulo animador todavía, por lo que el ítem sigue sin cerrarse.
- [x] `va(t)` y `S(t)` muestran y justifican `t_eq`.
  - Estado: cerrado el 2026-08-30. `figures/final_production_v1/` tiene `{vicsek,voter}_{va,S}_t_{rho_2,rho_4,rho_8}.png` (12 figuras) con `eta={0,0.40,6}`, banda de desvío entre realizaciones y línea vertical `t_eq=1500` rotulada, más `S(t)` para las tres densidades bajas de cada modelo.
- [x] `<va>` vs. `eta` cubre ambos modelos y `rho=2,4,8`.
  - Estado: cerrado el 2026-08-30. `figures/final_production_v1/{vicsek,voter}_va_vs_eta.png` (más zooms `eta<=0.5`) y `comparison_va_vs_eta.png`, los 14 puntos de la grilla común y `R=20` en ambos modelos.
- [x] `<S>` vs. `eta` incorpora las densidades adicionales solo en clusters.
  - Estado: cerrado el 2026-08-30. `figures/final_production_v1/{vicsek,voter}_S_vs_eta.png` para `rho=2,4,8` y `{vicsek,voter}_S_vs_eta_lowrho.png` para `N=32,16,11`, más zooms y `comparison_S_vs_eta_lowrho.png`. Las densidades bajas no se incorporaron a `<va>` vs. `eta` ni a `<va>` vs. `<S>`.
- [x] `<va>` vs. `<S>` usa `S` en x, `va` en y y las tres densidades base.
  - Estado: cerrado el 2026-08-30. `figures/final_production_v1/{vicsek,voter}_va_vs_S.png` y `comparison_va_vs_S.png`, con `x=<S>`, `y=<va>`, `rho=2,4,8` y barras en ambos ejes.
- [x] Todos los gráficos tienen barras definidas cuando corresponde.
  - Estado: cerrado el 2026-08-30 para las figuras finales. Las 36 PNG de `figures/final_production_v1/` usan desvío estándar entre realizaciones (`va_stdev_between_realizations`/`S_stdev_between_realizations` en curvas estacionarias, `va_stdev`/`S_stdev` como banda en series) y ninguna usa `*_stderr`. Las carpetas diagnósticas previas siguen con error estándar y quedan explícitamente fuera de la entrega.
- [x] Vicsek y votante se comparan bajo el mismo protocolo.
  - Estado: cerrado el 2026-08-30. `comparison_va_vs_eta.png`, `comparison_S_vs_eta_base.png`, `comparison_va_vs_S.png` y `comparison_S_vs_eta_lowrho.png`, con la misma grilla de 14 `eta`, `steps=3000`, `R=20`, `t_eq=1500` y la misma definición de barras en ambos modelos; un panel por densidad para mantener la legibilidad.
- [ ] Las exportaciones para diapositivas cumplen tamaños de fuente, ejes, símbolos y ubicación de parámetros de la guía.
  - Estado: en progreso. Las figuras finales usan fuente interna >=20 pt, no tienen título/caption ni grilla y conservan proporción. La auditoría del 2026-08-31 contra la guía oficial confirmó que los parámetros deben ubicarse **al costado**; varios bloques del borrador todavía aparecen debajo de las figuras. El render completo no tiene overflow, pero falta corregir esa maquetación antes de cerrar el criterio.
- [ ] La versión para exposición integra las animaciones y el PDF usa fotogramas con links probados.
