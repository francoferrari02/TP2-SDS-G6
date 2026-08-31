# Figuras finales de producción del TP2 (`final_production_v1`)

Este directorio contiene **las figuras finales** del TP2. Es independiente de las
carpetas diagnósticas anteriores de `figures/` (`vicsek_eta0_6_deta0p5_steps3000_R20_v1/`,
`vicsek_lowrho_cluster_study_1/`, etc.), que se conservan como evidencia histórica y
**no** deben usarse en la presentación ni en el informe: usan error estándar en vez de
desvío estándar entre realizaciones y no cubren la grilla común completa.

Todas las PNG de esta carpeta se generan con un único script, a partir de tres tablas
consolidadas, sin ejecutar simulaciones ni recomputar observables.

## Protocolo (vinculante, idéntico en las 36 figuras)

```text
modelos          {vicsek, voter}
L=10  rc=1  dt=1  v=0.03
eta              {0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}  (14 puntos, rad)
rho base         {2, 4, 8}                      -> N = {200, 400, 800}
rho bajas        {1/pi, 1/(2pi), 1/(3pi)}       -> N = {32, 16, 11}  (solo clusters)
steps            3000
R                20 realizaciones independientes por combinación
t_eq             1500
ventana estac.   t = 1500..3000
```

El escalar estacionario de cada realización es el promedio temporal del observable en
`t=1500..3000`; luego se promedia entre las `R=20` realizaciones.

## Definición de las barras

| Tipo de figura | Qué se dibuja | Columna usada |
|---|---|---|
| Curvas estacionarias (`*_vs_eta*`, `*_va_vs_S*`) | barra de error | `va_stdev_between_realizations`, `S_stdev_between_realizations` |
| Series temporales (`*_t_*`) | banda sombreada | `va_stdev`, `S_stdev` (desvío entre realizaciones en cada instante `t`) |

**No se usa error estándar** (`*_stderr`) en ninguna figura de esta carpeta. En
`*_va_vs_S*` la barra horizontal es el desvío de `<S>` y la vertical el de `<va>`.

## Colores y estilos

El color identifica **siempre la misma densidad** en todas las figuras:

| Densidad | Color | Uso |
|---|---|---|
| `rho=2` (N=200) | azul `#1f77b4` | matriz base |
| `rho=4` (N=400) | rojo `#d62728` | matriz base |
| `rho=8` (N=800) | verde `#2ca02c` | matriz base |
| `rho=1/pi` (N=32) | violeta `#7b3294` | solo clusters |
| `rho=1/(2pi)` (N=16) | naranja `#e08214` | solo clusters |
| `rho=1/(3pi)` (N=11) | verde azulado `#01665e` | solo clusters |

En las figuras de comparación el **modelo** se distingue por marcador y estilo de línea,
conservando el color de la densidad: Vicsek = círculo lleno + línea continua;
votante = cuadrado vacío + línea de trazos.

En las series temporales el color identifica el valor de `eta` (`0` azul, `0.40` naranja,
`6` verde) y la línea vertical punteada negra marca `t_eq=1500`.

## Convenciones de presentación aplicadas

- Sin título interno ni *caption* dentro de la figura: el contenido se identifica por el
  nombre de archivo y por esta tabla. Los parámetros van al costado de la figura en la
  diapositiva.
- Sin grilla de fondo.
- `va` y `S` en figuras separadas; eje `y` en `[0,1]` con margen visual mínimo
  (`[-0.04, 1.04]`). Una barra de error puede quedar recortada en `rho` bajas: el rango
  `[0,1]` es el rango físico del observable y se conserva.
- Cada punto del barrido es visible; las líneas solo conectan puntos consecutivos del
  barrido de `eta` como guía visual, no son un ajuste ni una interpolación.
- Fuente ≥ 20 pt (ejes 23 pt, ticks 20 pt, leyenda 19 pt). PNG a **220 dpi**.

## Tablas fuente

```text
data/summary/final_vicsek_base_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv
data/summary/final_voter_base_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv
data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_{manifest,by_realization,by_combo,series_sampled}.csv
```

Cada una lleva `source_run` con el lote de origen de cada fila:

| Tabla consolidada | Filas `by_realization` | Combinaciones | Lotes de origen |
|---|---:|---:|---|
| `final_vicsek_base_grid_steps3000_R20_v1` | 840 | 42 | `final_fine_grid_steps3000_R20_v1` (vicsek), `vicsek_eta0_6_deta0p5_steps3000_R20_v1` |
| `final_voter_base_grid_steps3000_R20_v1` | 840 | 42 | `final_fine_grid_steps3000_R20_v1` (voter), `final_voter_base_coarse_v1` |
| `final_lowrho_cluster_grid_steps3000_R20_v1` | 1680 | 84 | `vicsek_lowrho_cluster_study_1`, `final_voter_lowrho_grid_v1` |

## Archivos generados y punto del enunciado que cubren

36 PNG. Los puntos son los de `bibliografia/enunciado_tp2_guia_de_trabajo.md`, sección 4.

### Vicsek base — `rho={2,4,8}`

| Archivo | Punto | Contenido |
|---|:--:|---|
| `vicsek_va_vs_eta.png` | C | `<va>` vs. `eta`, 14 puntos, tres densidades |
| `vicsek_va_vs_eta_zoom_0_0p5.png` | C | idem, zoom `eta<=0.5` |
| `vicsek_S_vs_eta.png` | D | `<S>` vs. `eta`, tres densidades |
| `vicsek_S_vs_eta_zoom_0_0p5.png` | D | idem, zoom `eta<=0.5` |
| `vicsek_va_vs_S.png` | E | `x=<S>`, `y=<va>`; cada punto es un `eta` |

### Votante base — `rho={2,4,8}`

| Archivo | Punto | Contenido |
|---|:--:|---|
| `voter_va_vs_eta.png` | F sobre C | `<va>` vs. `eta` |
| `voter_va_vs_eta_zoom_0_0p5.png` | F sobre C | idem, zoom `eta<=0.5` |
| `voter_S_vs_eta.png` | F sobre D | `<S>` vs. `eta` |
| `voter_S_vs_eta_zoom_0_0p5.png` | F sobre D | idem, zoom `eta<=0.5` |
| `voter_va_vs_S.png` | F sobre E | `x=<S>`, `y=<va>` |

### Series temporales de la matriz base

Cada figura muestra ruido bajo y alto (`eta={0, 0.40, 6}`) con banda de desvío entre
realizaciones y la línea vertical `t_eq=1500`.

| Archivo | Punto | Contenido |
|---|:--:|---|
| `vicsek_va_t_rho_2.png`, `vicsek_va_t_rho_4.png`, `vicsek_va_t_rho_8.png` | B | `va(t)` de Vicsek por densidad |
| `vicsek_S_t_rho_2.png`, `vicsek_S_t_rho_4.png`, `vicsek_S_t_rho_8.png` | D | `S(t)` de Vicsek por densidad |
| `voter_va_t_rho_2.png`, `voter_va_t_rho_4.png`, `voter_va_t_rho_8.png` | F sobre B | `va(t)` del votante por densidad |
| `voter_S_t_rho_2.png`, `voter_S_t_rho_4.png`, `voter_S_t_rho_8.png` | F sobre D | `S(t)` del votante por densidad |

### Clusters en densidades bajas — `rho={1/pi, 1/(2pi), 1/(3pi)}`

Extensión del punto D únicamente. Estas densidades **no** entran en `<va>` vs. `eta`
ni en `<va>` vs. `<S>`, según la decisión registrada en `plan_desarrollo_tp2/`.

| Archivo | Punto | Contenido |
|---|:--:|---|
| `vicsek_S_vs_eta_lowrho.png` | D | `<S>` vs. `eta`, tres densidades bajas |
| `vicsek_S_vs_eta_lowrho_zoom_0_0p5.png` | D | idem, zoom `eta<=0.5` |
| `vicsek_S_t_rho_1_over_pi_lowrho.png` | D | `S(t)` de Vicsek, `N=32` |
| `vicsek_S_t_rho_1_over_2pi_lowrho.png` | D | `S(t)` de Vicsek, `N=16` |
| `vicsek_S_t_rho_1_over_3pi_lowrho.png` | D | `S(t)` de Vicsek, `N=11` |
| `voter_S_vs_eta_lowrho.png` | F sobre D | `<S>` vs. `eta`, votante |
| `voter_S_vs_eta_lowrho_zoom_0_0p5.png` | F sobre D | idem, zoom `eta<=0.5` |
| `voter_S_t_rho_1_over_pi_lowrho.png` | F sobre D | `S(t)` del votante, `N=32` |
| `voter_S_t_rho_1_over_2pi_lowrho.png` | F sobre D | `S(t)` del votante, `N=16` |
| `voter_S_t_rho_1_over_3pi_lowrho.png` | F sobre D | `S(t)` del votante, `N=11` |

### Comparación entre modelos

Un panel por densidad, para que la comparación sea legible sin superponer seis curvas.

| Archivo | Punto | Contenido |
|---|:--:|---|
| `comparison_va_vs_eta.png` | F | `<va>` vs. `eta`, Vicsek vs. votante, 3 paneles (`rho=2,4,8`) |
| `comparison_S_vs_eta_base.png` | F | `<S>` vs. `eta`, ambos modelos, 3 paneles (`rho=2,4,8`) |
| `comparison_va_vs_S.png` | F | `<va>` vs. `<S>`, ambos modelos, 3 paneles (`rho=2,4,8`) |
| `comparison_S_vs_eta_lowrho.png` | F sobre D | `<S>` vs. `eta`, ambos modelos, 3 paneles de densidad baja |

## Comandos de regeneración

Desde la raíz del repositorio. Los dos primeros comandos solo consolidan tablas ya
existentes (no corren simulaciones); el tercero solo lee esas tablas y escribe PNG.

```bash
# 1. Consolidar la tabla final del votante base (rho=2,4,8)
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/build_final_voter_base_table.py

# 2. Consolidar la tabla final de clusters en densidades bajas (ambos modelos)
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/build_final_lowrho_cluster_table.py

# (la tabla final de Vicsek base ya se consolida con)
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/build_final_vicsek_base_table.py

# 3. Generar las 36 figuras finales
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache \
  .venv-mpl311/bin/python python/generate_final_figures.py
```

`matplotlib` no está instalado en el `python3` del sistema; se usa el entorno
`.venv-mpl311` (matplotlib 3.8.4). Los scripts de consolidación usan solo biblioteca
estándar.

`generate_final_figures.py` acepta `--out-dir`, pero rechaza cualquier destino fuera de
`figures/`; por defecto escribe en esta carpeta y no toca ninguna otra.

## Qué NO hay acá

Animaciones, videos, benchmark del CIM, informe y presentación. Tampoco susceptibilidad,
`eta_c`, ajustes críticos ni ningún análisis fuera de los puntos A-F del enunciado.
