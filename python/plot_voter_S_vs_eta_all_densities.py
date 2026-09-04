#!/usr/bin/env python3
"""<S> vs. ruido eta para el votante, las seis densidades juntas (degrade azul->rojo).

Analogo a plot_vicsek_S_vs_eta_all_densities.py: combina en una sola figura
las tres densidades base (rho=2,4,8, grilla de 37 puntos de eta) y las tres
densidades bajas de clusters (rho=1/pi,1/(2pi),1/(3pi), grilla de 14 puntos
-- el bloque de clusters bajos del votante no se amplio a 37 puntos, a
diferencia de Vicsek), leyendo las dos tablas finales consolidadas:

    data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv
    data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_by_combo.csv

Mismo color: degrade azul (densidad mas baja, rho=1/(3pi)) a rojo (densidad
mas alta, rho=8), colormap 'coolwarm', con marcador propio por densidad.
Barras de error = desvio estandar entre las R=20 realizaciones
(S_stdev_between_realizations, definicion ya cerrada para todo el TP).

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_voter_S_vs_eta_all_densities.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "voter_S_vs_eta_all_densities_v1"

BASE_RUN = "final_voter_base_grid_steps3000_R20_v1"
LOWRHO_RUN = "final_lowrho_cluster_grid_steps3000_R20_v1"

# Orden de menor a mayor densidad (define el degrade azul -> rojo).
RHO_ORDER = ["rho_1_over_3pi", "rho_1_over_2pi", "rho_1_over_pi", "rho_2", "rho_4", "rho_8"]
RHO_DISPLAY = {
    "rho_1_over_3pi": r"$\rho=1/(3\pi)$ (N=11)",
    "rho_1_over_2pi": r"$\rho=1/(2\pi)$ (N=16)",
    "rho_1_over_pi": r"$\rho=1/\pi$ (N=32)",
    "rho_2": r"$\rho=2$ (N=200)",
    "rho_4": r"$\rho=4$ (N=400)",
    "rho_8": r"$\rho=8$ (N=800)",
}
RHO_MARKER = {
    "rho_1_over_3pi": "v",
    "rho_1_over_2pi": "D",
    "rho_1_over_pi": "P",
    "rho_2": "o",
    "rho_4": "s",
    "rho_8": "^",
}
CMAP = matplotlib.colormaps["coolwarm"]
RHO_COLOR = {rho: CMAP(i / (len(RHO_ORDER) - 1)) for i, rho in enumerate(RHO_ORDER)}


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def combo_curve(rows, rho_label):
    selected = [r for r in rows if r["model"] == "voter" and r["rho_label"] == rho_label]
    selected.sort(key=lambda r: float(r["eta"]))
    etas = [float(r["eta"]) for r in selected]
    means = [float(r["S_mean"]) for r in selected]
    errs = [float(r["S_stdev_between_realizations"]) for r in selected]
    return etas, means, errs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_rows = read_csv_rows(SUMMARY_DIR / f"{BASE_RUN}_by_combo.csv")
    lowrho_rows = read_csv_rows(SUMMARY_DIR / f"{LOWRHO_RUN}_by_combo.csv")
    rows_by_rho = {
        "rho_2": base_rows, "rho_4": base_rows, "rho_8": base_rows,
        "rho_1_over_pi": lowrho_rows, "rho_1_over_2pi": lowrho_rows, "rho_1_over_3pi": lowrho_rows,
    }

    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 16,
        "axes.grid": False,
        "lines.markersize": 8,
        "lines.linewidth": 1.6,
        "errorbar.capsize": 3,
    })

    fig, ax = plt.subplots(figsize=(11.5, 7.4))
    for rho_label in RHO_ORDER:
        etas, means, errs = combo_curve(rows_by_rho[rho_label], rho_label)
        ax.errorbar(
            etas, means, yerr=errs,
            marker=RHO_MARKER[rho_label], linestyle="-",
            color=RHO_COLOR[rho_label],
            label=RHO_DISPLAY[rho_label],
        )

    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"Componente gigante $\langle S \rangle$")
    ax.set_xlim(-0.15, 6.45)
    ax.set_ylim(-0.02, 1.04)
    ax.grid(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, frameon=False)

    fig.subplots_adjust(left=0.10, right=0.72, top=0.97, bottom=0.12)
    out_path = OUT_DIR / "voter_S_vs_eta_all_densities.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Figura escrita en {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
