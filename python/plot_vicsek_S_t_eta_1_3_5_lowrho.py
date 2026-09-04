#!/usr/bin/env python3
"""Serie temporal S(t) de Vicsek con eta={1,3,5}, rho=1/pi (N=32).

Analogo a plot_vicsek_va_t_eta_1_3_5.py (mismo estilo: figura ancha, marcas
del eje x cada 250 pasos, sin marcar t_eq, banda = desvio estandar entre las
R=20 realizaciones en cada instante t), pero para la fraccion del mayor
cluster S(t) en vez de va(t), y con la densidad baja rho=1/pi en vez de
rho=2,4,8.

Lee exclusivamente
data/summary/vicsek_S_t_eta_1_3_5_lowrho_v1_series_sampled.csv (ver
python/vicsek_S_t_eta_1_3_5_lowrho_analyze.py, --sample-stride 10, 300
puntos en 3000 pasos).

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_vicsek_S_t_eta_1_3_5_lowrho.py
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.ticker as mticker

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "vicsek_S_t_eta_1_3_5_lowrho_v1"

VICSEK_RUN = "vicsek_S_t_eta_1_3_5_lowrho_v1"
DPI = 220
Y_LIMITS = (-0.04, 1.04)

RHO_LABEL = "rho_1_over_pi"
RHO_DISPLAY = r"$\rho=1/\pi$ (N=32)"

SERIES_ETAS = [1.0, 3.0, 5.0]
SERIES_ETA_COLOR = {1.0: "#08519c", 3.0: "#e6550d", 5.0: "#31a354"}


def apply_style() -> None:
    plt.rcParams.update({
        "font.size": 21,
        "axes.labelsize": 23,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 19,
        "axes.grid": False,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "lines.linewidth": 2.0,
    })


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def plot_time_series(series_rows, out_dir):
    fig, ax = plt.subplots(figsize=(16.0, 7.2))
    by_eta = defaultdict(list)
    for r in series_rows:
        if r["rho_label"] != RHO_LABEL:
            continue
        eta = float(r["eta"])
        for target in SERIES_ETAS:
            if abs(eta - target) < 1e-6:
                by_eta[target].append(r)

    for eta in SERIES_ETAS:
        rows = sorted(by_eta[eta], key=lambda r: int(r["t"]))
        if not rows:
            continue
        ts = [int(r["t"]) for r in rows]
        means = [float(r["S_mean"]) for r in rows]
        stdev = [float(r["S_stdev"]) for r in rows]
        color = SERIES_ETA_COLOR[eta]
        ax.plot(ts, means, color=color, linestyle="-", label=rf"$\eta={eta:g}$")
        ax.fill_between(ts,
                        [m - s for m, s in zip(means, stdev)],
                        [m + s for m, s in zip(means, stdev)],
                        color=color, alpha=0.20, linewidth=0)

    ax.set_xlabel("tiempo t [pasos]")
    ax.set_ylabel(r"fracción del mayor cluster $S(t)$")
    ax.set_ylim(*Y_LIMITS)
    ax.set_xlim(0, 3000)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(250))
    ax.grid(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0,
              frameon=False, title=RHO_DISPLAY, title_fontsize=19)

    name = "vicsek_S_t_rho_1_over_pi_eta_1_3_5.png"
    fig.tight_layout(rect=(0.0, 0.0, 0.80, 1.0))
    fig.savefig(out_dir / name, dpi=DPI)
    plt.close(fig)
    print(f"  {name}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    apply_style()
    series = read_csv_rows(SUMMARY_DIR / f"{VICSEK_RUN}_series_sampled.csv")

    print(f"Escribiendo figuras en {OUT_DIR.relative_to(REPO_ROOT)}:")
    plot_time_series(series, OUT_DIR)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
