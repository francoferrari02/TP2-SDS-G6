#!/usr/bin/env python3
"""Render de fotogramas estaticos de referencia para la presentacion.

Genera imagenes fijas (PNG) de las particulas con su vector de direccion, a
partir EXCLUSIVAMENTE de archivos `trajectory.csv` ya escritos por el motor.
Este script no ejecuta simulaciones, no depende del tiempo de computo del
motor y no produce videos ni animaciones: son fotogramas de referencia para
las diapositivas.

Convencion visual:

- caja cuadrada [0,L]x[0,L] con aspecto igual, sin grilla de fondo;
- una flecha por particula, con origen en su posicion (x,y);
- direccion dada por theta;
- color dado por theta con un mapa ciclico (HSV), barra de color de 0 a 2pi;
- la rapidez fisica es constante (v=0.03 para todas las particulas). Ese
  modulo es practicamente invisible en una caja de L=10, asi que la longitud
  dibujada se amplifica por un unico factor comun (`--arrow-scale`) igual
  para todas las particulas: la longitud en pantalla NO codifica rapidez.

Uso:
    python3 python/render_reference_snapshots.py [--time 2000]
        [--arrow-scale 15.0] [--out-dir figures/reference_snapshots_v1]
"""

import argparse
import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

TWO_PI = 2.0 * math.pi
CYCLIC_CMAP = "hsv"
DPI = 220

# Casos elegidos a partir de las tablas finales de produccion
# (data/summary/final_{vicsek,voter}_base_grid_steps3000_R20_v1_by_combo.csv),
# ambos con rho=2, N=200, L=10, steps=3000:
#
#   vicsek eta=3.00 -> <va>=0.4627 (zona donde cae el orden)
#   voter  eta=0.40 -> <va>=0.4625 (zona fina eta<=0.5, ruido ya visible)
CASES = {
    "vicsek": {
        "label": "Vicsek",
        "eta": 3.0,
        "eta_text": "3.00",
        "va_mean_final_table": 0.4627,
        "base_seed": 9100000,
        "realization": 0,
        "trajectory": (
            "data/illustrations/reference_snapshots_v1/vicsek/rho_2/eta_3/"
            "steps_3000/realization_000_seed_9100000/trajectory.csv"
        ),
        "png": "vicsek_rho2_snapshot.png",
    },
    "voter": {
        "label": "Votante",
        "eta": 0.40,
        "eta_text": "0.40",
        "va_mean_final_table": 0.4625,
        "base_seed": 9200000,
        "realization": 0,
        "trajectory": (
            "data/illustrations/reference_snapshots_v1/voter/rho_2/"
            "eta_0p40000000000000002/steps_3000/"
            "realization_000_seed_9200000/trajectory.csv"
        ),
        "png": "voter_rho2_snapshot.png",
    },
}

COMPARISON_PNG = "rho2_model_comparison_snapshot.png"


def read_snapshot(path: Path, t_target: int):
    """Devuelve (xs, ys, thetas, metadatos) del instante t_target."""
    if not path.exists():
        raise SystemExit(f"No existe la trayectoria esperada: {path}")

    meta = {}
    xs, ys, thetas, ids = [], [], [], []
    header = None
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                body = line[1:].strip()
                if "=" in body:
                    key, value = body.split("=", 1)
                    meta[key.strip()] = value.strip()
                continue
            if header is None:
                header = next(csv.reader([line]))
                continue
            fields = line.split(",")
            if int(fields[header.index("t")]) != t_target:
                continue
            ids.append(int(fields[header.index("id")]))
            xs.append(float(fields[header.index("x")]))
            ys.append(float(fields[header.index("y")]))
            thetas.append(float(fields[header.index("theta")]))

    if not xs:
        raise SystemExit(f"La trayectoria {path} no contiene el instante t={t_target}.")
    if len(set(ids)) != len(ids):
        raise SystemExit(f"IDs repetidos en t={t_target} dentro de {path}.")
    for theta in thetas:
        if not (0.0 <= theta < TWO_PI):
            raise SystemExit(f"theta fuera de [0,2pi) en {path}: {theta}")
    return xs, ys, thetas, meta


def draw_panel(ax, xs, ys, thetas, box_size, arrow_scale, physical_speed, fontsize):
    ax.set_xlim(0.0, box_size)
    ax.set_ylim(0.0, box_size)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.set_xlabel("x (unidades de caja)", fontsize=fontsize)
    ax.set_ylabel("y (unidades de caja)", fontsize=fontsize)
    ax.tick_params(labelsize=fontsize - 2)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([0, 2, 4, 6, 8, 10])

    drawn_length = physical_speed * arrow_scale
    us = [drawn_length * math.cos(theta) for theta in thetas]
    vs = [drawn_length * math.sin(theta) for theta in thetas]

    ax.quiver(
        xs, ys, us, vs, thetas,
        cmap=CYCLIC_CMAP,
        norm=Normalize(vmin=0.0, vmax=TWO_PI),
        angles="xy",
        scale_units="xy",
        scale=1.0,
        width=0.007,
        headwidth=3.4,
        headlength=4.2,
        headaxislength=3.8,
        pivot="tail",
    )


def add_angle_colorbar(fig, axes, fontsize):
    mappable = ScalarMappable(norm=Normalize(vmin=0.0, vmax=TWO_PI), cmap=CYCLIC_CMAP)
    mappable.set_array([])
    cbar = fig.colorbar(mappable, ax=axes, fraction=0.046, pad=0.03)
    cbar.set_ticks([0.0, math.pi / 2, math.pi, 3 * math.pi / 2, TWO_PI])
    cbar.set_ticklabels(["0", "pi/2", "pi", "3pi/2", "2pi"])
    cbar.set_label("theta (rad)", fontsize=fontsize)
    cbar.ax.tick_params(labelsize=fontsize - 2)
    return cbar


def render_single(case_key, snapshot, out_path, box_size, arrow_scale, speed):
    xs, ys, thetas, _meta = snapshot
    fontsize = 20
    fig, ax = plt.subplots(figsize=(8.2, 7.4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    draw_panel(ax, xs, ys, thetas, box_size, arrow_scale, speed, fontsize)
    add_angle_colorbar(fig, ax, fontsize)
    fig.savefig(out_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_comparison(snapshots, out_path, box_size, arrow_scale, speed):
    fontsize = 20
    fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.4))
    fig.patch.set_facecolor("white")
    for ax, key in zip(axes, ("vicsek", "voter")):
        xs, ys, thetas, _meta = snapshots[key]
        ax.set_facecolor("white")
        draw_panel(ax, xs, ys, thetas, box_size, arrow_scale, speed, fontsize)
    axes[1].set_ylabel("")
    add_angle_colorbar(fig, list(axes), fontsize)
    fig.savefig(out_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time", type=int, default=2000,
                        help="instante estacionario guardado a renderizar")
    parser.add_argument("--arrow-scale", type=float, default=15.0,
                        help="factor visual comun de longitud de flecha "
                             "(no cambia la rapidez fisica, que es v=0.03 para todas)")
    parser.add_argument("--box-size", type=float, default=10.0)
    parser.add_argument("--speed", type=float, default=0.03)
    parser.add_argument("--out-dir", type=Path,
                        default=REPO_ROOT / "figures" / "reference_snapshots_v1")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    figures_root = (REPO_ROOT / "figures").resolve()
    if figures_root not in out_dir.parents and out_dir != figures_root:
        print(f"--out-dir debe estar dentro de {figures_root}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshots = {}
    for key, case in CASES.items():
        path = REPO_ROOT / case["trajectory"]
        snapshots[key] = read_snapshot(path, args.time)
        print(f"{key}: {len(snapshots[key][0])} particulas en t={args.time} "
              f"desde {case['trajectory']}")

    written = []
    for key, case in CASES.items():
        written.append(render_single(key, snapshots[key], out_dir / case["png"],
                                     args.box_size, args.arrow_scale, args.speed))
    written.append(render_comparison(snapshots, out_dir / COMPARISON_PNG,
                                     args.box_size, args.arrow_scale, args.speed))

    for path in written:
        print(f"escrito: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
