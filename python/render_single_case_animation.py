#!/usr/bin/env python3
"""Animacion MP4 de un unico caso (un modelo, un eta), con va(t)/S(t) en vivo como texto.

Un solo panel de particulas (flecha por particula, color = theta, mapa HSV,
caja [0,10]x[0,10], igual estilo que los fotogramas estaticos), que
evoluciona con la trayectoria real. Debajo, en texto (sin subplots de
lineas), el eta fijo del caso y los valores de va(t) y S(t) actualizandose
en cada fotograma.

Lee exclusivamente `trajectory.csv` y `observables.csv` ya escritos por el
motor (mismo stride en ambos). No ejecuta simulaciones.

Requiere ffmpeg instalado (brew install ffmpeg) para el writer de MP4.
"""

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402

TWO_PI = 2.0 * math.pi
CMAP = "hsv"


def read_observables_csv(path: Path):
    rows = []
    header = None
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                if line.startswith("#"):
                    continue
                continue
            if header is None:
                header = next(csv.reader([line]))
                continue
            fields = next(csv.reader([line]))
            rows.append({
                "t": int(fields[header.index("t")]),
                "va": float(fields[header.index("va")]),
                "S": float(fields[header.index("S")]),
            })
    return rows


def read_trajectory_csv(path: Path):
    header = None
    by_t = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if header is None:
                header = next(csv.reader([line]))
                continue
            fields = next(csv.reader([line]))
            t = int(fields[header.index("t")])
            x = float(fields[header.index("x")])
            y = float(fields[header.index("y")])
            theta = float(fields[header.index("theta")])
            by_t.setdefault(t, []).append((x, y, theta))
    return by_t


def render(label: str, trajectory: Path, observables: Path, out_path: Path,
           box_size=10.0, speed=0.03, arrow_scale=15.0, fps=20, dpi=150):
    fontsize = 20
    traj_by_t = read_trajectory_csv(trajectory)
    obs_rows = read_observables_csv(observables)
    ts = sorted(traj_by_t.keys())
    obs_by_t = {r["t"]: r for r in obs_rows}
    n_frames = len(ts)
    drawn_length = speed * arrow_scale

    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0.0, box_size)
    ax.set_ylim(0.0, box_size)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.set_xlabel("Posición x", fontsize=fontsize)
    ax.set_ylabel("Posición y", fontsize=fontsize)
    ax.tick_params(labelsize=fontsize - 2)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([0, 2, 4, 6, 8, 10])

    t0 = ts[0]
    p0 = traj_by_t[t0]
    xs0 = [p[0] for p in p0]
    ys0 = [p[1] for p in p0]
    th0 = [p[2] for p in p0]
    us0 = [drawn_length * math.cos(th) for th in th0]
    vs0 = [drawn_length * math.sin(th) for th in th0]
    q = ax.quiver(xs0, ys0, us0, vs0, th0, cmap=CMAP, norm=Normalize(vmin=0.0, vmax=TWO_PI),
                  angles="xy", scale_units="xy", scale=1.0, width=0.007,
                  headwidth=3.4, headlength=4.2, headaxislength=3.8, pivot="tail")

    mappable = ScalarMappable(norm=Normalize(vmin=0.0, vmax=TWO_PI), cmap=CMAP)
    mappable.set_array([])
    cbar = fig.colorbar(mappable, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_ticks([0.0, math.pi / 2, math.pi, 3 * math.pi / 2, TWO_PI])
    cbar.set_ticklabels(["0", "pi/2", "pi", "3pi/2", "2pi"])
    cbar.set_label(r"$\theta$ (rad)", fontsize=fontsize)
    cbar.ax.tick_params(labelsize=fontsize - 2)

    txt = ax.text(0.5, -0.19, "", transform=ax.transAxes, ha="center", va="top", fontsize=fontsize)

    def init():
        return [q, txt]

    def update(frame_idx):
        t = ts[frame_idx]
        particles = traj_by_t[t]
        xs = [p[0] for p in particles]
        ys = [p[1] for p in particles]
        thetas = [p[2] for p in particles]
        us = [drawn_length * math.cos(th) for th in thetas]
        vs = [drawn_length * math.sin(th) for th in thetas]
        q.set_offsets(list(zip(xs, ys)))
        q.set_UVC(us, vs, thetas)
        obs = obs_by_t.get(t)
        va_now = obs["va"] if obs else float("nan")
        s_now = obs["S"] if obs else float("nan")
        txt.set_text(f"{label}\n" + r"$v_a(t)$" + f"={va_now:.3f},  " + r"$S(t)$" + f"={s_now:.3f}")
        return [q, txt]

    fig.subplots_adjust(left=0.14, right=0.83, top=0.97, bottom=0.14)

    anim = animation.FuncAnimation(fig, update, frames=n_frames, init_func=init,
                                    blit=False, interval=1000 / fps)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out_path), writer=writer, dpi=dpi)
    plt.close(fig)
    print(f"escrito: {out_path} ({n_frames} fotogramas, {n_frames / fps:.1f}s a {fps} fps)")
