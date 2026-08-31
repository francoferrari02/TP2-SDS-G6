# Fotogramas estaticos de referencia (`reference_snapshots_v1`)

Imagenes fijas de las particulas con su vector de direccion, pensadas como
fotograma de referencia para las diapositivas (punto A del enunciado pide una
animacion; **esto no es una animacion**: no hay video, GIF ni animador todavia).

Generadas por `python/render_reference_snapshots.py`, que lee **exclusivamente**
archivos `trajectory.csv` ya escritos por el motor. El script no ejecuta
simulaciones ni depende del tiempo de computo del motor.

## Parametros comunes

| Parametro | Valor |
|---|---|
| `L` | 10 (caja periodica cuadrada) |
| `rho` | 2 |
| `N` | 200 |
| `rc`, `dt`, `v` | 1, 1, 0.03 |
| `steps` | 3000 |
| instante mostrado | `t = 2000` (ventana estacionaria, `t_eq = 1500`) |
| `--trajectory-stride` | 10 |
| realizacion | 0 (una sola realizacion por caso; los fotogramas son ilustrativos, no estadistica) |

## Archivos

| Archivo | Modelo | `eta` | `<va>` de la tabla final (`rho=2`, `R=20`) | `va` de esta realizacion en `t=2000` | `base_seed` | realizacion | `t` |
|---|---|---:|---:|---:|---:|---:|---:|
| `vicsek_rho2_snapshot.png` | Vicsek | 3.00 | 0.4627 | 0.5144 | 9100000 | 0 | 2000 |
| `voter_rho2_snapshot.png` | Votante | 0.40 | 0.4625 | 0.5153 | 9200000 | 0 | 2000 |
| `rho2_model_comparison_snapshot.png` | Vicsek (izq.) + Votante (der.) | 3.00 / 0.40 | 0.4627 / 0.4625 | 0.5144 / 0.5153 | 9100000 / 9200000 | 0 / 0 | 2000 |

La figura comparativa usa la **misma escala espacial** (`[0,10]x[0,10]`, aspecto
igual) y el **mismo mapeo de color angular** en los dos paneles.

### Por que estos `eta`

Los valores no se copiaron de ninguna otra fuente: se eligieron leyendo nuestras
tablas finales de produccion en `rho=2`.

- **Vicsek, `eta=3.00`**: en
  `data/summary/final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv` la
  polarizacion estacionaria en `rho=2` pasa de `0.9284` (`eta=1`) a `0.7336`
  (`eta=2`), `0.4627` (`eta=3`) y `0.1897` (`eta=4`). `eta=3` es el punto de
  polarizacion intermedia, dentro de la zona donde el orden cae.
- **Votante, `eta=0.40`**: en
  `data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv`, dentro de
  la zona fina `eta<=0.5`, `<va>` cae de `1.0000` (`eta=0`) a `0.7318`
  (`eta=0.20`) y `0.4625` (`eta=0.40`): el efecto del ruido ya es evidente. Ese
  valor ademas coincide practicamente con el `<va>` de Vicsek en `eta=3`
  (`0.4625` vs. `0.4627`), asi que la comparacion lado a lado enfrenta dos
  estados con el mismo grado de orden global alcanzado con ruidos muy distintos.

## Trayectorias fuente

```text
data/illustrations/reference_snapshots_v1/vicsek/rho_2/eta_3/steps_3000/realization_000_seed_9100000/trajectory.csv
data/illustrations/reference_snapshots_v1/voter/rho_2/eta_0p40000000000000002/steps_3000/realization_000_seed_9200000/trajectory.csv
```

Estas trayectorias viven en un directorio separado del resto de los datos
(`data/illustrations/`, ignorado por git como el resto de las salidas crudas) y
se regeneran de forma determinista con los comandos de abajo.

## Escala visual de las flechas

**Factor de escala visual: `15.0`.** La rapidez fisica es `v = 0.03` e **igual
para todas las particulas**; a escala `L = 10` una flecha de largo `0.03` seria
practicamente invisible. Por eso todas las flechas se dibujan con longitud
`v * 15 = 0.45` unidades de caja. Es un **unico factor comun aplicado a todas
las particulas, solo por legibilidad**: la longitud dibujada no codifica rapidez
ni ninguna diferencia entre particulas. Lo unico que varia entre particulas es
la direccion (`theta`), y todas tienen exactamente el mismo modulo fisico.

## Convencion de color

Color por `theta` con mapa **ciclico HSV**, normalizado a `[0, 2pi]`, con barra
de color angular rotulada en `0, pi/2, pi, 3pi/2, 2pi`. El mapa es ciclico
precisamente para que `theta=0` y `theta=2pi` tengan el mismo color, como
corresponde a un angulo. El mismo mapeo y la misma normalizacion se usan en las
tres imagenes, incluida la comparativa.

## Otras convenciones

- Caja `[0,10]x[0,10]`, aspecto igual, sin grilla de fondo, fondo blanco.
- Sin titulo interno, sin caption, sin texto de diapositiva ni links dentro del
  PNG (los parametros van al costado de la figura, en la diapositiva).
- Ejes rotulados con palabras, tamano de fuente `20` pt.
- Exportacion PNG a `220` dpi.

## Regeneracion exacta

```text
# 1) trayectorias (motor C++; solo hace falta si no existen)
./build/simulate --model vicsek --rho-nominal 2 --rho-label rho_2 --N 200 \
    --eta 3 --steps 3000 --base-seed 9100000 --realization 0 \
    --output-dir data/illustrations/reference_snapshots_v1 \
    --observables-stride 100 --write-trajectory --trajectory-stride 10

./build/simulate --model voter --rho-nominal 2 --rho-label rho_2 --N 200 \
    --eta 0.40 --steps 3000 --base-seed 9200000 --realization 0 \
    --output-dir data/illustrations/reference_snapshots_v1 \
    --observables-stride 100 --write-trajectory --trajectory-stride 10

# 2) render de los tres PNG (solo lee trajectory.csv)
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache \
    .venv-mpl311/bin/python python/render_reference_snapshots.py
```

Valores por defecto del render: `--time 2000`, `--arrow-scale 15.0`,
`--box-size 10.0`, `--speed 0.03`,
`--out-dir figures/reference_snapshots_v1`.

## Verificacion realizada

- Cada `trajectory.csv` tiene exactamente `200` IDs unicos en `t=2000`.
- `theta` en `[0, 2pi)` y posiciones dentro de `[0,10]x[0,10]` en ambos casos.
- Las tres imagenes se inspeccionaron visualmente.
- `python3 -m py_compile python/render_reference_snapshots.py` sin errores.
