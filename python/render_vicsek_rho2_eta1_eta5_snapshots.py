#!/usr/bin/env python3
"""Render de dos fotogramas Vicsek rho=2 para eta=1 y eta=5.

Lee exclusivamente `trajectory.csv` generados por el motor y produce una figura
estatica lado a lado. No ejecuta simulaciones ni depende del tiempo de computo
del motor.
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
DPI = 220
CMAP = "hsv"

CASES = [
    {
        "eta": "1",
        "label": r"$\eta=1$",
        "seed": 922000,
        "trajectory": (
            "data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/"
            "rho_2/eta_1/steps_3000/realization_000_seed_922000/trajectory.csv"
        ),
    },
    {
        "eta": "5",
        "label": r"$\eta=5$",
        "seed": 930000,
        "trajectory": (
            "data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/"
            "rho_2/eta_5/steps_3000/realization_000_seed_930000/trajectory.csv"
        ),
    },
]


def read_snapshot(path: Path, t_target: int):
    if not path.exists():
        raise SystemExit(f"No existe la trayectoria: {path}")

    meta = {}
    rows = []
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

            fields = next(csv.reader([line]))
            t = int(fields[header.index("t")])
            if t != t_target:
                continue
            rows.append({
                "id": int(fields[header.index("id")]),
                "x": float(fields[header.index("x")]),
                "y": float(fields[header.index("y")]),
                "theta": float(fields[header.index("theta")]),
            })

    if not rows:
        raise SystemExit(f"{path} no contiene t={t_target}.")
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"IDs repetidos en {path} para t={t_target}.")
    expected_n = int(meta.get("N", "0"))
    if expected_n and len(rows) != expected_n:
        raise SystemExit(f"{path}: se esperaban {expected_n} particulas y se leyeron {len(rows)}.")
    for row in rows:
        if not (0.0 <= row["x"] <= 10.0 and 0.0 <= row["y"] <= 10.0):
            raise SystemExit(f"posicion fuera de caja en {path}: {row}")
        if not (0.0 <= row["theta"] < TWO_PI):
            raise SystemExit(f"theta fuera de [0,2pi) en {path}: {row['theta']}")
    return rows, meta


def polarization(rows):
    sx = sum(math.cos(row["theta"]) for row in rows)
    sy = sum(math.sin(row["theta"]) for row in rows)
    return math.hypot(sx, sy) / len(rows)


def draw_panel(ax, rows, box_size, speed, arrow_scale, fontsize):
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]
    thetas = [row["theta"] for row in rows]
    drawn_length = speed * arrow_scale
    us = [drawn_length * math.cos(theta) for theta in thetas]
    vs = [drawn_length * math.sin(theta) for theta in thetas]

    ax.quiver(
        xs,
        ys,
        us,
        vs,
        thetas,
        cmap=CMAP,
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
    ax.set_xlim(0.0, box_size)
    ax.set_ylim(0.0, box_size)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.tick_params(labelsize=fontsize - 2)
    ax.set_xlabel("Posición x", fontsize=fontsize)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time", type=int, default=2000)
    parser.add_argument("--box-size", type=float, default=10.0)
    parser.add_argument("--speed", type=float, default=0.03)
    parser.add_argument("--arrow-scale", type=float, default=15.0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "figures" / "vicsek_rho2_eta1_eta5_snapshots_v1",
    )
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    figures_root = (REPO_ROOT / "figures").resolve()
    if out_dir != figures_root and figures_root not in out_dir.parents:
        print(f"--out-dir debe estar dentro de {figures_root}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshots = []
    for case in CASES:
        rows, meta = read_snapshot(REPO_ROOT / case["trajectory"], args.time)
        va = polarization(rows)
        snapshots.append((case, rows, meta, va))
        print(
            f"eta={case['eta']}: {len(rows)} particulas, t={args.time}, "
            f"va(t)={va:.6f}, trayectoria={case['trajectory']}"
        )

    fontsize = 20
    fig, axes = plt.subplots(1, 2, figsize=(15.2, 8.0), constrained_layout=True)
    fig.patch.set_facecolor("white")
    for ax, (case, rows, _meta, va) in zip(axes, snapshots):
        ax.set_facecolor("white")
        draw_panel(ax, rows, args.box_size, args.speed, args.arrow_scale, fontsize)
        ax.set_title(
            case["label"] + ",  " + r"$v_a(t)$" + f"={va:.3f}",
            fontsize=fontsize, pad=14, y=-0.30,
        )
    axes[0].set_ylabel("Posición y", fontsize=fontsize)
    axes[1].set_ylabel("")

    mappable = ScalarMappable(norm=Normalize(vmin=0.0, vmax=TWO_PI), cmap=CMAP)
    mappable.set_array([])
    colorbar = fig.colorbar(mappable, ax=list(axes), fraction=0.046, pad=0.02)
    colorbar.set_ticks([0.0, math.pi / 2, math.pi, 3.0 * math.pi / 2, TWO_PI])
    colorbar.set_ticklabels(["0", "pi/2", "pi", "3pi/2", "2pi"])
    colorbar.set_label(r"$\theta$ (rad)", fontsize=fontsize)
    colorbar.ax.tick_params(labelsize=fontsize - 2)

    out_path = out_dir / "vicsek_rho2_eta1_eta5_t2000_side_by_side.png"
    fig.savefig(out_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)

    readme = out_dir / "README.md"
    readme.write_text(
        "# Fotogramas Vicsek rho=2, eta=1 y eta=5\n\n"
        "Figura estatica lado a lado generada desde `trajectory.csv`, sin ejecutar "
        "simulacion dentro del renderizador.\n\n"
        "## Protocolo\n\n"
        "- Modelo: Vicsek.\n"
        "- Densidad: `rho=2`, `N=200`, `L=10`.\n"
        f"- Tiempo mostrado: `t={args.time}` (`t_eq=1500`, ventana estacionaria).\n"
        "- Corridas: `steps=3000`, `trajectory_stride=10`, `observables_stride=100`.\n"
        "- Panel izquierdo: `eta=1`, `base_seed=922000`, realizacion `0`.\n"
        "- Panel derecho: `eta=5`, `base_seed=930000`, realizacion `0`.\n"
        "- Color: angulo `theta` en radianes, mapa ciclico HSV.\n"
        "- Longitud: rapidez fisica constante `v=0.03` amplificada por factor comun "
        f"`{args.arrow_scale}` solo por legibilidad.\n\n"
        "## Archivos\n\n"
        f"- PNG: `{out_path.relative_to(REPO_ROOT)}`\n"
        f"- Script: `python/{Path(__file__).name}`\n\n"
        "## Evidencia\n\n"
        + "\n".join(
            f"- `eta={case['eta']}`: `N={len(rows)}`, `va(t={args.time})={va:.6f}`, "
            f"`trajectory={case['trajectory']}`."
            for case, rows, _meta, va in snapshots
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"escrito: {out_path}")
    print(f"escrito: {readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
