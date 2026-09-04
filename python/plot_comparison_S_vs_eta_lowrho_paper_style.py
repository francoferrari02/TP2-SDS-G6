#!/usr/bin/env python3
"""Comparacion Vicsek vs. votante, <S> vs. ruido eta, solo densidades bajas.

Analogo a plot_comparison_va_vs_eta_paper_style.py, pero para la componente
gigante <S> en vez de <va>, restringido a las tres densidades bajas de
clusters (rho=1/pi,1/(2pi),1/(3pi), grilla de 37 puntos de eta, ambos
modelos), leyendo la tabla final consolidada:

    data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_by_combo.csv

Convencion de color: Vicsek en tonos de violeta, votante en tonos de verde;
dentro de cada modelo, el tono se oscurece con la densidad (mas claro =
rho=1/(3pi), mas oscuro = rho=1/pi). El marcador identifica la densidad
(triangulo=1/(3pi), diamante=1/(2pi), cruz gruesa=1/pi), igual que en
plot_vicsek_S_vs_eta_all_densities.py / plot_voter_S_vs_eta_all_densities.py.

Barras de error = desvio estandar entre las R=20 realizaciones
(S_stdev_between_realizations, definicion ya cerrada para todo el TP). Sin
titulo interno, leyenda sin marco.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_comparison_S_vs_eta_lowrho_paper_style.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "comparison_S_vs_eta_lowrho_paper_style_v1"

LOWRHO_RUN = "final_lowrho_cluster_grid_steps3000_R20_v1"

# Orden de menor a mayor densidad (define el degrade claro -> oscuro).
RHO_ORDER = ["rho_1_over_3pi", "rho_1_over_2pi", "rho_1_over_pi"]
RHO_MARKER = {"rho_1_over_3pi": "v", "rho_1_over_2pi": "D", "rho_1_over_pi": "P"}
RHO_DISPLAY = {
    "rho_1_over_3pi": r"$\rho=1/(3\pi)$",
    "rho_1_over_2pi": r"$\rho=1/(2\pi)$",
    "rho_1_over_pi": r"$\rho=1/\pi$",
}

# Vicsek: tonos de violeta (claro -> oscuro con la densidad).
# Votante: tonos de verde (claro -> oscuro con la densidad).
MODEL_COLOR = {
    "vicsek": {"rho_1_over_3pi": "#d4b9da", "rho_1_over_2pi": "#9970ab", "rho_1_over_pi": "#631879"},
    "voter": {"rho_1_over_3pi": "#a1d99b", "rho_1_over_2pi": "#41ab5d", "rho_1_over_pi": "#00441b"},
}
MODEL_LINESTYLE = {"vicsek": "-", "voter": "--"}
MODEL_DISPLAY = {"vicsek": "Vicsek", "voter": "Votante"}


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def combo_curve(rows, model, rho_label):
    selected = [r for r in rows if r["model"] == model and r["rho_label"] == rho_label]
    selected.sort(key=lambda r: float(r["eta"]))
    etas = [float(r["eta"]) for r in selected]
    means = [float(r["S_mean"]) for r in selected]
    errs = [float(r["S_stdev_between_realizations"]) for r in selected]
    return etas, means, errs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_csv_rows(SUMMARY_DIR / f"{LOWRHO_RUN}_by_combo.csv")

    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 17,
        "axes.grid": False,
        "lines.markersize": 9,
        "lines.linewidth": 1.8,
        "errorbar.capsize": 3,
    })

    fig, ax = plt.subplots(figsize=(12.5, 7.4))
    for model in ("vicsek", "voter"):
        for rho_label in RHO_ORDER:
            etas, means, errs = combo_curve(rows, model, rho_label)
            ax.errorbar(
                etas, means, yerr=errs,
                marker=RHO_MARKER[rho_label], linestyle=MODEL_LINESTYLE[model],
                color=MODEL_COLOR[model][rho_label],
                label=f"{MODEL_DISPLAY[model]}, {RHO_DISPLAY[rho_label]}",
            )

    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"Componente gigante $\langle S \rangle$")
    ax.set_xlim(-0.15, 6.45)
    ax.set_ylim(-0.02, 1.04)
    ax.grid(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, frameon=False)

    fig.subplots_adjust(left=0.08, right=0.62, top=0.97, bottom=0.12)
    out_path = OUT_DIR / "comparison_S_vs_eta_lowrho_paper_style.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Figura escrita en {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
