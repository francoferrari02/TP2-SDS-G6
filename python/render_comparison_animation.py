#!/usr/bin/env python3
"""Animacion MP4 de dos casos lado a lado (bajo/alto ruido), con va(t)/S(t) en vivo.

Generaliza render_vicsek_rho2_eta1_eta5_snapshots.py /
render_voter_rho2_eta0p5_eta1_snapshots.py (que producen un unico fotograma
estatico en t=2000) a una animacion completa: arriba, dos paneles de
partículas (flechas por particula, color = theta, mapa HSV, misma caja
[0,10]x[0,10]) que evolucionan con la trayectoria real; abajo, dos paneles
de lineas que van dibujando va(t) y S(t) a medida que avanza la animacion,
con una marca vertical en el instante actual.

Lee exclusivamente `trajectory.csv` y `observables.csv` ya escritos por el
motor (mismo stride en ambos, para que cada fotograma de flechas tenga su
va/S exacto correspondiente). No ejecuta simulaciones.

Requiere ffmpeg instalado (brew install ffmpeg) para el writer de MP4.

Uso (ver los dos lanzadores concretos: render_vicsek_rho2_eta1_eta5_animation.py,
render_voter_rho2_eta0p1_eta1_animation.py):
    python3 python/render_comparison_animation.py --help
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

REPO_ROOT = Path(__file__).resolve().parent.parent
TWO_PI = 2.0 * math.pi
CMAP = "hsv"


def read_observables_csv(path: Path):
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
            rows.append({
                "t": int(fields[header.index("t")]),
                "va": float(fields[header.index("va")]),
                "S": float(fields[header.index("S")]),
            })
    return meta, rows


def read_trajectory_csv(path: Path):
    """Devuelve dict t -> (xs, ys, thetas), ordenado por id."""
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


def render(cases, out_path: Path, box_size=10.0, speed=0.03, arrow_scale=15.0,
           fps=20, dpi=150):
    """cases: lista de dicts {label, trajectory (Path), observables (Path)}."""
    fontsize = 18
    loaded = []
    for case in cases:
        traj_by_t = read_trajectory_csv(case["trajectory"])
        _meta, obs_rows = read_observables_csv(case["observables"])
        ts_sorted = sorted(traj_by_t.keys())
        obs_by_t = {r["t"]: r for r in obs_rows}
        loaded.append({**case, "traj_by_t": traj_by_t, "ts": ts_sorted, "obs_by_t": obs_by_t})

    n_frames = len(loaded[0]["ts"])
    for case in loaded:
        if len(case["ts"]) != n_frames:
            raise SystemExit(f"Los casos no tienen la misma cantidad de fotogramas: {case['label']}")

    t_max = loaded[0]["ts"][-1]

    fig = plt.figure(figsize=(14.0, 10.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.2, 1.0], hspace=0.85, wspace=0.25)
    fig.patch.set_facecolor("white")

    quiver_axes = [fig.add_subplot(gs[0, i]) for i in range(2)]
    line_axes = [fig.add_subplot(gs[1, i]) for i in range(2)]

    quivers = []
    case_texts = []
    drawn_length = speed * arrow_scale
    for ax, case in zip(quiver_axes, loaded):
        ax.set_xlim(0.0, box_size)
        ax.set_ylim(0.0, box_size)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(False)
        ax.set_facecolor("white")
        ax.set_xlabel("Posición x", fontsize=fontsize)
        ax.tick_params(labelsize=fontsize - 3)
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_yticks([0, 2, 4, 6, 8, 10])
        t0 = case["ts"][0]
        p0 = case["traj_by_t"][t0]
        xs0 = [p[0] for p in p0]
        ys0 = [p[1] for p in p0]
        th0 = [p[2] for p in p0]
        us0 = [drawn_length * math.cos(th) for th in th0]
        vs0 = [drawn_length * math.sin(th) for th in th0]
        q = ax.quiver(xs0, ys0, us0, vs0, th0, cmap=CMAP, norm=Normalize(vmin=0.0, vmax=TWO_PI),
                      angles="xy", scale_units="xy", scale=1.0, width=0.007,
                      headwidth=3.4, headlength=4.2, headaxislength=3.8, pivot="tail")
        quivers.append(q)
        txt = ax.text(0.5, -0.24, "", transform=ax.transAxes, ha="center", va="top", fontsize=fontsize)
        case_texts.append(txt)
    quiver_axes[0].set_ylabel("Posición y", fontsize=fontsize)

    mappable = ScalarMappable(norm=Normalize(vmin=0.0, vmax=TWO_PI), cmap=CMAP)
    mappable.set_array([])
    cbar = fig.colorbar(mappable, ax=quiver_axes, fraction=0.046, pad=0.02)
    cbar.set_ticks([0.0, math.pi / 2, math.pi, 3 * math.pi / 2, TWO_PI])
    cbar.set_ticklabels(["0", "pi/2", "pi", "3pi/2", "2pi"])
    cbar.set_label(r"$\theta$ (rad)", fontsize=fontsize)
    cbar.ax.tick_params(labelsize=fontsize - 3)

    case_colors = ["#08519c", "#e6550d"]

    line_specs = [("va", r"polarización $v_a(t)$"), ("S", r"componente gigante $S(t)$")]
    lines = {}
    vlines = []
    for ax, (key, ylabel) in zip(line_axes, line_specs):
        ax.set_xlim(0, t_max)
        ax.set_ylim(-0.04, 1.04)
        ax.set_xlabel("tiempo t [pasos]", fontsize=fontsize)
        ax.set_ylabel(ylabel, fontsize=fontsize)
        ax.tick_params(labelsize=fontsize - 3)
        ax.grid(False)
        case_lines = []
        for case, color in zip(loaded, case_colors):
            (line,) = ax.plot([], [], color=color, linewidth=2.0, label=case["label"])
            case_lines.append(line)
        lines[key] = case_lines
        vline = ax.axvline(0.0, color="black", linestyle=":", linewidth=1.4)
        vlines.append(vline)
        ax.legend(loc="upper right", frameon=False, fontsize=fontsize - 4)

    def init():
        artists = list(quivers) + case_texts + vlines
        for key in lines:
            artists += lines[key]
        return artists

    def update(frame_idx):
        artists = []
        for q, txt, case in zip(quivers, case_texts, loaded):
            t = case["ts"][frame_idx]
            particles = case["traj_by_t"][t]
            xs = [p[0] for p in particles]
            ys = [p[1] for p in particles]
            thetas = [p[2] for p in particles]
            us = [drawn_length * math.cos(th) for th in thetas]
            vs = [drawn_length * math.sin(th) for th in thetas]
            q.set_offsets(list(zip(xs, ys)))
            q.set_UVC(us, vs, thetas)
            obs = case["obs_by_t"].get(t)
            va_now = obs["va"] if obs else float("nan")
            txt.set_text(f"{case['label']},  " + r"$v_a(t)$" + f"={va_now:.3f}")
            artists.extend([q, txt])

        current_t = loaded[0]["ts"][frame_idx]
        for key in ("va", "S"):
            for line, case in zip(lines[key], loaded):
                ts = case["ts"][: frame_idx + 1]
                ys = [case["obs_by_t"][t][key] for t in ts]
                line.set_data(ts, ys)
                artists.append(line)
        for vline in vlines:
            vline.set_xdata([current_t, current_t])
            artists.append(vline)
        return artists

    fig.subplots_adjust(left=0.07, right=0.90, top=0.97, bottom=0.10)

    anim = animation.FuncAnimation(fig, update, frames=n_frames, init_func=init,
                                    blit=False, interval=1000 / fps)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out_path), writer=writer, dpi=dpi)
    plt.close(fig)
    print(f"escrito: {out_path} ({n_frames} fotogramas, {n_frames / fps:.1f}s a {fps} fps)")
