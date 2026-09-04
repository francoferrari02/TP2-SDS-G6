#!/usr/bin/env python3
"""Genera polarizacion <v_a> vs ruido eta para el votante, estilo "paper".

Analogo a plot_vicsek_va_vs_eta_paper_style.py: lee
data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv (tabla final
consolidada, grilla de 37 puntos de eta) y grafica una curva por densidad
(rho=2,4,8), con marcador distinto por densidad, barras de error = desvio
estandar entre las R=20 realizaciones (va_stdev_between_realizations, la
definicion de barra ya cerrada para todo el TP en DECISIONES_PENDIENTES.md),
sin titulo interno, leyenda sin marco.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_voter_va_vs_eta_paper_style.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "voter_va_vs_eta_paper_style_v1"

VOTER_RUN = "final_voter_base_grid_steps3000_R20_v1"

RHO_ORDER = ["rho_8", "rho_4", "rho_2"]
RHO_DISPLAY = {"rho_8": r"$\rho=8$", "rho_4": r"$\rho=4$", "rho_2": r"$\rho=2$"}
RHO_COLOR = {"rho_8": "#7b3294", "rho_4": "#e08214", "rho_2": "#2ca02c"}
RHO_MARKER = {"rho_8": "^", "rho_4": "s", "rho_2": "o"}


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def combo_curve(rows, rho_label):
    selected = [r for r in rows if r["model"] == "voter" and r["rho_label"] == rho_label]
    selected.sort(key=lambda r: float(r["eta"]))
    etas = [float(r["eta"]) for r in selected]
    means = [float(r["va_mean"]) for r in selected]
    errs = [float(r["va_stdev_between_realizations"]) for r in selected]
    return etas, means, errs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_csv_rows(SUMMARY_DIR / f"{VOTER_RUN}_by_combo.csv")

    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 20,
        "axes.grid": False,
        "lines.markersize": 9,
        "lines.linewidth": 1.8,
        "errorbar.capsize": 3,
    })

    fig, ax = plt.subplots(figsize=(8.5, 6.8))
    for rho_label in RHO_ORDER:
        etas, means, errs = combo_curve(rows, rho_label)
        ax.errorbar(etas, means, yerr=errs,
                    marker=RHO_MARKER[rho_label], linestyle="-",
                    color=RHO_COLOR[rho_label],
                    label=RHO_DISPLAY[rho_label])

    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"Polarización $v_a$")
    ax.set_xlim(-0.15, 6.45)
    ax.set_ylim(-0.02, 1.04)
    ax.grid(False)
    ax.legend(loc="upper right", frameon=False)

    fig.tight_layout()
    out_path = OUT_DIR / "voter_va_vs_eta_paper_style.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Figura escrita en {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
