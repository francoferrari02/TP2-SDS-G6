#!/usr/bin/env python3
"""S(t) de una unica realizacion del votante, eta={0.05,0.3,1}, rho=1/pi (N=32).

Analogo a plot_vicsek_S_t_eta_1_3_5_lowrho_single_realization.py: grafica la
trayectoria cruda de UNA sola realizacion (realization=0), sin promediar y
sin banda de error. Con N=32 el tamano del mayor cluster solo puede tomar
valores discretos k/32, por lo que S(t) de una realizacion aislada tiene
forma de escalera (mesetas horizontales entre eventos de fusion/ruptura de
cluster).

Lee directamente los observables.csv crudos ya existentes de
final_voter_lowrho_grid_v1 (steps=3000, observables_stride=1), sin volver a
correr el motor ni promediar entre realizaciones.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_voter_S_t_eta_1_3_5_lowrho_single_realization.py
"""

import csv
import sys
from pathlib import Path

import matplotlib.ticker as mticker

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))
from pilot_analyze import read_observables_csv, validate_observables  # noqa: E402

OUT_DIR = REPO_ROOT / "figures" / "voter_S_t_eta_1_3_5_lowrho_single_realization_v1"
SOURCE_RUN = "final_voter_lowrho_grid_v1"
RHO_LABEL = "rho_1_over_pi"
RHO_DISPLAY = "$\\rho=1/\\pi$ (N=32)\nrealización 0"
DPI = 220
Y_LIMITS = (-0.04, 1.04)

SERIES_ETAS = [0.05, 0.30, 1.0]
SERIES_ETA_COLOR = {0.05: "#08519c", 0.30: "#e6550d", 1.0: "#31a354"}
REALIZATION = 0


def find_realization_file(eta: float) -> Path:
    run_dir = REPO_ROOT / "data" / "pilots" / SOURCE_RUN
    for path in sorted(run_dir.rglob("observables.csv")):
        metadata, _ = read_observables_csv(path)
        if (metadata["model"] == "voter" and metadata["rho_label"] == RHO_LABEL
                and abs(float(metadata["eta"]) - eta) < 1e-6
                and int(metadata["realization"]) == REALIZATION):
            return path
    raise SystemExit(f"No se encontro observables.csv para eta={eta}, "
                      f"rho={RHO_LABEL}, realization={REALIZATION}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.size": 21,
        "axes.labelsize": 23,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 19,
        "axes.grid": False,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "lines.linewidth": 1.6,
    })

    fig, ax = plt.subplots(figsize=(16.0, 7.2))
    for eta in SERIES_ETAS:
        path = find_realization_file(eta)
        metadata, rows = read_observables_csv(path)
        problems = validate_observables(path, metadata, rows)
        if problems:
            raise SystemExit(f"{path}: {problems}")
        ts = [r["t"] for r in rows]
        s_vals = [r["S"] for r in rows]
        ax.step(ts, s_vals, where="post", color=SERIES_ETA_COLOR[eta],
                label=rf"$\eta={eta:g}$")

    ax.set_xlabel("tiempo t [pasos]")
    ax.set_ylabel(r"componente gigante $S(t)$")
    ax.set_ylim(*Y_LIMITS)
    ax.set_xlim(0, 3000)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(250))
    ax.grid(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0,
              frameon=False, title=RHO_DISPLAY, title_fontsize=19)

    name = "voter_S_t_rho_1_over_pi_eta_0p05_0p3_1_single_realization.png"
    fig.subplots_adjust(left=0.06, right=0.76, top=0.95, bottom=0.15)
    fig.savefig(OUT_DIR / name, dpi=DPI)
    plt.close(fig)
    print(f"Escrito: {(OUT_DIR / name).relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
