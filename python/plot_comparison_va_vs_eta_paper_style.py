#!/usr/bin/env python3
"""Comparacion Vicsek vs. votante, polarizacion <v_a> vs. ruido eta, estilo "paper".

Combina en una sola figura las seis curvas de
plot_vicsek_va_vs_eta_paper_style.py y plot_voter_va_vs_eta_paper_style.py
(rho=2,4,8 de cada modelo), leyendo las mismas dos tablas finales
consolidadas (grilla de 37 puntos de eta, rho=2,4,8):

    data/summary/final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv
    data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv

Convencion de color: Vicsek en tonos de violeta, votante en tonos de verde;
dentro de cada modelo, el tono se oscurece con la densidad
(mas claro = rho=2, mas oscuro = rho=8). El marcador identifica la densidad
igual que en las figuras individuales (triangulo=rho=8, cuadrado=rho=4,
circulo=rho=2) y el estilo de linea identifica el modelo (solido=Vicsek,
punteado=votante), como refuerzo redundante ademas del color.

Barras de error = desvio estandar entre las R=20 realizaciones
(va_stdev_between_realizations, definicion de barra ya cerrada para todo el
TP). Sin titulo interno, leyenda sin marco.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_comparison_va_vs_eta_paper_style.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "comparison_va_vs_eta_paper_style_v1"

VICSEK_RUN = "final_vicsek_base_grid_steps3000_R20_v1"
VOTER_RUN = "final_voter_base_grid_steps3000_R20_v1"

RHO_ORDER = ["rho_8", "rho_4", "rho_2"]
RHO_MARKER = {"rho_8": "^", "rho_4": "s", "rho_2": "o"}
RHO_DISPLAY = {"rho_8": r"$\rho=8$", "rho_4": r"$\rho=4$", "rho_2": r"$\rho=2$"}

# Vicsek: tonos de violeta (claro -> oscuro con la densidad).
# Votante: tonos de verde (claro -> oscuro con la densidad).
MODEL_COLOR = {
    "vicsek": {"rho_2": "#dadaeb", "rho_4": "#9e9ac8", "rho_8": "#3f007d"},
    "voter": {"rho_2": "#c7e9c0", "rho_4": "#74c476", "rho_8": "#00441b"},
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
    means = [float(r["va_mean"]) for r in selected]
    errs = [float(r["va_stdev_between_realizations"]) for r in selected]
    return etas, means, errs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables = {
        "vicsek": read_csv_rows(SUMMARY_DIR / f"{VICSEK_RUN}_by_combo.csv"),
        "voter": read_csv_rows(SUMMARY_DIR / f"{VOTER_RUN}_by_combo.csv"),
    }

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

    fig, ax = plt.subplots(figsize=(9.5, 7.4))
    for model in ("vicsek", "voter"):
        for rho_label in RHO_ORDER:
            etas, means, errs = combo_curve(tables[model], model, rho_label)
            ax.errorbar(
                etas, means, yerr=errs,
                marker=RHO_MARKER[rho_label], linestyle=MODEL_LINESTYLE[model],
                color=MODEL_COLOR[model][rho_label],
                label=f"{MODEL_DISPLAY[model]}, {RHO_DISPLAY[rho_label]}",
            )

    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"Polarización $v_a$")
    ax.set_xlim(-0.15, 6.45)
    ax.set_ylim(-0.02, 1.04)
    ax.grid(False)
    ax.legend(loc="upper right", frameon=False, ncol=2, fontsize=16)

    fig.tight_layout()
    out_path = OUT_DIR / "comparison_va_vs_eta_paper_style.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Figura escrita en {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
